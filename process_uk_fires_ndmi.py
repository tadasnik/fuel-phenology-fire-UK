import time
import tomli
import numpy as np
import pandas as pd
import seaborn as sns
import geopandas as gpd
from open_meteo import fetch_vpd_hist
from gee_data import gee_features_from_points, gee_VNP09GA_to_drive
from ceh_lc_proc import sampled_lc_file_path


def get_soil_props(dfr):
    soils = gpd.read_file("/Users/tadas/modFire/ndmi/data/soilsDB_UK_joined.zip")
    # soils = soils.set_crs("EPSG:27700")
    soils = soils.to_crs("EPSG:4326")
    geometry = gpd.points_from_xy(dfr.longitude, dfr.latitude)
    gdf = gpd.GeoDataFrame(dfr, geometry=geometry, crs=4326)
    pts = gpd.sjoin(soils, gdf)
    pts = pts.drop(["geometry", "index_right"], axis=1)
    df = pd.DataFrame(pts)
    return df


class ERA5LandGrid(object):
    def __init__(self):
        self.lon_min = -180
        self.lat_min = -90
        self.nx = 3600
        self.ny = 1801
        self.dx = 0.1
        self.dy = 0.1

    def modulo_positive(self, arr):
        return np.where(arr >= 0, arr % self.ny, (arr + self.ny) % self.ny)

    def find_point_xy(self, lat_arr, lon_arr):
        # Calculate the x and y grid indices for the arrays
        x = np.round((lon_arr - self.lon_min) / self.dx).astype(int)
        y = np.round((lat_arr - self.lat_min) / self.dy).astype(int)

        # Check if the grid wraps around for global grids
        xx = np.where((self.nx * self.dx >= 359), x % self.nx, x)
        yy = np.where((self.ny * self.dy >= 179), self.modulo_positive(y), y)

        # Create masks to check for out-of-bound indices
        valid_mask = (yy >= 0) & (xx >= 0) & (yy < self.ny) & (xx < self.nx)

        # Return indices where valid, otherwise return None
        return np.where(valid_mask, xx, np.nan), np.where(valid_mask, yy, np.nan)


def fetch_vpd_hourly_hist(dfrg, start_date=None, end_date=None):
    vpds = []
    # er5g = ERA5LandGrid()
    # dfr_event = dfr.groupby("event")[["latitude", "longitude"]].median().reset_index()
    # xx, yy = er5g.find_point_xy(dfr_event["latitude"], dfr_event["longitude"])
    # dfr_event["latind"] = yy.astype(int)
    # dfr_event["lonind"] = xx.astype(int)
    # dfrg = (
    #     dfr_event.groupby(["latind", "lonind"])[["latitude", "longitude"]]
    #     .median()
    #     .reset_index()
    # )
    print(start_date)
    if start_date is None:
        start_date = "2013-01-01"
    if end_date is None:
        end_date = "2024-09-01"
    for nr, row in dfrg.iterrows():
        try:
            vpd_h = fetch_vpd_hist(row.latitude, row.longitude, start_date, end_date)
            vpd_h["latind"] = row.latind.astype(int)
            vpd_h["lonind"] = row.lonind.astype(int)
            vpds.append(vpd_h)
        except:
            print(f"Failed to fetch data for row {nr}, {row.latind}, {row.lonind}")
            break
    return pd.concat(vpds)


