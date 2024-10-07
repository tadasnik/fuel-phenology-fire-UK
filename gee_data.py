"""
Functions for querying Google Earth Engine datasets
author: tadasnik@gmail.com
"""

import ee
import ee_extra
from numpy import ndim
from cloudMask import maskClouds
import time
import tomli
import pandas as pd
from pathlib import Path
from rclone_python import rclone

from ceh_lc_proc import sampled_lc_file_path

# ee.Authenticate()
ee.Initialize()


def zonal_stats_no_timestamp(ic, fc, params):
    """Get statistics for image collection ic for features
    in feature collection fc with optional params. Translated
    from gee tutorial.
    """

    # Map the reduceRegions function over the image collection.
    def map_func(img):
        # Select bands (optionally rename), set a datetime & timestamp props.
        img = img.select("b1")

        # Subset points that intersect the given image.
        fcSub = fc.filterBounds(img.geometry())

        # Reduce the image by regions.
        reduced = img.reduceRegions(
            collection=fcSub, reducer=ee.Reducer.mean(), scale=20
        )

        return reduced

    results = ic.map(map_func).flatten()  # .filter(ee.Filter.notNull("b1"))

    return results


def zonal_stats_no_datetime(ic, fc, params):
    """Get statistics for image collection ic for features
    in feature collection fc with optional params. Translated
    from gee tutorial.
    """

    # Map the reduceRegions function over the image collection.
    def map_func(img):
        # Select bands (optionally rename), set a datetime & timestamp props.
        img = img.select("b1")

        # Subset points that intersect the given image.
        fcSub = fc.filterBounds(img.geometry())

        # Reduce the image by regions.
        reduced = img.reduceRegions(
            collection=fcSub, reducer=ee.Reducer.mean(), scale=20
        )

        return reduced

    results = ic.map(map_func).flatten()  # .filter(ee.Filter.notNull("b1"))

    return results


def zonal_stats(ic, fc, params=None):
    """Get statistics for image collection ic for features
    in feature collection fc with optional params. Translated
    from gee tutorial.
    """
    # Initialize internal params dictionary.
    _params = {
        "reducer": ee.Reducer.first(),
        "scale": None,
        "crs": None,
        "bands": None,
        "bandsRename": None,
        "imgProps": None,
        "imgPropsRename": None,
        "datetimeName": "datetime",
        "datetimeFormat": "YYYY-MM-dd HH:mm:ss",
    }

    # Replace initialized params with provided params.
    if params:
        _params.update(params)

    # Set default parameters based on an image representative.
    imgRep = ic.first()
    nonSystemImgProps = ee.Feature(None).copyProperties(imgRep).propertyNames()
    if not _params["bands"]:
        _params["bands"] = imgRep.bandNames()
    if not _params["bandsRename"]:
        _params["bandsRename"] = _params["bands"]
    if not _params["imgProps"]:
        _params["imgProps"] = nonSystemImgProps
    if not _params["imgPropsRename"]:
        _params["imgPropsRename"] = _params["imgProps"]

    # Map the reduceRegions function over the image collection.
    def map_func(img):
        # Select bands (optionally rename), set a datetime & timestamp props.
        # img = (
        #     img.select(_params["bands"], _params["bandsRename"]).set(
        #         _params["datetimeName"], img.date().format(_params["datetimeFormat"])
        #     )
        # )

        # Define final image property dictionary to set in output features.
        # propsFrom = ee.List(_params["imgProps"]).cat(
        #     [_params["datetimeName"], "timestamp"]
        # )
        # propsTo = ee.List(_params["imgPropsRename"]).cat(
        #     [_params["datetimeName"], "timestamp"]
        # )

        # imgProps = img.toDictionary(propsFrom).rename(propsFrom, propsTo)

        # Subset points that intersect the given image.
        fcSub = fc.filterBounds(img.geometry())

        # Reduce the image by regions.
        reduced = img.reduceRegions(
            collection=fcSub,
            reducer=_params["reducer"],
            scale=_params["scale"],
            crs=_params["crs"],
        )

        # Add metadata to each feature.
        mapped = reduced.map(
            lambda f: f.set(
                _params["datetimeName"], img.date().format(_params["datetimeFormat"])
            )
        )
        return mapped

    results = (
        ic.map(map_func).flatten().filter(ee.Filter.notNull(_params["bandsRename"]))
    )
    return results


