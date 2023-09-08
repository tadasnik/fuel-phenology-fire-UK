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
    phenology_file,
    fire_file_name,
    fwi_file_name,
    fwi_quantiles_file_name,
)


def spearmanr_matrix(fwi_q, evi_q, fires):
    """Calculate spearman correlation values for region/predictor combinations"""
    results = {}
    for region in config["regions"]:
        fwi_dfr = (
            fwi_q.loc[region, slice(None), slice(6, 13)]
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


if __name__ == "__main__":
    # phe = pd.read_parquet(phenology_file())
    fires = pd.read_parquet(fire_phenology_file_name())
    fwi = pd.read_parquet(fwi_file_name())
    evi_q = pd.read_parquet(evi2_quantiles_monthly_file())
    fwi_q = pd.read_parquet(fwi_quantiles_monthly_file_name())
    # for region in config["regions"]:
    results = spearmanr_matrix(fwi_q, evi_q, fires)
    region = "North-west"
    stats = results.loc[:, (region, slice(None))].loc[0].unstack()
    pvals = results.loc[:, (region, slice(None))].loc[1].unstack()
    cm = sns.color_palette("vlag", as_cmap=True)
    sns.heatmap(stats[pvals<0.05], cmap = cm)
    plt.show()
