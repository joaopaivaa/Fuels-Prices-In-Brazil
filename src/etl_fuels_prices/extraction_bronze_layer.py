import pandas as pd
from datetime import datetime
import os
from sqlalchemy import create_engine
from download_functions import download_LPG, download_Gasoline_Ethanol, download_Diesel_CNG

db_url = os.getenv("postgresql://gasoline_prices_brazil_db_user:XzY1BJlModxlNnutEWXJIaGZX0kRRmBJ@dpg-d7qkagegvqtc73asirv0-a.virginia-postgres.render.com/gasoline_prices_brazil_db")

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)

current_date = datetime.now().strftime('%d/%m/%Y')
end = pd.to_datetime(current_date, format='%d/%m/%Y')

# LPG Prices

df_lpg = pd.read_parquet('data/fuels_prices/bronze/LPG Prices.parquet', engine='pyarrow')

most_recent_date = df_lpg['Data da Coleta'].values[-1]

start = pd.to_datetime(most_recent_date, format='%d/%m/%Y')
new_months = pd.date_range(start, end, freq='MS').strftime('%m/%Y').tolist()

df_lpg_new = download_LPG(new_months)

df_lpg = pd.concat([df_lpg, df_lpg_new])
df_lpg.to_parquet('data/fuels_prices/bronze/LPG Prices.parquet', index=False, engine='pyarrow')

# Gasoline Ethanol Prices

df_gasoline_ethanol = pd.read_parquet('data/fuels_prices/bronze/Gasoline and Ethanol Prices.parquet', engine='pyarrow')

most_recent_date = df_gasoline_ethanol['Data da Coleta'].values[-1]

start = pd.to_datetime(most_recent_date, format='%d/%m/%Y')
new_months = pd.date_range(start, end, freq='MS').strftime('%m/%Y').tolist()

df_gasoline_ethanol_new = download_Gasoline_Ethanol(new_months)

df_gasoline_ethanol = pd.concat([df_gasoline_ethanol, df_gasoline_ethanol_new])
df_gasoline_ethanol.to_parquet('data/fuels_prices/bronze/Gasoline and Ethanol Prices.parquet', index=False, engine='pyarrow')

# Diesel and CNG Prices

df_diesel_cng = pd.read_parquet('data/fuels_prices/bronze/Diesel and CNG Prices.parquet', engine='pyarrow')

most_recent_date = df_diesel_cng['Data da Coleta'].values[-1]

start = pd.to_datetime(most_recent_date, format='%d/%m/%Y')
new_months = pd.date_range(start, end, freq='MS').strftime('%m/%Y').tolist()

df_diesel_cng_new = download_Diesel_CNG(new_months)

df_diesel_cng = pd.concat([df_diesel_cng, df_diesel_cng_new])
df_diesel_cng.to_parquet('data/fuels_prices/bronze/Diesel and CNG Prices.parquet', index=False, engine='pyarrow')