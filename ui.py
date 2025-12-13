import streamlit as st
import requests 
import os
from dotenv import load_dotenv
import pandas as pd
import altair as alt
from data import *
from itad_integration import fetch_all_wishlist_history, fetch_price_history_for_game, ITADClient, get_price_stats_for_game
from steam import steamclient

load_dotenv()
STEAMID=os.getenv("STEAMID")
WEBAPIKEY=os.getenv("WEBAPIKEY")
ITAD_API_KEY=os.getenv("ITAD_API_KEY")

def showSteamWishList():
    st.write("Esta é a seção SteamData onde você pode gerenciar sua lista de espera do Steam.")     

    steamclient_instance = steamclient(STEAMID, WEBAPIKEY)
    data_instance = WishlistDatabase()

    # Área de botões principais
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Buscar WishList", key="fetch_wishlist"):

            with st.spinner("Buscando itens da wishlist..."):
                wishlist_ids = steamclient_instance.getSteamWishList()

            total = len(wishlist_ids)
            progress = st.progress(0)

            # Como já vem nome e preço, só iteramos p/ mostrar progresso
            appData = []
            for i, id in enumerate(wishlist_ids, start=1):
                appData.append(steamclient_instance.getAppPrice(id))
                progress.progress(int(i * 100 / total))

            # Save to database
            for item in appData:
                data_instance.save_wishlist_game(item)
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
    
#     with col2:
#         # Botão para buscar histórico de TODOS os jogos
#         if st.button("📊 Buscar Histórico Completo (ITAD)", key="fetch_all_history", 
#                      disabled=not ITAD_API_KEY or not latest):
#             if not ITAD_API_KEY:
#                 st.error("❌ Configure ITAD_API_KEY no arquivo .env")
#             elif not latest:
#                 st.warning("⚠️ Busque a wishlist primeiro!")
#             else:
#                 st.info("🔍 Buscando histórico de preços para todos os jogos...")
                
#                 # Container para exibir progresso
#                 progress_container = st.empty()
#                 status_container = st.empty()
                
#                 def progress_callback(current, total, result):
#                     progress_container.progress(current / total)
#                     status_container.text(f"Processando {current}/{total}: {result['message']}")
                
#                 # Buscar histórico
#                 result = fetch_all_wishlist_history(
#                     latest['items'], 
#                     progress_callback=progress_callback,
#                     months=24
#                 )
                
#                 if result['success']:
#                     st.success(f"✅ {result['message']}")
#                     st.rerun()
#                 else:
#                     st.error(f"❌ {result['message']}")

#     # Separador
#     st.divider()

#     # Seção para buscar histórico de jogo individual
#     if latest and ITAD_API_KEY:
#         st.subheader("🎯 Buscar Histórico Individual")
        
#         # Criar lista de jogos para seleção
#         game_options = {f"{item[1]} (ID: {item[0]})": (item[0], item[1]) 
#                        for item in latest['items']}
        
#         col_select, col_button = st.columns([3, 1])
        
#         with col_select:
#             selected_game = st.selectbox(
#                 "Selecione um jogo:",
#                 options=list(game_options.keys()),
#                 key="individual_game_select"
#             )
        
#         with col_button:
#             st.write("")  # Spacer
#             st.write("")  # Spacer
#             if st.button("🔍 Buscar", key="fetch_individual"):
#                 appid, game_name = game_options[selected_game]
                
#                 with st.spinner(f"Buscando histórico de '{game_name}'..."):
#                     client = ITADClient(ITAD_API_KEY)
#                     result = fetch_price_history_for_game(appid, game_name, client, months=24)
                    
#                     if result['success']:
#                         st.success(result['message'])
                        
#                         # Mostrar estatísticas
#                         stats = get_price_stats_for_game(appid)
#                         if stats:
#                             col1, col2, col3, col4 = st.columns(4)
#                             with col1:
#                                 st.metric("Menor Preço", f"R$ {stats['min_price']:.2f}")
#                             with col2:
#                                 st.metric("Maior Preço", f"R$ {stats['max_price']:.2f}")
#                             with col3:
#                                 st.metric("Preço Médio", f"R$ {stats['avg_price']:.2f}")
#                             with col4:
#                                 st.metric("Mudanças", stats['num_changes'])
                        
#                         st.rerun()
#                     else:
#                         st.error(result['message'])

#     st.divider()
#     plot_wishlist_altair()

# def getAppDetails(appid):
#     """Fetch app details including name and price"""
#     appdetail = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=br").json()
    
#     if appdetail[str(appid)]["success"]:
#         data = appdetail[str(appid)]["data"]
#         name = data.get("name", "Unknown App")
        
#         # Extract price from price_overview
#         price = None
#         currency = None
#         if "price_overview" in data:
#             price_overview = data["price_overview"]
#             price = price_overview.get("final", 0) / 100  # Price is in cents
#             currency = price_overview.get("currency", "BRL")
        
#         return {
#             "appid": appid,
#             "name": name,
#             "price": price,
#             "currency": currency
#         }
    
