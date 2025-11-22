import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
from shapely.geometry import Point

fuel_types_colors = {
    "Etanol": "#A8D8A8",
    "Gasolina": "#FF5733",
    "Gasolina Aditivada": "#FF6F61",
    "Diesel": "#5F6366",
    "Diesel S10": "#8B9A9A",
    "CNG": "#00A1E4",
    "LPG": "#F4C542"
}

st.set_page_config(layout='wide')

df_fuels = pd.read_parquet('gold/fuels_prices')
gdf_cities = gpd.read_file("brazil_cities_shape_adjusted/brazil_cities.shp")

df_fuels_copy = df_fuels.copy()
gdf_cities_copy = gdf_cities.copy()

with st.sidebar:

    st.title('Preços de combustíveis no Brasil :fuelpump:')

    st.space("small")

    start_date = st.date_input("Data inicial", df_fuels_copy['dt_date_month_start'].min())
    end_date = st.date_input("Data final", df_fuels_copy['dt_date_month_start'].max())

    state_selected = st.multiselect(
        "Estado",
        sorted(df_fuels_copy['nm_state'].unique().tolist() + ['Todos']),
        max_selections=1
    )

    city_selected = st.multiselect(
        "Cidade",
        sorted(df_fuels_copy['nm_city'].unique().tolist() + ['Todas']),
        max_selections=1
    )

    fuel_types_selected = st.multiselect(
        "Tipos de combustível",
        sorted(df_fuels_copy['nm_fuel_type'].unique().tolist() + ['Todas']),
        default=['Gasolina']
    )

    fuel_brands_selected = st.multiselect(
        "Marcas de combustível",
        sorted(df_fuels_copy['nm_fuel_brand'].unique().tolist() + ['Todas'])
    )

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

df_fuels_copy['dt_date_month_start'] = pd.to_datetime(df_fuels_copy['dt_date_month_start'])

df_fuels_copy = df_fuels_copy[
    (df_fuels_copy['dt_date_month_start'] >= start_date) &
    (df_fuels_copy['dt_date_month_start'] <= end_date)
].reset_index(drop=True)

if len(state_selected) != 0:
    df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_state'].isin(state_selected)].reset_index(drop=True)
    gdf_cities_copy = gdf_cities_copy[gdf_cities_copy['nm_state'].isin(state_selected)].reset_index(drop=True)

if len(city_selected) != 0:
    df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_city'].isin(city_selected)].reset_index(drop=True)
    gdf_cities_copy = gdf_cities_copy[gdf_cities_copy['nm_city'].isin(city_selected)].reset_index(drop=True)

if len(fuel_brands_selected) != 0:
    df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_fuel_brand'].isin(fuel_brands_selected)].reset_index(drop=True)

if len(fuel_types_selected) != 0: 
    df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_fuel_type'].isin(fuel_types_selected)].reset_index(drop=True)

col1_sup, col2_sup = st.columns([2, 1], vertical_alignment="center", border=True)

with col1_sup:

    subcol1, subcol2 = st.columns([4, 1])

    with subcol2:
        map_selection = st.pills(
            "Nível de visualização",
            options=['Regional', 'Estadual', 'Municipal'],
            default='Estadual',
            selection_mode="single"
        )

    if map_selection == 'Municipal':



    df_fuels_by_city = df_fuels_copy.groupby(['key_uf_city_lower'], as_index=False).agg(avg_fuel_price=('avg_fuel_price', 'mean')).sort_values('key_uf_city_lower').reset_index(drop=True)

    gdf_cities_copy = gdf_cities_copy.sort_values('uf_city').reset_index(drop=True)
    gdf_cities_copy = gdf_cities_copy.merge(df_fuels_by_city, left_on= 'uf_city', right_on="key_uf_city_lower", how="left")

    print(gdf_cities_copy.head())

    min_price = gdf_cities_copy['avg_fuel_price'].min()
    max_price = gdf_cities_copy['avg_fuel_price'].max()

    brazil_cities_map_blank = px.choropleth(
        gdf_cities_copy,
        geojson=gdf_cities_copy.__geo_interface__,
        locations=gdf_cities_copy.index,
        color_discrete_sequence=["white"]
    )
    brazil_cities_map_blank.update_traces(
        marker_line_width=1, 
        marker_line_color="black"
    )

    gdf_cities_no_nan = gdf_cities_copy.dropna(subset=["avg_fuel_price"]).reset_index(drop=True)

    brazil_cities_map = px.choropleth(
        gdf_cities_no_nan,
        geojson=gdf_cities_no_nan.__geo_interface__,
        locations=gdf_cities_no_nan.index,
        color="avg_fuel_price",
        hover_data=["key_uf_city_lower", "avg_fuel_price"],
        color_continuous_scale='rdylgn_r',
        range_color=(min_price, max_price) 
    )

    brazil_cities_map_blank.add_trace(brazil_cities_map.data[0])

    brazil_cities_map_blank.update_layout(
        margin=dict(r=0,l=0,t=0,b=0),
        dragmode=False
    )
    brazil_cities_map_blank.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator"
    )
    brazil_cities_map_blank.update_traces(
        marker_line_width=1,
        marker_line_color="black"
    )

    with subcol1:
        st.plotly_chart(brazil_cities_map_blank, width='stretch')

