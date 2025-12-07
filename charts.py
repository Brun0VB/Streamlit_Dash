import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import altair as alt
from streamlit_highcharts import streamlit_highcharts as st_hc


def plot_matplotlib(df):
    """Render Matplotlib chart"""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.step(df["Date"], df["Price"], where="post", linewidth=2)
    ax.plot(df["Date"], df["Price"], "o")
    ax.set_ylim(100, 300)
    ax.set_ylabel("Preço (R$)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%b/%Y"))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")
    fig.patch.set_alpha(0)
    plt.xticks(rotation=90)
    plt.tight_layout()
    st.pyplot(fig, transparent=True)


def plot_altair(df):
    """Render Altair chart"""
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


def plot_highcharts(df):
    """Render Highcharts chart"""
    timestamps_ms = (df["Date"].astype("int64") // 10**6).tolist()
    series_data = [[int(t), float(p)] for t, p in zip(timestamps_ms, df["Price"].tolist())]

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