def fetch_daily_vpd_hist(dfrg, start_date=None, end_date=None):
    vpd_daily = []
    # er5g = ERA5LandGrid()
    # dfr_event = dfr.groupby("event")[["latitude", "longitude"]].median().reset_index()
    # xx, yy = er5g.find_point_xy(dfr_event["latitude"], dfr_event["longitude"])
    # dfr_event["latind"] = yy.astype(int)
    # dfr_event["lonind"] = xx.astype(int)
    # dfrg = (
    #     dfr_event.groupby(["latind", "lonind"])[["latitude", "longitude"]]
    #     .median()
    #     .reset_index()
    # )
    print(start_date)
    if start_date is None:
        start_date = "2013-01-01"
    if end_date is None:
        end_date = "2024-09-01"
    for nr, row in dfrg.iterrows():
        try:
            vpd_h = fetch_vpd_hist(row.latitude, row.longitude, start_date, end_date)
            vpd_d = vpd_h.groupby(vpd_h.date.dt.date)["vpd"].max().reset_index()
            vpd_d["vpd_min"] = vpd_h.groupby(vpd_h.date.dt.date)["vpd"].min().values
            vpd_d["latind"] = row.latind.astype(int)
            vpd_d["lonind"] = row.lonind.astype(int)
            vpd_daily.append(vpd_d)
        except:
            print(f"Failed to fetch data for row {nr}, {row.latind}, {row.lonind}")
            break
    return pd.concat(vpd_daily)


with open("config.toml", mode="rb") as fp:
    config = tomli.load(fp)


lc = 4
region = "Central"


def get_vpd_ndmi(lc, region):
    sampled_file_name = sampled_lc_file_path(
        lc, config["window_size"], config["data_dir"], config["land_cover_file_name"]
    )
    dfr = pd.read_parquet(sampled_file_name)
    dfr = dfr[dfr.Region == region].copy()
    ndmi = pd.read_csv(
        # "/Users/tadas/repos/fire-observatory-backend/UK_VIIRS_lc7.parquet"
        f"/Users/tadas/modFire/ndmi/data/gee_results/VNP09GA_ndmi_{region}_{lc}.csv"
    )
    # dfr["date"] = pd.to_datetime(dfr.date)
    # dfr["year"] = dfr["date"].dt.year
    # dfr["week"] = dfr["date"].dt.isocalendar().week
    er5g = ERA5LandGrid()
    xx, yy = er5g.find_point_xy(dfr["latitude"], dfr["longitude"])
    dfr["latind"] = yy.astype(int)
    dfr["lonind"] = xx.astype(int)
    dfr["fid"] = dfr.index
    dfrg = (
        dfr.groupby(["latind", "lonind"])[["latitude", "longitude"]]
        .median()
        .reset_index()
    )
    vpd = fetch_daily_vpd_hist(dfrg)
    ndmi = ndmi.merge(dfr[["lonind", "latind", "fid"]], on=["fid"], how="left")
    ndmig = ndmi.groupby(["latind", "lonind", "date"])[["ndmi"]].mean().reset_index()
    # vpd = pd.read_parquet("lc7_VIIRS_fire_vpd.parquet")
    vpd["date"] = pd.to_datetime(vpd["date"])
    # ndmi = pd.read_csv("~/modFire/ndmi/data/gee_results/VNP09GA_ndmi_lc7_fires.csv")
    ndmig["date"] = pd.to_datetime(ndmig["date"])
    df = dfrg.merge(vpd, on=["latind", "lonind"], how="left")
    df = df.merge(ndmig, on=["latind", "lonind", "date"], how="left")
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month
    df["week"] = df["date"].dt.isocalendar().week
    season_mean = df.groupby(["week"])["ndmi"].transform("mean")
    df["ndmi_des"] = df.ndmi - season_mean

    season_mean_vpd = df.groupby(["week"])["vpd"].transform("mean")
    df["vpd_des"] = df.vpd - season_mean_vpd
    df["vpd1"] = df.vpd_des.shift(1)
    df["vpd2"] = df.vpd_des.shift(2)
    df.to_parquet(f"~/modFire/ndmi/data/ndmi_vpd_{lc}_{region}.parquet")


