import pandas as pd
import spatial as sp
from pathlib import Path
from configuration import config


# 5th Percentile
def q5(x):
    return x.quantile(0.05)


# 25th Percentile
def q25(x):
    return x.quantile(0.25)


# 50th Percentile
def q50(x):
    return x.quantile(0.5)


# 75th Percentile
def q75(x):
    return x.quantile(0.75)


# 50th Percentile
def q95(x):
    return x.quantile(0.95)


def dem_file():
    file_name = Path(config["data_dir"], "results", "merit_dem.parquet")
    return file_name


def phenology_file():
    window = config["window_size"]
    file_name = Path(config["data_dir"], "results", f"phenology_{window}.parquet")
    return file_name


def phenology_quantiles_file():
    window = config["window_size"]
    file_name = Path(
        config["data_dir"], "results", f"phenology_quantiles_{window}.parquet"
    )
    return file_name


def evi2_quantiles_file():
    window = config["window_size"]
    file_name = Path(config["data_dir"], "results", f"evi2_quantiles_{window}.parquet")
    return file_name


def fire_file_name():
    file_name = Path(config["data_dir"], "results", "UK_fire.parquet")
    return file_name


def fire_phenology_file_name():
    file_name = Path(config["data_dir"], "results", "UK_fire_phenology_dates.parquet")
    return file_name

def phenology_doy(dfr):
    """Convert VNP22Q2 product date columns to standard dates"""
    date_cols = [
        x for x in dfr.columns if (x.startswith("Onset") or x.startswith("Date"))
    ]
    for column in date_cols:
        dfr[column] = dfr[column] - (366 * (dfr.year - 2000))
    return dfr


def combine_phenology():
    dfrs = []
    for lc in config["land_covers"]:
        for region in config["regions"]:
            file_name = Path(
                config["data_dir"], "gee_results", f"VNP22Q2_{region}_{lc}_sample.csv"
            )
            try:
                df = pd.read_csv(file_name)
            except FileNotFoundError:
                continue
            df["date"] = pd.to_datetime(df.date)
            df["year"] = df.date.dt.year
            df["Region"] = region
            df["lc"] = lc
            df = phenology_doy(df)
            dfrs.append(df)
    phe = pd.concat(dfrs)
    phe_file_name = phenology_file()
    phe.to_parquet(phe_file_name)
    return phe


def combine_dem():
    dfrs = []
    for lc in config["land_covers"]:
        for region in config["regions"]:
            file_name = Path(
                config["data_dir"], "gee_results", f"MERIT_DEM_{region}_{lc}_sample.csv"
            )
            try:
                df = pd.read_csv(file_name)
            except FileNotFoundError:
                continue
            df["Region"] = region
            df["lc"] = lc
            df = df.drop(["date"], axis=1)
            dfrs.append(df)
    dem = pd.concat(dfrs)
    dem_file_name = dem_file()
    dem.to_parquet(dem_file_name)
    return dem


def phenology_quantiles():
    phe_file_name = phenology_file()
    phe = pd.read_parquet(phe_file_name)
    pheg = phe.groupby(["Region", "lc"])
    pheg = pheg.agg(
        {
            "Onset_Greenness_Increase_1": [q5, q25, q50, q75, q95],
            "Onset_Greenness_Maximum_1": [q5, q25, q50, q75, q95],
            "Onset_Greenness_Decrease_1": [q5, q25, q50, q75, q95],
            "Onset_Greenness_Minimum_1": [q5, q25, q50, q75, q95],
            "Date_Mid_Greenup_Phase_1": [q5, q25, q50, q75, q95],
            "Date_Mid_Senescence_Phase_1": [q5, q25, q50, q75, q95],
            "EVI2_Growing_Season_Area_1": [q5, q25, q50, q75, q95],
            "Growing_Season_Length_1": [q5, q25, q50, q75, q95],
            "EVI2_Onset_Greenness_Increase_1": [q5, q25, q50, q75, q95],
            "EVI2_Onset_Greenness_Maximum_1": [q5, q25, q50, q75, q95],
        }
    )
    file_name = phenology_quantiles_file()
    pheg.to_parquet(file_name)
    return pheg


