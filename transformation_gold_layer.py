import findspark
findspark.init()

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *

import geopandas as  gpd
import pandas as pd

spark = (
    SparkSession.builder
    .appName("Fuel Prices in Brazil")
    .config("spark.driver.memory", "6g")
    .getOrCreate()
)

df = spark.read.parquet("silver/fuels_prices")

df = df.dropna(how='all')

df = df.withColumn('dt_date_month_start', to_date(concat_ws('-', col('dt_year'), col('dt_month'), lit('01'))))

df = (
    df
    .groupBy('nm_region', 'ab_state', 'nm_state', 'nm_city', 'nm_fuel_type', 'dt_date_month_start', 'nm_fuel_brand', 'key_uf_city_lower')
    .agg(
        mean('nu_fuel_price').alias('avg_fuel_price')
    )
)

df.write.mode("overwrite").format("parquet").save("gold/fuels_prices")