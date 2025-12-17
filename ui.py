import streamlit as st
import requests 
import os
from dotenv import load_dotenv
import pandas as pd
import altair as alt
from data import *
from itad_integration import *
from steam import steamclient
import utils

load_dotenv()
STEAMID=os.getenv("STEAMID")
WEBAPIKEY=os.getenv("WEBAPIKEY")
ITAD_API_KEY=os.getenv("ITAD_API_KEY")

def showSteamWishList():
    st.write("Esta é a seção SteamData onde você pode gerenciar sua lista de espera do Steam.")     

    steamclient_instance = steamclient(STEAMID, WEBAPIKEY)
    data_instance = WishlistDatabase()
    itad_client_instance = ITADClient(ITAD_API_KEY)

    latest_wishlist = data_instance.get_latest_wishlist()

    # Área de botões principais
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Buscar WishList", key="fetch_wishlist"):

            with st.spinner("Buscando itens da wishlist..."):
                wishlist_ids = steamclient_instance.getSteamWishList()

            total = len(wishlist_ids)
            progress = st.progress(0)

            # Como já vem nome e preço, só iteramos p/ mostrar progresso
            appData = []
            for i, id in enumerate(wishlist_ids, start=1):
                appData.append(steamclient_instance.getAppDetails(id))
                progress.progress(int(i * 100 / total))

            # Save to database
            data_instance.save_wishlist_multiple_games(appData)
            st.success(f"✅ WishList atualizada com {len(appData)} jogos!")
            st.rerun()
    with col2:
        if st.button("load prices", key="load_prices"):
            with st.spinner("Carregando preços atuais..."):
                wishlist = data_instance.get_latest_wishlist()
                total = len(wishlist['items'])
                progress = st.progress(0)

                for i, item in enumerate(wishlist['items'], start=1):
                    appid = item[0]
                    price_info = steamclient_instance.getSteamAppPrice(appid)
                    data_instance.save_wishlist_game_price(price_info, appid)
                    progress.progress(int(i * 100 / total))
                
                st.success(f"✅ Preços atualizados para {total} jogos!")
                st.rerun()
    with col3:
        # Botão para buscar histórico de TODOS os jogos
        if st.button("📊 Buscar Histórico Completo (ITAD)", key="fetch_all_history", disabled=not ITAD_API_KEY or not latest_wishlist):
            st.info("🔍 Buscando histórico de preços para todos os jogos...")

            progress_callback = utils.create_progress_callback()
            # Buscar histórico
            result = itad_client_instance.fetch_all_wishlist_history(
                latest_wishlist['items'], 
                progress_callback=progress_callback,
                months=12
            )
            
            if result['success']:
                st.success(f"✅ {result['message']}")
                st.rerun()
            else:
                st.error(f"❌ {result['message']}")

    # Separador
    st.divider()

    # Seção para buscar histórico de jogo individual
    st.subheader("🎯 Buscar Histórico Individual")

    # Criar lista de jogos para seleção
    game_options = {f"{item[1]} (ID: {item[0]})": (item[0], item[1]) 
                    for item in latest_wishlist['items']}
    
    col_select, col_button = st.columns([3, 1])
    
    with col_select:
        selected_game = st.selectbox(
            "Selecione um jogo:",
            options=list(game_options.keys()),
            key="individual_game_select"
        )
    
    with col_button:
        if st.button("🔍 Buscar", key="fetch_individual"):
            appid, game_name = game_options[selected_game]
            
            with st.spinner(f"Buscando histórico de '{game_name}'..."):
                result = itad_client_instance.fetch_price_history_for_game(appid, game_name, months=12)
                
                if result['success']:
                    st.success(result['message'])                 
                else:
                    st.error(result['message'])

def plot_wishlist_altair():
    """Module-level: build and render Altair chart for wishlist price history"""

    data_instance = WishlistDatabase()

    games_with_prices = data_instance.get_latest_wishlist_with_prices()
    games_with_prices_df = pd.DataFrame(games_with_prices['items'], columns=['appid', 'name', 'price', 'currency', 'fetch_date'])
    st.dataframe(games_with_prices_df)

    if games_with_prices is None or games_with_prices_df.empty:
        st.info("📉 Nenhum histórico de preços disponível para os jogos da wishlist.")
        return
    
    games_with_prices_df['fetch_date_dt'] = pd.to_datetime(games_with_prices_df['fetch_date'], utc=True)

    # Get unique game names sorted
    game_names = sorted(games_with_prices_df['name'].unique())
    
    if not game_names:
        st.info("📉 Nenhum preço disponível para plotagem na wishlist.")
        return
    
    # Add selectbox for user to choose a game
    st.subheader('📈 Histórico de Preços (WishList)')
    selected_game = st.selectbox("Selecione um jogo para visualizar:", game_names, key="wishlist_game_select")
    
    # Filter data for selected game
    game_data = games_with_prices_df[games_with_prices_df['name'] == selected_game].copy()
    game_data = game_data.dropna(subset=['price', 'fetch_date_dt'])

    period = st.radio(
        "Mostrar dados de:",
        options=[
            "Últimos 3 meses",
            "Últimos 6 meses",
            "Último ano",
            "Max"
        ],
        index=2,          # Último ano como padrão
        horizontal=True,
        key="wishlist_period"
    )

    game_data = utils.filter_by_period(
        game_data,
        period,
        date_column='fetch_date_dt'
    )
    
    if game_data.empty or sum(game_data['price']) == 0:
        st.warning(f"⚠️ Nenhum preço disponível para {selected_game}.")
        return
    
    game_data['fetch_date_dt'] = pd.to_datetime(game_data['fetch_date_dt'], errors='coerce')

    # Create a nearest selection for hover interaction (like Highcharts)
    nearest = alt.selection_point(nearest=True, on='mouseover', fields=['fetch_date_dt'], empty='none')

    # Build Altair chart with interactive hover
    line = (
        alt.Chart(game_data)
        .mark_line(interpolate='step-after', point=True, color='#66CCFF')
        .encode(
            x=alt.X('fetch_date_dt:T', axis=alt.Axis(format='%d/%b/%Y', labelAngle=-90, title='Data')),
            y=alt.Y('price:Q', scale=alt.Scale(), title='Preço (R$)'),
        )
    )

    # Points that appear on hover
    points = (
        alt.Chart(game_data)
        .mark_circle(color="#8766FF", size=100)
        .encode(
            x='fetch_date_dt:T',
            y='price:Q',
            opacity=alt.condition(nearest, alt.value(1), alt.value(0))
        )
        .add_params(nearest)
    )

    # Combine all layers
    chart = (
        (line + points)
        .properties(height=500, width='container', title=f'Histórico de Preços — {selected_game}')
        .configure_axis(labelColor='white', titleColor='white')
        .configure_title(color='white')
    )

    st.altair_chart(chart, width='stretch')