def gee_features_from_points(dfr):
    features = []
    for ind, row in dfr.iterrows():
        geom = (
            ee.Feature(ee.Geometry.Point([row.longitude, row.latitude]), {"fid": ind})
            .buffer(20)
            .bounds()
        )
        features.append(geom)
    gee_features = ee.FeatureCollection(features)
    return gee_features


def gee_VNP09GA_to_drive(gee_features, out_dir, file_name, selectors):

    start_date = "2013-01-01"
    end_date = "2024-09-01"
    viirsCollection = (
        ee.ImageCollection("NASA/VIIRS/002/VNP09GA")
        .filterDate(start_date, end_date)
        .filterBounds(gee_features.geometry())
    )
    masked_coll = maskClouds(viirsCollection)
    ndmi_collection = masked_coll.map(compute_ndmi)
    #

    params = {
        "reducer": ee.Reducer.mean(),
        "bands": ["ndmi"],
        "scale": 1000,
        "datetimeName": "date",
        "datetimeFormat": "YYYY-MM-dd",
    }
    results = zonal_stats(ndmi_collection, gee_features, params)
    task = ee.batch.Export.table.toDrive(
        **{
            "collection": results,
            "description": file_name,
            "folder": out_dir,
            "selectors": ["date", "fid", "ndmi"],
            "fileFormat": "CSV",
        }
    )
    task.start()


def gee_VNP13A1_to_drive(gee_features, out_dir, file_name):
    bands = ["EVI2", "NDVI", "pixel_reliability", "composite_day_of_the_year"]
    params = {
        "reducer": ee.Reducer.first(),
        "bands": bands,
        "scale": 500,
        "datetimeName": "date",
        "datetimeFormat": "YYYY-MM-dd",
    }
    collection_evi = ee.ImageCollection("NOAA/VIIRS/001/VNP13A1")
    start_date = "2012-01-01"
    end_date = "2024-02-29"
    filt_collection = collection_evi.filterDate(start_date, end_date).filterBounds(
        gee_features.geometry()
    )
    results = zonal_stats(filt_collection, gee_features, params)

    task = ee.batch.Export.table.toDrive(
        **{
            "collection": results,
            "description": file_name,
            "folder": out_dir,
            "selectors": ["date", "timestamp", "fid"] + bands,
            "fileFormat": "CSV",
        }
    )
    task.start()


def gee_VNP22Q2_to_drive(gee_features, out_dir, file_name):
    phen_columns = [
        "Onset_Greenness_Increase_1",
        "Onset_Greenness_Maximum_1",
        "Onset_Greenness_Decrease_1",
        "Onset_Greenness_Minimum_1",
        "Date_Mid_Greenup_Phase_1",
        "Date_Mid_Senescence_Phase_1",
        "EVI2_Growing_Season_Area_1",
        "Growing_Season_Length_1",
        "EVI2_Onset_Greenness_Increase_1",
        "EVI2_Onset_Greenness_Maximum_1",
    ]
    params = {
        "reducer": ee.Reducer.first(),
        "bands": phen_columns,
        "scale": 500,
        "datetimeName": "date",
        "datetimeFormat": "YYYY-MM-dd",
    }
    collection = ee.ImageCollection("NOAA/VIIRS/001/VNP22Q2")
    start_date = "2013-01-01"
    end_date = "2022-01-02"
    filt_collection = collection.filterDate(start_date, end_date).filterBounds(
        gee_features.geometry()
    )
    results = zonal_stats(filt_collection, gee_features, params)
    task = ee.batch.Export.table.toDrive(
        **{
            "collection": results,
            "folder": out_dir,
            "description": file_name,
            "selectors": ["date", "timestamp", "fid"] + phen_columns,
            "fileFormat": "CSV",
        }
    )
    task.start()


