import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from configuration import config, ukceh_classes_n
from prepare_data import fire_file_name


def fire_rates_region_lc(dfr: pd.DataFrame, fire: pd.DataFrame):
    """Calculate area normalizes fire occurrence rates per region and land cover"""
    fire_c = fire.groupby(["Region", "lc"])["frp"].count().reset_index()
    fdfr = fire_c.pivot(index="lc", columns="Region", values="frp").fillna(0)
    dfr = dfr.loc[:, config["regions"]]
    fdfr = fdfr.loc[:, config["regions"]]
    fdfr.loc[:, "Combined"] = fdfr.sum(axis=1)
    dfrk = dfr * 400 / 1e6
    dfrk.loc[:, "Combined"] = dfrk.sum(axis=1)
    rates = ((fdfr / dfrk).fillna(0))
    rates = rates[dfrk > 20]
    rates = rates.loc[config["land_covers"], :]
    _, ax = plt.subplots(1, 1, figsize=(7, 7))
    sns.heatmap(rates.T, cmap="Reds", annot=True, fmt=".2f", cbar=False, ax=ax)
    xtick_labels = [ukceh_classes_n[x] for x in config["land_covers"]]
    # xtick_labels.extend(["Barren\nland", "Inland\nwater",
    #                      "Other\nvegetation", "Urban\nsuburban"])
    print(xtick_labels)
    ax.set_xticklabels(xtick_labels, rotation=90)
    ax.set_title("Fire detections per km\u00b2")
    ax.set_ylabel("")
    plt.savefig(
        Path(config["data_dir"], "results/figures", "fire_rates_region_land_cover.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()


def percent_cover_heatmap(dfr: pd.DataFrame):
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
    _, axs = plt.subplots(1, 1, figsize=(10, 7))
    ax = axs[0][0]
    sns.heatmap(prc.T, cmap="Reds", annot=True, fmt=".1f", cbar=False, ax=ax)
    xtick_labels = [ukceh_classes_n[x] for x in config["land_covers"]]
    xtick_labels.extend(["Barren\nland", "Inland\nwater",
                         "Other\nvegetation", "Urban\nsuburban"])
    ax.set_xticklabels(xtick_labels, rotation=90)
    ax.set_title("Land cover as % of the region's area")
    plt.savefig(
        Path(config["data_dir"], "results/figures", "land_cover_percent_region.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()


if __name__ == "__main__":
    fire = pd.read_parquet(fire_file_name())
    dfr = pd.read_parquet(Path(config["data_dir"], "lc_counts_per_region.parquet"))
    fire_rates_region_lc(dfr, fire)

