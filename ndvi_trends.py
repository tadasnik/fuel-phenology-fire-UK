from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import theilslopes
from configuration import config

from prepare_data import (
    fwi_quantiles_monthly_file_name,
    fire_phenology_file_name,
    fwi_file_name,
    fwi_phen_phase_file,
    phenology_quantiles_file,
    evi2_phen_phase_file,
)


def ndvi_change_vs_fwi(region, lc, fwis):
    dfr = pd.read_parquet(
        f"/Users/tadas/modFire/fire_lc_ndvi/data/cehlc/gee_results/VNP13A1_{region}_{lc}_sample.parquet"
    )
    dfr = dfr[dfr.pixel_reliability < 5]
    dfr = dfr.drop_duplicates(["fid", "composite_day_of_the_year"])

    dfr["year"] = pd.to_datetime(dfr.date).dt.year
    dfr["month"] = pd.to_datetime(dfr.date).dt.month
    dfr["doy"] = pd.to_datetime(dfr.date).dt.dayofyear
    dfr["obs_date"] = pd.to_datetime(
        dfr["year"] * 1000 + dfr["composite_day_of_the_year"], format="%Y%j"
    )
    dfr["change"] = dfr.groupby("fid")["NDVI"].transform(pd.Series.diff)

    fwisg = (
        fwis.groupby(["year", "woy"])[["dufmcode", "fwinx", "drtcode"]]
        .median()
        .reset_index()
    )
    fwisg["season"] = (
        fwis.groupby(["year", "woy"])["season"]
        .agg(lambda x: pd.Series.mode(x)[0])
        .values
    )
    fwisg["month"] = (
        fwis.groupby(["year", "woy"])["month"]
        .agg(lambda x: pd.Series.mode(x)[0])
        .values
    )

    dfrg = dfr.groupby(["year", "woy"])[["change", "NDVI"]].quantile(0.5).reset_index()
    dfrg = pd.merge(dfrg, fwisg, on=["year", "woy"], how="left")
    dfrg = dfrg.dropna()
    sns.scatterplot(
        data=dfrg[dfrg.season.isin(["Increase_early", "Increase_late", "Maximum"])],
        x="dufmcode",
        y="change",
        hue="season",
    )
    plt.show()


fwi = pd.read_parquet(fwi_phen_phase_file())

results = []
for region in config["regions"]:
    for lc in config["land_covers"]:
        print(region, lc)
        fwis = fwi[fwi.Region == region]
        # ndvi_change_vs_fwi(region, lc, fwis)
        try:
            dfr = pd.read_parquet(
                f"/Users/tadas/modFire/fire_lc_ndvi/data/cehlc/gee_results/VNP13A1_{region}_{lc}_sample.parquet"
            )
        except FileNotFoundError:
            continue
        dfr = dfr[dfr.pixel_reliability < 5]
        dfr = dfr.drop_duplicates(["fid", "composite_day_of_the_year"])

        dfr["year"] = pd.to_datetime(dfr.date).dt.year
        dfr["month"] = pd.to_datetime(dfr.date).dt.month
        dfr["doy"] = pd.to_datetime(dfr.date).dt.dayofyear
        dfr["obs_date"] = pd.to_datetime(
            dfr["year"] * 1000 + dfr["composite_day_of_the_year"], format="%Y%j"
        )
        dfr["ndvi_med"] = dfr.groupby("fid")["NDVI"].transform(
            lambda s: s.rolling(2, min_periods=1).median()
        )
        dfr["change"] = dfr.groupby("fid")["ndvi_med"].transform(pd.Series.diff)
        """
        dfr["slope"] = 0.0
        dfr["min_slope"] = 0.0
        dfr["max_slope"] = 0.0
        dates = dfr.date.unique()
        slopes = []
        for nr, date in enumerate(dates[1:-2], 1):
            print(nr, date)
            dfrs = dfr[dfr.date.isin([dates[nr - 1], date])]
            result = theilslopes(dfrs.NDVI, dfrs.composite_day_of_the_year)
            print(result.slope)
            slopes.append(result.slope)
            dfr.loc[dfr.date == date, "slope"] = result.slope
            dfr.loc[dfr.date == date, "min_slope"] = result.low_slope
            dfr.loc[dfr.date == date, "max_slope"] = result.high_slope
        """
        fwisg = (
            fwis.groupby(["year", "woy"])[["dufmcode", "fwinx", "drtcode", "ffmcode"]]
            .median()
            .reset_index()
        )
        fwisg["season"] = (
            fwis.groupby(["year", "woy"])["season"]
            .agg(lambda x: pd.Series.mode(x)[0])
            .values
        )
        fwisg["month"] = (
            fwis.groupby(["year", "woy"])["month"]
            .agg(lambda x: pd.Series.mode(x)[0])
            .values
        )

        dfrg = (
            # dfr.groupby(["year", "woy"])[["change", "slope", "min_slope", "max_slope", "NDVI"]]
            dfr.groupby(["year", "woy"])[["change", "NDVI"]]
            .quantile(0.5)
            .reset_index()
        )
        dfrg = pd.merge(dfrg, fwisg, on=["year", "woy"], how="left")
        dfrg = dfrg.dropna()
        dfrg["Region"] = region
        dfrg["lc"] = lc
        results.append(dfrg)
