import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import FuncFormatter
from matplotlib.dates import MonthLocator, num2date
from configuration import config
from prepare_data import (
    q5,
    q25,
    q50,
    q75,
    q95,
    evi2_quantiles_file,
    phenology_quantiles_file,
    phenology_file,
    fire_file_name,
    dem_file
)


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


def land_cover_evi(pheg, fire):
    lcs = [9, 11, 7, 10, 3, 4, 1, 2]
    Fig, axs = plt.subplots(2, 4, figsize=(24, 10))
    for nr, ax in enumerate(axs.flatten()):
        lc = lcs[nr]
        file_name = Path(
            config["data_dir"],
            "gee_results",
            f"VNP13A1_{lc}_quantiles.parquet",
        )
        sub = pd.read_parquet(file_name)
        sub["date"] = pd.to_datetime(2016 * 1000 + sub["doy"], format="%Y%j")
        artists = []
        artists += ax.plot(sub.date, sub.q50, ls="-", c=color_dict[lc], zorder=5)
        artists += [
            ax.fill_between(
                sub.date, sub.q25, sub.q75, color=color_dict[lc], alpha=0.2, zorder=4,
            )
        ]
        artists += [
            ax.fill_between(
                sub.date, sub.q5, sub.q95, color=color_dict[lc], alpha=0.1, zorder=3,
            )
        ]
        phesub = phe[phe.lc == lc].copy()
        phesub['doy'] = phesub.date.dt.dayofyear
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
        ser = (
                fire[(fire.lc == lc)]
                .groupby("doy")["frp"]
                .count()
            )
        sns.ecdfplot(data=fire[fire.lc == lc], x='doy', c=color_dict[lc])
        f_dates = pd.to_datetime(2016 * 1000 + ser.index, format="%Y%j")
        ax2 = ax.twinx()
        ax2.bar(f_dates, ser, color=color_dict[21], width=1, alpha=0.8, zorder=0)
        ax2.set_ylim(0, 150)
        ax2.set_yticks([])
        ax.grid(True, which="major", c="gray", ls="-", lw=1, alpha=0.2)
        months = MonthLocator([3, 6, 9, 12], bymonthday=1)  # , interval=3)
        ax.xaxis.set_major_formatter(
            FuncFormatter(
                lambda x, pos=None: "{dt:%b} {dt.day}".format(dt=num2date(x))
            )
        )
        ax.xaxis.set_major_locator(months)
        ax.set_ylim(0.1, .8)
        ax.set_title(f"{ukceh_classes[lc]}")
    plt.savefig(
        Path(config["data_dir"], "results/figures", "land_cover_UK_evi_phen.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()



def region_evi(eviq, pheg, fire):
    lcs = [9, 11, 7, 10, 3, 4, 1, 2]
    eviq["date"] = pd.to_datetime(2016 * 1000 + eviq["doy"], format="%Y%j")
    Fig, axs = plt.subplots(len(config["regions"]), len(lcs), figsize=(45, 35))
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
            sizes = (
                fire[(fire.Region == region) & (fire.lc == lc)]
                .groupby("doy")["size"]
                .max()
            )
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
        df = df[df.elevation < 200]
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
        artists += ax.plot(df_subg.date, df_subg[("EVI2", "q50")], ls="-", c=color_dict[lc])
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
            ax.set_ylabel('EVI2')
        ax.tick_params(
            axis="both",
            which="major",
            labelsize="medium",
        )
    plt.savefig(
        Path(config["data_dir"], "results/figures", "drought_events.png"),
        dpi=300,
        bbox_inches="tight",
    )
    plt.show()


if __name__ == "__main__":
    pheg = pd.read_parquet(phenology_quantiles_file())
    phe = pd.read_parquet(phenology_file())
    eviq = pd.read_parquet(evi2_quantiles_file())
    fires = pd.read_parquet(fire_file_name())

    # land_cover_evi(phe, fires)
    # drought_evi_vs_norm(pheg, fires)
    # region_evi(eviq, pheg, fires)