df_fuel_prices_by_brand = (
    df_fuels_copy
    .groupby(['nm_fuel_brand', 'nm_fuel_type'], as_index=False)
    .agg(avg_fuel_price=('avg_fuel_price', 'mean'))
)

df_fuel_prices_by_brand["nm_brand_label"] = (
    df_fuel_prices_by_brand["nm_fuel_brand"] + " (" + df_fuel_prices_by_brand["nm_fuel_type"] + ")"
)

df_fuel_prices_by_brand_top5_highest = df_fuel_prices_by_brand.sort_values('avg_fuel_price', ascending=False).reset_index().head(5)

order_y_highest = df_fuel_prices_by_brand_top5_highest["nm_brand_label"].tolist()

fig_fuel_prices_by_brand_top5_highest = px.bar(
    df_fuel_prices_by_brand_top5_highest,
    x='avg_fuel_price',
    y='nm_brand_label',
    color='nm_fuel_type',
    color_discrete_map=fuel_types_colors,
    text_auto=True,
    title='5 marcas de combustível com maior preço médio',
    orientation='h',
    category_orders={"nm_brand_label": order_y_highest}
)
fig_fuel_prices_by_brand_top5_highest.update_xaxes(title_text=None)
fig_fuel_prices_by_brand_top5_highest.update_yaxes(title_text=None)
fig_fuel_prices_by_brand_top5_highest.update_layout(
    legend=dict(
        x=0,
        y=-0.1,
        orientation="h",
        xanchor='left'
    ),
    legend_title=None
)

df_fuel_prices_by_brand_top5_lowest = df_fuel_prices_by_brand.sort_values('avg_fuel_price', ascending=True).reset_index().head(5)

order_y_lowest = df_fuel_prices_by_brand_top5_lowest["nm_brand_label"].tolist()

fig_fuel_prices_by_brand_top5_lowest = px.bar(
    df_fuel_prices_by_brand_top5_lowest,
    x='avg_fuel_price',
    y='nm_brand_label',
    color='nm_fuel_type',
    color_discrete_map=fuel_types_colors,
    text_auto=True,
    title='5 marcas de combustível com menor preço médio',
    orientation='h',
    category_orders={"nm_brand_label": order_y_lowest},
    
)
fig_fuel_prices_by_brand_top5_lowest.update_xaxes(title_text=None)
fig_fuel_prices_by_brand_top5_lowest.update_yaxes(title_text=None)
fig_fuel_prices_by_brand_top5_lowest.update_layout(
    legend=dict(
        x=0,
        y=-0.1,
        orientation="h",
        xanchor='left'
    ),
    legend_title=None
)

with col2_sup:
    st.plotly_chart(fig_fuel_prices_by_brand_top5_highest, width='stretch')

col1_inf, col2_inf = st.columns([2, 1], vertical_alignment="center", border=True)

df_fuel_prices_overtime = df_fuels_copy.groupby(['dt_date_month_start', 'nm_fuel_type']).mean('avg_fuel_price').reset_index()
 
fig_fuel_prices_overtime = px.line(
    df_fuel_prices_overtime,
    x='dt_date_month_start',
    y='avg_fuel_price',
    color='nm_fuel_type',
    color_discrete_map=fuel_types_colors,
    markers=True,
    title='Evolução dos preços médios dos combustíveis ao longo do tempo'
)
fig_fuel_prices_overtime.update_xaxes(title_text=None)
fig_fuel_prices_overtime.update_yaxes(title_text=None)
fig_fuel_prices_overtime.update_layout(
    legend=dict(
        x=0,
        y=-0.1,
        orientation="h",
        xanchor='left'
    ),
    legend_title=None
)

with col1_inf:
    st.plotly_chart(fig_fuel_prices_overtime, width='stretch')

with col2_inf:
    st.plotly_chart(fig_fuel_prices_by_brand_top5_lowest, width='stretch')

















