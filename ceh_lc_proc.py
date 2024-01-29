import os
import glob
import tomli
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
import spatial as sp
from pathlib import Path
from osgeo import gdal
from scipy.ndimage import binary_erosion

# from rasterstats import zonal_stats
from configuration import config


def file_name_without_extension(file_name):
    """Return file name without extension"""
    file_path = Path(file_name)
    file_name_wt_ext = file_path.stem
    return file_name_wt_ext


def sampled_lc_file_path(
    lc: int, window_size: int, data_dir: str, land_cover_file_name: str
):
    """Return path of eroded pixels for the given land cover"""
    file_base_str = file_name_without_extension(land_cover_file_name)
    file_name = file_base_str + f"_sampled_eroded_{window_size}_lc_{lc}.parquet"
    file_path = Path(data_dir, file_name)
    return file_path


def eroded_lc_file_path(
    lc: int, window_size: int, data_dir: str, land_cover_file_name: str
):
    """Return path of eroded pixels for the given land cover"""
    file_base_str = file_name_without_extension(land_cover_file_name)
    file_name = file_base_str + f"_eroded_{window_size}_lc_{lc}.parquet"
    file_path = Path(data_dir, file_name)
    return file_path


def sample_lc_regions(dfr, sample_size):
    # First check counts per region
    gdfr = dfr.groupby("Region")
    sampled = gdfr.apply(lambda x: x.sample(min(len(x), sample_size)))
    return sampled.reset_index(drop=True)


def split_to_tiles(file_name):
    file_name_wt_ext = file_name_without_extension(file_name)
    ds = gdal.Open(file_name, gdal.GA_ReadOnly)
    width = ds.RasterXSize
    height = ds.RasterYSize
    print(width, "x", height)
    tilesize = 11000
    for i in range(0, width, tilesize):
        for j in range(0, height, tilesize):
            w = min(i + tilesize, width) - i
            h = min(j + tilesize, height) - j
            gdaltranString = (
                "gdal_translate -of GTIFF -srcwin "
                + str(i)
                + ", "
                + str(j)
                + ", "
                + str(w)
                + ", "
                + str(h)
                + " "
                + file_name
                + " "
                + file_name_wt_ext
                + "_"
                + str(i)
                + "_"
                + str(j)
                + ".tif"
            )
            os.system(gdaltranString)


def ceh_tiles_region_value_counts(
    data_dir: str, land_cover_file_name: str
) -> pd.DataFrame:
    """
    Iteratively reads CEH land cover raster tiles found in data_dir that match
    file_base_* and compiles land cover value counts into a single results
    """
    file_base = file_name_without_extension(land_cover_file_name)
    tiles = glob.glob(str(Path(data_dir, file_base + "_*.tif")))
    regions_file = config["regions_file"]
    regions_dfr = gpd.read_file(regions_file)
    regions = regions_dfr.Region.values
    data = {}
    for region in regions:
        data[region] = np.zeros(21)
    dfr = pd.DataFrame(data, index=range(1, 22, 1))
    for tile in tiles:
        print(tile)
        stats = zonal_stats(regions_file, tile, categorical=True)
        for nr, region in enumerate(regions):
            for lc in range(1, 22, 1):
                try:
                    dfr.loc[lc, region] += stats[nr][lc]
                except KeyError:
                    pass
        print(dfr.max())
    return dfr


def ceh_tiles_binary_erosion(
    lc: int, window_size: int, data_dir: str, land_cover_file_name: str
):
    """
    Reads CEH land cover raster tiles found in data_dir that match
    file_base_*, selects pixels that equal the lc argument, performs
    binary errosion using window_size and saves the remaining
    data to dataframe.
    """
    dfrs = []
    file_base = file_name_without_extension(land_cover_file_name)
    tiles = glob.glob(str(Path(data_dir, file_base + "_*.tif")))
    print(lc)
    for tile in tiles:
        print(tile)
        lc_prod = xr.open_rasterio(tile)
        lc_prod = lc_prod.squeeze("band")
        lc_prod = lc_prod.drop("band")
        values = lc_prod.where(lc_prod == lc, other=0).values
        print(values.max())
        eroding_block = np.ones((window_size, window_size))
        values_eroded = binary_erosion(
            values.squeeze(), structure=eroding_block
        ).astype(int)
        print(values_eroded.max())
        lc_prod.values = values_eroded
        dfr = lc_prod.to_dataframe(name="lc")
        dfr = dfr[dfr.lc > 0]
        dfr["lc"] = lc
        print(dfr.shape)
        if dfr.shape[0] == 0:
            continue
        dfrs.append(dfr)
    done = pd.concat(dfrs)
    done.to_parquet(
        eroded_lc_file_path(lc, window_size, data_dir, land_cover_file_name)
    )


def percent_cover(dfr: pd.DataFrame, lcs: list[int]) -> pd.DataFrame:
    """Calculate percent area coverage by region by the land covers listed in lcs"""
    total = dfr.sum(axis=0)
    lcs_cover = dfr.loc[lcs, :].sum(axis=0)
    return lcs_cover / total


if __name__ == "__main__":
    pass
    # To split CEH product to tiles.
    # cur_dir = os.getcwd()
    # os.chdir(config['data_dir'])
    # split_to_tiles(config['land_cover_file_name'])
    # os.chdir(cur_dir)
    # Perform lc value counts per region
    # dfr = ceh_tiles_region_value_counts(
    #     config["data_dir"], config["land_cover_file_name"]
    # )
    # dfr.to_parquet(Path(config["data_dir"], "lc_counts_per_region.parquet"))
    dfr = pd.read_parquet(Path(config["data_dir"], "lc_counts_per_region.parquet"))

    """
    # perform binary errosion on lc tiles
    for lc in config['land_covers']:
        ceh_tiles_binary_erosion(lc,
                                 config['window_size'],
                                 config['data_dir'],
                                 config['land_cover_file_name'])

    """
    # reproject and add UK precipitation region column
    """
    for lc in config['land_covers']:
        file_path = eroded_lc_file_path(lc,
                                        config['window_size'],
                                        config['data_dir'],
                                        config['land_cover_file_name'])

        dfr = pd.read_parquet(file_path)
        dfr = sp.osgb_to_lonlat(dfr)
        dfr = sp.get_UK_climate_region(dfr, config['regions_file'])
        dfr.to_parquet(file_path)
        sdfr = sample_lc_regions(dfr, 10000)
        out_path = sampled_lc_file_path(lc,
                                        config['window_size'],
                                        config['data_dir'],
                                        config['land_cover_file_name'])
        sdfr.to_parquet(out_path)
        """
