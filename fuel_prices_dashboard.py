import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import locale

locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

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
gdf_states = gpd.read_file("brazil_states_shape_adjusted/brazil_states.shp")
gdf_regions = gpd.read_file("brazil_regions_shape_adjusted/brazil_regions.shp")

df_fuels_copy = df_fuels.copy()

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

if len(state_selected) != 0:
    df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_state'].isin(state_selected)].reset_index(drop=True)

if len(city_selected) != 0:
    df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_city'].isin(city_selected)].reset_index(drop=True)

most_recent_month = df_fuels_copy['dt_date_month_start'].max()
st.subheader(f"Preço médio de {most_recent_month.strftime('%B').title()} de {most_recent_month.year}")

col1_header_line1, col2_header_line1, col3_header_line1, col4_header_line1 = st.columns(4, vertical_alignment="center", border=True)
col1_header_line2, col2_header_line2, col3_header_line2, col4_header_line2 = st.columns(4, vertical_alignment="center", border=True)

header_cols = [col1_header_line1, col2_header_line1, col3_header_line1, col4_header_line1,
               col1_header_line2, col2_header_line2, col3_header_line2]

average_price_fuel_type = (
    df_fuels_copy
    .groupby(['dt_date_month_start', 'nm_fuel_type'])
    .agg(avg_fuel_price=('avg_fuel_price', 'mean'))
    .sort_values('dt_date_month_start', ascending=False)
    .reset_index()
)

most_recent_average_price_fuel_type = average_price_fuel_type.iloc[0:7].reset_index(drop=True)
last_month_average_price_fuel_type = average_price_fuel_type.iloc[7:14].reset_index(drop=True)

for i in range(len(header_cols)):

    col = header_cols[i]
    fuel_type = most_recent_average_price_fuel_type.iloc[i]['nm_fuel_type']

    with col:
    
        most_recent_price = most_recent_average_price_fuel_type[most_recent_average_price_fuel_type['nm_fuel_type'] == fuel_type]['avg_fuel_price'].values[0]
        last_month_price = last_month_average_price_fuel_type[last_month_average_price_fuel_type['nm_fuel_type'] == fuel_type]['avg_fuel_price'].values[0]

        monthly_change = (most_recent_price - last_month_price) / last_month_price * 100 if last_month_price != 0 else 0

        st.metric(
            fuel_type,
            f"R$ {most_recent_price:.2f}",
            delta=f"{monthly_change:.2f}%",
            delta_color="inverse"
        )

with col4_header_line2:

    inflation_adustment = st.toggle(
        "Deflacionar preços",
        value=False
    )  

if inflation_adustment:
    print('')

if len(fuel_brands_selected) != 0:
    df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_fuel_brand'].isin(fuel_brands_selected)].reset_index(drop=True)

if len(fuel_types_selected) != 0: 
    df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_fuel_type'].isin(fuel_types_selected)].reset_index(drop=True)

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

df_fuels_copy['dt_date_month_start'] = pd.to_datetime(df_fuels_copy['dt_date_month_start'])

df_fuels_copy = df_fuels_copy[
    (df_fuels_copy['dt_date_month_start'] >= start_date) &
    (df_fuels_copy['dt_date_month_start'] <= end_date)
].reset_index(drop=True)

col1_sup, col2_sup = st.columns([2, 1], vertical_alignment="center", border=True)

with col1_sup:

    subcol1, subcol2 = st.columns([5, 1], vertical_alignment="center", border=False)

    with subcol2:
        map_selection = st.radio(
            "Nível territorial",
            options=['Regional', 'Estadual', 'Municipal'],
            index=2
        )

    if map_selection == 'Municipal':
        territory_key = 'uf_city'
        gdf_territory = gdf_cities.copy()
    elif map_selection == 'Estadual':
        territory_key = 'nm_state'
        gdf_territory = gdf_states.copy()
    else:
        territory_key = 'nm_region'
        gdf_territory = gdf_regions.copy()

    if len(state_selected) != 0:
        gdf_territory= gdf_territory[gdf_territory['nm_state'].isin(state_selected)].reset_index(drop=True)

    if len(city_selected) != 0:
        gdf_territory = gdf_territory[gdf_territory['nm_city'].isin(city_selected)].reset_index(drop=True)

    df_fuels_by_territory = df_fuels_copy.groupby([territory_key], as_index=False).agg(avg_fuel_price=('avg_fuel_price', 'mean')).sort_values(territory_key).reset_index(drop=True)

    gdf_territory = gdf_territory.sort_values(territory_key).reset_index(drop=True)
    gdf_territory = gdf_territory.merge(df_fuels_by_territory, left_on= territory_key, right_on=territory_key, how="left")

    min_price = gdf_territory['avg_fuel_price'].min()
    max_price = gdf_territory['avg_fuel_price'].max()

    brazil_territory_map_blank = px.choropleth(
        gdf_territory,
        geojson=gdf_territory.__geo_interface__,
        locations=gdf_territory.index,
        color_discrete_sequence=["#EEEEEE"]
    )
    brazil_territory_map_blank.update_traces(
        marker_line_width=1, 
        marker_line_color="black"
    )

    gdf_territory_no_nan = gdf_territory.dropna(subset=["avg_fuel_price"]).reset_index(drop=True)

    brazil_territory_map = px.choropleth(
        gdf_territory_no_nan,
        geojson=gdf_territory_no_nan.__geo_interface__,
        locations=gdf_territory_no_nan.index,
        color="avg_fuel_price",
        hover_data=[territory_key, "avg_fuel_price"],
        range_color=(min_price, max_price) 
    )

    brazil_territory_map_blank.add_trace(brazil_territory_map.data[0])

    brazil_territory_map_blank.update_layout(
        margin=dict(r=0,l=0,t=0,b=0),
        paper_bgcolor='#0e1117',
        plot_bgcolor='#0e1117',
        coloraxis_colorscale='RdYlGn_r',
        dragmode=False,
        coloraxis=dict(
            showscale=False
        )
    )
    brazil_territory_map_blank.update_geos(
        fitbounds="locations",
        visible=False,
        projection_type="mercator",
        bgcolor='#0e1117'
    )
    brazil_territory_map_blank.update_traces(
        marker_line_width=0.5,
        marker_line_color="black"
    )

    with subcol1:
        st.plotly_chart(brazil_territory_map_blank, width='stretch')

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
    title='5 marcas com maior preço médio',
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
    title='5 marcas com menor preço médio',
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
    title='Evolução dos preço médio ao longo do tempo'
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

















