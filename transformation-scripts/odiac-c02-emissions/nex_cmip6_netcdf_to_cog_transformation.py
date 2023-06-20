import json
import boto3
import xarray
import pandas as pd
from io import StringIO
import tempfile
import s3fs

profile_name = ""
session = boto3.session.Session(profile_name=profile_name)


s3_client = session.client("s3")
SOURCE_S3_BUCKET = "nex-gddp-cmip6"
TARGET_S3_BUCKET = "cmip6-staging"
CSV_FILE_NAME = "gddp-cmip6-files.csv"

var1 = "ACCESS-CM2"
var2 = "ACCESS-CM2/historical/r1i1p1f1/hurs"

source_data = s3_client.get_object(Bucket=SOURCE_S3_BUCKET, Key=CSV_FILE_NAME)
# Fetching .csv file from our bucket to compare the files processed.
target_data = s3_client.get_object(Bucket=TARGET_S3_BUCKET, Key=CSV_FILE_NAME)

source_file_names = pd.read_csv(StringIO(source_data["Body"].read().decode("utf-8")))
target_file_names = pd.read_csv(StringIO(target_data["Body"].read().decode("utf-8")))


# Comparing both .csv files to check which files are already processed.
data_to_be_processed = source_file_names.merge(
    target_file_names, how="outer", indicator=True
).loc[lambda x: x["_merge"] == "left_only"]
data_to_be_processed.reset_index(inplace=True)
data_to_be_processed = source_file_names.merge(
    target_file_names, how="outer", indicator=True
).loc[lambda x: x["_merge"] == "left_only"]


data_to_be_processed.reset_index(drop=True, inplace=True)

# Comment the above line and uncomment below to test run the script for single model or single variable
# Use var1 for testing one model
# use var2 for testing one model and one variable
# data_to_be_processed = source_file_names[
#     source_file_names[" fileURL"].str.contains(var2)
# ]
# data_to_be_processed.reset_index(drop=True, inplace=True)

# Looping over the file names to transform the remaining files.
for index in range(len(data_to_be_processed)):
    s3_key = data_to_be_processed[" fileURL"].iloc[index][51:]
    filename = s3_key.split("/")[-1]

    filename_elements = filename.split("_")

    # Variable name, used to access the data in the NetCDF
    variable = filename_elements[0]

    # timestep (month, day or year). Used to determine
    # the format of the date element of the filename
    # for the generated COG. (year) dateformat is ignored
    # since the API only supports daily and monthly data
    # for the time being
    timestep = filename_elements[1]

    date_fmt = None
    if timestep == "day":
        date_fmt = "%Y%m%d"
    elif timestep == "monthly":
        date_fmt = "%Y%m"
    elif timestep == "CrossingYear":
        pass
    else:
        raise ValueError(f"Unrecognized date format in key: {s3_key}")

    fs = s3fs.S3FileSystem(profile=profile_name)

    with fs.open(f"s3://{SOURCE_S3_BUCKET}/{s3_key}") as infile:
        xds = xarray.open_dataset(infile, engine="h5netcdf")
        xds = xds.assign_coords(lon=(((xds.lon + 180) % 360) - 180)).sortby("lon")

        for time_increment in range(0, len(xds.time)):
            # slice out each time_increment (either day or month) of the var
            data = getattr(xds.isel(time=time_increment), variable)
            data = data.isel(lat=slice(None, None, -1))
            data.rio.set_spatial_dims("lon", "lat", inplace=True)
            data.rio.write_crs("epsg:4326", inplace=True)

            # get date from slice
            date = data.time.dt.strftime(date_fmt).item(0)
            # # insert date of generated COG into filename
            filename_elements[-1] = date
            cog_filename = "_".join(filename_elements)
            # # add extension
            cog_filename = f"{cog_filename}.tif"
            cog_filepath = "/".join(s3_key.split("/")[:-1])

            with tempfile.NamedTemporaryFile() as temp_file:
                data.rio.to_raster(
                    temp_file.name,
                    driver="COG",
                )
                s3_client.upload_file(
                    Filename=temp_file.name,
                    Bucket=TARGET_S3_BUCKET,
                    Key=f"{cog_filepath}/{cog_filename}",
                )

            print(f"Generated and saved COG: {cog_filename}")

        print("Done generating COGs")

        target_file_names = target_file_names._append(
            {
                "fileMD5": data_to_be_processed["fileMD5"].iloc[index],
                " fileURL": data_to_be_processed[" fileURL"].iloc[index],
            },
            ignore_index=True,
        )

        target_file_names.to_csv(
            f"s3://{TARGET_S3_BUCKET}/{CSV_FILE_NAME}",
            storage_options={"profile": profile_name},
        )
        with tempfile.NamedTemporaryFile(mode="w+") as fp:
            json.dump(xds.attrs, fp)
            json.dump({"data_dimensions": dict(xds.dims)}, fp)
            json.dump({"data_variables": list(xds.data_vars)}, fp)
            fp.flush()

            s3_client.upload_file(
                Filename=fp.name,
                Bucket=TARGET_S3_BUCKET,
                Key="ODIAC_COGs/{cog_filename}_metadata.json",
            )
