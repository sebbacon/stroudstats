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
from datetime import date
from dateutil.relativedelta import relativedelta

def scrape_data(start_date, end_date):
    df = pd.DataFrame()
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    for date in dates:
        url = 'https://www.police.uk/gloucestershire/CA1/crime/{}/data/'.format(date.strftime("%Y-%m"))
        mdf = pd.read_json(url)
        mdf['date'] = date
        df = df.append(mdf)
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    return df

# Get data from file, or scrape if not present
try:
    df = pd.DataFrame().from_csv('all_crime.csv')
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
except FileNotFoundError:
    start_date = date(2015, 8, 1)
    today = date.today()
    end_date = date(today.year, today.month - 2, 1)
    df = scrape_data(start_date, end_date)
    df.to_csv('all_crime.csv')

# Add any new data
last_scraped_month = df.sort_values('date').iloc[-1].date.date()
# Stats are published 2 months following collection
two_months_ago = date.today() - relativedelta(months=2)
last_publication_month = date(two_months_ago.year, two_months_ago.month, 1)
if last_publication_month > last_scraped_month:
    new_data = scrape_data(last_scraped_month + relativedelta(months=1), last_publication_month)
df = df.append(new_data)

# + {"scrolled": false}
import matplotlib.pyplot as plt
# %matplotlib inline

# Count incidents by month and category
grouped = df.groupby(['category', 'date']).agg('count').reset_index(level=0).pivot_table(
    index='date', columns='category', values='location')

# Restrict to categories with more data
top_categories = ["Anti-social behaviour", "Burglary", "Criminal damage and arson", 
                  "Other theft", "Public order", "Shoplifting", "Vehicle crime", "Violence and sexual offences"]

non_person_crimes = ["Drugs", "Vehicle crime", "Robbery", "Shoplifting", "Other theft", "Burglary", "Criminal damage and arson", "Bicycle theft"]
person_crimes = [x for x in grouped.columns if x not in non_person_crimes]
# Normalise to maximum as baseline
df2 = pd.DataFrame()
for col in grouped.columns:
    df2[col] = grouped[col]/grouped[col].max()

# Plot them
from matplotlib.pyplot import figure
figure(num=None, figsize=(18, 16), dpi=80, facecolor='w', edgecolor='k')

plt.rcParams["figure.figsize"] = (20,10)
grouped.rolling(3).sum().plot.area(legend='reverse')
plt.suptitle("All crime, smoothed by quarter")

ax = df2.rolling(12).sum().plot(legend='reverse')
plt.suptitle("All crimes, normalised to same scale, smoothed to 12 months")


ax = df2[non_person_crimes].rolling(12).sum().plot.area(legend='reverse')
plt.suptitle("Crimes not against the person, smoothed to 12 months")


ax = df2[person_crimes].rolling(12).sum().plot.area(legend='reverse')
plt.suptitle("Crimes against the person, smoothed to 12 months")
# -



grouped.tail(10)
