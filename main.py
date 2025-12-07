import streamlit as st
from data import load_price_data
from charts import plot_matplotlib, plot_altair, plot_highcharts
from steam import *

# Load data from SQLite database
df = load_price_data()
df = df.sort_values(by="Date").reset_index(drop=True)

# Create tabs
tabs = st.tabs(["Gráficos", "Dados", "SteamData", "WishList"])
with tabs[0]:
    st.title("Comparativo de Gráficos — Matplotlib / Altair / Highcharts")
    st.write("Dados: Histórico de preços – Horizon Forbidden West")

    # --------------------------------------------------
    # 1️⃣ Matplotlib
    # --------------------------------------------------
    st.header("1️⃣ Matplotlib")
    plot_matplotlib(df)

    # --------------------------------------------------
    # 2️⃣ Altair
    # --------------------------------------------------
    st.header("2️⃣ Altair")
    plot_altair(df)

    # --------------------------------------------------
    # 3️⃣ Highcharts (streamlit-highcharts)
    # --------------------------------------------------
    st.header("3️⃣ Highcharts (streamlit-highcharts)")
    plot_highcharts(df)

with tabs[1]:
    st.title("Dados")
    st.dataframe(df, use_container_width=True)

with tabs[2]:
    st.title("SteamData")
    getSteamWishList()

with tabs[3]:
    st.title("WishList")
    viewWishlistDatabase()
