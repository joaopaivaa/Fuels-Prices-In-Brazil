from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import os
from sqlalchemy import create_engine
from download_functions import download_LPG, download_Gasoline_Ethanol, download_Diesel_CNG

load_dotenv() 
db_url = os.getenv('database_url')
    
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)

# current_date = datetime.now().strftime('%d/%m/%Y')
# end = pd.to_datetime(current_date, format='%d/%m/%Y')
end = pd.to_datetime('2026-02-01', format='%Y-%m-%d')

# # LPG Prices

# # df_lpg = pd.read_parquet('data/fuels_prices/bronze/LPG Prices.parquet', engine='pyarrow')
# df_lpg = pd.read_sql("SELECT * FROM bronze.lpg_bronze", engine)

# most_recent_date = df_lpg['Data da Coleta'].values[-1]

# start = pd.to_datetime(most_recent_date, format='%d/%m/%Y')
# new_months = pd.date_range(start, end, freq='MS').strftime('%m/%Y').tolist()

# print('LPG')
# print(f"First date to download: {start}")
# print(f"Last date to download: {end}")
# print(f"Downloading new LPG data for months: {new_months} ...")
# print('\n')

# df_lpg_new = download_LPG(new_months)

# df_lpg = pd.concat([df_lpg, df_lpg_new])
# # df_lpg.to_parquet('data/fuels_prices/bronze/LPG Prices.parquet', index=False, engine='pyarrow')
# df_lpg.to_sql('lpg_bronze', engine, if_exists='replace', index=False, schema='bronze')

# Gasoline Ethanol Prices

# df_gasoline_ethanol = pd.read_parquet('data/fuels_prices/bronze/Gasoline and Ethanol Prices.parquet', engine='pyarrow')
df_gasoline_ethanol = pd.read_sql("SELECT * FROM bronze.gasoline_ethanol_bronze", engine)

most_recent_date = df_gasoline_ethanol['Data da Coleta'].values[-1]

start = pd.to_datetime(most_recent_date, format='%d/%m/%Y')
new_months = pd.date_range(start, end, freq='MS').strftime('%m/%Y').tolist()

print('Gasoline and Ethanol')
print(f"First date to download: {start}")
print(f"Last date to download: {end}")
print(f"Downloading new Gasoline and Ethanol data for months: {new_months} ...")
print('\n')

df_gasoline_ethanol_new = download_Gasoline_Ethanol(new_months)

df_gasoline_ethanol = pd.concat([df_gasoline_ethanol, df_gasoline_ethanol_new])
# df_gasoline_ethanol.to_parquet('data/fuels_prices/bronze/Gasoline and Ethanol Prices.parquet', index=False, engine='pyarrow')
df_gasoline_ethanol.to_sql('gasoline_ethanol_bronze', engine, if_exists='replace', index=False, schema='bronze')

# Diesel and CNG Prices

# df_diesel_cng = pd.read_parquet('data/fuels_prices/bronze/Diesel and CNG Prices.parquet', engine='pyarrow')
df_diesel_cng = pd.read_sql("SELECT * FROM bronze.diesel_cng_bronze", engine)

most_recent_date = df_diesel_cng['Data da Coleta'].values[-1]

start = pd.to_datetime(most_recent_date, format='%d/%m/%Y')
new_months = pd.date_range(start, end, freq='MS').strftime('%m/%Y').tolist()

print('Diesel and CNG')
print(f"First date to download: {start}")
print(f"Last date to download: {end}")
print(f"Downloading new Diesel and CNG data for months: {new_months} ...")
print('\n')

df_diesel_cng_new = download_Diesel_CNG(new_months)

df_diesel_cng = pd.concat([df_diesel_cng, df_diesel_cng_new])
# df_diesel_cng.to_parquet('data/fuels_prices/bronze/Diesel and CNG Prices.parquet', index=False, engine='pyarrow')
df_diesel_cng.to_sql('diesel_cng_bronze', engine, if_exists='replace', index=False, schema='bronze')