def MERIT_DEM_dataset(gee_features, out_dir, file_name):
    params = {
        "bands": [0, 1],
        "bandsRename": ["elevation", "slope"],
        "reducer": ee.Reducer.first(),
        "scale": 500,
        "datetimeName": "date",
        "datetimeFormat": "YYYY-MM-dd",
    }
    # Import the MERIT global elevation dataset.
    elev = ee.Image("MERIT/DEM/v1_0_3")
    # Calculate slope from the DEM.
    slope = ee.Terrain.slope(elev)

    # Concatenate elevation and slope as two bands of an image.
    topo = ee.Image.cat(elev, slope)
    # Computed images do not have a 'system:time_start' property; add one based
    # on when the data were collected.
    topo = topo.set("system:time_start", ee.Date("2000-01-01").millis())

    # Wrap the single image in an ImageCollection for use in the zonalStats function.
    topoCol = ee.ImageCollection([topo])
    results = zonal_stats(topoCol, gee_features, params)
    task = ee.batch.Export.table.toDrive(
        **{
            "collection": results,
            "folder": out_dir,
            "description": file_name,
            "selectors": ["date", "fid"] + params["bandsRename"],
            "fileFormat": "CSV",
        }
    )
    task.start()


def vegatation_agb(gee_features, out_dir, file_name):
    agb_image = ee.Image("projects/ee-ukfdrs/assets/agb/results/agb_final/agb_final")
    agb_col = ee.ImageCollection([agb_image])
    results = zonal_stats_no_datetime(agb_col, gee_features, None)

    task = ee.batch.Export.table.toDrive(
        **{
            "collection": results,
            "folder": out_dir,
            "description": file_name,
            "selectors": ["fid"] + ["mean"],
            "fileFormat": "CSV",
        }
    )
    task.start()


def vegatation_height(gee_features, out_dir, file_name):
    height = ee.Image(
        "projects/ee-ukfdrs/assets/height_modelling/H_results/kf12/final_height_Cal"
    )

    heightCol = ee.ImageCollection([height])
    results = zonal_stats_no_datetime(heightCol, gee_features, None)
    task = ee.batch.Export.table.toDrive(
        **{
            "collection": results,
            "folder": out_dir,
            "description": file_name,
            "selectors": ["fid"] + ["mean"],
            "fileFormat": "CSV",
        }
    )
    task.start()


def wait_for_gee_file():
    file_list = rclone.ls("remote:gee_result")


def compute_ndmi(image):
    ndmi = image.normalizedDifference(["M7", "M11"]).rename("ndmi")
    return image.addBands(ndmi)


with open("config.toml", mode="rb") as fp:
    config = tomli.load(fp)


