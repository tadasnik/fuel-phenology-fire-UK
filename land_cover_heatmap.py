import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import MonthLocator, num2date
from configuration import config, ukceh_classes_n, color_dict


def percent_cover_heatmap(dfr: pd.DataFrame) -> pd.DataFrame:
    """Calculate percent area coverage by region by the land covers listed in lcs"""
    dfr = dfr.loc[:, config["regions"]]
    urban = [20, 21]
    water = [13, 14]
    veg = [5, 6, 8, 19]
    barren = [12, 15, 16, 17, 18]
    lcs_dfr = dfr.loc[config["land_covers"]]
    lcs_dfr.loc[12, :] = dfr.loc[barren].sum(axis=0)
    lcs_dfr.loc[13, :] = dfr.loc[water].sum(axis=0)
    lcs_dfr.loc[19, :] = dfr.loc[veg].sum(axis=0)
    lcs_dfr.loc[20, :] = dfr.loc[urban].sum(axis=0)
    total = dfr.sum(axis=0)
    prc = (lcs_dfr / total) * 100

    fig, axs = plt.subplots(1, 1, figsize=(10, 7))
    sns.heatmap(prc.T, cmap="Reds", annot=True, fmt=".1f", cbar=False, ax=axs)
    xtick_labels = [ukceh_classes_n[x] for x in config["land_covers"]]
    xtick_labels.extend(["Barren\nland", "Inland\nwater",
                         "Other\nvegetation", "Urban\nsuburban"])
    axs.set_xticklabels(xtick_labels, rotation=90)
    axs.set_title("Land cover as % of the region's area")
    plt.savefig(
        Path(config["data_dir"], "results/figures", "land_cover_percent_region.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()


if __name__ == "__main__":
    dfr = pd.read_parquet(Path(config["data_dir"], "lc_counts_per_region.parquet"))

