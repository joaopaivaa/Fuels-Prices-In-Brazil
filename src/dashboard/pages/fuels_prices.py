from sqlalchemy import create_engine
import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import numpy as np
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv() 
db_url = os.getenv('database_url')

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)

df_fuels = pd.read_sql("SELECT * FROM gold.fact_fuels_prices_gold", engine)

fuel_types_colors = {
    "Etanol": "#A8D8A8",
    "Gasolina": "#FF5733",
    "Gasolina Aditivada": "#FF6F61",
    "Diesel": "#5F6366",
    "Diesel S10": "#8B9A9A",
    "CNG": "#00A1E4",
    "LPG": "#F4C542"
}

def clean_filters(available_dates):
    st.session_state.start_date = available_dates[0]
    st.session_state.end_date = available_dates[-1]
    st.session_state.regions_selected = []
    st.session_state.states_selected = []
    st.session_state.cities_selected = []
    st.session_state.fuel_types_selected = ['Gasolina']
    st.session_state.fuel_brands_selected = []
    st.session_state.inflation_adjustment = False

st.set_page_config(layout='wide')

st.title('Preços de combustíveis no Brasil :fuelpump:')

# df_fuels = pd.read_parquet('data/fuels_prices/gold/fuels_prices.parquet')

df_fuels["nm_state"] = df_fuels["nm_state"].astype("category")
df_fuels["nm_city"] = df_fuels["nm_city"].astype("category")
df_fuels["nm_fuel_type"] = df_fuels["nm_fuel_type"].astype("category")

df_fuels["avg_fuel_price"] = df_fuels["avg_fuel_price"].astype("float32")

df_vehicles = pd.read_csv('data/vehicles_efficiency/dim_vehicles_efficiency.csv', encoding="utf-8")

gdf_cities = gpd.read_file("data/shape_files/brazil_cities_shape_adjusted/brazil_cities.shp")
gdf_states = gpd.read_file("data/shape_files/brazil_states_shape_adjusted/brazil_states.shp")
gdf_regions = gpd.read_file("data/shape_files/brazil_regions_shape_adjusted/brazil_regions.shp")

df_fuels_copy = df_fuels.copy()
df_vehicles_copy = df_vehicles.copy()

most_recent_month = df_fuels_copy['dt_date_month_start'].max()
second_most_recent_month = df_fuels_copy['dt_date_month_start'].sort_values(ascending=False).unique()[1]

if "inflation_adjustment" not in st.session_state:
        st.session_state.inflation_adjustment = False

inflation_adjustment = st.session_state.inflation_adjustment

if st.session_state.inflation_adjustment:
    avg_fuel_price_col = 'inflation_adjusted_avg_fuel_price'
else:
    avg_fuel_price_col = 'avg_fuel_price'

# Sidebar

with st.sidebar:

    st.title('Filtros')

    st.space('small')

    available_dates = pd.period_range(df_fuels['dt_date_month_start'].min(), df_fuels['dt_date_month_start'].max(), freq="M").to_timestamp().to_list()

    if "start_date" not in st.session_state:
        st.session_state.start_date = available_dates[0]

    if "end_date" not in st.session_state:
        st.session_state.end_date = available_dates[-1]

    start_date = st.select_slider(
        "Data inicial",
        options=[d for d in available_dates if d <= st.session_state.end_date],
        format_func=lambda d: d.strftime("%m/%Y"),
        key="start_date"
    )

    end_date = st.select_slider(
        "Data final",
        options=[d for d in available_dates if d >= st.session_state.start_date],
        format_func=lambda d: d.strftime("%m/%Y"),
        key="end_date"
    )

    region_selected = st.multiselect(
        "Região",
        sorted(df_fuels_copy['nm_region'].unique().tolist()),
        max_selections=1,
        placeholder="Selecione uma região",
        key='regions_selected'
    )

    if len(region_selected) != 0:
        df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_region'].isin(region_selected)].reset_index(drop=True)

    state_selected = st.multiselect(
        "Estado",
        sorted(df_fuels_copy['nm_state'].unique().tolist()),
        max_selections=1,
        placeholder="Selecione um estado",
        key='states_selected'
    )

    if len(state_selected) != 0:
        df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_state'].isin(state_selected)].reset_index(drop=True)

    city_selected = st.multiselect(
        "Cidade",
        sorted(df_fuels_copy['nm_city'].unique().tolist()),
        max_selections=1,
        placeholder="Selecione uma cidade",
        key='cities_selected'
    )

    if len(city_selected) != 0:
        df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_city'].isin(city_selected)].reset_index(drop=True)

    fuel_types_selected = st.multiselect(
        "Tipos de combustível",
        sorted(df_fuels_copy['nm_fuel_type'].unique().tolist()),
        default=['Gasolina'],
        placeholder="Selecione um combustível",
        key='fuel_types_selected'
    )

    fuel_brands_selected = st.multiselect(
        "Marcas de combustível",
        sorted(df_fuels_copy['nm_fuel_brand'].unique().tolist()),
        placeholder="Selecione uma marca",
        key='fuel_brands_selected'
    )

    st.space('small')

    st.button(
        "Limpar filtros",
        on_click=clean_filters,
        args=(available_dates,)
    )

    st.space('small')

    today_date = date.today().strftime('%d/%m/%Y')
    st.text(f"Atualizado em: {today_date}")

    st.text(f"Competência mais recente: {pd.to_datetime(most_recent_month).strftime('%m/%Y')}")

