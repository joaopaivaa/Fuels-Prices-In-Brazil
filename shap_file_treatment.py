import geopandas as gpd
import unicodedata

def remove_accents(text):
    if isinstance(text, str):
        return ''.join(
            c for c in unicodedata.normalize('NFKD', text)
            if not unicodedata.combining(c)
        )
    return text

brazil_cities_shp = gpd.read_file("databases/brazil_map/brazil_cities_shape/BR_Municipios_2024.shp")

brazil_cities_shp['NM_MUN_NO_ACCENT'] = brazil_cities_shp['NM_MUN'].apply(remove_accents)

brazil_cities_shp = brazil_cities_shp[['NM_REGIA', 'NM_UF', 'NM_MUN_NO_ACCENT', 'geometry']]
brazil_cities_shp.columns = ['nm_region', 'nm_state', 'nm_city', 'geometry']

brazil_cities_shp['nm_region'] = brazil_cities_shp['nm_region'].str.title()

brazil_cities_shp["geometry"] = brazil_cities_shp["geometry"].simplify(tolerance=0.01, preserve_topology=True)

brazil_cities_shp.to_file("databases/brazil_map/brazil_cities_shape_adjusted/brazil_cities.shp", driver="ESRI Shapefile")



brazil_states_shp = gpd.read_file("databases/brazil_map/brazil_states_shape/BR_UF_2024.shp")
brazil_states_shp = brazil_states_shp[['NM_REGIA', 'NM_UF', 'geometry']]
brazil_states_shp.columns = ['nm_region', 'nm_state', 'geometry']

brazil_states_shp['nm_region'] = brazil_states_shp['nm_region'].str.title()

brazil_states_shp["geometry"] = brazil_states_shp["geometry"].simplify(tolerance=0.01, preserve_topology=True)

brazil_states_shp.to_file("databases/brazil_map/brazil_states_shape_adjusted/brazil_states.shp", driver="ESRI Shapefile")



brazil_regions_shp = gpd.read_file("databases/brazil_map/brazil_regions_shape/BR_Regioes_2024.shp")
brazil_regions_shp = brazil_regions_shp[['NM_REGIA', 'geometry']]
brazil_regions_shp.columns = ['nm_region', 'geometry']

brazil_regions_shp['nm_region'] = brazil_regions_shp['nm_region'].str.title()
    
brazil_regions_shp["geometry"] = brazil_regions_shp["geometry"].simplify(tolerance=0.01, preserve_topology=True)

brazil_regions_shp.to_file("databases/brazil_map/brazil_regions_shape_adjusted/brazil_regions.shp", driver="ESRI Shapefile")