dfr = pd.concat(results)


dfr["anomaly"] = dfr["change"] - dfr.groupby(["lc", "Region", "woy"])[
    "change"
].transform("median")

dfr["ndvi_anom"] = dfr["NDVI"] - dfr.groupby(["lc", "Region", "woy"])["NDVI"].transform(
    "median"
)


regions = [
    ["North-west", "North-east", "South-west"],
    ["North-west", "North-east", "South-west"],
    ["Central", "South-east"],
]
lcs = [7, 9, 4]
_, axs = plt.subplots(1, 3, figsize=(18, 5))
for nr, ax in enumerate(axs.flatten()):
    g = sns.scatterplot(
        data=dfr[
            # (dfr.Region.isin(regions[nr]))
            # (dfr.Region.isin(["Central"]))
            (dfr.lc == lcs[nr])
            & (dfr.season.isin(["Maximum"]))
        ],
        # data=dfrg[dfrg.month.isin([5])],
        x="drtcode",
        y="anomaly",
        hue="dufmcode",
        ax=ax,
    )
    ax.set_ylabel("NDVI anomaly")
    ax.set_xlabel("Drought Code")
    g.legend().set_title("DMC")
    if nr == 0:
        ax.set_title("Acid grassland")
        # ax.set_ylim(-0.07, 0.11)
    if nr == 1:
        ax.set_title("Heather")
        # ax.set_ylim(-0.05, 0.11)
    if nr == 2:
        ax.set_title("Improved grassland")
        # ax.set_ylim(-0.11, 0.05)
# plt.savefig(
#     Path(config["data_dir"], "results/figures", "NDVI_trend_anomaly.png"),
#     dpi=300,
#     bbox_inches="tight",
# )
plt.show()


"""
# the bellow is slow
dfr["slope"] = 0.0
dfr["min_slope"] = 0.0
dfr["max_slope"] = 0.0
dates = dfr.date.unique()
slopes = []
for nr, date in enumerate(dates[1:-2], 1):
    print(nr, date)
    dfrs = dfr[dfr.date.isin([dates[nr - 1], date])]
    result = theilslopes(dfrs.NDVI, dfrs.composite_day_of_the_year)
    print(result.slope)
    slopes.append(result.slope)
    dfr.loc[dfr.date == date, "slope"] = result.slope
    dfr.loc[dfr.date == date, "min_slope"] = result.low_slope
    dfr.loc[dfr.date == date, "max_slope"] = result.high_slope
"""
