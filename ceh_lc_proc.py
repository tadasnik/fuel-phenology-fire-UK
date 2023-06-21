import os
import glob
import pyproj
import numpy as np
import xarray as xr
import pandas as pd
import geopandas as gpd
from pathlib import Path
from osgeo import gdal
from scipy.ndimage import binary_erosion


# Reproject and get UK region
def osgb_to_lonlat(dfr):
    dfr = dfr.reset_index()
    transformer = pyproj.Transformer.from_crs("EPSG:27700", "EPSG:4326",
                                              always_xy=True)
    dfr['longitude'], dfr['latitude'] = transformer.transform(dfr['x'],
                                                              dfr['y'])
    dfr = dfr.drop(['x', 'y'], axis=1)
    return dfr


def get_UK_climate_region(dfr, data_path):
    regions = gpd.read_file(Path(data_path, 'HadUKP_regions.shp'))
    regions = regions.set_crs('EPSG:27700')
    regions = regions.to_crs('EPSG:4326')
    geometry = gpd.points_from_xy(dfr.longitude, dfr.latitude)
    gdf = gpd.GeoDataFrame(dfr, geometry=geometry, crs=4326)
    pts = gpd.sjoin(regions, gdf)
    pts = pts.drop(['geometry', 'index_right'], axis=1)
    df = pd.DataFrame(pts)
    return df


def sample_regions(file_name, data_path, sample_size):
    dfr = pd.read_parquet(Path(data_path, file_name)).reset_index()
    if dfr.shape[0] > 50000000:
        dfr = dfr.sample(n=50000000)
    dfr = get_UK_climate_region(dfr)
    dfr_sample = dfr.groupby('Region') \
                    .sample(n=sample_size, replace=True) \
                    .reset_index(drop=True)
    return dfr_sample


def split_to_tiles(file_name):
    file_path = Path(file_name)
    file_name_wt_ext = file_path.with_suffix("")
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
                            " " + file_name + " " + str(file_name_wt_ext) + \
                            "_" + str(i) + "_" + str(j) + ".tif"
            os.system(gdaltranString)


def ceh_tiles_binary_erosion(lc: int, window_size: int, data_path: str, file_base: str):
    """
    Reads CEH land cover raster tiles found in data_path that match file_base_*,
    selects pixels that equal the lc argument, performs binary errosion using
    window_size and saves the remaining data to dataframe.
    """
    dfrs = []
    tiles = glob.glob(str(Path(data_path, file_base + '_*.tif')))
    #tiles = [x.split('2018')[1] for x in agb_tiles]
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
    done.to_parquet(Path(data_path, file_base + f'_eroded_{window_size}_lc_{lc}.parquet'))


def sample_lc_region(lc, data_path, file_base, window_size):
    dfr = pd.read_parquet(Path(data_path, file_base +
                               f'_eroded_{window_size}_lc_{lc}.parquet'))
    dfr = osgb_to_lonlat(dfr)
    dfr = get_UK_region(dfr)




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

data_dir = '/Users/tadas/modFire/fire_lc_ndvi/data/cehlc'
# To split CEH product to tiles.
# file_name = "LCD_2018.tif"
# cur_dir = os.getcwd()
# os.chdir(data_dir)
# split_to_tiles(file_name)
# os.chdir(cur_dir)

# perform binary errosion on lc tiles
# for lc in [1, 2, 3, 4, 7, 9, 10, 11]:
#     ceh_tiles_binary_erosion(lc, 5, data_dir, 'LCD_2018')






