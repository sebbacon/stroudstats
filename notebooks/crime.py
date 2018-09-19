# ---
# jupyter:
#   jupytext_format_version: '1.2'
#   kernelspec:
#     display_name: Python (stroudcrime)
#     language: python
#     name: stroudcrim
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.6.5
# ---

import pandas as pd

# Get data from file, or scrape if not present
df = pd.DataFrame()
try:
    df = df.from_csv('all_crime.csv')
except FileNotFoundError:
    from datetime import date
    start_date = date(2015, 8, 1)
    today = date.today()
    end_date = date(today.year, today.month - 2, 1)
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    for date in dates:
        url = 'https://www.police.uk/gloucestershire/CA1/crime/{}/data/'.format(date.strftime("%Y-%m"))
        mdf = pd.read_json(url)
        mdf['date'] = date
        df = df.append(mdf)
    # Save it
    df.to_csv('all_crime.csv')

df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# +
import matplotlib.pyplot as plt
# %matplotlib inline

# Count incidents by month and category
grouped = df.groupby(['category', 'date']).agg('count').reset_index(level=0).pivot_table(
    index='date', columns='category', values='location')

# Restrict to categories with more data
top_categories = ["Anti-social behaviour", "Burglary", "Criminal damage and arson", 
                  "Other theft", "Public order", "Shoplifting", "Vehicle crime", "Violence and sexual offences"]

# Normalise to maximum as baseline
df2 = pd.DataFrame()
for col in grouped.columns:
    df2[col] = grouped[col]/grouped[col].max()

# Plot them
from matplotlib.pyplot import figure
figure(num=None, figsize=(18, 16), dpi=80, facecolor='w', edgecolor='k')

plt.rcParams["figure.figsize"] = (20,10)
grouped.rolling(3).mean().plot.area(legend='reverse')
plt.suptitle("All crime")

ax = df2[top_categories].rolling(3).mean().plot(legend='reverse')
plt.suptitle("Most common crimes, normalised to same scale")

# -



df2.head()
