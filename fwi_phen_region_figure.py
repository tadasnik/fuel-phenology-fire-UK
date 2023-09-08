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
    q5,
    q25,
    q50,
    q75,
    q95,
    evi2_quantiles_file,
    phenology_quantiles_file,
    fire_phenology_file_name,
    phenology_file,
    fire_file_name,
    fwi_file_name,
    fwi_quantiles_file_name,
)


COLOR = "0.3"
plt.rcParams["font.family"] = "Fira Sans"
plt.rcParams["text.color"] = COLOR
plt.rcParams["axes.labelcolor"] = COLOR
plt.rcParams["axes.edgecolor"] = COLOR
plt.rcParams["xtick.color"] = COLOR
plt.rcParams["ytick.color"] = COLOR


def region_fwi_phen_box(fwi, phe):
    regions = config["regions"]
    _, axs = plt.subplots(3, 3, figsize=(10, 10))
    lc = 7
    year = 2022
    for nr, region in enumerate(regions):
        ax = axs.flatten()[nr]
        fbdfr = subg[["month", "fbupinx"]]
        sns.boxplot(subg, x="month", y="fbupinx", color=color_dict[3], ax=ax)
        # ser = fire[(fire.Region == region)].groupby("doy")["frp"].count()
        # f_dates = pd.to_datetime(2016 * 1000 + ser.index, format="%Y%j")
        # print(f_dates.min(), f_dates.max())
        # ax2 = ax.twinx()
        # ax2.bar(f_dates, ser, color=color_dict[21], width=1, alpha=0.8, zorder=0)
        # ax2.set_ylim(0, 150)
        # ax2.set_yticks([])
        # ax.grid(True, which="major", c="gray", ls="-", lw=1, alpha=0.2)
        # months = MonthLocator([3, 6, 9, 12], bymonthday=1)  # , interval=3)
        # ax.xaxis.set_major_formatter(
        #    FuncFormatter(lambda x, pos=None: "{dt:%b} {dt.day}".format(dt=num2date(x)))
        # )
        # ax.xaxis.set_major_locator(months)
        # ax.set_ylim(0.1, 120)
        ax.set_title(f"{region}")
        months = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        ax.set_xticklabels(months)
        if nr < 6:
            sns.despine(bottom=False, left=False, trim=True, offset=1, ax=ax)
            ax.tick_params(
                axis="both",
                bottom=False,
                top=False,
                labelbottom=False,
                left=True,
                right=False,
                labelleft=True,
            )
        else:
            sns.despine(left=False, bottom=False, trim=True, offset=1, ax=ax)
        ax.grid(True, which="major", axis="x", c="gray", ls="--", lw=1, alpha=0.2)
        ax.set_xlabel("")
        ax.set_ylim(0, 175)
    # plt.savefig(
    #     Path(config["data_dir"], "results/figures", "region_fwi_phen_box.png"),
    #     dpi=300,
    #     bbox_inches="tight",
    # )
    plt.show()