def evi_files_to_parquet():
    """Pre-proocess EVI2 csv files and write parquet"""
    for lc in config["land_covers"]:
        for region in config["regions"]:
            file_name = Path(
                config["data_dir"], "gee_results", f"VNP13A1_{region}_{lc}_sample.csv"
            )
            try:
                df = pd.read_csv(file_name)
            except FileNotFoundError:
                continue
            # Select good quality observations
            df = df[df["pixel_reliability"] < 5]
            df["date"] = pd.to_datetime(df.date)
            df["woy"] = df.date.dt.isocalendar().week
            df["doy"] = df.date.dt.dayofyear
            df["year"] = df.date.dt.year
            df["lc"] = lc
            df["Region"] = region
            out_file_name = Path(
                config["data_dir"],
                "gee_results",
                f"VNP13A1_{region}_{lc}_sample.parquet",
            )
            df.to_parquet(out_file_name)


def evi_quentiles_land_cover():
    for lc in config["land_covers"]:
        dfrs = []
        for region in config["regions"]:
            file_name = Path(
                config["data_dir"],
                "gee_results",
                f"VNP13A1_{region}_{lc}_sample.parquet",
            )
            try:
                df = pd.read_parquet(file_name)
                dfrs.append(df)
            except FileNotFoundError:
                continue
        dfr_land = pd.concat(dfrs)
        dfr_land["EVI2"] *= 0.0001
        dfrg = dfr_land.groupby(["doy"]).agg({"EVI2": [q5, q25, q50, q75, q95]})
        dfrg.columns = dfrg.columns.droplevel(level=0)
        dfrg["lc"] = lc
        dfrg = dfrg.reset_index()
        out_file_name = Path(
            config["data_dir"],
            "gee_results",
            f"VNP13A1_{lc}_quantiles.parquet",
        )
        dfrg.to_parquet(out_file_name)


def evi_quantiles():
    """Calculate EVI2 quantiles per lc and region"""
    results = []
    for lc in config["land_covers"]:
        dfrs = []
        for region in config["regions"]:
            file_name = Path(
                config["data_dir"], "gee_results", f"VNP13A1_{region}_{lc}_sample.csv"
            )
            try:
                df = pd.read_csv(file_name)
            except FileNotFoundError:
                continue
            # Select good quality observations
            df = df[df["pixel_reliability"] < 5]
            df["date"] = pd.to_datetime(df.date)
            df["woy"] = df.date.dt.isocalendar().week
            df["doy"] = df.date.dt.dayofyear
            df["year"] = df.date.dt.year
            df["lc"] = lc
            df["Region"] = region
            dfrs.append(df)
        dfr_evi = pd.concat(dfrs)
        dfrg = dfr_evi.groupby(["Region", "doy"]).agg(
            {"EVI2": [q5, q25, q50, q75, q95]}
        )
        dfrg.columns = dfrg.columns.droplevel(level=0)
        dfrg["lc"] = lc
        dfrg = dfrg.reset_index()
        results.append(dfrg)
    eviq = pd.concat(results)
    eviq_file_name = evi2_quantiles_file()
    eviq.to_parquet(eviq_file_name)
    return eviq


def UK_fire_dfr(file_path: str, regions_file_path: str):
    """Read and prepare UK fire detections"""
    fire = pd.read_parquet(file_path)
    fire["date"] = pd.to_datetime(fire["date"], unit="s")
    fire["year"] = fire.date.dt.year
    fire["month"] = fire.date.dt.month
    fire["doy"] = fire.date.dt.dayofyear
    fire["dow"] = fire.date.dt.dayofweek
    fire["woy"] = fire.date.dt.isocalendar().week
    fire["size"] = fire.groupby("event")["event"].transform("size")
    fire["id"] = fire.id.astype(int)
    fire = sp.get_UK_climate_region(fire, regions_file_path)
    file_name = fire_file_name()
    fire.to_parquet(file_name)
    return fire

