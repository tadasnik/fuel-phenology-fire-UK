import pandas as pd

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import MonthLocator, num2date
from configuration import config, ukceh_classes_n, color_dict
from prepare_data import fire_phenology_file_name, phenology_quantiles_file

COLOR = "0.3"
plt.rcParams["font.family"] = "Fira Sans"
plt.rcParams["text.color"] = COLOR
plt.rcParams["axes.labelcolor"] = COLOR
plt.rcParams["axes.edgecolor"] = COLOR
plt.rcParams["xtick.color"] = COLOR
plt.rcParams["ytick.color"] = COLOR


# fire = fire[fire.Region == region]
def phenology_fire_size(fire):
    fire = fire[fire.lc.isin(config["land_covers"])]

    hue_order = [
        "Dormant",
        "Increase_early",
        "Increase_late",
        "Maximum",
        "Decrease_early",
        "Decrease_late",
    ]
    x_labels = [
        "Dormant",
        "Early \n green-up",
        "Late \ngreen-up",
        "Maximum",
        "Early \nsenescence",
        "Late\nsenescence",
    ]
    # _, axs = plt.subplots(1, 1, figsize=(8, 4), constrained_layout=True)
    # sns.countplot(data=fire, x='lc', hue="season", hue_order=hue_order)
    # plt.show()
    # years = range(2012, 2024)

    lc_groups = [config["land_covers"][:4], config["land_covers"][4:]]
    len_rows = int(len(config["land_covers"]) / 2)
    _, axs = plt.subplots(len_rows, 2, figsize=(10, 5))

    date_cols = [
        "Onset_Greenness_Increase_1",
        "Date_Mid_Greenup_Phase_1",
        "Onset_Greenness_Maximum_1",
        "Onset_Greenness_Decrease_1",
        "Date_Mid_Senescence_Phase_1",
        "Onset_Greenness_Minimum_1",
    ]
    for nr_row, ax_row in enumerate(axs):
        for nr_col, ax_col in enumerate(ax_row):
            lcs = lc_groups[nr_col]
            cs = lc_groups[nr_col]
            lc = lcs[nr_row]
            sub = fire[(fire.lc == lc)]
            durations = []
            for nr, phase in enumerate(hue_order):
                ph_sub = sub[sub.season == phase]
                if phase == "Dormant":
                    end_year = int(365 - sub["Onset_Greenness_Minimum_1"].median())
                    start_year = int(sub["Onset_Greenness_Increase_1"].median())
                    duration = end_year + start_year
                else:
                    duration = int(
                        sub[date_cols[nr]].median() - sub[date_cols[nr - 1]].median()
                    )
                durations.append(duration)
            subg = (
                sub.groupby(["season", "event"])["size"]
                .first()
                .reset_index()
                .groupby("season")["size"]
                .mean()[hue_order]
                .values
            )
            rates = subg  #  / np.array(durations)) / 11
            color = (color_dict[lc],)
            bars = ax_col.bar(range(6), rates, color=color)
            ax_col.bar_label(bars, fmt="%.0f")
            ax_col.axhline(0, color=COLOR)
            ax_col.grid(
                True, which="major", axis="x", c="gray", ls="--", lw=1, alpha=0.2
            )
            # if nr_row == len_rows - 1:
            #     sns.despine(bottom=False, left=False, ax=ax_col)
            # ax_col.set_xlim(2011.5, 2023.5)
            ax_col.set_xticks(range(6))
            # ax_col.set_ylim(0, 2.5)
            ax_col.set_yticks([])
            ax_col.set_ylabel(ukceh_classes_n[lc])
            if nr_row < len_rows - 1:
                sns.despine(bottom=True, left=True, ax=ax_col)
                # ax_col.set_xticks([])
                ax_col.tick_params(
                    axis="both",
                    bottom=False,
                    top=False,
                    labelbottom=False,
                    left=False,
                    right=False,
                    labelleft=True,
                )
            else:
                sns.despine(left=True, bottom=False, trim=True, offset=2, ax=ax_col)
                ax_col.set_xticklabels(x_labels)
                for tick in ax_col.xaxis.get_major_ticks()[2::2]:
                    tick.set_pad(14)
            ax_col.set_ylim(0, 38)
            plt.subplots_adjust(hspace=0.2)
        # plt.savefig(
        #     Path(
        #         config["data_dir"], "results/figures", "fire_phen_phase_mean_size.png"
        #     ),
        #     dpi=300,
        #     bbox_inches="tight",
        # )
    plt.show()