def region_fwi_phen_doy(fwi):
    regions = config["regions"]
    fig, axs = plt.subplots(3, 3, figsize=(10, 7))
    var_labels = ["Fine Fuel Moisture Code", "Duff Moisture Code", ]
    for nr, region in enumerate(regions):
        ax = axs.flatten()[nr]
        subg = fwi.loc[region].copy()
        subg["date"] = pd.to_datetime(2016 * 1000 + subg.index, format="%Y%j")
        artists = []
        variables = [["ffmcode", color_dict[2]], ["dufmcode", color_dict[7]], ]
        for nr_var, (variable, color) in enumerate(variables):
            if nr_var == 1:
                pass
                # ax = ax.twinx()
                # ax.set_ylim(-10, 10)
            values_med = subg.loc[:, variable]["q75"]
            values_med = values_med.rolling(
                window=14, min_periods=1, center=True
            ).mean()
            values_low = (
                subg.loc[:, variable]["q50"]
                .rolling(window=14, min_periods=1, center=True)
                .mean()
            )
            values_high = (
                subg.loc[:, variable]["q95"]
                .rolling(window=14, min_periods=1, center=True)
                .mean()
            )
            artists += ax.plot(subg["date"], values_med, ls="-", c=color, zorder=5, label=var_labels[nr_var])
            artists += [
                ax.fill_between(
                    subg.date,
                    values_low,
                    values_high,
                    color=color,
                    alpha=0.2,
                    zorder=4,
                )
            ]
        ax.grid(True, which="major", axis='x', c="gray", ls="--", lw=1, alpha=0.2)
        if (nr < 6):
            sns.despine(bottom=False, left=False, trim=False, offset=1, ax=ax)
            ax.tick_params(
                axis="both",
                bottom=False,
                top=False,
                labelbottom=False,
                left=True,
                right=False,
                labelleft=True,
            )
        else:
            sns.despine(left=False, bottom=False, trim=False, offset=1, ax=ax)
        ax.set_yticks(range(0, 101, 20))
        months = MonthLocator([3, 6, 9, 12], bymonthday=1)  # , interval=3)
        ax.xaxis.set_major_formatter(
            FuncFormatter(lambda x, pos=None: "{dt:%b}".format(dt=num2date(x)))
        )
        ax.xaxis.set_major_locator(months)
        ax.set_title(f"{region}", y=0.9)

    lines, labels = ax.get_legend_handles_labels()
    print(lines, labels)
    # lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    fig.legend(lines, labels, loc='lower center', frameon=False, ncol=2)
    plt.subplots_adjust(hspace=.1)
    plt.savefig(
        Path(config["data_dir"], "results/figures", "region_fwi_phen.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()


if __name__ == "__main__":
    # pheg = pd.read_parquet(phenology_quantiles_file())
    phe = pd.read_parquet(phenology_file())
    fires = pd.read_parquet(fire_phenology_file_name())
    fwi = pd.read_parquet(fwi_file_name())
    fwi_q = pd.read_parquet(fwi_quantiles_file_name())
    # region_fwi_phen_box(fwi, phe)
    # region_fwi_phen(fwi_q, phe, fires)
    region_fwi_phen_doy(fwi_q)
    # sub = fwi[(fwi.Region == "Central")].copy()
    # subg = sub.groupby("doy")
    # subg = subg.agg(
    #     {
    #         "fbupinx": [q25, q50, q75],
    #         "infsinx": [q25, q50, q75],
    #         "fwinx": [q25, q50, q75],
    #         "dufmcode": [q25, q50, q75],
    #     }
    # )
    # subg["date"] = pd.to_datetime(2016 * 1000 + subg.index, format="%Y%j")
    # for region in config["regions"]:
    # region = "South-west"
    # for lc in config["land_covers"]:
    #     print(lc)
    #     fire_s = fires[(fires.Region == region) & (fires.lc == lc) & (fires.year != 2023) & (fires.month > 5)]
    #     y = fire_s.groupby(['year', "month"])['frp'].count()
    #     # fwi_s = fwi[(fwi.Region == region) & (fwi.month < 5)]
    #     fwi_s = fwi[(fwi.Region == region) & (fwi.month > 5)]
    #     vars = ["drtcode", "dufmcode", "ffmcode", "fwinx", "fbupinx", "infsinx"]
    #     for var in vars:
    #         x = fwi_s.groupby(['year', "month"])[var].quantile(.95)
    #         xy = pd.merge(x, y, left_index=True, right_index=True, how='outer').fillna(0)
    #         if xy.frp.max() > 0:
    #             st = stats.spearmanr(xy[var].values, xy["frp"].values)
    #             if st.pvalue < 0.05:
    #                 print(var, st)
    #             #plt.scatter(xy[var].values, xy["frp"].values)
    #         #plt.show()
    #