tab_fuels_comparison, tab_gasoline_or_ethanol = st.tabs(['Comparativo de combustíveis', 'Gasolina ou etanol?'])

with tab_fuels_comparison:

    title_col1, title_col2 = st.columns([2, 1], vertical_alignment="center", border=False)

    with title_col1:

        months_in_portuguese = {
            1: "Janeiro",
            2: "Fevereiro",
            3: "Março",
            4: "Abril",
            5: "Maio",
            6: "Junho",
            7: "Julho",
            8: "Agosto",
            9: "Setembro",
            10: "Outubro",
            11: "Novembro",
            12: "Dezembro"
        }

        month_number = pd.to_datetime(most_recent_month).month
        month_name = months_in_portuguese.get(month_number)

        month_year = pd.to_datetime(most_recent_month).year

        st.subheader(f"Preço médio em {month_name} de {month_year}")

    with title_col2:

        st.toggle("Deflacionar preços", key="inflation_adjustment")

    header_box1, header_box2 = st.columns([2, 1], vertical_alignment="center", border=False)

    average_price_fuel_type = (
        df_fuels_copy
        .groupby(['dt_date_month_start', 'nm_fuel_type'])[avg_fuel_price_col]
        .mean()
        .reset_index()
    )

    most_recent_average_price_fuel_type = average_price_fuel_type[average_price_fuel_type['dt_date_month_start'] == most_recent_month].reset_index(drop=True)
    last_month_average_price_fuel_type = average_price_fuel_type[average_price_fuel_type['dt_date_month_start'] == second_most_recent_month].reset_index(drop=True)

    unavailable_fuel_type = sorted(list(set(df_fuels['nm_fuel_type'].unique()) - set(most_recent_average_price_fuel_type['nm_fuel_type'].unique())))
    unavailable_fuel_type_index = 0

    # Last month change and most recent price for each fuel type

    with header_box1:

        col1_header_line1, col2_header_line1, col3_header_line1, col4_header_line1 = st.columns(4, vertical_alignment="center", border=True)
        header_box1_cols = [col1_header_line1, col2_header_line1, col3_header_line1, col4_header_line1]

        for i in range(len(header_box1_cols)):

            col = header_box1_cols[i]
            fuel_type = most_recent_average_price_fuel_type.sort_values('nm_fuel_type').reset_index(drop=True).iloc[i]['nm_fuel_type']

            with col:
            
                most_recent_price = most_recent_average_price_fuel_type[most_recent_average_price_fuel_type['nm_fuel_type'] == fuel_type][avg_fuel_price_col].values[0]
                last_month_price = last_month_average_price_fuel_type[last_month_average_price_fuel_type['nm_fuel_type'] == fuel_type][avg_fuel_price_col].values[0]

                monthly_change = (most_recent_price - last_month_price) / last_month_price * 100 if last_month_price != 0 else 0

                st.metric(
                    fuel_type,
                    f"R$ {most_recent_price:.2f}",
                    delta=f"{monthly_change:.2f}%",
                    delta_color="inverse"
                )

    with header_box2:

        col5_header_line1, col6_header_line1 = st.columns(2, vertical_alignment="center", border=True)
        header_box2_cols = [col5_header_line1, col6_header_line1]

        for i in range(len(header_box2_cols)):

            col = header_box2_cols[i]

            if i+4 > len(most_recent_average_price_fuel_type)-1:

                fuel_type = unavailable_fuel_type[unavailable_fuel_type_index - 1]

                with col: 
                    st.metric(
                        fuel_type,
                        f"R$ -",
                        delta=f"-",
                        delta_color="off"
                    )

                unavailable_fuel_type_index += 1

            else:

                fuel_type = most_recent_average_price_fuel_type.sort_values('nm_fuel_type').reset_index(drop=True).iloc[i+4]['nm_fuel_type']

                with col:
                
                    most_recent_price = most_recent_average_price_fuel_type[most_recent_average_price_fuel_type['nm_fuel_type'] == fuel_type][avg_fuel_price_col].values[0]
                    last_month_price = last_month_average_price_fuel_type[last_month_average_price_fuel_type['nm_fuel_type'] == fuel_type][avg_fuel_price_col].values[0]

                    monthly_change = (most_recent_price - last_month_price) / last_month_price * 100 if last_month_price != 0 else 0

                    st.metric(
                        fuel_type,
                        f"R$ {most_recent_price:.2f}",
                        delta=f"{monthly_change:.2f}%",
                        delta_color="inverse"
                    )

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    start_date_month_name = months_in_portuguese.get(start_date.month)
    start_date_month_year = start_date.year

    end_date_month_name = months_in_portuguese.get(end_date.month)
    end_date_month_year = end_date.year

    df_fuels_copy['dt_date_month_start'] = pd.to_datetime(df_fuels_copy['dt_date_month_start'])

    df_fuels_copy = df_fuels_copy[
        (df_fuels_copy['dt_date_month_start'] >= start_date) &
        (df_fuels_copy['dt_date_month_start'] <= end_date)
    ].reset_index(drop=True)

    df_fuels_copy_vehicles = df_fuels_copy.copy()

    if len(fuel_brands_selected) != 0:
        df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_fuel_brand'].isin(fuel_brands_selected)].reset_index(drop=True)

    if len(fuel_types_selected) != 0: 
        df_fuels_copy = df_fuels_copy[df_fuels_copy['nm_fuel_type'].isin(fuel_types_selected)].reset_index(drop=True)

    df_fuel_prices_overtime = df_fuels_copy
    df_fuels_copy = df_fuels_copy[df_fuels_copy['dt_date_month_start'] == end_date].reset_index(drop=True)

    col1_sup, col2_sup = st.columns([2, 1], vertical_alignment="center", border=True)

    # Map of average fuel price by territory

    with col1_sup:

        subcol1, subcol2 = st.columns([5, 1], vertical_alignment="center", border=False)

        with subcol2:
            map_selection = st.radio(
                "Nível territorial",
                options=['Regional', 'Estadual', 'Municipal'],
                index=1
            )

        if map_selection == 'Municipal':
            territory_key = 'nm_city'
            territory_level = "município"
            gdf_territory = gdf_cities.copy()
        elif map_selection == 'Estadual':
            territory_key = 'nm_state'
            territory_level = "estado"
            gdf_territory = gdf_states.copy()
        else:
            territory_key = 'nm_region'
            territory_level = "região"
            gdf_territory = gdf_regions.copy()

        if (len(region_selected) != 0) and ('nm_region' in gdf_territory.columns):
            gdf_territory = gdf_territory[gdf_territory['nm_region'].isin(region_selected)].reset_index(drop=True)

        if (len(state_selected) != 0) and ('nm_state' in gdf_territory.columns):
            gdf_territory = gdf_territory[gdf_territory['nm_state'].isin(state_selected)].reset_index(drop=True)

        if (len(city_selected) != 0) and ('nm_city' in gdf_territory.columns):
            gdf_territory = gdf_territory[gdf_territory['nm_city'].isin(city_selected)].reset_index(drop=True)

        df_fuels_by_territory = df_fuels_copy.groupby([territory_key], as_index=False)[avg_fuel_price_col].mean().sort_values(territory_key).reset_index(drop=True)

        gdf_territory = gdf_territory.sort_values(territory_key).reset_index(drop=True)
        gdf_territory = gdf_territory.merge(df_fuels_by_territory, left_on= territory_key, right_on=territory_key, how="left")

        min_price = gdf_territory[avg_fuel_price_col].min()
        max_price = gdf_territory[avg_fuel_price_col].max()

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

        gdf_territory_no_nan = gdf_territory.dropna(subset=[avg_fuel_price_col]).reset_index(drop=True)
        gdf_territory_no_nan['id'] = gdf_territory_no_nan.index

        brazil_territory_map = px.choropleth(
            gdf_territory_no_nan,
            geojson=gdf_territory_no_nan.__geo_interface__,
            locations='id',
            color=avg_fuel_price_col,
            hover_data={
                'id': False,
                territory_key: True,
                avg_fuel_price_col: ':.2f'
            },
            range_color=(min_price, max_price),
            labels={
                "nm_region": "Região",
                "nm_state": "Estado",
                "nm_city": "Município",
                avg_fuel_price_col: "Preço Médio (R$)"
            }
        )

        brazil_territory_map_blank.add_trace(brazil_territory_map.data[0])

        brazil_territory_map_blank.update_layout(
            title={
                'text': f'Preço médio por {territory_level} - {end_date_month_name} de {end_date_month_year}',
                'y': 0.975,
                'x': 0,
                'xanchor': 'left',
                'yanchor': 'top',
                'font': {'color': 'white'}
            },
            margin=dict(r=0,l=0,t=0,b=0),
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            coloraxis_colorscale='RdYlGn_r',
            dragmode=False,
            coloraxis=dict(
                showscale=False
            ),
            showlegend=False
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
            st.plotly_chart(brazil_territory_map_blank, width='stretch', config={'displayModeBar': False})

    df_fuel_prices_by_brand = (
        df_fuels_copy
        .groupby(['nm_fuel_brand', 'nm_fuel_type'], as_index=False)[avg_fuel_price_col]
        .mean()
        .dropna(subset=[avg_fuel_price_col])
    )

    if len(fuel_types_selected) != 1:

        df_fuel_prices_by_brand["nm_brand_label"] = (
            df_fuel_prices_by_brand["nm_fuel_brand"] + " (" + df_fuel_prices_by_brand["nm_fuel_type"] + ")"
        )

    else:
        df_fuel_prices_by_brand["nm_brand_label"] = df_fuel_prices_by_brand["nm_fuel_brand"]

    df_fuel_prices_by_brand_top5_highest = df_fuel_prices_by_brand.sort_values(avg_fuel_price_col, ascending=False).reset_index().head(5)

    order_y_highest = df_fuel_prices_by_brand_top5_highest["nm_brand_label"].tolist()

    fig_fuel_prices_by_brand_top5_highest = px.bar(
        df_fuel_prices_by_brand_top5_highest,
        x=avg_fuel_price_col,
        y='nm_brand_label',
        color='nm_fuel_type',
        color_discrete_map=fuel_types_colors,
        text_auto='.2f',
        title=f'5 marcas com maior preço médio<br>{end_date_month_name} de {end_date_month_year}',
        orientation='h',
        category_orders={"nm_brand_label": order_y_highest},
        hover_data={
            'nm_fuel_type': True,
            'nm_brand_label': True,
            avg_fuel_price_col: ':.2f'
        },
        labels={
            "nm_fuel_type": "Combustível",
            "nm_brand_label": "Marca",
            avg_fuel_price_col: "Preço Médio (R$)"
        }
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
    fig_fuel_prices_by_brand_top5_highest.update_traces(
        textfont_weight='bold'
    )

    df_fuel_prices_by_brand_top5_lowest = df_fuel_prices_by_brand.sort_values(avg_fuel_price_col, ascending=True).reset_index().head(5)

    order_y_lowest = df_fuel_prices_by_brand_top5_lowest["nm_brand_label"].tolist()

    fig_fuel_prices_by_brand_top5_lowest = px.bar(
        df_fuel_prices_by_brand_top5_lowest,
        x=avg_fuel_price_col,
        y='nm_brand_label',
        color='nm_fuel_type',
        color_discrete_map=fuel_types_colors,
        text_auto='.2f',
        title=f'5 marcas com menor preço médio<br>{end_date_month_name} de {end_date_month_year}',
        orientation='h',
        category_orders={"nm_brand_label": order_y_lowest},
        hover_data={
            'nm_fuel_type': True,
            'nm_brand_label': True,
            avg_fuel_price_col: ':.2f'
        },
        labels={
            "nm_fuel_type": "Combustível",
            "nm_brand_label": "Marca",
            avg_fuel_price_col: "Preço Médio (R$)"
        }
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
    fig_fuel_prices_by_brand_top5_lowest.update_traces(
        textfont_weight='bold'
    )

    with col2_sup:
        st.plotly_chart(fig_fuel_prices_by_brand_top5_highest, width='stretch', config={'displayModeBar': False})

    col1_inf, col2_inf = st.columns([2, 1], vertical_alignment="center", border=True)

    df_fuel_prices_overtime = (
        df_fuel_prices_overtime
        .groupby(['dt_date_month_start', 'nm_fuel_type'])
        .mean(avg_fuel_price_col)
        .dropna(subset=[avg_fuel_price_col])
        .reset_index()
    )

    fig_fuel_prices_overtime = px.line(
        df_fuel_prices_overtime,
        x='dt_date_month_start',
        y=avg_fuel_price_col,
        color='nm_fuel_type',
        color_discrete_map=fuel_types_colors,
        markers=True,
        title=f'Evolução do preço médio<br>{start_date_month_name} de {start_date_month_year} - {end_date_month_name} de {end_date_month_year}',
        range_y=[0, df_fuel_prices_overtime[avg_fuel_price_col].max() * 1.1],
        hover_data={
            'dt_date_month_start': True,
            'nm_fuel_type': True,
            avg_fuel_price_col: ':.2f'
        },
        labels={
            "dt_date_month_start": "Data",
            "nm_fuel_type": "Combustível",
            avg_fuel_price_col: "Preço Médio (R$)"
        }
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
        st.plotly_chart(fig_fuel_prices_overtime, width='stretch', config={'displayModeBar': False})

    with col2_inf:
        st.plotly_chart(fig_fuel_prices_by_brand_top5_lowest, width='stretch', config={'displayModeBar': False})

    st.space('small')
    st.link_button("Desenvolvido por João Paiva", "https://joaopaivaa.github.io/")


# "Gasolina ou etanol" tab

with tab_gasoline_or_ethanol:

    col1, col2, col3 = st.columns(3, vertical_alignment="center", border=False)

    with col1:
        brand_selected = st.multiselect(
            "Marca",
            sorted(df_vehicles_copy['nm_brand'].unique().tolist()),
            max_selections=1,
            placeholder="Selecione uma marca"
        )
 
    if len(brand_selected) != 0:
        df_vehicles_copy = df_vehicles_copy[df_vehicles_copy['nm_brand'].isin(brand_selected)]

    with col2:
        model_selected = st.multiselect(
            "Modelo",
            sorted(df_vehicles_copy['nm_model'].unique().tolist()),
            max_selections=1,
            placeholder="Selecione um modelo"
        )

    if len(model_selected) != 0:
        df_vehicles_copy = df_vehicles_copy[df_vehicles_copy['nm_model'].isin(model_selected)]

    with col3:
        version_selected = st.multiselect(
            "Versão",
            sorted(df_vehicles_copy['nm_version'].unique().tolist()),
            max_selections=1,
            placeholder="Selecione uma versão"
        )

    if len(version_selected) != 0:
        df_vehicles_copy = df_vehicles_copy[df_vehicles_copy['nm_version'].isin(version_selected)]

    if df_vehicles_copy.empty:
        st.warning("Nenhum veículo encontrado com os filtros selecionados. Por favor, ajuste a seleção.")
        st.space('small')
        st.link_button("Desenvolvido por João Paiva", "https://joaopaivaa.github.io/")
        st.stop()

    if (len(brand_selected) == 0) or (len(model_selected) == 0) or (len(version_selected) == 0):
        st.warning("Selecione uma marca, modelo e versão de veículo para continuar.")
        st.space('small')
        st.link_button("Desenvolvido por João Paiva", "https://joaopaivaa.github.io/")
        st.stop()
    
    df_fuels_copy_vehicles = df_fuels_copy_vehicles[df_fuels_copy_vehicles['nm_fuel_type'].isin(['Etanol', 'Gasolina'])]
    df_fuels_copy_vehicles = df_fuels_copy_vehicles.groupby(['nm_region', 'nm_state', 'nm_city', 'nm_fuel_type', 'dt_date_month_start', 'uf_city']).mean(avg_fuel_price_col).reset_index()

    col_city, col_road = st.columns(2, vertical_alignment="center", border=True)

    with col_city:

        st.subheader('Cidade')

        st.space('small')

        ethanol_efficiency = df_vehicles_copy['ethanol_city_efficiency'].values[0]
        gasoline_efficiency = df_vehicles_copy['gasoline_city_efficiency'].values[0]

        df_fuels_copy_vehicles['nu_km_cost'] = np.where(df_fuels_copy_vehicles['nm_fuel_type'] == 'Gasolina',
                                                        df_fuels_copy_vehicles[avg_fuel_price_col] / gasoline_efficiency,
                                                        df_fuels_copy_vehicles[avg_fuel_price_col] / ethanol_efficiency)
        
        df_gasoline_ethanol_overtime = df_fuels_copy_vehicles.groupby(['dt_date_month_start', 'nm_fuel_type']).mean('nu_km_cost').reset_index()

        if start_date != end_date:

            fig_gasoline_ethanol_overtime = px.line(
                df_gasoline_ethanol_overtime,
                x='dt_date_month_start',
                y='nu_km_cost',
                color='nm_fuel_type',
                color_discrete_map=fuel_types_colors,
                markers=True,
                title='Evolução do preço médio por Km (R$) ao longo do tempo',
                range_y=[0, df_gasoline_ethanol_overtime['nu_km_cost'].max() * 1.1],
                hover_data={
                    'dt_date_month_start': True,
                    'nm_fuel_type': True,
                    "nu_km_cost": ':.2f'
                },
                labels={
                    "dt_date_month_start": "Data",
                    "nm_fuel_type": "Combustível",
                    "nu_km_cost": "Preço Médio por Km (R$)"
                }
            )
            fig_gasoline_ethanol_overtime.update_xaxes(title_text=None)
            fig_gasoline_ethanol_overtime.update_yaxes(title_text=None)
            fig_gasoline_ethanol_overtime.update_layout(
                legend=dict(
                    x=0,
                    y=-0.1,
                    orientation="h",
                    xanchor='left'
                ),
                legend_title=None
            )

            st.plotly_chart(fig_gasoline_ethanol_overtime, width='stretch', config={'displayModeBar': False})

        else:

            selected_date = df_gasoline_ethanol_overtime['dt_date_month_start'].values[0]
            selected_date = pd.to_datetime(selected_date)

            month_number = selected_date.month
            month_name = months_in_portuguese.get(month_number)

            month_year = selected_date.year

            gasoline_ethanol_at_date = df_gasoline_ethanol_overtime.drop(['dt_date_month_start', avg_fuel_price_col], axis=1)

            fig_gasoline_ethanol_at_date = px.bar(
                gasoline_ethanol_at_date,
                x='nm_fuel_type',
                y='nu_km_cost',
                text="nu_km_cost",
                color='nm_fuel_type',
                color_discrete_map=fuel_types_colors,
                title=f'Preço médio por Km (R$) em {month_name.lower()} de {month_year}',
                hover_data={
                    'nm_fuel_type': True,
                    "nu_km_cost": ':.2f'
                },
                labels={
                    "nm_fuel_type": "Combustível",
                    "nu_km_cost": "Preço Médio por Km (R$)"
                }
            )
            fig_gasoline_ethanol_at_date.update_xaxes(title_text=None)
            fig_gasoline_ethanol_at_date.update_yaxes(title_text=None)
            fig_gasoline_ethanol_at_date.update_traces(
                width=0.3,
                textposition="inside",
                texttemplate="%{y:.2f}",
                textfont_color="black",
                textfont_weight='bold'
            )
            fig_gasoline_ethanol_at_date.update_layout(
                legend=dict(
                    x=0,
                    y=-0.1,
                    orientation="h",
                    xanchor='left'
                ),
                legend_title=None
            )

            st.plotly_chart(fig_gasoline_ethanol_at_date, width='stretch', config={'displayModeBar': False})

        subcol1_city, subcol2_city = st.columns([3, 1], vertical_alignment="center", border=False)

        with subcol2_city:
            map_selection_gasolina_ethanol = st.radio(
                "Nível territorial",
                options=['Regional', 'Estadual', 'Municipal'],
                index=1,
                key="map_selection_gasolina_ethanol_city"
            )

        if map_selection_gasolina_ethanol == 'Municipal':
            territory_key = 'nm_city'
            gdf_territory = gdf_cities.copy()
        elif map_selection_gasolina_ethanol == 'Estadual':
            territory_key = 'nm_state'
            gdf_territory = gdf_states.copy()
        else:
            territory_key = 'nm_region'
            gdf_territory = gdf_regions.copy()

        df_gasoline_ethanol_by_territory = df_fuels_copy_vehicles.groupby([territory_key, 'nm_fuel_type']).mean('nu_km_cost').reset_index()

        df_gasoline_ethanol_by_territory_pivoted = df_gasoline_ethanol_by_territory.pivot(index=territory_key, columns='nm_fuel_type', values='nu_km_cost')

        df_gasoline_ethanol_by_territory_pivoted['choice'] = np.where(df_gasoline_ethanol_by_territory_pivoted['Etanol'] > df_gasoline_ethanol_by_territory_pivoted['Gasolina'],
                                                                    'Gasolina',
                                                                    np.where(df_gasoline_ethanol_by_territory_pivoted['Etanol'] < df_gasoline_ethanol_by_territory_pivoted['Gasolina'],
                                                                            'Etanol',
                                                                            'Indiferente'))

        df_gasoline_ethanol_by_territory_pivoted = df_gasoline_ethanol_by_territory_pivoted.drop(['Etanol', 'Gasolina'], axis=1)

        if (len(region_selected) != 0) and ('nm_region' in gdf_territory.columns):
            gdf_territory = gdf_territory[gdf_territory['nm_region'].isin(region_selected)].reset_index(drop=True)

        if (len(state_selected) != 0) and ('nm_state' in gdf_territory.columns):
            gdf_territory = gdf_territory[gdf_territory['nm_state'].isin(state_selected)].reset_index(drop=True)

        if (len(city_selected) != 0) and ('nm_city' in gdf_territory.columns):
            gdf_territory = gdf_territory[gdf_territory['nm_city'].isin(city_selected)].reset_index(drop=True)

        gdf_territory = gdf_territory.sort_values(territory_key).reset_index(drop=True)
        gdf_territory = gdf_territory.merge(df_gasoline_ethanol_by_territory_pivoted, left_on= territory_key, right_on=territory_key, how="left")
        
        brazil_territory_map_eff_city_blank = px.choropleth(
            gdf_territory,
            geojson=gdf_territory.__geo_interface__,
            locations=gdf_territory.index,
            color_discrete_sequence=["#EEEEEE"]
        )
        brazil_territory_map_eff_city_blank.update_traces(
            marker_line_width=1, 
            marker_line_color="black"
        )

        gdf_territory_no_nan = gdf_territory.dropna(subset=["choice"]).reset_index(drop=True)
        gdf_territory_no_nan['id'] = gdf_territory_no_nan.index

        brazil_territory_map_eff_city = px.choropleth(
            gdf_territory_no_nan,
            geojson=gdf_territory_no_nan.__geo_interface__,
            locations='id',
            color="choice",
            color_discrete_map=fuel_types_colors,
            hover_data={
                'id': False,
                territory_key: True,
                "choice": True
            },
            labels={
                "nm_region": "Região",
                "nm_state": "Estado",
                "nm_city": "Município",
                "choice": "Escolha"
            }
        )

        brazil_territory_map_eff_city_blank.add_traces(brazil_territory_map_eff_city.data)
        
        brazil_territory_map_eff_city_blank.update_layout(
            margin=dict(r=0,l=0,t=0,b=0),
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            dragmode=False,
            showlegend=False
        )
        brazil_territory_map_eff_city_blank.update_geos(
            fitbounds="locations",
            visible=False,
            projection_type="mercator",
            bgcolor='#0e1117'
        )
        brazil_territory_map_eff_city_blank.update_traces(
            marker_line_width=0.5,
            marker_line_color="black"
        )

        with subcol1_city:
            st.plotly_chart(brazil_territory_map_eff_city_blank, width='stretch', config={'displayModeBar': False}, key="map_eff_city")

    with col_road:

        st.subheader('Estrada')

        st.space('small')

        ethanol_efficiency = df_vehicles_copy['ethanol_road_efficiency'].values[0]
        gasoline_efficiency = df_vehicles_copy['gasoline_road_efficiency'].values[0]

        df_fuels_copy_vehicles['nu_km_cost'] = np.where(df_fuels_copy_vehicles['nm_fuel_type'] == 'Gasolina',
                                                        df_fuels_copy_vehicles[avg_fuel_price_col] / gasoline_efficiency ,
                                                        df_fuels_copy_vehicles[avg_fuel_price_col] / ethanol_efficiency)

        df_gasoline_ethanol_overtime = df_fuels_copy_vehicles.groupby(['dt_date_month_start', 'nm_fuel_type']).mean('nu_km_cost').reset_index()

        if start_date != end_date:

            fig_gasoline_ethanol_overtime = px.line(
                df_gasoline_ethanol_overtime,
                x='dt_date_month_start',
                y='nu_km_cost',
                color='nm_fuel_type',
                color_discrete_map=fuel_types_colors,
                markers=True,
                title='Evolução do preço médio por Km (R$) ao longo do tempo',
                range_y=[0, df_gasoline_ethanol_overtime['nu_km_cost'].max() * 1.1],
                hover_data={
                    'dt_date_month_start': True,
                    'nm_fuel_type': True,
                    "nu_km_cost": ':.2f'
                },
                labels={
                    "dt_date_month_start": "Data",
                    "nm_fuel_type": "Combustível",
                    "nu_km_cost": "Preço Médio por Km (R$)"
                }
            )
            fig_gasoline_ethanol_overtime.update_xaxes(title_text=None)
            fig_gasoline_ethanol_overtime.update_yaxes(title_text=None)
            fig_gasoline_ethanol_overtime.update_layout(
                legend=dict(
                    x=0,
                    y=-0.1,
                    orientation="h",
                    xanchor='left'
                ),
                legend_title=None
            )

            st.plotly_chart(fig_gasoline_ethanol_overtime, width='stretch', config={'displayModeBar': False})

        else:

            selected_date = df_gasoline_ethanol_overtime['dt_date_month_start'].values[0]
            selected_date = pd.to_datetime(selected_date)

            month_number = selected_date.month
            month_name = months_in_portuguese.get(month_number)

            month_year = selected_date.year

            gasoline_ethanol_at_date = df_gasoline_ethanol_overtime.drop(['dt_date_month_start', avg_fuel_price_col], axis=1)

            fig_gasoline_ethanol_at_date = px.bar(
                gasoline_ethanol_at_date,
                x='nm_fuel_type',
                y='nu_km_cost',
                text="nu_km_cost",
                color='nm_fuel_type',
                color_discrete_map=fuel_types_colors,
                title=f'Preço médio por Km (R$) em {month_name.lower()} de {month_year}',
                hover_data={
                    'nm_fuel_type': True,
                    "nu_km_cost": ':.2f'
                },
                labels={
                    "nm_fuel_type": "Combustível",
                    "nu_km_cost": "Preço Médio por Km (R$)"
                }
            )
            fig_gasoline_ethanol_at_date.update_xaxes(title_text=None)
            fig_gasoline_ethanol_at_date.update_yaxes(title_text=None)
            fig_gasoline_ethanol_at_date.update_traces(
                width=0.3,
                textposition="inside",
                texttemplate="%{y:.2f}",
                textfont_color="black",
                textfont_weight='bold'
            )
            fig_gasoline_ethanol_at_date.update_layout(
                legend=None
            )

            st.plotly_chart(fig_gasoline_ethanol_at_date, width='stretch', config={'displayModeBar': False})

        subcol1_road, subcol2_road = st.columns([3, 1], vertical_alignment="center", border=False)

        with subcol2_road:
            map_selection_gasolina_ethanol = st.radio(
                "Nível territorial",
                options=['Regional', 'Estadual', 'Municipal'],
                index=1,
                key="map_selection_gasolina_ethanol_road"
            )

        if map_selection_gasolina_ethanol == 'Municipal':
            territory_key = 'nm_city'
            gdf_territory = gdf_cities.copy()
        elif map_selection_gasolina_ethanol == 'Estadual':
            territory_key = 'nm_state'
            gdf_territory = gdf_states.copy()
        else:
            territory_key = 'nm_region'
            gdf_territory = gdf_regions.copy()

        df_gasoline_ethanol_by_territory = df_fuels_copy_vehicles.groupby([territory_key, 'nm_fuel_type']).mean('nu_km_cost').reset_index()

        df_gasoline_ethanol_by_territory_pivoted = df_gasoline_ethanol_by_territory.pivot(index=territory_key, columns='nm_fuel_type', values='nu_km_cost')

        df_gasoline_ethanol_by_territory_pivoted['choice'] = np.where(df_gasoline_ethanol_by_territory_pivoted['Etanol'] > df_gasoline_ethanol_by_territory_pivoted['Gasolina'],
                                                                    'Gasolina',
                                                                    np.where(df_gasoline_ethanol_by_territory_pivoted['Etanol'] < df_gasoline_ethanol_by_territory_pivoted['Gasolina'],
                                                                            'Etanol',
                                                                            'Indiferente'))

        df_gasoline_ethanol_by_territory_pivoted = df_gasoline_ethanol_by_territory_pivoted.drop(['Etanol', 'Gasolina'], axis=1)

        if (len(region_selected) != 0) and ('nm_region' in gdf_territory.columns):
            gdf_territory = gdf_territory[gdf_territory['nm_region'].isin(region_selected)].reset_index(drop=True)

        if (len(state_selected) != 0) and ('nm_state' in gdf_territory.columns):
            gdf_territory = gdf_territory[gdf_territory['nm_state'].isin(state_selected)].reset_index(drop=True)

        if (len(city_selected) != 0) and ('nm_city' in gdf_territory.columns):
            gdf_territory = gdf_territory[gdf_territory['nm_city'].isin(city_selected)].reset_index(drop=True)

        gdf_territory = gdf_territory.sort_values(territory_key).reset_index(drop=True)
        gdf_territory = gdf_territory.merge(df_gasoline_ethanol_by_territory_pivoted, left_on= territory_key, right_on=territory_key, how="left")
        
        brazil_territory_map_eff_road_blank = px.choropleth(
            gdf_territory,
            geojson=gdf_territory.__geo_interface__,
            locations=gdf_territory.index,
            color_discrete_sequence=["#EEEEEE"]
        )
        brazil_territory_map_eff_road_blank.update_traces(
            marker_line_width=1, 
            marker_line_color="black"
        )

        gdf_territory_no_nan = gdf_territory.dropna(subset=["choice"]).reset_index(drop=True)
        gdf_territory_no_nan['id'] = gdf_territory_no_nan.index

        brazil_territory_map_eff_road = px.choropleth(
            gdf_territory_no_nan,
            geojson=gdf_territory_no_nan.__geo_interface__,
            locations='id',
            color="choice",
            color_discrete_map=fuel_types_colors,
            hover_data={
                'id': False,
                territory_key: True,
                "choice": True
            },
            labels={
                "nm_region": "Região",
                "nm_state": "Estado",
                "nm_city": "Município",
                "choice": "Escolha"
            }
        )

        brazil_territory_map_eff_road_blank.add_traces(brazil_territory_map_eff_road.data)
        
        brazil_territory_map_eff_road_blank.update_layout(
            margin=dict(r=0,l=0,t=0,b=0),
            paper_bgcolor='#0e1117',
            plot_bgcolor='#0e1117',
            dragmode=False,
            showlegend=False
        )
        brazil_territory_map_eff_road_blank.update_geos(
            fitbounds="locations",
            visible=False,
            projection_type="mercator",
            bgcolor='#0e1117'
        )
        brazil_territory_map_eff_road_blank.update_traces(
            marker_line_width=0.5,
            marker_line_color="black"
        )

        with subcol1_road:
            st.plotly_chart(brazil_territory_map_eff_road_blank, width='stretch', config={'displayModeBar': False}, key="map_eff_road")

    st.space('small')
    st.link_button("Desenvolvido por João Paiva", "https://joaopaivaa.github.io/")