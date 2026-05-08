import time
start = time.perf_counter()

from dotenv import load_dotenv
import pandas as pd
import unicodedata
import numpy as np
import os
from sqlalchemy import create_engine

load_dotenv() 
db_url = os.getenv('database_url')

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)

def remove_accents(s):
    if not isinstance(s, str):
        return s
    s = unicodedata.normalize('NFD', s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("ç", "c").replace("Ç", "C")

df_diesel_cng = pd.read_sql("SELECT * FROM bronze.diesel_cng_bronze", engine)
# df_diesel_cng = pd.read_parquet("./data/fuels_prices/bronze/Diesel and CNG Prices.parquet")

# df_lpg = pd.read_sql("SELECT * FROM bronze.lpg_bronze", engine)
# df_lpg = pd.read_parquet("./data/fuels_prices/bronze/LPG Prices.parquet")

df_gasoline_ethanol = pd.read_sql("SELECT * FROM bronze.gasoline_ethanol_bronze", engine)
# df_gasoline_ethanol = pd.read_parquet("./data/fuels_prices/bronze/Gasoline and Ethanol Prices.parquet")

df = pd.concat([df_diesel_cng, df_gasoline_ethanol], ignore_index=True)

cols_to_drop = ['CNPJ da Revenda', 'Nome da Rua', 'Numero Rua', 'Complemento', 'Cep', 'Valor de Compra']
df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])

new_columns = {
    df.columns[0]: 'nm_region', df.columns[1]: 'nm_state', df.columns[2]: 'nm_city',
    df.columns[3]: 'nm_gas_station', df.columns[4]: 'nm_neighborhood', df.columns[5]: 'nm_fuel_type',
    df.columns[6]: 'dt_date', df.columns[7]: 'nu_fuel_price', df.columns[8]: 'nm_unit_of_measurement',
    df.columns[9]: 'nm_fuel_brand'
}
df = df.rename(columns=new_columns)

df['dt_date'] = pd.to_datetime(df['dt_date'], format='%d/%m/%Y')
df['dt_year'] = df['dt_date'].dt.year.astype(str).replace('\.0', '', regex=True)
df['dt_month'] = df['dt_date'].dt.month.astype(str).replace('\.0', '', regex=True)

df['dt_year'] = np.where(df['dt_year'] == 'nan', np.nan, df['dt_year'])
df['dt_month'] = np.where(df['dt_month'] == 'nan', np.nan, df['dt_month'])

string_cols = ['nm_city', 'nm_gas_station', 'nm_neighborhood', 'nm_fuel_type', 'nm_fuel_brand']
for col in string_cols:
    df[col] = df[col].str.title()

df['nu_fuel_price'] = df['nu_fuel_price'].astype(str).str.replace(',', '.')
df['nu_fuel_price'] = pd.to_numeric(df['nu_fuel_price'], errors='coerce')

regions_map = {'N': 'Norte', 'NE': 'Nordeste', 'CO': 'Centro-Oeste', 'SE': 'Sudeste', 'S': 'Sul'}
states_map = {
    'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas', 'BA': 'Bahia', 
    'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo', 'GO': 'Goiás', 
    'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais', 
    'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco', 'PI': 'Piauí', 
    'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte', 'RS': 'Rio Grande do Sul', 
    'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina', 'SP': 'São Paulo', 
    'SE': 'Sergipe', 'TO': 'Tocantins'
}

df['ab_state'] = df['nm_state']
df['nm_region'] = df['nm_region'].replace(regions_map)
df['nm_state'] = df['nm_state'].replace(states_map)

df['nm_fuel_type'] = df['nm_fuel_type'].replace({'Gnv': 'GNV', 'Glp': 'GLP'})

df['nm_unit_of_measurement'] = df['nm_unit_of_measurement'].str.replace('mÂ³', 'm³', regex=False)
repl_map = {'ã\x81': 'a'}
for col in ['nm_gas_station', 'nm_neighborhood', 'nm_fuel_brand']:
    df[col] = df[col].str.replace('ã\x81', 'a', regex=False)

df['uf_city'] = (
    df['ab_state'].str.lower() + 
    '_' + 
    df['nm_city'].str.lower().str.replace(' ', '_', regex=False)
)

df = df[df['nm_fuel_type'] != 'GLP']

# df.to_parquet("data/fuels_prices/silver/fuels_prices.parquet", index=False)
df.to_sql('fact_fuels_prices_silver', engine, if_exists='replace', index=False, schema='silver')

print('Transformation to Silver Layer completed successfully!')

end = time.perf_counter()
print(f"Execution time: {end - start:.4f} seconds")