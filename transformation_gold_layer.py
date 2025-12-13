import datetime
import findspark
import pandas as pd
findspark.init()

import sys
print(sys.version)

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *

import requests

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
    .groupBy('nm_region', 'ab_state', 'nm_state', 'nm_city', 'nm_fuel_type', 'dt_date_month_start', 'nm_fuel_brand', 'uf_city')
    .agg(
        mean('nu_fuel_price').alias('avg_fuel_price')
    )
    .orderBy('dt_date_month_start', 'ab_state', 'nm_state', 'nm_city', 'nm_fuel_type')
)

most_recent_date = df.select('dt_date_month_start').distinct().orderBy(col('dt_date_month_start').desc()).first()['dt_date_month_start'].strftime('%Y-%m-%d')

# list_of_dates = df.select('dt_date_month_start').rdd.flatMap(lambda x: x).collect()
# list_of_values = df.select('avg_fuel_price').rdd.flatMap(lambda x: x).collect()
list_of_dates = [row.dt_date_month_start for row in df.select('dt_date_month_start').collect()]
list_of_values = [row.avg_fuel_price for row in df.select('avg_fuel_price').collect()]

dates_as_strings = [
    d.isoformat() if isinstance(d, (datetime.date, datetime.datetime)) else d 
    for d in list_of_dates
]

payload = {
    'dates': dates_as_strings,
    'values': list_of_values,
    'currency': 'BRL',
    'present_date': most_recent_date
}

headers = {
    "Content-Type": "application/json"
}

values_inflation_adjusted = requests.post('https://financial-utilities-api.onrender.com/inflation_adjustment', json=payload, headers=headers)

if values_inflation_adjusted.status_code != 200:
    values_inflation_adjusted = requests.post('https://financial-utilities-api.onrender.com/inflation_adjustment', json=payload, headers=headers)

df_inflation_adjusted_values = spark.createDataFrame(pd.DataFrame(values_inflation_adjusted.json()))

df_inflation_adjusted_values = df_inflation_adjusted_values.toDF('date', 'original_value', 'inflation_adjusted_value', 'inflation_perc')

df = (
    df
    .join(
        df_inflation_adjusted_values.select(
            'date',
            'original_value',
            'inflation_adjusted_value'
        ),
        (df.dt_date_month_start == df_inflation_adjusted_values.date) &
        (df.avg_fuel_price == df_inflation_adjusted_values.original_value),
        how='left'
    )
)

df.write.mode("overwrite").format("parquet").save("gold/fuels_prices")