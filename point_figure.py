import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import MonthLocator, num2date
from configuration import config
from prepare_data import phenology_file


COLOR = "0.3"
plt.rcParams["font.family"] = "Fira Sans"
plt.rcParams["text.color"] = COLOR
plt.rcParams["axes.labelcolor"] = COLOR
plt.rcParams["axes.edgecolor"] = COLOR
plt.rcParams["xtick.color"] = COLOR
plt.rcParams["ytick.color"] = COLOR

torange = (1.0, 0.4980392156862745, 0.054901960784313725)
tblue = (0.12156862745098039, 0.4666666666666667, 0.7058823529411765)
tgreen = (0.17254901960784313, 0.6274509803921569, 0.17254901960784313)
tpurple = (0.5803921568627451, 0.403921568627451, 0.7411764705882353)
tpink = (0.8901960784313725, 0.4666666666666667, 0.7607843137254902)
tbrown = (0.5490196078431373, 0.33725490196078434, 0.29411764705882354)
tchaki = (0.7372549019607844, 0.7411764705882353, 0.13333333333333333)
tred = (0.8392156862745098, 0.15294117647058825, 0.1568627450980392)

ukceh_classes = {
    1: "Deciduous woodland",
    2: "Coniferous woodland",
    3: "Arable",
    4: "Improved grassland",
    5: "Neutral grassland",
    6: "Calcareous grassland",
    7: "Acid grassland",
    8: "Fen",
    9: "Heather",
    10: "Heather grassland",
    11: "Bog",
    12: "Inland rock",
    13: "Saltwater",
    14: "Freshwater",
    15: "Supralittoral rock",
    16: "Supralittoral sediment",
    17: "Littoral rock",
    18: "Littoral sediment",
    19: "Saltmarsh",
    20: "Urban",
    21: "Suburban",
}

ukceh_classes_n = {
    1: "Deciduous\nwoodland",
    2: "Coniferous\nwoodland",
    3: "Arable",
    4: "Improved\ngrassland",
    5: "Neutral\ngrassland",
    6: "Calcareous\ngrassland",
    7: "Acid\ngrassland",
    8: "Fen",
    9: "Heather",
    10: "Heather\ngrassland",
    11: "Bog",
    12: "Inland\nrock",
    13: "Saltwater",
    14: "Freshwater",
    15: "Supralittoral\nrock",
    16: "Supralittoral\nsediment",
    17: "Littoral\nrock",
    18: "Littoral\nsediment",
    19: "Saltmarsh",
    20: "Urban",
    21: "Suburban",
}

color_dict = {
    0: "white",
    1: tgreen,
    2: tblue,
    3: tchaki,
    4: tchaki,
    7: torange,
    9: tpink,
    10: tbrown,
    11: tpurple,
    21: tred,
}


def phen_values_point_plot(phe: pd.DataFrame, params: list, out_file_name):
    _, axs = plt.subplots(1, 2, figsize=(15, 7), constrained_layout=True)
    lcs = [3, 7, 9, 10, 11]
    markers = ["o", "v", "s", "*", "D"]
    ylabels = [x.replace(" ", "\n") for x in config["regions"]]
    colors = [color_dict[x] for x in lcs]
    dfs = phe[phe.lc.isin(lcs)].copy()
    dfs["lc"] = dfs["lc"].replace(ukceh_classes)
    for nr, ax in enumerate(axs):
        var = params[nr]["column"]
        print(var)
        sns.pointplot(
            data=dfs,
            x=var,
            y="Region",
            hue="lc",
            markers=markers,
            errorbar=("pi", 50),
            capsize=0.3,
            errwidth=0.6,
            join=False,
            dodge=0.4,
            palette=colors,
            ax=ax,
        )
        ax.grid(True, "major", "x", ls="--", lw=1, c="k", alpha=0.3)
        ax.set_yticks(np.linspace(-0.5, 8.5, 10), minor=True)
        ax.grid(True, "minor", "y", ls="-", lw=1, c="k", alpha=0.1)
        ax.tick_params(
            axis="both",
            which="major",
            labelsize="medium",
            bottom=False,
            top=False,
            labelbottom=True,
            left=True,
            right=False,
            labelleft=True,
        )
        ax.tick_params(
            which="minor",
            left=False,
        )
        if nr != 0:
            ax.tick_params(
                axis="both",
                which="major",
                left=False,
                right=True,
                labelright=True,
                labelleft=False,
            )
            ax.tick_params(
                which="minor",
                right=False,
            )
            ax.get_legend().remove()
        ax.set_yticklabels(ylabels)
        ax.set_ylabel(None)
        ax.set_xlabel(f"{params[nr]['xlabel']}")
        ax.set_title(f"{params[nr]['title']}")
    plt.savefig(
        Path(config["data_dir"], "results/figures", f"{out_file_name}.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()


params_season_length = [
    {
        "column": "Growing_Season_Length_1",
        "title": "Growing Season Length",
        "xlabel": "Days",
    },
    {
        "column": "EVI2_Onset_Greenness_Maximum_1",
        "title": "EVI2 Onset Greenness Maximum",
        "xlabel": "EVI2",
    },
]

params_season_onset = [
    {
        "column": "Date_Mid_Greenup_Phase_1",
        "title": "Mid Greenup",
        "xlabel": "DOY",
    },
    {
        "column": "Date_Mid_Senescence_Phase_1",
        "title": "Mid Senescence",
        "xlabel": "DOY",
    },
]


phe = pd.read_parquet(phenology_file())
# phen_values_point_plot(phe, params=params_season_length, out_file_name="phen_values")
# phen_values_point_plot(phe, params=params_season_onset, out_file_name="phen_mid_seasons")
