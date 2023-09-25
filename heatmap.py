import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import MonthLocator, num2date
from configuration import config, color_dict, ukceh_classes
from prepare_data import (
    evi2_quantiles_monthly_file,
    fwi_quantiles_monthly_file_name,
    fire_phenology_file_name,
    fwi_file_name,
    fwi_quantiles_file_name,
    fwi_phen_phase_file,
    phenology_quantiles_file,
    evi2_phen_phase_file,
)

COLOR = "0.3"
plt.rcParams["font.family"] = "Fira Sans"
plt.rcParams["text.color"] = COLOR
plt.rcParams["axes.labelcolor"] = COLOR
plt.rcParams["axes.edgecolor"] = COLOR
plt.rcParams["xtick.color"] = COLOR
plt.rcParams["ytick.color"] = COLOR


def heatmap_matrix(res):
    regions = config["regions"]
    lcs = config["land_covers"]
    _, axs = plt.subplots(len(lcs), len(regions), figsize=(10, 10))
    for nr_r, lc in enumerate(lcs):
        for nr_c, region in enumerate(regions):
            ax = axs[nr_r][nr_c]
            try:
                stats = res.loc[0, (region, str(lc), slice(None))].unstack()
                pvals = res.loc[0, (region, str(lc), slice(None))].unstack()
                cm = sns.color_palette("vlag", as_cmap=True)
                sns.heatmap(stats[pvals < 0.05].values, cmap=cm, vmin=-1, vmax=1, ax=ax)
            except:
                pass
    plt.show()
    # stats = res.loc[:, (region, slice(None))].loc[0].unstack()
    # pvals = res.loc[:, (region, slice(None))].loc[1].unstack()
    # cm = sns.color_palette("vlag", as_cmap=True)
    # sns.heatmap(stats[pvals<0.05], cmap = cm, vmin=-1, vmax=1)


def spearmanr_matrix(fwi_q, evi_q, fires):
    """Calculate spearman correlation values for region/predictor combinations"""
    results = {}
    for region in config["regions"]:
        fwi_dfr = (
            fwi_q.loc[region, slice(None), slice(6, 10)]
            .loc[:, (slice(None), "q50")]
            .droplevel(1, axis=1)
            .reset_index()
        )
        for lc in config["land_covers"]:
            fire_s = fires[
                (fires.Region == region)
                & (fires.lc == lc)
                & (fires.year != 2023)
                & (fires.month > 5)
            ]
            y = fire_s.groupby(["year", "month"])["frp"].count()
            # fwi_s = fwi[(fwi.Region == region) & (fwi.month < 5)]
            evi_dfr = evi_q[
                (evi_q.Region == region)
                & (evi_q.lc == lc)
                & (evi_q.year != 2023)
                & (evi_q.month > 5)
            ]
            x_dfr = fwi_dfr.merge(
                evi_dfr[["year", "month", "q50"]], on=["year", "month"], how="left"
            )
            variables = [
                "drtcode",
                "dufmcode",
                "ffmcode",
                "fwinx",
                "fbupinx",
                "infsinx",
                "q50",
            ]
            for variable in variables:
                x = x_dfr[["year", "month", variable]]
                xy = pd.merge(x, y, on=["year", "month"], how="outer").fillna(0)
                if xy.frp.max() > 0:
                    st = stats.spearmanr(xy[variable].values, xy["frp"].values)
                    results[(region, lc, variable)] = [st.statistic, st.pvalue]
    return pd.DataFrame(results)

