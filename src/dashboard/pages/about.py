import streamlit as st

st.set_page_config(
    layout='wide',
    page_title="Sobre"
)

st.title('Sobre o painel')

st.space('small')

st.text('Autor: João Vitor de Paiva Marcotti')
st.text('Contato: joaopaiva.datascience@gmail.com')

st.space('small')

st.text('Frequência de atualização dos dados: Mensal')

st.space('small')

st.text('Desenvolvido com finalidade única de informar a população sobre os preços dos combustíveis no Brasil, utilizando dados públicos disponibilizados pela ANP (Agência Nacional do Petróleo, Gás Natural e Biocombustíveis) e pelo INMETRO(Instituto Nacional de Metrologia, Qualidade e Tecnologia).')

st.space('small')

st.text('Para mais informações sobre o projeto: \nhttps://github.com/joaopaivaa/Fuel-Prices-In-Brazil/blob/main/README.md')