import os
import glob
import tomli
import numpy as np
import xarray as xr
import pandas as pd
import spatial as sp
from pathlib import Path
from osgeo import gdal
from scipy.ndimage import binary_erosion


def file_name_without_extension(file_name):
    """Return file name without extension"""
    file_path = Path(file_name)
    file_name_wt_ext = file_path.stem
    return file_name_wt_ext


def sampled_lc_file_path(lc: int,
                         window_size: int,
                         data_dir: str,
                         land_cover_file_name: str):
    """Return path of eroded pixels for the given land cover"""
    file_base_str = file_name_without_extension(land_cover_file_name)
    file_name = file_base_str + f'_sampled_eroded_{window_size}_lc_{lc}.parquet'
    file_path = Path(data_dir, file_name)
    return file_path


def eroded_lc_file_path(lc: int,
                        window_size: int,
                        data_dir: str,
                        land_cover_file_name: str):
    """Return path of eroded pixels for the given land cover"""
    file_base_str = file_name_without_extension(land_cover_file_name)
    file_name = file_base_str + f'_eroded_{window_size}_lc_{lc}.parquet'
    file_path = Path(data_dir, file_name)
    return file_path


def sample_lc_regions(dfr, sample_size):
    # First check counts per region
    gdfr = dfr.groupby('Region')
    sampled = gdfr.apply(lambda x: x.sample(min(len(x), sample_size)))
    return sampled.reset_index(drop=True)


def split_to_tiles(file_name):
    file_name_wt_ext = file_name_without_extension(file_name)
    ds = gdal.Open(file_name, gdal.GA_ReadOnly)
    width = ds.RasterXSize
    height = ds.RasterYSize
    print(width, 'x', height)
    tilesize = 11000
    for i in range(0, width, tilesize):
        for j in range(0, height, tilesize):
            w = min(i+tilesize, width) - i
            h = min(j+tilesize, height) - j
            gdaltranString = "gdal_translate -of GTIFF -srcwin " + str(i) + \
                             ", " + str(j) + ", " + str(w) + ", " + str(h) + \
                             " " + file_name + " " + file_name_wt_ext + \
                             "_" + str(i) + "_" + str(j) + ".tif"
            os.system(gdaltranString)


def ceh_tiles_binary_erosion(lc: int,
                             window_size: int,
                             data_dir: str,
                             land_cover_file_name: str):
    """
    Reads CEH land cover raster tiles found in data_dir that match
    file_base_*, selects pixels that equal the lc argument, performs
    binary errosion using window_size and saves the remaining
    data to dataframe.
    """
    dfrs = []
    file_base = file_name_without_extension(land_cover_file_name)
    tiles = glob.glob(str(Path(data_dir, file_base + '_*.tif')))
    print(lc)
    for tile in tiles:
        print(tile)
        lc_prod = xr.open_rasterio(tile)
        lc_prod = lc_prod.squeeze('band')
        lc_prod = lc_prod.drop('band')
        values = lc_prod.where(lc_prod == lc, other=0).values
        print(values.max())
        eroding_block = np.ones((window_size, window_size))
        values_eroded = binary_erosion(values.squeeze(),
                                       structure=eroding_block).astype(int)
        print(values_eroded.max())
        lc_prod.values = values_eroded
        dfr = lc_prod.to_dataframe(name='lc')
        dfr = dfr[dfr.lc > 0]
        dfr['lc'] = lc
        print(dfr.shape)
        if dfr.shape[0] == 0:
            continue
        dfrs.append(dfr)
    done = pd.concat(dfrs)
    done.to_parquet(eroded_lc_file_path(lc, window_size, data_dir, land_cover_file_name))


if __name__ == "__main__":
    ukceh_classes = {
        1: 'Deciduous woodland',
        2: 'Coniferous woodland',
        3: 'Arable',
        4: 'Improve grassland',
        5: 'Neutral grassland',
        6: 'Calcareous grassland',
        7: 'Acid grassland',
        8: 'Fen',
        9: 'Heather',
        10: 'Heather grassland',
        11: 'Bog',
        12: 'Inland rock',
        13: 'Saltwater',
        14: 'Freshwater',
        15: 'Supralittoral rock',
        16: 'Supralittoral sediment',
        17: 'Littoral rock',
        18: 'Littoral sediment',
        19: 'Saltmarsh',
        20: 'Urban',
        21: 'Suburban'
    }

    with open("config.toml", mode="rb") as fp:
        config = tomli.load(fp)
# To split CEH product to tiles.
# cur_dir = os.getcwd()
# os.chdir(config['data_dir'])
# split_to_tiles(config['land_cover_file_name'])
# os.chdir(cur_dir)

# perform binary errosion on lc tiles
    """
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
