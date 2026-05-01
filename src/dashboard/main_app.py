import streamlit as st

p1 = st.Page("pages/fuels_prices.py", title="Indicadores", icon="⛽")
p2 = st.Page("pages/about.py", title="Sobre", icon="ℹ️"  )
pg = st.navigation([p1, p2])
pg.run()