import pandas as pd
from download_functions import download_LPG, download_Gasoline_Ethanol, download_Diesel_CNG

# LPG Prices

df_lpg = pd.read_parquet('bronze/LPG Prices.parquet', engine='pyarrow')

df_lpg_new = download_LPG(first_year_month = '2025-09', last_year_month = '2025-09')

df_lpg = pd.concat([df_lpg, df_lpg_new])
df_lpg.to_parquet('bronze/LPG Prices.parquet', index=False, engine='pyarrow')

# Gasoline Ethanol Prices

df_gasoline_ethanol = pd.read_parquet('bronze/Gasoline and Ethanol Prices.parquet', engine='pyarrow')

df_gasoline_ethanol_new = download_Gasoline_Ethanol(first_year_month = '2025-09', last_year_month = '2025-09')

df_gasoline_ethanol = pd.concat([df_gasoline_ethanol, df_gasoline_ethanol_new])
df_gasoline_ethanol.to_parquet('bronze/Gasoline and Ethanol Prices.parquet', index=False, engine='pyarrow')

# Diesel and CNG Prices

df_diesel_cng = pd.read_parquet('bronze/Diesel and CNG Prices.parquet', engine='pyarrow')

df_diesel_cng_new = download_Diesel_CNG(first_year_month = '2025-09', last_year_month = '2025-09')

df_diesel_cng = pd.concat([df_diesel_cng, df_diesel_cng_new])
df_diesel_cng.to_parquet('bronze/Diesel and CNG Prices.parquet', index=False, engine='pyarrow')