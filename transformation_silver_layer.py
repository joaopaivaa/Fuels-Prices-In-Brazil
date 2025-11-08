from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("Fuel Prices in Brazil") \
    .getOrCreate()

df_diesel_cng = spark.read.parquet("bronze/Diesel and CNG Prices.parquet")
df_lpg = spark.read.parquet("bronze/LPG Prices.parquet")
df_gasoline_ethanol = spark.read.parquet("bronze/Gasoline and Ethanol Prices.parquet")

df = df_diesel_cng.unionByName(df_lpg, allowMissingColumns=True).unionByName(df_gasoline_ethanol, allowMissingColumns=True)

df = df.drop('CNPJ da Revenda', 'Nome da Rua', 'Numero Rua', 'Complemento', 'Cep', 'Valor de Compra')

df = df.toDF('nm_region', 'nm_state', 'nm_city', 'nm_gas_station', 'nm_neighborhood', 'nm_fuel_type', 'dt_date', 'nu_fuel_price', 'nm_unit_of_measurement', 'nm_fuel_brand')

df = (
    df
    .withColumn('dt_date', to_date(col('dt_date'), 'dd/MM/yyyy'))
    .withColumn('dt_year', year(col('dt_date')))
    .withColumn('dt_month', month(col('dt_date')))
)

df = (
    df
    .withColumn('nm_city', initcap(col('nm_city')))
    .withColumn('nm_gas_station', initcap(col('nm_gas_station')))
    .withColumn('nm_neighborhood', initcap(col('nm_neighborhood')))
    .withColumn('nm_fuel_type', initcap(col('nm_fuel_type')))
    .withColumn('nm_fuel_brand', initcap(col('nm_fuel_brand')))
)

df = (
    df
    .withColumn('nu_fuel_price', regexp_replace(col('nu_fuel_price'), ',', '.'))
    .withColumn('nu_fuel_price', col('nu_fuel_price').cast('float'))
)

df = (
    df
    .withColumn('nm_region', when(col('nm_region') == 'N', 'North')
                            .when(col('nm_region') == 'NE', 'Northeast')
                            .when(col('nm_region') == 'CO', 'Central-West')
                            .when(col('nm_region') == 'SE', 'Southeast')
                            .when(col('nm_region') == 'S', 'South')
                            .otherwise(col('nm_region')))
    .withColumn('nm_region', when(col('nm_state') == 'AC', 'Acre')
                            .when(col('nm_state') == 'AL', 'Alagoas')
                            .when(col('nm_state') == 'AP', 'Amapá')
                            .when(col('nm_state') == 'AM', 'Amazonas')
                            .when(col('nm_state') == 'BA', 'Bahia')
                            .when(col('nm_state') == 'CE', 'Ceará')
                            .when(col('nm_state') == 'DF', 'Distrito Federal')
                            .when(col('nm_state') == 'ES', 'Espírito Santo')
                            .when(col('nm_state') == 'GO', 'Goiás')
                            .when(col('nm_state') == 'MA', 'Maranhão')
                            .when(col('nm_state') == 'MT', 'Mato Grosso')
                            .when(col('nm_state') == 'MS', 'Mato Grosso do Sul')
                            .when(col('nm_state') == 'MG', 'Minas Gerais')
                            .when(col('nm_state') == 'PA', 'Pará')
                            .when(col('nm_state') == 'PB', 'Paraíba')
                            .when(col('nm_state') == 'PR', 'Paraná')
                            .when(col('nm_state') == 'PE', 'Pernambuco')
                            .when(col('nm_state') == 'PI', 'Piauí')
                            .when(col('nm_state') == 'RJ', 'Rio de Janeiro')
                            .when(col('nm_state') == 'RN', 'Rio Grande do Norte')
                            .when(col('nm_state') == 'RS', 'Rio Grande do Sul')
                            .when(col('nm_state') == 'RO', 'Rondônia')
                            .when(col('nm_state') == 'RR', 'Roraima')
                            .when(col('nm_state') == 'SC', 'Santa Catarina')
                            .when(col('nm_state') == 'SP', 'São Paulo')
                            .when(col('nm_state') == 'SE', 'Sergipe')
                            .when(col('nm_state') == 'TO', 'Tocantins')
                            .otherwise(col('nm_state')))
)

df = (
    df
    .withColumn('nm_unit_of_measurement', regexp_replace(col('nm_unit_of_measurement'), 'mÂ³', 'm³'))
    .withColumn('nm_gas_station', regexp_replace(col('nm_gas_station'), 'ã', 'a'))
    .withColumn('nm_neighborhood', regexp_replace(col('nm_neighborhood'), 'ã', 'a'))
    .withColumn('nm_fuel_brand', regexp_replace(col('nm_fuel_brand'), 'ã', 'a'))
)

df.to_parquet('silver/fuels_prices.parquet', index=False, engine='pyarrow')