def fire_event_phenology():
    """Determine fuel phenological season for VIIRS fire events"""
    fire = pd.read_parquet(fire_file_name())
    pheq = pd.read_parquet(phenology_quantiles_file())
    columns = [
        "Onset_Greenness_Increase_1",
        "Date_Mid_Greenup_Phase_1",
        "Onset_Greenness_Maximum_1",
        "Onset_Greenness_Decrease_1",
        "Date_Mid_Senescence_Phase_1",
        "Onset_Greenness_Minimum_1",
    ]
    pheq50 = pheq.loc[:, (slice(None), "q50")].droplevel(level=1, axis=1)
    res = pd.merge(fire, pheq50.reset_index()[columns + ["Region", "lc"]],
                   on=["Region", "lc"], how="left")
    res["season"] = None
    res.loc[
        (res.doy <= res["Onset_Greenness_Increase_1"])
        | (res.doy > res["Onset_Greenness_Minimum_1"]),
        "season",
    ] = "Dormant"
    res.loc[
        (res.doy > res["Onset_Greenness_Increase_1"])
        & (res.doy <= res["Date_Mid_Greenup_Phase_1"]),
        "season",
    ] = "Increase_early"
    res.loc[
        (res.doy > res["Date_Mid_Greenup_Phase_1"])
        & (res.doy <= res["Onset_Greenness_Maximum_1"]),
        "season",
    ] = "Increase_late"

    res.loc[
        (res.doy > res["Onset_Greenness_Maximum_1"])
        & (res.doy <= res["Onset_Greenness_Decrease_1"]),
        "season",
    ] = "Maximum"
    res.loc[
        (res.doy > res["Onset_Greenness_Decrease_1"])
        & (res.doy <= res["Date_Mid_Senescence_Phase_1"]),
        "season",
    ] = "Decrease_early"
    res.loc[
        (res.doy > res["Date_Mid_Senescence_Phase_1"])
        & (res.doy <= res["Onset_Greenness_Minimum_1"]),
        "season",
    ] = "Decrease_late"

    res["season_green"] = 0
    res.loc[
        (res.doy < res["Date_Mid_Senescence_Phase_1"])
        & (res.doy > res["Date_Mid_Greenup_Phase_1"]),
        "season_green",
    ] = 1
    file_name = fire_phenology_file_name()
    res.to_parquet(file_name)
    return res


def fire_pixel_phenology_season():
    """Determine fuel phenological season for VIIRS fire detections"""
    fire = pd.read_parquet(fire_file_name())
    fire_phen = pd.read_csv(Path(config["data_dir"], 'gee_results', 'masked_fire_mean_phen_all_events.csv'))
    columns = [
        "Onset_Greenness_Increase_1",
        "Date_Mid_Greenup_Phase_1",
        "Onset_Greenness_Maximum_1",
        "Onset_Greenness_Decrease_1",
        "Date_Mid_Senescence_Phase_1",
        "Onset_Greenness_Minimum_1",
    ]
    fire_phen['year'] = [int(x.split('_')[0]) for x in fire_phen['system:index'].astype(str)]
    fire_phen = phenology_doy(fire_phen)
    fire_phen = fire_phen.drop(['system:index', '.geo'], axis=1)
    res = pd.merge(fire, fire_phen.reset_index()[columns + ["Region", "lc"]],
                   on=["Region", "lc"], how="left")
    res["season"] = None
    res.loc[
        (res.doy <= res["Onset_Greenness_Increase_1"])
        | (res.doy > res["Onset_Greenness_Minimum_1"]),
        "season",
    ] = "Dormant"
    res.loc[
        (res.doy > res["Onset_Greenness_Increase_1"])
        & (res.doy <= res["Onset_Greenness_Maximum_1"]),
        "season",
    ] = "Increase"
    res.loc[
        (res.doy > res["Onset_Greenness_Maximum_1"])
        & (res.doy <= res["Onset_Greenness_Decrease_1"]),
        "season",
    ] = "Maximum"
    res.loc[
        (res.doy > res["Onset_Greenness_Decrease_1"])
        & (res.doy <= res["Onset_Greenness_Minimum_1"]),
        "season",
    ] = "Decraese"
    res["season_green"] = 0
    res.loc[
        (res.doy < res["Date_Mid_Senescence_Phase_1"])
        & (res.doy > res["Date_Mid_Greenup_Phase_1"]),
        "season_green",
    ] = 1
    file_name = fire_phenology_file_name()
    res.to_parquet(file_name)
    return res



