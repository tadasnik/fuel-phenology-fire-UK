import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import theilslopes

dfr = pd.read_csv(
    "/Users/tadas/modFire/fire_lc_ndvi/data/cehlc/gee_results/VNP13A1_South-west_7_sample.csv"
)
dfr = dfr[dfr.pixel_reliability < 5]
dfr["year"] = pd.to_datetime(dfr.date).dt.year
dfr["month"] = pd.to_datetime(dfr.date).dt.month
dfr["doy"] = pd.to_datetime(dfr.date).dt.dayofyear
dfr["obs_date"] = pd.to_datetime(
    dfr["year"] * 1000 + dfr["composite_day_of_the_year"], format="%Y%j"
)

# the bellow is slow
"""
dfr["slope"] = 0
dates = dfr.date.unique()
slopes = []
for nr, date in enumerate(dates[1:-2], 1):
    print(nr, date)
    dfrs = dfr[dfr.date.isin([dates[nr - 1], date])]
    result = theilslopes(dfrs.NDVI, dfrs.obs_date)
    slopes.append(result.slope)
    dfr.loc[dfr.date == date, "slope"] = result.slope
"""