def proc_fuel_moisture_UK():
    dfr = pd.read_csv("/Users/tadas/modFire/ndmi/data/UK_fuel_moisture_dataset.csv")
    dfr.columns = dfr.columns.str.lower()
    dfr["date"] = pd.to_datetime(dfr["date"], dayfirst=True)
    dfr["year"] = dfr["date"].dt.year
    dfr["week"] = dfr["date"].dt.isocalendar().week
    dfr["month"] = dfr["date"].dt.month
    return dfr


def get_vpd(dfr):
    er5g = ERA5LandGrid()
    xx, yy = er5g.find_point_xy(dfr["latitude"], dfr["longitude"])
    dfr["latind"] = yy.astype(int)
    dfr["lonind"] = xx.astype(int)
    dfrg = (
        dfr.groupby(["latind", "lonind"])[["latitude", "longitude"]]
        .median()
        .reset_index()
    )
    vpd = fetch_vpd_hourly_hist(
        dfrg,
        start_date=dfr.date.min().strftime("%Y-%m-%d"),
        end_date=dfr.date.max().strftime("%Y-%m-%d"),
    )
    vpd["date"] = pd.to_datetime(vpd["date"])
    df = dfrg.merge(vpd, on=["latind", "lonind"], how="left")
    # dfa = df.merge(dfr, on=["latind", "lonind"], how="left")
    return df


"""
er5g = ERA5LandGrid()
dfr_event = dfr.groupby("event")[["latitude", "longitude"]].median().reset_index()
dfr_event["region"] = dfr.groupby("event")["region"].first().values
dfr_event["date"] = dfr.groupby("event")["date"].min().values
xx, yy = er5g.find_point_xy(dfr_event["latitude"], dfr_event["longitude"])
dfr_event["latind"] = yy.astype(int)
dfr_event["lonind"] = xx.astype(int)
dfrg = (
    dfr_event.groupby(["latind", "lonind"])[["latitude", "longitude"]]
    .median()
    .reset_index()
)
dfrg["region"] = dfr_event.groupby(["latind", "lonind"])["region"].first().values
dfrg["fdate"] = dfr_event.groupby(["latind", "lonind"])["date"].first().values
dfrg["fid"] = dfrg.index
"""
"""


# gee_features = gee_features_from_points(dfrg)
#
# gee_VNP09GA_to_drive(
#     gee_features,
#     "gee_results",
#     f"VNP09GA_ndmi_lc4_fires",
#     ["date", "fid", "ndmi"],
# )
# vpd_daily = fetch_daily_vpd_hist(dfr)

vpd = pd.read_parquet("lc7_VIIRS_fire_vpd.parquet")
vpd["date"] = pd.to_datetime(vpd["date"])
ndmi = pd.read_csv("~/modFire/ndmi/data/gee_results/VNP09GA_ndmi_lc7_fires.csv")
ndmi["date"] = pd.to_datetime(ndmi["date"])
df = dfrg.merge(vpd, on=["latind", "lonind"], how="left")
df = df.merge(ndmi, on=["fid", "date"], how="left")
df["year"] = df["date"].dt.year
df["month"] = df["date"].dt.month
df["week"] = df["date"].dt.isocalendar().week
season_mean = df.groupby(["region", "week"])["ndmi"].transform("mean")
df["ndmi_des"] = df.ndmi - season_mean

season_mean_vpd = df.groupby(["region", "week"])["vpd"].transform("mean")
df["vpd_des"] = df.vpd - season_mean_vpd
df["vpd1"] = df.vpd_des.shift(1)
df["vpd2"] = df.vpd_des.shift(2)

dfrg = get_soil_props(dfrg)

dfs = df.merge(
    dfrg[["fid", "ALT", "TEXT", "PEAT", "PMH", "EAWCTOP"]], on=["fid"], how="left"
)
"""
# g = sns.relplot(
#     data=df,
#     x="week", y="ndmi", col="year", hue="year",
#     kind="line", palette="crest", linewidth=4, zorder=5,
#     col_wrap=3, height=2, aspect=1.5, legend=False,
# )
