import streamlit as st
import requests 
import os
from dotenv import load_dotenv
import sqlite3
from pathlib import Path
from datetime import datetime
import pandas as pd

load_dotenv()
STEAMID=os.getenv("STEAMID")
WEBAPIKEY=os.getenv("WEBAPIKEY")

WISHLIST_DB_PATH = Path(__file__).parent / "wishlist.db"

def init_wishlist_database():
    """Initialize SQLite database for wishlist data"""
    conn = sqlite3.connect(WISHLIST_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appid INTEGER NOT NULL,
            name TEXT NOT NULL,
            price REAL,
            currency TEXT,
            fetch_date TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def save_wishlist_to_db(wishlist_data):
    """Save wishlist data to SQLite database"""
    init_wishlist_database()
    conn = sqlite3.connect(WISHLIST_DB_PATH)
    cursor = conn.cursor()
    fetch_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    for item in wishlist_data:
        cursor.execute('''
            INSERT INTO wishlist (appid, name, price, currency, fetch_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (item["appid"], item["name"], item.get("price"), item.get("currency"), fetch_date))
    
    conn.commit()
    conn.close()

def getSteamWishList():
    st.write("Esta é a seção SteamData onde você pode gerenciar sua lista de espera do Steam.")     
    
    if st.button("🔄 Buscar WishList", key="fetch_wishlist"):
        wishlist = requests.get(f"https://api.steampowered.com/IWishlistService/GetWishlist/v1/?key={WEBAPIKEY}&steamid={STEAMID}").json()["response"]["items"]
        appids = [item["appid"] for item in wishlist]
        appData = []

        total = len(appids)
        progress = st.progress(0)
        with st.spinner("Buscando nomes e preços na wishlist..."):
            for i, appid in enumerate(appids, start=1):
                app_info = getAppDetails(appid)
                appData.append(app_info)
                progress.progress(int(i * 100 / total))

        # Save to database
        save_wishlist_to_db(appData)
        st.success(f"✅ WishList atualizada com {len(appData)} jogos!")
        
        # Display data
        st.subheader("Dados da WishList:")
        for item in appData:
            price_str = f"R$ {item['price']:.2f}" if item['price'] else "Gratuito/Não disponível"
            st.write(f"**{item['name']}** - {price_str}")

def getAppDetails(appid):
    """Fetch app details including name and price"""
    appdetail = requests.get(f"https://store.steampowered.com/api/appdetails?appids={appid}&cc=br").json()
    
    if appdetail[str(appid)]["success"]:
        data = appdetail[str(appid)]["data"]
        name = data.get("name", "Unknown App")
        
        # Extract price from price_overview
        price = None
        currency = None
        if "price_overview" in data:
            price_overview = data["price_overview"]
            price = price_overview.get("final", 0) / 100  # Price is in cents
            currency = price_overview.get("currency", "BRL")
        
        return {
            "appid": appid,
            "name": name,
            "price": price,
            "currency": currency
        }
    
    return {
        "appid": appid,
        "name": "Unknown App",
        "price": None,
        "currency": None
    }

def viewWishlistDatabase():
    """View wishlist data from database"""
    from data import get_latest_wishlist, get_wishlist_history
    
    st.subheader("📊 Dados Salvos da WishList")
    
    # Tabs for different views
    tab1, tab2 = st.tabs(["Última Busca", "Histórico Completo"])
    
    with tab1:
        latest = get_latest_wishlist()
        if latest:
            st.write(f"**Data da busca:** {latest['fetch_date']}")
            st.write(f"**Total de jogos:** {len(latest['items'])}")
            
            # Create a nice dataframe
            df_latest = __create_wishlist_df(latest['items'])
            st.dataframe(df_latest, use_container_width=True)
            
            # Show summary stats
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de Jogos", len(latest['items']))
            with col2:
                total_price = sum([item[2] for item in latest['items'] if item[2]])
                st.metric("Valor Total", f"{total_price:.2f}")
            with col3:
                free_count = sum([1 for item in latest['items'] if not item[2]])
                st.metric("Jogos Gratuitos", free_count)
        else:
            st.info("📭 Nenhuma wishlist foi buscada ainda. Clique no botão 'Buscar WishList' acima!")
    
    with tab2:
        df_history = get_wishlist_history()
        if df_history is not None and len(df_history) > 0:
            st.write(f"**Total de registros:** {len(df_history)}")
            st.dataframe(df_history, use_container_width=True)
            
            # Summary by fetch date
            st.subheader("Resumo por Data")
            summary = df_history.groupby('fetch_date').agg({
                'appid': 'count',
                'price': lambda x: x[x.notna()].sum()
            }).rename(columns={'appid': 'Quantidade', 'price': 'Valor Total'})
            st.dataframe(summary, use_container_width=True)
        else:
            st.info("📭 Nenhum histórico disponível.")

def __create_wishlist_df(items):
    """Helper function to create a nice dataframe from wishlist items"""
    
    data = []
    for item in items:
        appid, name, price, currency = item
        price_display = f"R$ {price:.2f}" if price else "Gratuito"
        data.append({
            "ID": appid,
            "Nome do Jogo": name,
            "Preço": price_display,
            "Moeda": currency or "N/A"
        })
    
    return pd.DataFrame(data)
