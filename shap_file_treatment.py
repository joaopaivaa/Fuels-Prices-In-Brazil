import geopandas as gpd
import pandas as pd

brazil_cities_shp = gpd.read_file("brazil_shape\\BR_Municipios_2024.shp")

brazil_cities_shp['key_uf_city_lower'] = (brazil_cities_shp['SIGLA_UF'] + "_" + brazil_cities_shp['NM_MUN']).str.lower().str.replace(' ', '_')

brazil_cities_shp = brazil_cities_shp[['key_uf_city_lower', 'geometry']]

brazil_cities_shp.to_file("brazil_shape_adjusted\\brazil_cities.shp", driver="ESRI Shapefile")