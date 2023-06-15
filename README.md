# veda-data

This repo houses data used to define a VEDA dataset.

For information on how this data gets consumed by the VEDA data ingestion system, see [veda-data-airflow](https://github.com/NASA-IMPACT/veda-data-airflow).

The VEDA user docs explain the [dataset ingestion process](https://nasa-impact.github.io/veda-docs/contributing/dataset-ingestion/).

# Information about the scripts.
The repository contain multiple scripts to convert different types of netCDF or geotiff files to COGs. Below is the information about the scripts present in the repo:

* **odiac_netcdf_to_cog_transformation** : You need to download the netcdf ODIAC dataset from  https://db.cger.nies.go.jp/dataset/ODIAC/DL_odiac2022.html . Once downloaded, we can use this script to convert the raw netCDFs into COGs. For tracking purposes, this script also creates a csv file which contains the names of the all the files that have been transformed from the given dataset. A JSON file is also created which contains the metadata from the dataset.

* **odiac_geotiff_to_cog_transformation** : You need to download the ODIAC dataset from  https://db.cger.nies.go.jp/dataset/ODIAC/DL_odiac2022.html . Once downloaded, we can use this script to convert the geotiffs into COGs. For tracking purposes, this script also creates a csv file which contains the names of the all the files that have been transformed from the given dataset. The dataset does not provide any meaningful metadata that could be stored into a json file.

* **nex_cmip6_netcdf_to_cog_transformation** : The code directly reads the CMIP6 netcdf files from the NEX bucket and transforms them into COGs. The transformed COGs are then stored into the bucket specified in the code (for now it is cmip6-staging in the covid response AWS account). The code also allows us to keep a track of files that have been converted by storing their names in a .csv file which is then cross checked with the csv file that is present in the NEX bucket. Only the files which have not been previously transformed are read from the bucket and transformed when we run the code.
## In progress



