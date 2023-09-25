import tomli
import numpy as np
import pandas as pd
import seaborn as sn
import matplotlib.pyplot as plt
from pathlib import Path
from configuration import config, color_dict
from prepare_data import fire_file_name, fire_phenology_file_name


fire_p = pd.read_parquet(fire_phenology_file_name())
Fig, axs = plt.subplots(1, 2, figsize=(24, 10))
ax = axs[0]
sn.countplot(data=fire_p[(fire_p.lc.isin(config["land_covers"]))], x='lc', hue="season", ax=ax)
ax2 = axs[1]
sn.countplot(data=fire_p[(fire_p.lc.isin(config["land_covers"]))], x='year', hue="season_green", ax=ax2)
plt.show()
"""
fire_phen = pd.read_csv(Path(config["data_dir"], 'gee_results', 'masked_fire_mean_phen_all_events.csv'))
fire_phen['year'] = [int(x.split('_')[0]) for x in fire_phen['system:index'].astype(str)]
fire_phen = phenology_doy(fire_phen)
fire_phen = fire_phen.drop(['system:index', '.geo'], axis=1)
fire_evi = pd.read_csv(Path(config["data_dir"], 'gee_results', 'masked_fire_mean_evi2_all_events.csv'))
fire_evi['date'] = pd.to_datetime(['-'.join(x.split('_')[:3]) for x in fire_evi['system:index'].astype(str)])
fire_evi = fire_evi.drop(['system:index'], axis=1)
fire_evi['ewoy'] = fire_evi.date.dt.isocalendar().week
fire_evi['eyear'] = fire_evi.date.dt.year
"""
