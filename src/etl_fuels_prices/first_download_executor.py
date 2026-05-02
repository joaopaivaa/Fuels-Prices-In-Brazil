from datetime import datetime
import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from download_functions import download_LPG, download_Gasoline_Ethanol, download_Diesel_CNG

load_dotenv() 
db_url = os.getenv('database_url')

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)

current_date = datetime.now().strftime('%d/%m/%Y')
#end = pd.to_datetime(current_date, format='%d/%m/%Y')
end = pd.to_datetime('01/03/2022', format='%d/%m/%Y')

start = pd.to_datetime('01/01/2022', format='%d/%m/%Y')

new_months = pd.date_range(start, end, freq='MS').strftime('%m/%Y').tolist()

# LPG Prices

df_lpg = download_LPG(new_months)
#df_lpg.to_parquet('databases/fuel_prices/bronze/LPG Prices.parquet', index=False, engine='pyarrow')
df_lpg.to_sql('lpg_bronze', engine, if_exists='replace', index=False, schema='bronze')

# Gasoline Ethanol Prices

df_gasoline_ethanol = download_Gasoline_Ethanol(new_months)
#df_gasoline_ethanol.to_parquet('databases/fuel_prices/bronze/Gasoline and Ethanol Prices.parquet', index=False, engine='pyarrow')
df_gasoline_ethanol.to_sql('gasoline_ethanol_bronze', engine, if_exists='replace', index=False, schema='bronze')

# Diesel and CNG Prices

df_diesel_cng = download_Diesel_CNG(new_months)
#df_diesel_cng.to_parquet('databases/fuel_prices/bronze/Diesel and CNG Prices.parquet', index=False, engine='pyarrow')
df_diesel_cng.to_sql('diesel_cng_bronze', engine, if_exists='replace', index=False, schema='bronze')