if __name__ == "__main__":
    # eviq = evi_quantiles()
    # phe:= combine_phenology()
    # pheg = phenology_quantiles()
    fire = UK_fire_dfr(
        "/Users/tadas/modFire/fire_lc_ndvi/data/uk_viirs_fire_2023_07_16.parquet",
        config["regions_file"],
    )
    # dem = combine_dem()
    # evi_files_to_parquet()
    # evi_quentiles_land_cover()
    fire_event_phenology()

    """
    fire = pd.read_parquet(fire_file_name())
    pheq = pd.read_parquet(phenology_quantiles_file())
    # ph_dates = pheg.loc[lc][date_cols][:, "q50"]
    fire_g = (
        fire.groupby(["event"])[["doy", "year", "date", "size", "Region"]]
        .min()
        .reset_index()
    )
    fire_g["lc"] = (
        fire.groupby("event")[["lc"]].agg(lambda x: pd.Series.mode(x)[0]).values
    )
    fire_g["Region"] = (
        fire.groupby("event")[["Region"]].agg(lambda x: pd.Series.mode(x)[0]).values
    )
    columns = [
        "Onset_Greenness_Increase_1",
        "Date_Mid_Greenup_Phase_1",
        "Onset_Greenness_Maximum_1",
        "Onset_Greenness_Decrease_1",
        "Date_Mid_Senescence_Phase_1",
        "Onset_Greenness_Minimum_1",
    ]
    pheq50 = pheq.loc[:, (slice(None), "q50")].droplevel(level=1, axis=1)

    resg = pd.merge(fire_g, pheq50.reset_index(), on=["Region", "lc"], how="left")

    res = pd.merge(fire, pheq50.reset_index(), on=["Region", "lc"], how="left")

    res["season"] = 0
    res.loc[
        (res.doy <= res["Onset_Greenness_Increase_1"])
        | (res.doy > res["Onset_Greenness_Minimum_1"]),
        "season",
    ] = "Dormant"
    res.loc[
        (res.doy > res["Onset_Greenness_Increase_1"])
        & (res.doy <= res["Onset_Greenness_Maximum_1"]),
        "season",
    ] = "Increase"
    res.loc[
        (res.doy > res["Onset_Greenness_Maximum_1"])
        & (res.doy <= res["Onset_Greenness_Decrease_1"]),
        "season",
    ] = "Maximum"
    res.loc[
        (res.doy > res["Onset_Greenness_Decrease_1"])
        & (res.doy <= res["Onset_Greenness_Minimum_1"]),
        "season",
    ] = "Decraese"
    res["season_green"] = 0
    res.loc[
        (res.doy < res["Date_Mid_Senescence_Phase_1"])
        & (res.doy > res["Date_Mid_Greenup_Phase_1"]),
        "season_green",
    ] = 1

    dormant_events = resg[(resg.doy < resg["Onset_Greenness_Increase_1"])]
    spring_events = resg[(resg.doy >= resg["Onset_Greenness_Increase_1"])]
    summer_events = resg[(resg.doy > resg["Onset_Greenness_Maximum_1"])]
    autumn_events = resg[(resg.doy > resg["Onset_Greenness_Decrease_1"])]
    dormant_events_2 = resg[(resg.doy > resg["Onset_Greenness_Minimum_1"])]
    green_events = resg[
        (resg.doy < resg["Date_Mid_Senescence_Phase_1"])
        & (resg.doy > resg["Date_Mid_Greenup_Phase_1"])
    ]

    resg["season"] = 0
    resg.loc[resg.event.isin(dormant_events.event), "season"] = "Dormant"
    resg.loc[resg.event.isin(spring_events.event), "season"] = "Increase"
    resg.loc[resg.event.isin(summer_events.event), "season"] = "Maximum"
    resg.loc[resg.event.isin(autumn_events.event), "season"] = "Decrease"
    resg.loc[resg.event.isin(dormant_events_2.event), "season"] = "Dormant"

    resg["season_green"] = 0
    resg.loc[resg.event.isin(green_events.event), "season_green"] = 1
    resg = resg[resg.season != 0]

    dormant_events = resg[(resg.doy<=resg['Onset_Greenness_Increase_1'])|(resg.doy>resg['Onset_Greenness_Minimum_1'])]
    espring_events = resg[(resg.doy>resg['Onset_Greenness_Increase_1'])&(resg.doy<=resg['Date_Mid_Greenup_Phase_1'])]
    lspring_events = resg[(resg.doy>resg['Date_Mid_Greenup_Phase_1'])&(resg.doy<=resg['Onset_Greenness_Maximum_1'])]
    summer_events = resg[(resg.doy>resg['Onset_Greenness_Maximum_1'])&(resg.doy<=resg['Onset_Greenness_Decrease_1'])]
    autumn_events = resg[(resg.doy>resg['Onset_Greenness_Decrease_1'])&(resg.doy<=resg['Onset_Greenness_Minimum_1'])]
    """
