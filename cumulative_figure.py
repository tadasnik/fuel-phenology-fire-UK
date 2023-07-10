import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import MonthLocator, num2date
from configuration import config, ukceh_classes, color_dict
from prepare_data import fire_phenology_file_name, phenology_quantiles_file

COLOR = "0.3"
plt.rcParams["font.family"] = "Fira Sans"
plt.rcParams["text.color"] = COLOR
plt.rcParams["axes.labelcolor"] = COLOR
plt.rcParams["axes.edgecolor"] = COLOR
plt.rcParams["xtick.color"] = COLOR
plt.rcParams["ytick.color"] = COLOR

fire = pd.read_parquet(fire_phenology_file_name())

region = "South-west"
lcw = [4, 9, 7]
lc = 4
# fire = fire[fire.Region == region]
fire = fire[fire.lc.isin(config["land_covers"])]
fire["dummy_doy"] = pd.to_datetime(2016 * 1000 + fire.doy, format="%Y%j")

pheg = pd.read_parquet(phenology_quantiles_file())
fire_g = (
    fire.groupby(["event", "lc"])[["dummy_doy", "year", "date", "size", "Region"]]
    .min()
    .reset_index()
)

date_cols = [
    "Onset_Greenness_Increase_1",
    "Onset_Greenness_Maximum_1",
    "Onset_Greenness_Decrease_1",
    "Onset_Greenness_Minimum_1",
    # "Date_Mid_Greenup_Phase_1",
    # "Date_Mid_Senescence_Phase_1"
]

colors = [color_dict[x] for x in lcw]
_, axs = plt.subplots(2, 4, figsize=(15, 8), constrained_layout=True)

for nr, ax in enumerate(axs.flatten()):
    lc = config["land_covers"][nr]

#ph_dates = pheg.loc[region, lc][date_cols][:, "q50"]
    ph_dates = pheg.loc[(slice(None), lc), (date_cols, "q50")].droplevel(level=1, axis=1).median()
    ph_dates = pd.to_datetime(2016 * 1000 + ph_dates, format="%Y%j")
# ph_dates_min = pheg.loc[region, lc][date_cols][:, "q25"]
    ph_dates_min = pheg.xs(lc, level="lc").loc[:, (date_cols, "q25")].droplevel(level=1, axis=1).min()
    ph_dates_min = pd.to_datetime(2016 * 1000 + ph_dates_min, format="%Y%j")
# ph_dates_m = pheg.loc[region, lc][date_cols][:, "q75"]
    ph_dates_m = pheg.xs(lc, level="lc").loc[:, (date_cols, "q75")].droplevel(level=1, axis=1).max()
    ph_dates_m = pd.to_datetime(2016 * 1000 + ph_dates_m, format="%Y%j")
    for pair in zip(ph_dates_min, ph_dates_m):
        ax.axvspan(pair[0], pair[1], color="0.9", alpha=0.2, zorder=0)
    for line in ph_dates:
        ax.axvline(line, linestyle="--", color="0.5", zorder=1)

    sns.ecdfplot(data=fire[fire.lc == lc], x='dummy_doy', color=color_dict[lc], ax=ax)
    sns.ecdfplot(data=fire_g[fire_g.lc == lc], x='dummy_doy', color=color_dict[lc], linestyle="--", ax=ax)

    months = MonthLocator([3,4, 5, 6, 9, 12], bymonthday=1)  # , interval=3)
    ax.xaxis.set_major_formatter(
        FuncFormatter(lambda x, pos=None: "{dt:%b} {dt.day}".format(dt=num2date(x)))
    )
    ax.xaxis.set_major_locator(months)
    ax.grid(True, which="major", c="gray", ls="-", lw=0.5, alpha=0.2)
    ax.set_xlim(pd.Timestamp('2016-1-1'), pd.Timestamp('2016-12-31'))
    if (nr != 0) & (nr != 4):
        ax.set_yticklabels([])
        ax.set_ylabel(None)
    if nr < 4:
        ax.set_xticklabels([])
    ax.set_xlabel(None)
    ax.set_title(ukceh_classes[lc])
    # axins = ax.inset_axes([0.6, 0.1, 0.35, 0.35])
    # sns.countplot(data=fire[fire.lc == lc], x='season_green', ax=axins)#, order=["Dormant", "Increase", "Maximum", "Decrease"])
    # axins.set_xlabel(None)
    plt.savefig(
        Path(config["data_dir"], "results/figures", "cumulative_fire.png"),
        dpi=300,
        bbox_inches="tight",
    )
plt.show()