def scatterplot_():
    results = {}

    dfr = pd.read_parquet(Path(config["data_dir"], "lc_counts_per_region.parquet"))
    dfr_p = dfr.divide(dfr.sum(axis=1), axis=0).loc[lc]
    for lc in config["land_covers"]:
        dfr_p = dfr.divide(dfr.sum(axis=1), axis=0).loc[lc]
        regions = dfr_p.index[dfr_p > 0.05]
        season_col = "season"
        variables = [
            "drtcode",
            "dufmcode",
            "ffmcode",
            "fwinx",
            "fbupinx",
            "infsinx",
        ]
        evi_dfr = evi_p[(evi_p.lc == lc) & (evi_p.Region.isin(regions))]
        evi_dfr = evi_dfr.set_index(["Region", season_col, "year"])
        fwi_dfr = (
            fwi_p[(fwi_p.lc == lc) & (fwi_p.Region.isin(regions))]
            .groupby(["Region", season_col, "year"])[variables]
            .quantile(0.95)
        )
        variables += ["EVI2"]
        fwi_dfr = pd.merge(
            fwi_dfr, evi_dfr, left_index=True, right_index=True, how="left"
        )
        fwi_dfr["EVI2"] *= 0.0001
        fire_s = fires[
            (fires.lc == lc) & (fires.year != 2023) & (fires.Region.isin(regions))
        ]
        days = (
            fwi_p[(fwi_p.lc == lc) & (fwi_p.Region.isin(regions))]
            .groupby(["Region", season_col, "year"])["doy"]
            .nunique()
        )
        fire_counts = fire_s.groupby(["Region", season_col, "year"])["frp"].count()
        y = pd.merge(
            days, fire_counts, left_index=True, right_index=True, how="outer"
        ).fillna(0)
        y["frp"] = y.frp.div(y.doy).replace(np.inf, 0)
        y = y[y.doy > 28]
        y.name = "frp"
        xy = pd.merge(
            fwi_dfr, y, left_index=True, right_index=True, how="outer"
        ).fillna(0)

def spearmanr_correlation_phenology(evi_p, fwi_p, fires):
    """Calculate spearman correlation values for region/predictor combinations"""
    results = {}
    for region in config["regions"]:
        for lc in config["land_covers"]:
            season_col = "season"
            variables = [
                "drtcode",
                "dufmcode",
                "ffmcode",
                "fwinx",
                "fbupinx",
                "infsinx",
            ]
            evi_dfr = evi_p[(evi_p.lc == lc) & (evi_p.Region == region)]
            evi_dfr = evi_dfr.set_index(["season", "year"])
            fwi_dfr = (
                fwi_p[(fwi_p.lc == lc) & (fwi_p.Region == region)]
                .groupby([season_col, "year"])[variables]
                .quantile(0.95)
            )
            variables += ["EVI2"]
            fwi_dfr = pd.merge(
                fwi_dfr, evi_dfr, left_index=True, right_index=True, how="left"
            )
            fwi_dfr["EVI2"] *= 0.0001
            fire_s = fires[
                (fires.Region == region) & (fires.lc == lc) & (fires.year != 2023)
            ]
            days = (
                fwi_p[(fwi_p.lc == lc) & (fwi_p.Region == region)]
                .groupby([season_col, "year"])["doy"]
                .nunique()
            )
            fire_counts = fire_s.groupby([season_col, "year"])["frp"].count()
            y = pd.merge(
                days, fire_counts, left_index=True, right_index=True, how="outer"
            ).fillna(0)
            y["frp"] = y.frp.div(y.doy).replace(np.inf, 0)
            y = y[y.doy > 28]
            y.name = "frp"
            xy = pd.merge(
                fwi_dfr, y, left_index=True, right_index=True, how="outer"
            ).fillna(0)
            for variable in variables:
                for season in xy.index.get_level_values(0).unique():
                    xy_sub = xy.loc[(season), slice(None), slice(None)]
                    if xy_sub["frp"].max() > 0:
                        st = stats.spearmanr(
                            xy_sub[variable].values, xy_sub["frp"].values
                        )
                        results[(region, lc, season, variable)] = [
                            st.statistic,
                            st.pvalue,
                        ]
                    else:
                        results[(region, lc, season, variable)] = [0., 1.]
    return results


