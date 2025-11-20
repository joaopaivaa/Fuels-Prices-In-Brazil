import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

df_fuels = pd.read_parquet('gold/fuels_prices')

st.title('Preços de combustíveis no Brasil')

col1, col2, col3 = st.columns(3)
with col1:
    fuel_types_selected = st.multiselect(
        "Tipo de combustível",
        ["Etanol", "Gasolina", "Gasolina Aditivada", "Diesel", "Diesel S10" , "CNG", "LPG"],
        default=["Gasolina"],
    )

df_fuel_prices_by_brand = df_fuels.groupby(['nm_fuel_brand', 'nm_fuel_type']).mean('avg_fuel_price').sort_values('avg_fuel_price').reset_index()
df_fuel_prices_by_brand = df_fuel_prices_by_brand[df_fuel_prices_by_brand['nm_fuel_type'].isin(fuel_types_selected)]

fig_fuel_prices_by_brand_top5_highest = px.bar(
    df_fuel_prices_by_brand.head(5),
    x='nm_fuel_brand',
    y='avg_fuel_price',
    color='nm_fuel_type',
    text_auto=True,
    barmode='group',
    title='5 marcas de combustível com maior preço médio'
)

fig_fuel_prices_by_brand_top5_lowest = px.bar(
    df_fuel_prices_by_brand.tail(5),
    x='nm_fuel_brand',
    y='avg_fuel_price',
    color='nm_fuel_type',
    text_auto=True,
    barmode='group',
    title='5 marcas de combustível com menor preço médio'
)

with col2:
    st.plotly_chart(fig_fuel_prices_by_brand_top5_highest, use_container_width=True)
with col3:
    st.plotly_chart(fig_fuel_prices_by_brand_top5_lowest, use_container_width=True)

df_fuel_prices_overtime = df_fuels.groupby(['dt_date_month_start', 'nm_fuel_type']).mean('avg_fuel_price').reset_index()
df_fuel_prices_overtime = df_fuel_prices_overtime[df_fuel_prices_overtime['nm_fuel_type'].isin(fuel_types_selected)]

fig_fuel_prices_overtime = px.line(
    df_fuel_prices_overtime,
    x='dt_date_month_start',
    y='avg_fuel_price',
    color='nm_fuel_type',
    title='Evolução dos preços médios dos combustíveis ao longo do tempo'
)

col1, col2, col3 = st.columns(3)
with col1:
    st.write('Espaço para filtros futuros')
with col2:
    st.plotly_chart(fig_fuel_prices_overtime, use_container_width=True)
with col3:
    st.write('Espaço para grafico de mapa')



















