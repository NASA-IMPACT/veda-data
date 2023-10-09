from os.path import basename
from typing import Optional
from urllib.parse import urlparse


def generate_yearly_fwi_metrics_key(
    src_url: str,
    dst_version: str,
    ensemble: str = "mme",
    pub_type: str = "netcdf",
    metric: Optional[str] = None,
    verbose: bool = False,
):
    """_summary_
    Generate the object key prefix to use when publishing a NetCDF from the
        staging bucket to the destination publication bucket.

    Args:
        src_url (str): full s3 url of the file staged for publication, i.e. s3://cmip6-staging/Sample/FWI/Yearly/MME/MME50_ssp245_fwi_metrics_yearly_2100.nc
        dst_version (str): data version to use for publication bucket key prefix
    """
    # Only dealing with yearly data at this point
    cadence = "yearly"

    parsed = urlparse(src_url, allow_fragments=False)
    nc_base = basename(parsed.path)

    # Assume pattern ensemble-stat_experiment_fwi_metrics_yearly_yyyy
    # MME50_ssp245_fwi_metrics_yearly_2100
    name_parts = nc_base.split("_")
    # For now just test that this is probably the filename format we expect,
    # this should be a regex match
    assert (len(name_parts)) == 6

    ensemble_stat = name_parts[0]
    experiment = name_parts[1]
    year = name_parts[-1].replace(".nc", "")

    if pub_type == "cog":
        # A metric must be supplied for COG outputs
        assert metric
        # Add additional information about the FWI metric to the data storage structure
        cog_base = nc_base.replace(".nc", f"_{metric}.tif")
        key = (
            f"{dst_version}/{pub_type}/fwi/{ensemble}/{ensemble_stat}/{cadence}/{experiment}/{year}/{cog_base}"
        ).lower()
    else:
        key = (
            f"{dst_version}/{pub_type}/fwi/{ensemble}/{ensemble_stat}/{cadence}/{experiment}/{year}/{nc_base}"
        ).lower()

    if verbose:
        print(key)
    return key


if __name__ == "__main__":

    def _test_generate_yearly_fwi_metrics_key():
        """Confirm keys are as expected"""
        # check projected experiment
        src_url = "s3://cmip6-staging/Sample/FWI/Yearly/MME/MME50_ssp245_fwi_metrics_yearly_2100.nc"

        # netcdf
        netcdf_key = generate_yearly_fwi_metrics_key(src_url, "v0", verbose=True)
        assert (
            netcdf_key == "v0/netcdf/fwi/mme/mme50/yearly/ssp245/2100/"
            "mme50_ssp245_fwi_metrics_yearly_2100.nc"
        )

        # cog
        cog_key = generate_yearly_fwi_metrics_key(
            src_url, "v0", pub_type="cog", metric="ffmc", verbose=True
        )
        assert (
            cog_key == "v0/cog/fwi/mme/mme50/yearly/ssp245/2100/"
            "mme50_ssp245_fwi_metrics_yearly_2100_ffmc.tif"
        )

        # check historical experiment
        src_url = "s3://cmip6-staging/Sample/FWI/Yearly/MME/MME50_historical_fwi_metrics_yearly_1950.nc"

        # netcdf
        netcdf_key = generate_yearly_fwi_metrics_key(src_url, "v0", verbose=True)
        assert (
            netcdf_key == "v0/netcdf/fwi/mme/mme50/yearly/historical/1950/"
            "mme50_historical_fwi_metrics_yearly_1950.nc"
        )

        # cog
        cog_key = generate_yearly_fwi_metrics_key(
            src_url, "v0", pub_type="cog", metric="dc", verbose=True
        )
        assert (
            cog_key == "v0/cog/fwi/mme/mme50/yearly/historical/1950/"
            "mme50_historical_fwi_metrics_yearly_1950_dc.tif"
        )

    _test_generate_yearly_fwi_metrics_key()
