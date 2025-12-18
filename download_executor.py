import pandas as pd
from download_functions import download_LPG, download_Gasoline_Ethanol, download_Diesel_CNG

def adjust_dates(most_recent_date):

    most_recent_month = most_recent_date.split('/')[1]
    most_recent_year = most_recent_date.split('/')[2]

    new_month = int(most_recent_month) + 1
    new_year = most_recent_year
    if new_month < 10:
        new_month = '0' + str(new_month)
    elif new_month > 12:
        new_month = '01'
        new_year = int(most_recent_year) + 1

    return most_recent_month, most_recent_year, new_month, new_year

# LPG Prices

df_lpg = pd.read_parquet('databases/fuel_prices/bronze/LPG Prices.parquet', engine='pyarrow')

most_recent_date = df_lpg['Data da Coleta'].values[-1]
most_recent_month, most_recent_year, new_month, new_year = adjust_dates(most_recent_date)

df_lpg_new = download_LPG(most_recent_month, most_recent_year, new_month, new_year)

df_lpg = pd.concat([df_lpg, df_lpg_new])
df_lpg.to_parquet('databases/fuel_prices/bronze/LPG Prices.parquet', index=False, engine='pyarrow')

# Gasoline Ethanol Prices

df_gasoline_ethanol = pd.read_parquet('databases/fuel_prices/bronze/Gasoline and Ethanol Prices.parquet', engine='pyarrow')
most_recent_date = df_gasoline_ethanol['Data da Coleta'].values[-1]
most_recent_month, most_recent_year, new_month, new_year = adjust_dates(most_recent_date)

df_gasoline_ethanol_new = download_Gasoline_Ethanol(most_recent_month, most_recent_year, new_month, new_year)

df_gasoline_ethanol = pd.concat([df_gasoline_ethanol, df_gasoline_ethanol_new])
df_gasoline_ethanol.to_parquet('databases/fuel_prices/bronze/Gasoline and Ethanol Prices.parquet', index=False, engine='pyarrow')

# Diesel and CNG Prices

df_diesel_cng = pd.read_parquet('databases/fuel_prices/bronze/Diesel and CNG Prices.parquet', engine='pyarrow')
most_recent_date = df_diesel_cng['Data da Coleta'].values[-1]
most_recent_month, most_recent_year, new_month, new_year = adjust_dates(most_recent_date)

df_diesel_cng_new = download_Diesel_CNG(most_recent_month, most_recent_year, new_month, new_year)

df_diesel_cng = pd.concat([df_diesel_cng, df_diesel_cng_new])
df_diesel_cng.to_parquet('databases/fuel_prices/bronze/Diesel and CNG Prices.parquet', index=False, engine='pyarrow')