"""
start_date = "2018-01-01"
end_date = "2018-12-31"
lc = 4
region = "Central"
out_dir = "gee_results"
file_name = f"VNP09GA_ndmi_{region}_{lc}_sample_masked"

sampled_file_name = sampled_lc_file_path(
    lc, config["window_size"], config["data_dir"], config["land_cover_file_name"]
)
dfr = pd.read_parquet(sampled_file_name)
gee_features = gee_features_from_points(dfr[dfr["Region"] == region])
gee_features_sub = gee_features_from_points(dfr[dfr["Region"] == region].sample(50))
viirsCollection = (
    ee.ImageCollection("NASA/VIIRS/002/VNP09GA")
    .filterDate(start_date, end_date)
    .filterBounds(gee_features.geometry())
)
masked_coll = maskClouds(viirsCollection)
ndmi_collection = masked_coll.map(compute_ndmi)
#

results = ndmi_collection.select(["ndmi"]).map(
    lambda img: img.reduceRegions(
        collection=gee_features_sub, reducer=ee.Reducer.mean(), scale=1000
    )
)
params = {
    "reducer": ee.Reducer.mean(),
    "bands": ["ndmi"],
    "scale": 1000,
    "datetimeName": "date",
    "datetimeFormat": "YYYY-MM-dd",
}
results = zonal_stats(ndmi_collection, gee_features_sub, params)

task = ee.batch.Export.table.toDrive(
    **{
        "collection": results,
        "description": file_name,
        "folder": out_dir,
        "selectors": ["date", "fid", "ndmi"],
        "fileFormat": "CSV",
    }
)
task.start()
"""
# task = ee.batch.Export.table.toDrive(
#     **{
#         "collection": gee_features_sub,
#         "description": "Central_4_sample",
#         "folder": out_dir,
#         "fileFormat": "CSV",
#     }
# )
# task.start()

#
#
# collection_evi = ee.ImageCollection("NOAA/VIIRS/001/VNP13A1")
# start_date = "2012-01-01"
# end_date = "2024-02-29"

# gee_VNP13A1_to_drive(gee_features, 'gee_results', f'VNP13A1_{region}_{lc}_sample')
# collection_evi = ee.ImageCollection('NOAA/VIIRS/001/VNP13A1')
# collection_evi = collection_evi.select(['EVI2', 'pixel_reliability',
#                                         'composite_day_of_the_year'])
# start_date = '2015-05-01'
# end_date = '2015-05-31'
# filt_collection = collection_evi.filterDate(start_date, end_date) \
#                                 .filterBounds(gee_features.geometry())
#
# results = filt_collection.map(zonalStats_first(gee_features)).flatten()
#
# for lc in config["land_covers"]:
"""
for lc in [9]:  # , 7, 9]:
    print(lc)
    sampled_file_name = sampled_lc_file_path(
        lc, config["window_size"], config["data_dir"], config["land_cover_file_name"]
    )
    dfr = pd.read_parquet(sampled_file_name)
    for region in dfr.Region.unique():
        out_fname = f"height_{region}_{lc}_sample.csv"
        print(region)
        if Path(
            # config["data_dir"], "gee_results", f"MERIT_DEM_{region}_{lc}_sample.csv"
            config["data_dir"],
            "gee_results",
            out_fname,
        ).is_file():
            print("file exists")
            continue
        if len(dfr[dfr["Region"] == region]) == 0:
            print("no samples found")
            continue
        gee_features = gee_features_from_points(dfr[dfr["Region"] == region])
        # vegatation_agb(gee_features, "gee_results", f"agb_{region}_{lc}_sample")
        # vegatation_height(gee_features, "gee_results", out_fname)
        # MERIT_DEM_dataset(
        #     gee_features, "gee_results", f"MERIT_DEM_{region}_{lc}_sample"
        # )
        # gee_VNP22Q2_to_drive(
        #     gee_features, "gee_results", f"VNP22Q2_{region}_{lc}_sample"
        # )
        # gee_VNP13A1_to_drive(
        #     gee_features, "gee_results", f"VNP13A1_{region}_{lc}_sample"
        # )
        # for year in range(2013, 2024):
"""

# gee_VNP09GA_to_drive(
#     gee_features, "gee_results", f"VNP09GA_ndmi_{region}_{lc}", None
# )

# while len(rclone.ls("remote:gee_results")) == 0:
#     print("waiting for result file")
#     time.sleep(20)
# print("copying result")
# rclone.copy(
#     "remote:gee_results",
#     str(Path("/Users/tadas/modFire/ndmi/data/", "gee_results")),
# )
# print("deleting result at remote")
# rclone.delete("remote:gee_results", args=["--drive-use-trash=false"])
