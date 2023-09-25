import os, sys
from osgeo import gdal

def get_bbox(ds):
    geoTransform = ds.GetGeoTransform()
    minx = geoTransform[0]
    maxy = geoTransform[3]
    maxx = minx + geoTransform[1] * ds.RasterXSize
    miny = maxy + geoTransform[5] * ds.RasterYSize
    return minx, miny, maxx, maxy

def split_to_tiles(file_name):
    ds = gdal.Open(file_name, gdal.gdalconst.GA_ReadOnly)
    width = ds.RasterXSize
    height = ds.RasterYSize
    print(width, 'x', height)
    tilesize = 11000
    for i in range(0, width, tilesize):
        for j in range(0, height, tilesize):
            w = min(i+tilesize, width) - i
            h = min(j+tilesize, height) - j
            gdaltranString = "gdal_translate -of GTIFF -srcwin " + str(i) +
                             ", " + str(j) + ", " + str(w) + ", " + str(h) +
                             " " + file_name + " " +
                             "_" + str(i) + "_" + str(j) + ".tif"
            os.system(gdaltranString)

#Clipping larger raster to extent of a smaller one:
#1. Get shapefile with smaller raster extent
#gdalindex clipper.shp CCI_agb2018_uk_20m.tif
#2. Cut the larger one
#gdalwarp -cutline clipper.shp -crop_to_cutline LCD_2018.tif clipped_lc.tif