#     return {
#         "appid": appid,
#         "name": "Unknown App",
#         "price": None,
#         "currency": None
#     }


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
    
    if game_data.empty:
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
            x=alt.X('fetch_date_dt:T', axis=alt.Axis(format='%d/%b/%Y', labelAngle=-90, title='Data', tickCount={'interval': 'day', 'step': 1})),
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
        .properties(height=400, width=900, title=f'Histórico de Preços — {selected_game}')
        .configure_axis(labelColor='white', titleColor='white')
        .configure_title(color='white')
    )

    st.altair_chart(chart, width='stretch')

# def viewWishlistDatabase():
#     """View wishlist data from database"""
    
#     st.subheader("📊 Dados Salvos da WishList")
    
#     tab1, tab2, tab3, tab4 = st.tabs([
#         "Última Busca", 
#         "Histórico Completo", 
#         "Tabela: wishlist_games", 
#         "Tabela: price_history"
#     ])    
#     with tab1:
#         latest = get_latest_wishlist()
#         if latest:
#             st.write(f"**Data da busca:** {latest['fetch_date']}")
#             st.write(f"**Total de jogos:** {len(latest['items'])}")
            
#             # Create a nice dataframe
#             df_latest = __create_wishlist_df(latest['items'])
#             st.dataframe(df_latest, width='stretch')
            
#             # Show summary stats
#             col1, col2, col3 = st.columns(3)
#             with col1:
#                 st.metric("Total de Jogos", len(latest['items']))
#             with col2:
#                 total_price = sum([item[2] for item in latest['items'] if item[2]])
#                 st.metric("Valor Total", f"{total_price:.2f}")
#             with col3:
#                 free_count = sum([1 for item in latest['items'] if not item[2]])
#                 st.metric("Jogos Gratuitos", free_count)
#         else:
#             st.info("📭 Nenhuma wishlist foi buscada ainda. Clique no botão 'Buscar WishList' acima!")
    
#     with tab2:
#         df_history = get_wishlist_history()
#         if df_history is not None and len(df_history) > 0:
#             st.write(f"**Total de registros:** {len(df_history)}")
#             st.dataframe(df_history, width='stretch')
            
#             # Summary by fetch date
#             st.subheader("Resumo por Data")
#             summary = df_history.groupby('fetch_date').agg({
#                 'appid': 'count',
#                 'price': lambda x: x[x.notna()].sum()
#             }).rename(columns={'appid': 'Quantidade', 'price': 'Valor Total'})
#             st.dataframe(summary, width='stretch')
            
#             # Delete options by fetch_date
#             st.subheader("🗑️ Deletar Dados por Data")
#             unique_dates = sorted(df_history['fetch_date'].unique(), reverse=True)
            
#             col1, col2 = st.columns([3, 1])
#             with col1:
#                 selected_date = st.selectbox("Selecione uma data para deletar:", unique_dates, key="delete_date_select")
#             with col2:
#                 if st.button("🗑️ Deletar", key="delete_wishlist_btn"):
#                     if delete_wishlist_by_fetch_date(selected_date):
#                         st.success(f"✅ Dados de {selected_date} deletados com sucesso!")
#                         st.rerun()
#                     else:
#                         st.error("❌ Erro ao deletar dados.")
#         else:
#             st.info("📭 Nenhum histórico disponível.")

#      # ---- TAB 3: RAW wishlist_games ----
#     with tab3:
#         st.subheader("📂 Tabela crua: wishlist_games")

#         import sqlite3
#         from data import WISHLIST_DB_PATH  # Ajuste se necessário

#         try:
#             conn = sqlite3.connect(WISHLIST_DB_PATH)
#             df_games_raw = pd.read_sql_query("SELECT * FROM wishlist_games", conn)
#             conn.close()
#             st.dataframe(df_games_raw, width='stretch')
#         except Exception as e:
#             st.error(f"Erro ao carregar tabela wishlist_games: {e}")

#     # ---- TAB 4: RAW price_history ----
#     with tab4:
#         st.subheader("📂 Tabela crua: price_history")

#         import sqlite3
#         from data import WISHLIST_DB_PATH  # Ajuste se necessário

#         try:
#             conn = sqlite3.connect(WISHLIST_DB_PATH)
#             df_prices_raw = pd.read_sql_query("SELECT * FROM wishlist_prices", conn)
#             conn.close()
#             st.dataframe(df_prices_raw, width='stretch')
#         except Exception as e:
#             st.error(f"Erro ao carregar tabela price_history: {e}")

# def __create_wishlist_df(items):
#     """Helper function to create a nice dataframe from wishlist items"""
    
#     data = []
#     for item in items:
#         appid, name, price, currency = item
#         price_display = f"R$ {price:.2f}" if price else "Gratuito"
#         data.append({
#             "ID": appid,
#             "Nome do Jogo": name,
#             "Preço": price_display,
#             "Moeda": currency or "N/A"
#         })
    
#     return pd.DataFrame(data)