def phenology_fire_rates(fire):
    fire = fire[fire.lc.isin(config["land_covers"])]

    hue_order = [
        "Dormant",
        "Increase_early",
        "Increase_late",
        "Maximum",
        "Decrease_early",
        "Decrease_late",
    ]
    x_labels = [
        "Dormant",
        "Early \n green-up",
        "Late \ngreen-up",
        "Maximum",
        "Early \nsenescence",
        "Late\nsenescence",
    ]
    # _, axs = plt.subplots(1, 1, figsize=(8, 4), constrained_layout=True)
    # sns.countplot(data=fire, x='lc', hue="season", hue_order=hue_order)
    # plt.show()
    # years = range(2012, 2024)

    lc_groups = [config["land_covers"][:4], config["land_covers"][4:]]
    len_rows = int(len(config["land_covers"]) / 2)
    _, axs = plt.subplots(len_rows, 2, figsize=(10, 5))

    date_cols = [
        "Onset_Greenness_Increase_1",
        "Date_Mid_Greenup_Phase_1",
        "Onset_Greenness_Maximum_1",
        "Onset_Greenness_Decrease_1",
        "Date_Mid_Senescence_Phase_1",
        "Onset_Greenness_Minimum_1",
    ]

    # calc days for phase

    for nr_row, ax_row in enumerate(axs):
        for nr_col, ax_col in enumerate(ax_row):
            lcs = lc_groups[nr_col]
            cs = lc_groups[nr_col]
            lc = lcs[nr_row]
            sub = fire[(fire.lc == lc)]
            durations = []
            for nr, phase in enumerate(hue_order):
                ph_sub = sub[sub.season == phase]
                if phase == "Dormant":
                    end_year = int(365 - sub["Onset_Greenness_Minimum_1"].median())
                    start_year = int(sub["Onset_Greenness_Increase_1"].median())
                    duration = end_year + start_year
                else:
                    duration = int(
                        sub[date_cols[nr]].median() - sub[date_cols[nr - 1]].median()
                    )
                durations.append(duration)
            subg = sub.groupby("season")["lc"].count()[hue_order].values
            rates = (subg / np.array(durations)) / 11
            color = (color_dict[lc],)
            bars = ax_col.bar(range(6), rates, color=color)
            ax_col.bar_label(bars, fmt="%.2f")
            ax_col.axhline(0, color=COLOR)
            ax_col.grid(
                True, which="major", axis="x", c="gray", ls="--", lw=1, alpha=0.2
            )
            # if nr_row == len_rows - 1:
            #     sns.despine(bottom=False, left=False, ax=ax_col)
            # ax_col.set_xlim(2011.5, 2023.5)
            ax_col.set_xticks(range(6))
            # ax_col.set_ylim(0, 2.5)
            ax_col.set_yticks([])
            ax_col.set_ylabel(ukceh_classes_n[lc])
            if nr_row < len_rows - 1:
                sns.despine(bottom=True, left=True, ax=ax_col)
                # ax_col.set_xticks([])
                ax_col.tick_params(
                    axis="both",
                    bottom=False,
                    top=False,
                    labelbottom=False,
                    left=False,
                    right=False,
                    labelleft=True,
                )
            else:
                sns.despine(left=True, bottom=False, trim=True, offset=2, ax=ax_col)
                ax_col.set_xticklabels(x_labels)
                for tick in ax_col.xaxis.get_major_ticks()[2::2]:
                    tick.set_pad(14)
            plt.subplots_adjust(hspace=0.2)
        # plt.savefig(
        #     Path(config["data_dir"], "results/figures", "fire_phen_phase_rate.png"),
        #     dpi=300,
        #     bbox_inches="tight",
        # )

    plt.show()


fire = pd.read_parquet(fire_phenology_file_name())
phenology_fire_size(fire)
