import geopandas as gpd
import pandas as pd
import unicodedata

def remove_accents(text):
    if isinstance(text, str):
        return ''.join(
            c for c in unicodedata.normalize('NFKD', text)
            if not unicodedata.combining(c)
        )
    return text

brazil_cities_shp = gpd.read_file("brazil_shape\\BR_Municipios_2024.shp")

brazil_cities_shp['NM_MUN_NO_ACCENT'] = brazil_cities_shp['NM_MUN'].apply(remove_accents)

brazil_cities_shp['key_uf_city_lower'] = (brazil_cities_shp['SIGLA_UF'] + "_" + brazil_cities_shp['NM_MUN_NO_ACCENT']).str.lower().str.replace(' ', '_')

brazil_cities_shp = brazil_cities_shp[['key_uf_city_lower', 'geometry']]

brazil_cities_shp["geometry"] = brazil_cities_shp["geometry"].simplify(tolerance=0.01, preserve_topology=True)

brazil_cities_shp.to_file("brazil_shape_adjusted\\brazil_cities.shp", driver="ESRI Shapefile")