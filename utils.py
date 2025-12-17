import pandas as pd
import streamlit as st


def filter_by_period(df, period, date_column):
    max_date = df[date_column].max()

    if period == "Últimos 3 meses":
        start_date = max_date - pd.DateOffset(months=3)
    elif period == "Últimos 6 meses":
        start_date = max_date - pd.DateOffset(months=6)
    elif period == "Último ano":
        start_date = max_date - pd.DateOffset(years=1)
    else:
        start_date = max_date - pd.DateOffset(months=18)

    df_period = df[df[date_column] >= start_date]

    df_ancora = (
        df[df[date_column] < start_date]
        .sort_values(date_column)
        .tail(1)
    )

    if not df_ancora.empty:
        df_ancora = df_ancora.assign(**{date_column: start_date})

    return (
        pd.concat([df_ancora, df_period])
        .sort_values(date_column)
    )

def create_progress_callback():
    progress_container = st.empty()
    status_container = st.empty()

    def progress_callback(current, total, result):
        progress_container.progress(current / total)
        status_container.text(
            f"Processando {current}/{total}: {result['message']}"
        )

    return progress_callback
