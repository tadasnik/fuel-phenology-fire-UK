from pathlib import Path

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shapereader
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import rioxarray
import seaborn as sns
from cartopy.feature import ShapelyFeature
from matplotlib import colors
from matplotlib.patches import Patch

from configuration import color_dict, config, ukceh_classes, ukceh_classes_n
from prepare_data import fire_file_name

COLOR = "0.3"
plt.rcParams["font.family"] = "Fira Sans"
plt.rcParams["text.color"] = COLOR
plt.rcParams["axes.labelcolor"] = COLOR
plt.rcParams["axes.edgecolor"] = COLOR
plt.rcParams["xtick.color"] = COLOR
plt.rcParams["ytick.color"] = COLOR
plt.rcParams["figure.constrained_layout.use"] = True
plt.rcParams["text.color"] = ".2"


def stack_map_legend_plot():
    fig = plt.figure(figsize=(12, 7.5))

    subfigs = fig.subfigures(1, 2, width_ratios=[1, 2.2])

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
    axs = subfigs[1].subplots(5, 2)
    plt.rcParams["text.color"] = ".2"
    for nr, ax in enumerate(axs.flatten()):
        try:
            region = config["regions"][nr]
            fireg = (
                fire[fire.Region == region]
                .groupby(["month"])["lc"]
                .value_counts()
                .unstack()
            )
        except IndexError:
            region = "Combined"
            fireg = fire.groupby(["month"])["lc"].value_counts().unstack()
        fireg = fireg.fillna(0, axis=1)
        vals = []
        labs = []
        colors_list = []
        for lc in config["land_covers"]:
            try:
                vals.append(fireg[lc].values)
                labs.append(ukceh_classes_n[lc])
                colors_list.append(color_dict[lc])
            except:
                pass
        ax.stackplot(
            fireg.index.values.astype(int),
            vals,
            colors=colors_list,
            labels=labs,
            linewidth=0.3,
            edgecolor="white",
        )
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(months)
        ax.set_xlim(0.95, 12.05)
        if region in ["South-east", "Central"]:
            ax.set_title(f"{region}", y=0.75, x=0.3)
        elif region == "North-west":
            ax.set_title(f"{region}", y=0.75, x=0.8)
        else:
            ax.set_title(f"{region}", y=0.75, x=0.7)
        ax.grid(True, which="major", axis="x", c="gray", ls="--", lw=1, alpha=0.2)
        if nr < 8:
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
        if nr == 4:
            ax.set_ylabel("VIIRS fire detection count")
        # if nr==0:
        #    ax.text(0.1, 0.9, 'A', transform=ax.transAxes, fontsize=15)
        plt.subplots_adjust(hspace=0.05)

    subfigs_ = subfigs[0].subfigures(2, 1, height_ratios=[2.5, 1.0])
    ax = subfigs_[0].add_subplot(1, 1, 1, projection=ccrs.OSGB())
    region_split = [
        "Northern\nScotland",
        "Eastern\nScotland",
        "Southern\nScotland",
        "North\nwest",
        "North\neast",
        "South\nwest",
        "Central",
        "South\neast",
        "Northern\nIreland",
    ]

    colors_list = [color_dict[x] for x in config["land_covers"]]
    c_map = colors.ListedColormap(colors_list)
    norm = colors.BoundaryNorm(
        [0.5, 1.5, 2.5, 3.5, 4.5, 7.5, 9.5, 10.5, 11.5], ncolors=8, clip=True
    )
    reg_file = Path(config["data_dir"], "HadUKP_regions.shp")
    c_shapes = shapereader.Reader(reg_file)
    geoms = list(c_shapes.geometries())
    regions = list(c_shapes.records())
    regions_geoms = [x[1] for x in zip(regions, geoms)]
    reg_feat = ShapelyFeature(
        regions_geoms,
        ccrs.OSGB(),
        facecolor=(1, 1, 1, 0),
        edgecolor="0.6",
        linewidth=0.1,
    )
    reg_int_file = Path(config["data_dir"], "Hadley_regions_interior.shp")
    c_int_shapes = shapereader.Reader(reg_int_file)
    geoms_int = list(c_int_shapes.geometries())
    regions_int = list(c_shapes.records())
    regions_int_geoms = [x[1] for x in zip(regions_int, geoms_int)]
    reg_int_feat = ShapelyFeature(
        regions_int_geoms,
        ccrs.OSGB(),
        facecolor=(1, 1, 1, 0),
        edgecolor="0.5",
        linewidth=1.5,
    )

    ds = rioxarray.open_rasterio(Path(config["data_dir"], "LCD_2018_500m.tif"))
    ds = ds.sel(band=1)
    ds_masked = ds.where(ds.isin(config["land_covers"]))
    ds_masked.plot.pcolormesh(
        ax=ax, transform=ccrs.OSGB(), cmap=c_map, norm=norm, add_colorbar=False
    )
    ax.add_feature(reg_feat, zorder=2)
    ax.add_feature(reg_int_feat, zorder=3)
    ax.add_feature(cfeature.OCEAN.with_scale("10m"), color="white", zorder=0)
    ax.set_ylim(250, 1050000)
    ax.axis("off")
    ax.set_title(None)
    for nr, reg in enumerate(regions):
        x = reg.geometry.centroid.x
        y = reg.geometry.centroid.y

        ax.text(
            x,
            y,
            region_split[nr],
            color="0.3",
            size=13,
            weight="bold",
            ha="center",
            va="center",
            transform=ccrs.OSGB(),
        )
    # ax.text(0.05, 0.95, 'B', transform=ax.transAxes, fontsize=15)
    ax = subfigs_[1].add_subplot(1, 1, 1)
    legend_elements = []
    for nr, item in enumerate(config["land_covers"]):
        pp = Patch(
            facecolor=color_dict[item],
            edgecolor="white",
            linewidth=1,
            label=ukceh_classes[item],
        )
        legend_elements.append(pp)

    # Create the figure
    leg = ax.legend(handles=legend_elements, loc="center", frameon=False)

    for patch in leg.get_patches():
        patch.set_height(12)
        patch.set_width(30)
        patch.set_x(-4)
        patch.set_y(-2.5)
    ax.set_axis_off()
    plt.savefig(
        Path(config["data_dir"], "results/figures", "fire_clim_stack_map_interior.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()


def stack_plot_all_regions(fire, config):
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
    fig, axs = plt.subplots(5, 2, figsize=(10, 10))
    plt.rcParams["text.color"] = ".2"
    # fig.tight_layout()
    for nr, ax in enumerate(axs.flatten()):
        try:
            region = config["regions"][nr]
            fireg = (
                fire[fire.Region == region]
                .groupby(["month"])["lc"]
                .value_counts()
                .unstack()
            )
        except IndexError:
            region = "All"
            fireg = fire.groupby(["month"])["lc"].value_counts().unstack()
        fireg = fireg.fillna(0, axis=1)
        vals = []
        labs = []
        # colors = [color_dict[x] for x in config["land_covers"]]
        colors = []
        for lc in config["land_covers"]:
            try:
                vals.append(fireg[lc].values)
                labs.append(ukceh_classes_n[lc])
                colors.append(color_dict[lc])
            except:
                pass
        ax.stackplot(
            fireg.index.values.astype(int),
            vals,
            colors=colors,
            labels=labs,
            linewidth=0.3,
            edgecolor="white",
        )
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(months)
        ax.set_xlim(0.95, 12.05)
        # ax.set_ylim(0, 500)
        if region in ["South-east", "Central"]:
            ax.set_title(f"{region}", y=0.75, x=0.3)
        elif region == "North-west":
            ax.set_title(f"{region}", y=0.75, x=0.8)
        else:
            ax.set_title(f"{region}", y=0.75, x=0.7)
        # ax.set_title(f"{region} monthly fire detection counts", pad=10)
        ax.grid(True, which="major", axis="x", c="gray", ls="--", lw=1, alpha=0.2)
        # if nr_row == len_rows - 1:
        #     sns.despine(bottom=False, left=False, ax=ax_col)
        # ax_col.set_yticks([])
        if nr < 8:
            sns.despine(bottom=False, left=False, trim=True, offset=1, ax=ax)
            # ax_col.set_xticks([])
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
        if nr == 4:
            ax.set_ylabel("VIIRS fire detection count")
        plt.subplots_adjust(hspace=0.05)

        # ax.tick_params(axis='x', rotation=90)
        # ax.tick_params(labelrotation=45)
        # for item in ax.get_xticklabels():
        #    item.set_rotation(45)

        # fig=plt.figure(figsize=(20,3), dpi= 100)
        # plt.suptitle('Fire detections per month and land cover type,
        #               VIIRS record (2012-2022/7/31)',y=1.05)
    # plt.tight_layout()
    # plt.xticks(rotation=90)
    # fig.subplots_adjust(top=0.85)
    plt.savefig(
        Path(config["data_dir"], "results/figures", "fire_clim_stack.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()


def stack_plot(dfr, region, config):
    fig, ax = plt.subplots(1, 1, figsize=(10, 3.5))
    plt.rcParams["text.color"] = ".2"
    fig.tight_layout()
    fireg = dfr.groupby(["month"])["lc"].value_counts().unstack()
    fireg = fireg.fillna(0, axis=1)
    vals = []
    labs = []
    # colors = [color_dict[x] for x in config["land_covers"]]
    colors_list = []
    for lc in config["land_covers"]:
        try:
            vals.append(fireg[lc].values)
            labs.append(ukceh_classes_n[lc])
            colors_list.append(color_dict[lc])
        except:
            pass
    ax.stackplot(
        fireg.index.values.astype(int),
        vals,
        colors=colors_list,
        labels=labs,
        linewidth=0.5,
        edgecolor="white",
    )
    ax.set_xticks(range(1, 13))
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
    ax.set_xlim(0.8, 12.2)
    # ax.set_ylim(0, 500)
    ax.set_ylabel("Active fire detections")
    ax.set_title(f"{region} monthly fire detection counts", pad=10)
    # ax.tick_params(axis='x', rotation=90)
    # ax.tick_params(labelrotation=45)
    # for item in ax.get_xticklabels():
    #    item.set_rotation(45)

    # fig=plt.figure(figsize=(20,3), dpi= 100)
    sns.despine(offset=10, trim=True)
    # plt.suptitle('Fire detections per month and land cover type,
    #               VIIRS record (2012-2022/7/31)',y=1.05)
    plt.tight_layout()
    # plt.xticks(rotation=90)
    # fig.subplots_adjust(top=0.85)
    # plt.savefig(f'figures/s_w_stackplot_{region}.png', dpi=300, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    # eviq = evi_quantiles()
    fire = pd.read_parquet(fire_file_name())
    fire = fire[fire.lc.isin(config["land_covers"])]
    # region = "North-west"
    stack_map_legend_plot()
    # stack_plot_all_regions(fire, config)
