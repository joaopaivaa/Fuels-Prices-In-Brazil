import unicodedata
import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *

spark = (
    SparkSession.builder
    .appName("Fuel Prices in Brazil")
    .getOrCreate()
)

def remove_accents(s):
    if s is None:
        return None
    s = unicodedata.normalize('NFD', s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("ç", "c").replace("Ç", "C")

remove_accents_udf = udf(remove_accents, StringType())

df_diesel_cng = spark.read.parquet("databases/fuel_prices/bronze/Diesel and CNG Prices.parquet")
df_lpg = spark.read.parquet("databases/fuel_prices/bronze/LPG Prices.parquet")
df_gasoline_ethanol = spark.read.parquet("databases/fuel_prices/bronze/Gasoline and Ethanol Prices.parquet")

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
    .withColumn('ab_state', col('nm_state'))
    .withColumn('nm_region', when(col('nm_region') == 'N', 'Norte')
                            .when(col('nm_region') == 'NE', 'Nordeste')
                            .when(col('nm_region') == 'CO', 'Centro-Oeste')
                            .when(col('nm_region') == 'SE', 'Sudeste')
                            .when(col('nm_region') == 'S', 'Sul')
                            .otherwise(col('nm_region')))
    .withColumn('nm_state', when(col('nm_state') == 'AC', 'Acre')
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
    .withColumn('nm_fuel_type', when(col('nm_fuel_type') == 'Gnv', 'GNV')
                               .when(col('nm_fuel_type') == 'Glp', 'GLP')
                               .otherwise(col('nm_fuel_type')))
)

df = (
    df
    .withColumn('nm_unit_of_measurement', regexp_replace(col('nm_unit_of_measurement'), 'mÂ³', 'm³'))
    .withColumn('nm_gas_station', regexp_replace(col('nm_gas_station'), 'ã', 'a'))
    .withColumn('nm_neighborhood', regexp_replace(col('nm_neighborhood'), 'ã', 'a'))
    .withColumn('nm_fuel_brand', regexp_replace(col('nm_fuel_brand'), 'ã', 'a'))
)

df = (
    df
    .withColumn('uf_city', concat(lower(col('ab_state')), lit('_'), regexp_replace(lower(col('nm_city')), ' ', '_')))
)

df = (
    df.filter(col('nm_fuel_type') != 'GLP')
)

df.write.mode("overwrite").format("parquet").save("databases/fuel_prices/silver/fuels_prices")