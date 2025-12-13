from download_functions import download_LPG, download_Gasoline_Ethanol, download_Diesel_CNG

# LPG Prices

df_lpg = download_LPG(1, 2022, 8, 2025)
df_lpg.to_parquet('bronze/LPG Prices.parquet', index=False, engine='pyarrow')

# Gasoline Ethanol Prices

df_gasoline_ethanol = download_Gasoline_Ethanol(1, 2022, 8, 2025)
df_gasoline_ethanol.to_parquet('bronze/Gasoline and Ethanol Prices.parquet', index=False, engine='pyarrow')

# Diesel and CNG Prices

df_diesel_cng = download_Diesel_CNG(1, 2022, 8, 2025)
df_diesel_cng.to_parquet('bronze/Diesel and CNG Prices.parquet', index=False, engine='pyarrow')