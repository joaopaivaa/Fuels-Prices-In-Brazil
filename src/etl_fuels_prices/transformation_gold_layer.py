import time
start = time.perf_counter()

import pandas as pd
import requests
import time

df = pd.read_parquet("data/fuels_prices/silver/fuels_prices.parquet")

df = df.dropna(how='all')

df['dt_date_month_start'] = pd.to_datetime(
    df['dt_year'].astype(str) + '-' + df['dt_month'].astype(str) + '-01'
)

df = df.groupby(
    ['nm_region', 'nm_state', 'nm_city', 'nm_fuel_type', 'dt_date_month_start', 'nm_fuel_brand', 'uf_city'],
    as_index=False
)['nu_fuel_price'].mean()

df = df.rename(columns={'nu_fuel_price': 'avg_fuel_price'})
df['avg_fuel_price'] = df['avg_fuel_price'].round(2)

df = df.sort_values(['dt_date_month_start', 'nm_state', 'nm_city', 'nm_fuel_type'])

most_recent_date = df['dt_date_month_start'].max().strftime('%Y-%m-%d')

df['dt_date_month_start'] = df['dt_date_month_start'].astype(str)

# Inflation Adjustment
df_monthly_ipca = pd.read_csv('data/inflation_adjustment/bronze/monthly_inflation_index.csv')
df_monthly_ipca = df_monthly_ipca[['Date', 'CPI Value']]

present_value_cpi = df_monthly_ipca[df_monthly_ipca['Date'] == most_recent_date]['CPI Value'].values[0]

df = df.merge(df_monthly_ipca, left_on='dt_date_month_start', right_on='Date', how='left')

df['inflation_adjustment_factor'] = present_value_cpi / df['CPI Value']

df['inflation_adjusted_avg_fuel_price'] = round(df['avg_fuel_price'] * df['inflation_adjustment_factor'], 2)

df.drop(columns=['Date', 'CPI Value', 'inflation_adjustment_factor'], inplace=True)

df.to_parquet("data/fuels_prices/gold/fuels_prices.parquet", index=False)

df_dates_memory = df['dt_date_month_start'].sort_values()
df_dates_memory.to_csv("data/dates_memory.csv", index=False)

print('Transformation to Gold Layer completed successfully!')

end = time.perf_counter()
print(f"Execution time: {end - start:.4f} seconds")