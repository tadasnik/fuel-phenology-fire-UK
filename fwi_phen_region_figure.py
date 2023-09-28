import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import MonthLocator, num2date
from configuration import config, color_dict
from prepare_data import (
    fire_phenology_file_name,
    phenology_file,
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
        subg = fwi[fwi.Region == region][["month", "fbupinx"]]
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
        ax.set_ylim(0, 200)
    # plt.savefig(
    #     Path(config["data_dir"], "results/figures", "region_fwi_phen_box.png"),
    #     dpi=300,
    #     bbox_inches="tight",
    # )
    plt.show()


def region_fwi_phen_isi_bui_doy(fwi):
    regions = config["regions"]
    fig, axs = plt.subplots(3, 3, figsize=(10, 7))
    var_labels = [
        "Initial Spread Index (ISI)",
        "Buildup Index (BUI)",
    ]
    for nr, region in enumerate(regions):
        ax = axs.flatten()[nr]
        subg = fwi.loc[region].copy()
        subg["date"] = pd.to_datetime(2016 * 1000 + subg.index, format="%Y%j")
        variables = [
            ["infsinx", color_dict[2]],
            ["fbupinx", color_dict[7]],
        ]
        # for nr_var, (variable, color) in enumerate(variables):
        artists = []
        variable, color = variables[0]
        # if nr_var == 1:
        #     ax = ax.twinx()
        values_med = subg.loc[:, variable]["q95"]
        values_med = values_med.rolling(window=14, min_periods=1, center=True).mean()
        values_low = (
            subg.loc[:, variable]["q75"]
            .rolling(window=14, min_periods=1, center=True)
            .mean()
        )
        values_high = (
            subg.loc[:, variable]["q99"]
            .rolling(window=14, min_periods=1, center=True)
            .mean()
        )
        artists += ax.plot(
            subg["date"], values_med, ls="-", c=color, zorder=5, label=var_labels[0]
        )
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
        ax.grid(True, which="major", axis="x", c="gray", ls="--", lw=1, alpha=0.2)
        sns.despine(bottom=False, left=False, right=True, offset=2, ax=ax)
        ax.tick_params(
            axis="both",
            bottom=False,
            top=False,
            labelbottom=False,
            left=True,
            right=False,
            labelleft=False,
        )
        # ax.set_yticks([])
        if nr in [0, 3, 6]:
            sns.despine(bottom=False, left=False, right=True, offset=2, ax=ax)
            ax.tick_params(
                axis="y",
                left=True,
                labelleft=True,
            )

            ax.set_yticks([0, 5, 10])
        else:
            ax.set_yticks([0, 5, 10])
        if nr > 5:
            ax.tick_params(
                axis="x",
                bottom=True,
                top=False,
                labelbottom=True,
                left=True,
                right=False,
                labelleft=False,
            )
        ax.set_ylim([0, 13])
        if nr == 3:
            ax.set_ylabel("ISI", color=color)

        months = MonthLocator([3, 6, 9, 12], bymonthday=1)  # , interval=3)
        ax.xaxis.set_major_formatter(
            FuncFormatter(lambda x, pos=None: "{dt:%b}".format(dt=num2date(x)))
        )
        ax.xaxis.set_major_locator(months)
        ax.set_title(f"{region}", y=0.9)

        artists = []
        variable, color = variables[1]
        ax2 = ax.twinx()
        values_med = subg.loc[:, variable]["q95"]
        values_med = values_med.rolling(window=14, min_periods=1, center=True).mean()
        values_low = (
            subg.loc[:, variable]["q75"]
            .rolling(window=14, min_periods=1, center=True)
            .mean()
        )
        values_high = (
            subg.loc[:, variable]["q99"]
            .rolling(window=14, min_periods=1, center=True)
            .mean()
        )
        artists += ax2.plot(
            subg["date"], values_med, ls="-", c=color, zorder=5, label=var_labels[1]
        )
        artists += [
            ax2.fill_between(
                subg.date,
                values_low,
                values_high,
                color=color,
                alpha=0.2,
                zorder=4,
            )
        ]
        sns.despine(bottom=True, left=True, right=False, offset=2, ax=ax2)
        ax2.tick_params(
            axis="y",
            bottom=False,
            top=False,
            labelbottom=False,
            left=False,
            right=True,
            labelright=False,
        )
        if nr in [2, 5, 8]:
            sns.despine(bottom=False, left=True, right=False, offset=2, ax=ax2)
            ax2.tick_params(
                axis="y",
                right=True,
                labelright=True,
            )
        ax2.set_yticks([0, 50, 100])
        ax2.set_ylim([0, 150])
        if nr == 5:
            ax2.set_ylabel("BUI", color=color)

    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    print(lines, labels)
    fig.legend(
        lines + lines2, labels + labels2, loc="lower center", frameon=False, ncol=2
    )
    plt.subplots_adjust(hspace=0.08)
    plt.savefig(
        Path(config["data_dir"], "results/figures", "region_fwi_isi_bui_phen.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()


def region_fwi_phen_doy(fwi):
    regions = config["regions"]
    fig, axs = plt.subplots(3, 3, figsize=(10, 7))
    var_labels = [
            "Fire Weather Index (FWI)"
        # "Fine Fuel Moisture Code (FFMC)",
        # "Duff Moisture Code (DMC)",
    ]
    for nr, region in enumerate(regions):
        ax = axs.flatten()[nr]
        subg = fwi.loc[region].copy()
        subg["date"] = pd.to_datetime(2016 * 1000 + subg.index, format="%Y%j")
        artists = []
        variables = [
            ["fwinx", color_dict[7]],
            # ["ffmcode", color_dict[2]],
            # ["dufmcode", color_dict[7]],
        ]
        for nr_var, (variable, color) in enumerate(variables):
            if nr_var == 1:
                pass
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
            artists += ax.plot(
                subg["date"],
                values_med,
                ls="-",
                c=color,
                zorder=5,
                label=var_labels[nr_var],
            )
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
        ax.grid(True, which="major", axis="x", c="gray", ls="--", lw=1, alpha=0.2)
        if nr < 6:
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
        if nr == 3:
            # ax.set_ylabel("FFMC/DMC")
            ax.set_ylabel("FWI")
        ax.set_yticks(range(0, 101, 10))
        ax.set_ylim(0, 35)
        months = MonthLocator([3, 6, 9, 12], bymonthday=1)  # , interval=3)
        ax.xaxis.set_major_formatter(
            FuncFormatter(lambda x, pos=None: "{dt:%b}".format(dt=num2date(x)))
        )
        ax.xaxis.set_major_locator(months)
        ax.set_title(f"{region}", y=0.9)

    lines, labels = ax.get_legend_handles_labels()
    print(lines, labels)
    # lines, labels = [sum(lol, []) for lol in zip(*lines_labels)]
    #fig.legend(lines, labels, loc="lower center", frameon=False, ncol=2)
    plt.subplots_adjust(hspace=0.08)
    plt.savefig(
        Path(config["data_dir"], "results/figures", "region_fwinx_phen.png"),
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
    # region_fwi_phen_isi_bui_doy(fwi_q)
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
