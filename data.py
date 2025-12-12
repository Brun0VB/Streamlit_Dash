import sqlite3
import pandas as pd
from pathlib import Path
import datetime

WISHLIST_DB_PATH = Path(__file__).parent / "wishlist.db"

class WishlistDatabase:

    def init_wishlist_database():
        """
        MUDANÇA 1: Criar duas tabelas ao invés de uma.
        
        Tabela wishlist_games:
        - Armazena informações básicas do jogo + quando foi adicionado à wishlist
        - Um registro por jogo por fetch
        
        Tabela wishlist_prices:
        - Armazena apenas dados de preço
        - Relacionada com wishlist_games através de game_id (chave estrangeira)
        - Permite múltiplos registros de preço para o mesmo jogo
        """
        conn = sqlite3.connect(WISHLIST_DB_PATH)
        cursor = conn.cursor()
        
        # Tabela principal de jogos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlist_games (
                appid INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                UNIQUE(name, appid)
            )
        ''')
        
        # Tabela de preços com relação
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wishlist_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                price REAL,
                currency TEXT,
                fetch_date TEXT NOT NULL,
                FOREIGN KEY (game_id) REFERENCES wishlist_games(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_price_game 
            ON wishlist_prices(game_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_price_fetch 
            ON wishlist_prices(fetch_date)
        ''')
        
        conn.commit()
        conn.close()

    def save_wishlist_game(self, wishlist_game:dict):
        """
        """
        self.init_wishlist_database()
        conn = sqlite3.connect(WISHLIST_DB_PATH)
        cursor = conn.cursor()

        try:
            # Passo 1: Inserir jogo na tabela principal
            cursor.execute('''
            INSERT INTO wishlist_games (appid, name)
                    VALUES (?, ?)
            ''', (wishlist_game["appid"], wishlist_game["name"]))
        except sqlite3.IntegrityError as e:
            return  # Jogo já existe, pula
                
        
        conn.commit()
        conn.close()

    def save_wishlist_game_price(self, game_data, game_id):
        """
        MUDANÇA 2: Salvar dados nas duas tabelas de forma relacionada.
        
        Processo:
        1. Gera uma data única para este fetch
        2. Para cada jogo:
        a) Insere na tabela wishlist_games
        b) Recupera o ID gerado (game_id)
        c) Insere o preço na wishlist_prices usando o game_id
        
        Isso mantém a integridade referencial entre as tabelas.
        """
        self.init_wishlist_database()
        conn = sqlite3.connect(WISHLIST_DB_PATH)
        cursor = conn.cursor()
        
        # Data única para todo este fetch
        fetch_date = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
        
        # Passo 3: Inserir preço relacionado ao jogo
        cursor.execute('''
            INSERT INTO wishlist_prices (game_id, price, currency, fetch_date)
            VALUES (?, ?, ?, ?)
        ''', (game_id, game_data.get("price"), game_data.get("currency"), fetch_date))
        
        conn.commit()
        conn.close()

    def get_latest_wishlist(self):
        try:
            conn = sqlite3.connect(WISHLIST_DB_PATH)
            cursor = conn.cursor()
            
            # JOIN entre as tabelas para pegar dados completos
            cursor.execute('''
                SELECT 
                *
                FROM wishlist_games g
                ORDER BY g.name
            ''',)
            
            rows = cursor.fetchall()
            conn.close()
            
            return {
                "items": rows
            }
        except Exception as e:
            print(f"Erro ao buscar wishlist: {e}")
            return None

    def get_latest_wishlist_with_prices(self):
        """
        MUDANÇA 3: Fazer JOIN entre as duas tabelas para recuperar dados completos.
        
        O JOIN conecta:
        - wishlist_games.id = wishlist_prices.game_id
        
        Isso retorna todas as colunas das duas tabelas unidas.
        """
        try:
            conn = sqlite3.connect(WISHLIST_DB_PATH)
            cursor = conn.cursor()
            
            # JOIN entre as tabelas para pegar dados completos
            cursor.execute('''
                SELECT 
                    g.appid,
                    g.name,
                    p.price,
                    p.currency
                FROM wishlist_games g
                INNER JOIN wishlist_prices p ON g.appid = p.game_id
                ORDER BY g.name
            ''',)
            
            rows = cursor.fetchall()
            conn.close()
            
            return {
                "items": rows
            }
        except Exception as e:
            print(f"Erro ao buscar wishlist: {e}")
            return None

    # Função auxiliar para visualizar a estrutura
    def show_database_structure():
        """
        Mostra a estrutura das tabelas e exemplos de dados.
        Útil para entender como os dados estão organizados.
        """
        conn = sqlite3.connect(WISHLIST_DB_PATH)
        cursor = conn.cursor()
        
        print("\n=== ESTRUTURA DO BANCO DE DADOS ===\n")
        
        # Estrutura da tabela wishlist_games
        print("📋 Tabela: wishlist_games")
        cursor.execute("PRAGMA table_info(wishlist_games)")
        for col in cursor.fetchall():
            print(f"  - {col[1]} ({col[2]})")
        
        cursor.execute("SELECT COUNT(*) FROM wishlist_games")
        count = cursor.fetchone()[0]
        print(f"  Total de registros: {count}\n")
        
        # Estrutura da tabela wishlist_prices
        print("💰 Tabela: wishlist_prices")
        cursor.execute("PRAGMA table_info(wishlist_prices)")
        for col in cursor.fetchall():
            print(f"  - {col[1]} ({col[2]})")
        
        cursor.execute("SELECT COUNT(*) FROM wishlist_prices")
        count = cursor.fetchone()[0]
        print(f"  Total de registros: {count}\n")
        
        conn.close()