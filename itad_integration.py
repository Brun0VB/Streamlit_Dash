import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import sqlite3
from pathlib import Path
import time
from data import *

load_dotenv()
ITAD_API_KEY = os.getenv("ITAD_API_KEY")

class ITADClient:
    """Cliente para interagir com a ITAD API"""
    
    BASE_URL = "https://api.isthereanydeal.com"
    
    def __init__(self, api_key):
        self.api_key = api_key
        
    def get_game_id_from_appid(self, appid):
        """
        Converte Steam AppID para ITAD Game ID
        """
        url = f"{self.BASE_URL}/games/lookup/v1"
        params = {
            "key": self.api_key,
            "appid": appid
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("game"):
                return data["game"]["id"]
            return None
        except Exception as e:
            print(f"Erro ao buscar game_id para appid {appid}: {e}")
            return None
    
    def get_price_history(self, game_id, months=12):
        """
        Busca histórico de preços para um jogo específico
        Retorna apenas dados da Steam
        """
        url = f"{self.BASE_URL}/games/history/v2"
        params = {
            "key": self.api_key,
            "id": game_id,
            "shops": 61,
            "country": "BR",
            "since": (datetime.now() - timedelta(days=30*months)).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            #price history is a list of json, each json is a price entry
            price_history = response.json()
            
            return self._parse_history_response(price_history)
        except Exception as e:
            print(f"Erro ao buscar histórico para game_id {game_id}: {e}")
            return []
    
    def _parse_history_response(self, price_history):
        """
        Processa a resposta da API e extrai apenas mudanças de preço
        """
        price_changes = []
        
        if not price_history or not isinstance(price_history, list) or len(price_history) == 0:
            return price_changes

        # Processa histórico
        for entry in price_history:
        
            deal_info = entry.get("deal", {})
            
            price_changes.append({
                "fetch_date": entry.get("timestamp"),
                "price": deal_info.get("price", {}).get("amount", 0),
                "currency": deal_info.get("price", {}).get("currency", "BRL"),
            })
        
        return price_changes


    def fetch_price_history_for_game(self, appid, name, months=12):
        """
        Busca e salva histórico de preços para um jogo específico
        """
        # Passo 1: Converter AppID para ITAD Game ID
        game_id = self.get_game_id_from_appid(appid)
        
        if not game_id:
            return {
                "success": False,
                "message": f"Jogo {name} não encontrado na ITAD",
                "records": 0
            }

        # Passo 2: Buscar histórico
        price_history = self.get_price_history(game_id, months=months)
        
        if not price_history:
            return {
                "success": False,
                "message": f"Nenhum histórico encontrado para {name} {game_id}",
                "records": 0
            }
        
        # Passo 3: Salvar no banco
        wishllist_instance = WishlistDatabase()
        saved_count = wishllist_instance.save_price_history_to_db(appid, price_history)
        
        return {
            "success": True,
            "message": f"✅ {saved_count} mudanças de preço salvas para {name}",
            "records": saved_count
        }


    def fetch_all_wishlist_history(self, wishlist_items, progress_callback=None, months=24):
        """
        Busca histórico de preços para todos os jogos da wishlist
        
        Args:
            wishlist_items: Lista de tuplas (appid, name, price, currency)
            progress_callback: Função callback para atualizar progresso
            months: Número de meses de histórico para buscar
        """
        if not ITAD_API_KEY:
            return {
                "success": False,
                "message": "Configure ITAD_API_KEY no arquivo .env"
            }
        
        results = []
        total = len(wishlist_items)
        
        for i, (appid, name, _, _) in enumerate(wishlist_items, 1):
            result = self.fetch_price_history_for_game(appid, name, months)
            results.append(result)
            
            # Callback de progresso
            if progress_callback:
                progress_callback(i, total, result)
            
            # Rate limiting: aguarda 1 segundo entre requisições
            if i < total:
                time.sleep(1)
        
        successful = sum(1 for r in results if r["success"])
        total_records = sum(r["records"] for r in results)
        
        return {
            "success": True,
            "message": f"Processados {successful}/{total} jogos, {total_records} registros salvos",
            "results": results,
            "total_records": total_records
        }