if __name__ == "__main__":
    # phe = pd.read_parquet(phenology_file())
    fires = pd.read_parquet(fire_phenology_file_name())
    fwi = pd.read_parquet(fwi_file_name())
    evi_p = pd.read_parquet(evi2_phen_phase_file())
    fwi_q = pd.read_parquet(fwi_quantiles_monthly_file_name())
    fwi_p = pd.read_parquet(fwi_phen_phase_file())
    phe_q = pd.read_parquet(phenology_quantiles_file())
    # results = spearmanr_correlation_phenology(evi_p, fwi_p, fires)
    # res = pd.DataFrame(results)
    # res.columns = pd.MultiIndex.from_frame(
    #          pd.DataFrame(index=res.columns)
    #          .reset_index().astype(str)
    #          )
    # res.to_parquet('spearmanr.parquet')
    res = pd.read_parquet("spearmanr.parquet")
    # heatmap_matrix(res)

    regions = config["regions"]
    lcs = config["land_covers"]
    variables = res.columns.get_level_values(3).unique()
    cm = sns.color_palette("vlag", as_cmap=True)
    _, axs = plt.subplots(len(lcs), len(regions), figsize=(20, 20))
    for nr_r, lc in enumerate(lcs):
        for nr_c, region in enumerate(regions):
            ax = axs[nr_r][nr_c]
            print(lc, region)
            try:
                spearr = (
                    res.loc[0, (region, str(lc), slice(None))].unstack().values
                ).transpose()
                pvals = (
                    res.loc[1, (region, str(lc), slice(None))].unstack().values
                ).transpose()
                spearr[pvals > 0.05] = 0
                print(spearr.shape)
                im = ax.imshow(spearr, cmap="coolwarm", vmin=-1, vmax=1)
                if nr_c == 0:
                    ax.set_yticks(range(7))
                    ax.set_yticklabels(res.loc[0, (region, str(lc), slice(None))].unstack().columns)
                    ax.set_ylabel(str(lc))
                if nr_r == 0:
                    ax.set_title(region)
                if nr_r == 7:
                    ax.set_xticks(range(6))
                    ax.set_xticklabels(res.loc[0, (region, str(lc), slice(None))].unstack().index.get_level_values(2), rotation=90)
                # sns.heatmap(
                #     spearr[pvals < 0.05].values,
                #     cmap=cm,
                #     vmin=-1,
                #     vmax=1,
                #     ax=ax,
                #     cbar=False,
                # )
            except KeyError:
                pass
    plt.tight_layout()
    plt.show()

    # for region in config["regions"]:
    region = "Eastern Scotland"
    lc = 1
    spearr = (
        res.loc[0, (region, str(lc), slice(None))].unstack()
    ).transpose()
    pvals = (
        res.loc[1, (region, str(lc), slice(None))].unstack()
    ).transpose()

    # season_col = "season"
    # variables = [
    #     "drtcode",
    #     "dufmcode",
    #     "ffmcode",
    #     "fwinx",
    #     "fbupinx",
    #     "infsinx",
    # ]
    #
    # evi_dfr = evi_p[(evi_p.lc == lc) & (evi_p.Region == region)]
    # evi_dfr = evi_dfr.set_index(["season", "year"])
    # fwi_dfr = (
    #     fwi_p[(fwi_p.lc == lc) & (fwi_p.Region == region)]
    #     .groupby([season_col, "year"])[variables]
    #     .quantile(0.95)
    # )
    #
    # variables += ["EVI2"]
    # fwi_dfr = pd.merge(fwi_dfr, evi_dfr, left_index=True, right_index=True, how="left")
    # fwi_dfr["EVI2"] *= 0.0001
    # fire_s = fires[(fires.Region == region) & (fires.lc == lc) & (fires.year != 2023)]
    # days = (
    #     fwi_p[(fwi_p.lc == lc) & (fwi_p.Region == region)]
    #     .groupby([season_col, "year"])["doy"]
    #     .nunique()
    # )
    # fire_counts = fire_s.groupby([season_col, "year"])["frp"].count()
    # y = pd.merge(
    #     days, fire_counts, left_index=True, right_index=True, how="outer"
    # ).fillna(0)
    # y["frp"] = y.frp.div(y.doy).replace(np.inf, 0)
    # y = y[y.doy > 28]
    # y.name = "frp"
    # results = {}
    # xy = pd.merge(fwi_dfr, y, left_index=True, right_index=True, how="outer").fillna(0)
    # for variable in variables:
    #     for season in xy.index.get_level_values(0).unique():
    #         xy_sub = xy.loc[(season), slice(None), slice(None)]
    #         if xy_sub["frp"].max() > 0:
    #             st = stats.spearmanr(xy_sub[variable].values, xy_sub["frp"].values)
    #             results[(region, lc, season, variable)] = [st.statistic, st.pvalue]
    #
    # res = spearmanr_matrix(fwi_q, evi_q, fires)
    # stats = res.loc[:, (region, slice(None))].loc[0].unstack()
    # pvals = res.loc[:, (region, slice(None))].loc[1].unstack()
    # cm = sns.color_palette("vlag", as_cmap=True)
    # sns.heatmap(stats[pvals<0.05], cmap = cm, vmin=-1, vmax=1)
    # plt.show()
