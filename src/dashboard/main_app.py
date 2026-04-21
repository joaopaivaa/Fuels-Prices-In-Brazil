import streamlit as st

main_page = st.Page(
    "fuel_prices_dashboard.py",
    title="Página principal",
    icon="⛽"
)

about_page = st.Page(
    "pages/about.py",
    title="Sobre o painel",
    icon='ℹ️'
)

nav = st.navigation([main_page, about_page])

nav.run()