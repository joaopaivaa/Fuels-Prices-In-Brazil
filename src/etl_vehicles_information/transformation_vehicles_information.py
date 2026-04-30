import pandas as pd

df_vehicles = pd.read_csv('databases/cars_efficiency/inmetro_2025.csv', sep=',', encoding="latin1")

df_vehicles.columns = ['nm_category', 'nm_brand', 'nm_model', 'nm_version', 'cd_fuel', 'ethanol_city_efficiency',
                       'ethanol_road_efficiency', 'gasoline_city_efficiency', 'gasoline_road_efficiency',
                       'electric_city_efficiency', 'electric_road_efficiency']

df_vehicles = df_vehicles[df_vehicles['cd_fuel'] == 'F'].reset_index(drop=True)

df_vehicles['nm_category'] = df_vehicles['nm_category'].str.title()
df_vehicles['nm_brand'] = df_vehicles['nm_brand'].str.title()
df_vehicles['nm_model'] = df_vehicles['nm_model'].str.title()
df_vehicles['nm_version'] = df_vehicles['nm_version'].str.title()

df_vehicles = df_vehicles.drop(['electric_city_efficiency', 'electric_road_efficiency', 'cd_fuel'], axis=1)

df_vehicles.to_csv('databases/cars_efficiency/dim_vehicles_efficiency.csv')