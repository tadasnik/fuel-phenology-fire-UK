from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.dates import MonthLocator, num2date
from matplotlib.ticker import FuncFormatter

from configuration import color_dict, config, ukceh_classes
from prepare_data import (
    evi2_quantiles_file,
    fire_file_name,
    phenology_file,
    phenology_quantiles_file,
    q5,
    q25,
    q50,
    q75,
    q95,
)

COLOR = "0.3"
plt.rcParams["font.family"] = "Fira Sans"
plt.rcParams["text.color"] = COLOR
plt.rcParams["axes.labelcolor"] = COLOR
plt.rcParams["axes.edgecolor"] = COLOR
plt.rcParams["xtick.color"] = COLOR
plt.rcParams["ytick.color"] = COLOR


def land_cover_evi_upd(pheg, fire):
    lcs = config["land_covers"]
    _, axs = plt.subplots(2, 4, figsize=(15, 7))
    for nr, ax in enumerate(axs.flatten()):
        ax2 = ax.twinx()
        lc = lcs[nr]
        file_name = Path(
            config["data_dir"],
            "gee_results",
            f"VNP13A1_{lc}_quantiles.parquet",
        )
        sub = pd.read_parquet(file_name)
        sub["date"] = pd.to_datetime(2016 * 1000 + sub["doy"], format="%Y%j")
        print(sub.date.min(), sub.date.max())
        if nr in [0, 4]:
            sns.despine(bottom=False, left=False, right=True, offset=2, ax=ax)
            ax.tick_params(
                axis="both",
                bottom=True,
                top=False,
                left=True,
                right=False,
                labelleft=True,
            )
            ax.set_ylabel("EVI2")
        else:
            sns.despine(bottom=False, left=True, right=True, offset=2, ax=ax)
            ax.tick_params(
                axis="both",
                bottom=True,
                top=False,
                left=False,
                right=False,
                labelleft=False,
            )
        artists = []
        artists += ax.plot(sub.date, sub.q50, ls="-", c=color_dict[lc], zorder=5)
        artists += [
            ax.fill_between(
                sub.date,
                sub.q25,
                sub.q75,
                color=color_dict[lc],
                alpha=0.2,
                zorder=4,
            )
        ]
        artists += [
            ax.fill_between(
                sub.date,
                sub.q5,
                sub.q95,
                color=color_dict[lc],
                alpha=0.1,
                zorder=3,
            )
        ]
        phesub = phe[phe.lc == lc].copy()
        phesub["doy"] = phesub.date.dt.dayofyear
        pheg = phesub.groupby(["lc"])
        pheg = pheg.agg(
            {
                "Onset_Greenness_Increase_1": [q25, q50, q75],
                "Onset_Greenness_Maximum_1": [q25, q50, q75],
                "Onset_Greenness_Decrease_1": [q25, q50, q75],
                "Onset_Greenness_Minimum_1": [q25, q50, q75],
            }
        )
        date_cols = [
            "Onset_Greenness_Increase_1",
            "Onset_Greenness_Maximum_1",
            "Onset_Greenness_Decrease_1",
            "Onset_Greenness_Minimum_1",
        ]
        try:
            ph_dates = pheg.loc[lc][date_cols][:, "q50"]
            ph_dates = pd.to_datetime(2016 * 1000 + ph_dates, format="%Y%j")
            ph_dates_min = pheg.loc[lc][date_cols][:, "q25"]
            ph_dates_min = pd.to_datetime(2016 * 1000 + ph_dates_min, format="%Y%j")
            ph_dates_m = pheg.loc[lc][date_cols][:, "q75"]
            ph_dates_m = pd.to_datetime(2016 * 1000 + ph_dates_m, format="%Y%j")
            for pair in zip(ph_dates_min, ph_dates_m):
                ax.axvspan(pair[0], pair[1], color="0.9", alpha=0.5, zorder=0)
            for line in ph_dates:
                ax.axvline(line, linestyle="--", color="0.5", zorder=1)
        except KeyError:
            continue
        ser = fire[(fire.lc == lc)].groupby("doy")["frp"].count()
        f_dates = pd.to_datetime(2016 * 1000 + ser.index, format="%Y%j")
        print(f_dates.min(), f_dates.max())
        ax.grid(True, which="major", c="gray", ls="-", lw=1, alpha=0.2)
        months = MonthLocator([3, 6, 9, 12], bymonthday=1)  # , interval=3)
        ax.xaxis.set_major_formatter(
            FuncFormatter(lambda x, pos=None: "{dt:%b} {dt.day}".format(dt=num2date(x)))
        )
        if nr > 3:
            ax.xaxis.set_major_locator(months)
        else:
            ax.xaxis.set_major_locator(months)
            ax.set_xticklabels([])
        ax.set_ylim(0.1, 0.8)
        ax.set_title(f"{ukceh_classes[lc]}")
        sns.despine(bottom=True, left=True, right=True, offset=2, ax=ax2)
        ax2.bar(f_dates, ser, color=color_dict[21], width=1, alpha=0.8, zorder=-1)
        ax2.set_ylim(0, 150)
        ax2.set_yticks([])
        if nr not in [3, 7]:
            sns.despine(bottom=True, left=True, right=True, offset=2, ax=ax2)
            ax2.tick_params(
                axis="both",
                bottom=False,
                top=False,
                left=False,
                right=False,
                labelleft=False,
            )
        else:
            sns.despine(bottom=True, left=True, right=False, offset=2, ax=ax2)
            ax2.set_ylabel("VIIRS fire detections", color="red")
            ax2.set_yticks([0, 75, 150])
            ax2.tick_params(
                axis="both",
                bottom=False,
                top=False,
                left=False,
                right=True,
                labelright=True,
                labelleft=False,
            )
    plt.subplots_adjust(wspace=0.05)
    plt.savefig(
        Path(config["data_dir"], "results/figures", "land_cover_evi2_phen.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()


def land_cover_evi(pheg, fire):
    lcs = config["land_covers"]
    _, axs = plt.subplots(2, 4, figsize=(15, 7))
    for nr, ax in enumerate(axs.flatten()):
        lc = lcs[nr]
        file_name = Path(
            config["data_dir"],
            "gee_results",
            f"VNP13A1_{lc}_quantiles.parquet",
        )
        sub = pd.read_parquet(file_name)
        sub["date"] = pd.to_datetime(2016 * 1000 + sub["doy"], format="%Y%j")
        print(sub.date.min(), sub.date.max())
        artists = []
        artists += ax.plot(sub.date, sub.q50, ls="-", c=color_dict[lc], zorder=5)
        artists += [
            ax.fill_between(
                sub.date,
                sub.q25,
                sub.q75,
                color=color_dict[lc],
                alpha=0.2,
                zorder=4,
            )
        ]
        artists += [
            ax.fill_between(
                sub.date,
                sub.q5,
                sub.q95,
                color=color_dict[lc],
                alpha=0.1,
                zorder=3,
            )
        ]
        phesub = phe[phe.lc == lc].copy()
        phesub["doy"] = phesub.date.dt.dayofyear
        pheg = phesub.groupby(["lc"])
        pheg = pheg.agg(
            {
                "Onset_Greenness_Increase_1": [q25, q50, q75],
                "Onset_Greenness_Maximum_1": [q25, q50, q75],
                "Onset_Greenness_Decrease_1": [q25, q50, q75],
                "Onset_Greenness_Minimum_1": [q25, q50, q75],
                # "Date_Mid_Greenup_Phase_1": [q5, q25, q50, q75, q95],
                # "Date_Mid_Senescence_Phase_1": [q5, q25, q50, q75, q95],
                # "EVI2_Growing_Season_Area_1": [q5, q25, q50, q75, q95],
                # "Growing_Season_Length_1": [q5, q25, q50, q75, q95],
                # "EVI2_Onset_Greenness_Increase_1": [q5, q25, q50, q75, q95],
                # "EVI2_Onset_Greenness_Maximum_1": [q5, q25, q50, q75, q95],
            }
        )
        date_cols = [
            "Onset_Greenness_Increase_1",
            "Onset_Greenness_Maximum_1",
            "Onset_Greenness_Decrease_1",
            "Onset_Greenness_Minimum_1",
        ]
        try:
            ph_dates = pheg.loc[lc][date_cols][:, "q50"]
            ph_dates = pd.to_datetime(2016 * 1000 + ph_dates, format="%Y%j")
            ph_dates_min = pheg.loc[lc][date_cols][:, "q25"]
            ph_dates_min = pd.to_datetime(2016 * 1000 + ph_dates_min, format="%Y%j")
            ph_dates_m = pheg.loc[lc][date_cols][:, "q75"]
            ph_dates_m = pd.to_datetime(2016 * 1000 + ph_dates_m, format="%Y%j")
            # low_d = ph_dates - ph_dates_min
            # high_d = ph_dates_m - ph_dates
            # errors = np.array(list(zip(low_d, high_d))).T
            # ph_values = pheg.loc[region, lc].filter(like='EVI2')[:, 'q25'].values * 10000
            # ax.scatter(ph_dates, ph_values[[0, 1, 1, 0]], color=cols_d[lc])
            # artists += ax.errorbar(ph_dates, ph_values[[0, 1, 1, 0]], xerr=errors,
            #              fmt='none', ecolor='k')
            for pair in zip(ph_dates_min, ph_dates_m):
                ax.axvspan(pair[0], pair[1], color="0.9", alpha=0.5, zorder=0)
            for line in ph_dates:
                ax.axvline(line, linestyle="--", color="0.5", zorder=1)
        except KeyError:
            continue
        ser = fire[(fire.lc == lc)].groupby("doy")["frp"].count()
        f_dates = pd.to_datetime(2016 * 1000 + ser.index, format="%Y%j")
        print(f_dates.min(), f_dates.max())
        ax2 = ax.twinx()
        ax2.bar(f_dates, ser, color=color_dict[21], width=1, alpha=0.8, zorder=0)
        ax2.set_ylim(0, 150)
        ax2.set_yticks([])
        ax.grid(True, which="major", c="gray", ls="-", lw=1, alpha=0.2)
        months = MonthLocator([3, 6, 9, 12], bymonthday=1)  # , interval=3)
        ax.xaxis.set_major_formatter(
            FuncFormatter(lambda x, pos=None: "{dt:%b} {dt.day}".format(dt=num2date(x)))
        )
        ax.xaxis.set_major_locator(months)
        ax.set_ylim(0.1, 0.8)
        ax.set_title(f"{ukceh_classes[lc]}")
    plt.savefig(
        Path(config["data_dir"], "results/figures", "land_cover_evi2_phen.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()


def region_evi(eviq, pheg, fire):
    lcs = [9, 11, 7, 10, 3, 4, 1, 2]
    eviq["date"] = pd.to_datetime(2016 * 1000 + eviq["doy"], format="%Y%j")
    _, axs = plt.subplots(len(config["regions"]), len(lcs), figsize=(45, 35))
    for nr_r, axr in enumerate(axs):
        for nr_lc, ax in enumerate(axr):
            lc = lcs[nr_lc]
            region = config["regions"][nr_r]
            sub = eviq[(eviq.Region == region) & (eviq.lc == lc)]
            artists = []
            artists += ax.plot(sub.date, sub.q50, ls="-", c=color_dict[lc])
            artists += [
                ax.fill_between(
                    sub.date, sub.q25, sub.q75, color=color_dict[lc], alpha=0.2
                )
            ]
            artists += [
                ax.fill_between(
                    sub.date, sub.q5, sub.q95, color=color_dict[lc], alpha=0.1
                )
            ]
            date_cols = [
                "Onset_Greenness_Increase_1",
                "Onset_Greenness_Maximum_1",
                "Onset_Greenness_Decrease_1",
                "Onset_Greenness_Minimum_1",
            ]
            try:
                ph_dates = pheg.loc[region, lc][date_cols][:, "q50"]
                ph_dates = pd.to_datetime(2016 * 1000 + ph_dates, format="%Y%j")
                ph_dates_min = pheg.loc[region, lc][date_cols][:, "q25"]
                ph_dates_min = pd.to_datetime(2016 * 1000 + ph_dates_min, format="%Y%j")
                ph_dates_m = pheg.loc[region, lc][date_cols][:, "q75"]
                ph_dates_m = pd.to_datetime(2016 * 1000 + ph_dates_m, format="%Y%j")
                # low_d = ph_dates - ph_dates_min
                # high_d = ph_dates_m - ph_dates
                # errors = np.array(list(zip(low_d, high_d))).T
                # ph_values = pheg.loc[region, lc].filter(like='EVI2')[:, 'q25'].values * 10000
                # ax.scatter(ph_dates, ph_values[[0, 1, 1, 0]], color=cols_d[lc])
                # artists += ax.errorbar(ph_dates, ph_values[[0, 1, 1, 0]], xerr=errors,
                #              fmt='none', ecolor='k')
                for pair in zip(ph_dates_min, ph_dates_m):
                    ax.axvspan(pair[0], pair[1], color="0.9", alpha=0.5, zorder=0)
                for line in ph_dates:
                    ax.axvline(line, linestyle="--", color="0.5", zorder=1)
            except KeyError:
                continue
            ser = (
                fire[(fire.Region == region) & (fire.lc == lc)]
                .groupby("doy")["frp"]
                .count()
            )
            # sizes = (
            #     fire[(fire.Region == region) & (fire.lc == lc)]
            #     .groupby("doy")["size"]
            #     .max()
            # )
            f_dates = pd.to_datetime(2016 * 1000 + ser.index, format="%Y%j")
            ax2 = ax.twinx()
            ax2.bar(f_dates, ser, color=color_dict[21], width=1, alpha=0.8, zorder=5)

            ax2.set_ylim(0, fire.groupby(["Region", "lc", "doy"])["frp"].count().max())
            ax2.set_yticks([])
            ax.grid(True, which="major", c="gray", ls="-", lw=1, alpha=0.2)

            months = MonthLocator([3, 6, 9, 12], bymonthday=1)  # , interval=3)
            ax.xaxis.set_major_formatter(
                FuncFormatter(
                    lambda x, pos=None: "{dt:%b} {dt.day}".format(dt=num2date(x))
                )
            )
            ax.xaxis.set_major_locator(months)
            ax.set_ylim(0, 8000)
            ax.set_title(f"{region}")
    plt.savefig(
        Path(config["data_dir"], "results/figures", "region_evi_phen.png"),
        dpi=300,
        bbox_inches="tight",
    )


def drought_evi_vs_norm(pheg, fires):
    events = [
        ["South-west", 7, 2018],
        ["North-west", 9, 2018],
        ["Central", 4, 2022],
        ["South-west", 10, 2023],
    ]
    _, axs = plt.subplots(2, 2, figsize=(15, 8), constrained_layout=True)
    # dem = pd.read_parquet(dem_file())
    for nr, event in enumerate(events):
        region = event[0]
        lc = event[1]
        year = event[2]
        ax = axs.flatten()[nr]
        file_name = Path(
            config["data_dir"],
            "gee_results",
            f"VNP13A1_{region}_{lc}_sample.parquet",
        )
        df = pd.read_parquet(file_name)
        # dem_sub = dem[(dem.Region == region) & (dem.lc == lc)]
        # df = pd.merge(df, dem_sub, on=['Region', 'lc', 'fid'], how='left')
        df["EVI2"] *= 0.0001
        # df = df[df["pixel_reliability"] < 5]
        df_sub = df[df.year == year]
        norm = df[df.year != year]
        df_subg = df_sub.groupby(["doy"]).agg({"EVI2": [q5, q25, q50, q75, q95]})
        norm_g = norm.groupby(["doy"]).agg({"EVI2": [q5, q25, q50, q75, q95]})
        norm_g["date"] = pd.to_datetime(2016 * 1000 + norm_g.index, format="%Y%j")
        df_subg["date"] = pd.to_datetime(2016 * 1000 + df_subg.index, format="%Y%j")
        artists = []
        artists += ax.plot(norm_g.date, norm_g[("EVI2", "q50")], ls="-", c="0.5")
        artists += [
            ax.fill_between(
                norm_g.date,
                norm_g[("EVI2", "q25")],
                norm_g[("EVI2", "q75")],
                color="0.5",
                alpha=0.2,
            )
        ]
        artists += ax.plot(
            df_subg.date, df_subg[("EVI2", "q50")], ls="-", c=color_dict[lc]
        )
        artists += [
            ax.fill_between(
                df_subg.date,
                df_subg[("EVI2", "q25")],
                df_subg[("EVI2", "q75")],
                color=color_dict[lc],
                alpha=0.2,
            )
        ]
        date_cols = ["Date_Mid_Greenup_Phase_1", "Date_Mid_Senescence_Phase_1"]
        ph_dates = pheg.loc[region, lc][date_cols][:, "q50"]
        ph_dates = pd.to_datetime(2016 * 1000 + ph_dates, format="%Y%j")
        ph_dates_min = pheg.loc[region, lc][date_cols][:, "q25"]
        ph_dates_min = pd.to_datetime(2016 * 1000 + ph_dates_min, format="%Y%j")
        ph_dates_m = pheg.loc[region, lc][date_cols][:, "q75"]
        ph_dates_m = pd.to_datetime(2016 * 1000 + ph_dates_m, format="%Y%j")
        for pair in zip(ph_dates_min, ph_dates_m):
            ax.axvspan(pair[0], pair[1], color="0.9", alpha=0.5, zorder=0)
        for line in ph_dates:
            ax.axvline(line, linestyle="--", color="0.5", zorder=1)
        event_fires = (
            fires[(fires.Region == region) & (fires.year == year)]
            .groupby("doy")["frp"]
            .count()
        )
        norm_fires = (
            fires[(fires.Region == region) & (fires.year != year)]
            .groupby("doy")["frp"]
            .count()
        )
        event_f_dates = pd.to_datetime(2016 * 1000 + event_fires.index, format="%Y%j")
        norm_f_dates = pd.to_datetime(2016 * 1000 + norm_fires.index, format="%Y%j")
        ax2 = ax.twinx()
        ax2.bar(norm_f_dates, norm_fires, color="0.5", width=1, alpha=0.8, zorder=4)
        ax2.bar(
            event_f_dates,
            event_fires,
            color=color_dict[21],
            width=1,
            alpha=0.8,
            zorder=5,
        )
        ax2.set_yticks([])
        months = MonthLocator([3, 6, 9, 12], bymonthday=1)  # , interval=3)
        ax.xaxis.set_major_formatter(
            FuncFormatter(lambda x, pos=None: "{dt:%b} {dt.day}".format(dt=num2date(x)))
        )
        ax.xaxis.set_major_locator(months)
        ax.grid(True, which="major", c="gray", ls="--", lw=1, alpha=0.2)
        ax.set_title(f"{event[0], ukceh_classes[event[1]], event[2]}")
        ax.set_ylim(0.2, 0.75)
        if (nr == 0) | (nr == 2):
            ax.set_ylabel("EVI2")
        ax.tick_params(
            axis="both",
            which="major",
            labelsize="medium",
        )
    """
    plt.savefig(
        Path(config["data_dir"], "results/figures", "drought_events.png"),
        dpi=300,
        bbox_inches="tight",
    )

    """
    plt.show()


def heatwave_sites_figure():
    sites = pd.read_csv("/Users/tadas/modFire/heatwave_vegetation_indices/heatwave.csv")
    sites["year"] = pd.to_datetime(sites.date).dt.year
    sites["NDVI"] *= 0.0001
    sites = sites[sites.pixel_reliability < 5]
    site_ids = pd.read_csv(
        "/Users/tadas/modFire/heatwave_vegetation_indices/heatwave_sites.csv"
    )
    fig, axs = plt.subplots(2, 3, figsize=(15, 7))
    for nr in site_ids.index:
        ax = axs.flatten()[nr]
        df = sites[sites.fid == nr]
        for year in df.year.unique():
            dfy = df[df.year == year]
            dfy = dfy.sort_values("composite_day_of_the_year")
            if year == 2022:
                ax.plot(dfy.composite_day_of_the_year, dfy.NDVI, c="r", zorder=1000)
                l_2022 = ax.scatter(
                    dfy.composite_day_of_the_year,
                    dfy.NDVI,
                    c="r",
                    zorder=1000,
                    label="2022",
                )
            elif year == 2018:
                ax.plot(
                    dfy.composite_day_of_the_year,
                    dfy.NDVI,
                    c="b",
                    zorder=1000,
                )
                l_2018 = ax.scatter(
                    dfy.composite_day_of_the_year,
                    dfy.NDVI,
                    c="b",
                    zorder=1000,
                    label="2018",
                )
            else:
                l_rest = ax.scatter(
                    dfy.composite_day_of_the_year,
                    dfy.NDVI,
                    c="0.5",
                    label="other years",
                )
        ax.set_title(
            site_ids.loc[nr, "site"]
            + " lon: "
            + str(site_ids.loc[nr, "longitude"].round(2))
            + " lat: "
            + str(site_ids.loc[nr, "Latitude"].round(2))
        )
        ax.legend(handles=[l_2018, l_2022])
        ax.set_ylim((0.4, 0.9))
        ax.set_xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335])
        ax.set_xticklabels(
            [
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
        )
        # leg = ax.legend(handles=legend_elements, loc="center", ncol=2, frameon=False)
        ax.set_ylabel("NDVI")

    for ax in axs.flat:
        ## check if something was plotted
        if not bool(ax.has_data()):
            fig.delaxes(ax)  ## delete if nothing is plotted in the axes obj

    plt.savefig(
        Path("/Users/tadas/modFire/heatwave_vegetation_indices/site_ndvi.png"),
        dpi=300,
        bbox_inches="tight",
    )


if __name__ == "__main__":
    pheg = pd.read_parquet(phenology_quantiles_file())
    phe = pd.read_parquet(phenology_file())
    eviq = pd.read_parquet(evi2_quantiles_file())
    fires = pd.read_parquet(fire_file_name())
    # land_cover_evi_upd(phe, fires)
    # drought_evi_vs_norm(pheg, fires)

    # region_evi(eviq, pheg, fires)
