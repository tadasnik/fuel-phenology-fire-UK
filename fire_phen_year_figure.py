import pandas as pd
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

fire = pd.read_parquet(fire_phenology_file_name())

# fire = fire[fire.Region == region]

fire = fire[fire.lc.isin(config["land_covers"])]

lc_groups = [config["land_covers"][:4], config["land_covers"][4:]]

years = range(2012, 2024)
len_rows = int(len(config["land_covers"]) / 2) 
_, axs = plt.subplots(
    len_rows, 2, figsize=(12, 8)
)
for nr_row, ax_row in enumerate(axs):
    for nr_col, ax_col in enumerate(ax_row):
        lcs = lc_groups[nr_col]
        lc = lcs[nr_row]
        subg = fire[(fire.lc == lc) & (fire.season_green == 1)]
        subg = subg.groupby("year")["lc"].count().values

        subd = fire[(fire.lc == lc) & (fire.season_green == 0) ]
        subd = subd.groupby("year")["lc"].count().values
        color = (color_dict[lc],)
        bars = ax_col.bar(years, subg, color=color)
        ax_col.bar_label(bars)
        bars_i = ax_col.bar(years, subd * -1, color=color, alpha=0.5)
        ax_col.bar_label(bars_i, labels=subd)
        ax_col.axhline(0, color=COLOR)
        ax_col.grid(True, which="major", axis='x', c="gray", ls="--", lw=1, alpha=0.2)
       # if nr_row == len_rows - 1:
        #     sns.despine(bottom=False, left=False, ax=ax_col)
        ax_col.set_xlim(2011.5, 2023.5)
        ax_col.set_xticks(years)
        ax_col.set_ylim(-565, 430)
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
            sns.despine(left=True, bottom=False, trim=True, offset=-2, ax=ax_col)
        plt.subplots_adjust(hspace=.05)
    plt.savefig(
        Path(config["data_dir"], "results/figures", "year_fire_phen.png"),
        dpi=300,
        bbox_inches="tight",
    )
 
plt.show()
