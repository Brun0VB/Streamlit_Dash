import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import altair as alt
import numpy as np
from streamlit_highcharts import streamlit_highcharts as st_hc  


# ----------------------------
# Preparar dados
# ----------------------------
data = {
    "Date": [
        "25/01/2024 16:00", "24/06/2024 17:24", "11/07/2024 17:34", "12/09/2024 17:03",
        "19/09/2024 17:03", "27/11/2024 18:36", "04/12/2024 18:34", "19/12/2024 20:30",
        "02/01/2025 19:01", "13/03/2025 17:16", "20/03/2025 18:01", "23/06/2025 17:21",
        "26/06/2025 19:57", "10/07/2025 17:11", "29/09/2025 17:08", "06/10/2025 17:11",
        "20/11/2025 18:01", "02/12/2025 18:01", "05/12/2025 16:09"
    ],
    "Price": [
        249.9, 199.92, 249.9, 199.92, 249.9, 167.43, 249.9, 167.43,
        249.9, 167.43, 249.9, 149.94, 149.94, 249.9, 149.94, 249.9,
        149.94, 249.9, 249.9
    ]
}

df = pd.DataFrame(data)
df["Date"] = pd.to_datetime(df["Date"], format='%d/%m/%Y %H:%M')
df = df.sort_values("Date")

dates_list = df["Date"]
prices_list = df["Price"]


# colocar tudo em uma única tab chamada "Gráficos"
tabs = st.tabs(["Gráficos"])
with tabs[0]:

    st.title("Comparativo de Gráficos — Matplotlib / Altair / Highcharts")
    st.write("Dados: Histórico de preços – Horizon Forbidden West")

    # --------------------------------------------------
    # 1️⃣ Matplotlib
    # --------------------------------------------------
    st.header("1️⃣ Matplotlib")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.step(df["Date"], df["Price"], where="post", linewidth=2)
    ax.plot(df["Date"], df["Price"], "o")
    ax.set_ylim(100, 300)
    ax.set_ylabel("Preço (R$)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%b/%Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    # Cor dos textos
    ax.tick_params(colors="white")            # ticks
    ax.xaxis.label.set_color("white")         # label eixo X
    ax.yaxis.label.set_color("white")         # label eixo Y
    ax.title.set_color("white")               # título
    fig.patch.set_alpha(0)        # Remove fundo da figura
    plt.xticks(rotation=90)
    plt.tight_layout()

    st.pyplot(fig, transparent=True)

    # --------------------------------------------------
    # 2️⃣ Altair
    # --------------------------------------------------
    st.header("2️⃣ Altair")

    alt_chart = (
        alt.Chart(df)
        .mark_line(interpolate="step-after", point=True)
        .encode(
            x=alt.X("Date:T", axis=alt.Axis(format="%b/%Y", labelAngle=-90, tickCount={"interval": "month", "step": 3})),
            y=alt.Y("Price:Q", scale=alt.Scale(domain=[100, 300])),
        )
        .properties(height=300)
    )

    st.altair_chart(alt_chart, width="stretch")

    # --------------------------------------------------
    # 3️⃣ Highcharts (streamlit-highcharts)
    # --------------------------------------------------
    st.header("3️⃣ Highcharts (streamlit-highcharts)")

    # converter datas para ms e preços para lista
    timestamps_ms = (df["Date"].astype("int64") // 10**6).tolist()
    prices = df["Price"].tolist()

    # pares [timestamp_ms, price] — JSON serializável e mantêm ordem cronológica
    series_data = [[int(t), float(p)] for t, p in zip(timestamps_ms, prices)]

    highcharts_options = {
        "chart": {
            "type": "line",
            "backgroundColor": "rgba(0,0,0,0)",
            "plotBackgroundColor": "rgba(0,0,0,0)",
        },
        "title": {
            "text": "Histórico de Preços",
            "style": {"color": "#FFFFFF"}
        },
        "xAxis": {
            "type": "datetime",
            "labels": {"rotation": -90, "style": {"color": "#FFFFFF"}, "format": "{value:%d/%b/%Y %H:%M}"},
            "title": {"style": {"color": "#FFFFFF"}},
            "lineColor": "#FFFFFF",
            "tickColor": "#FFFFFF",
        },
        "yAxis": {
            "title": {"text": "Preço (R$)", "style": {"color": "#FFFFFF"}},
            "labels": {"style": {"color": "#FFFFFF"}},
            "gridLineColor": "rgba(255,255,255,0.2)",
            "lineColor": "#FFFFFF",
        },
        "legend": {
            "itemStyle": {"color": "#FFFFFF"}
        },
        "series": [
            {
                "name": "Preço",
                "data": series_data,
                "step": "left",
                "color": "#66CCFF"
            }
        ]
    }

    st_hc(highcharts_options)
