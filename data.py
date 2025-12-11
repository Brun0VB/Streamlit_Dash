import sqlite3
import pandas as pd
from pathlib import Path
import datetime

DB_PATH = Path(__file__).parent / "prices.db"
WISHLIST_DB_PATH = Path(__file__).parent / "wishlist.db"

def init_database():
    """Initialize SQLite database with price data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    
    # Check if table is empty
    cursor.execute('SELECT COUNT(*) FROM prices')
    if cursor.fetchone()[0] == 0:
        # Insert data
        data = [
            ("25/01/2024 16:00", 249.9),
            ("24/06/2024 17:24", 199.92),
            ("11/07/2024 17:34", 249.9),
            ("12/09/2024 17:03", 199.92),
            ("19/09/2024 17:03", 249.9),
            ("27/11/2024 18:36", 167.43),
            ("04/12/2024 18:34", 249.9),
            ("19/12/2024 20:30", 167.43),
            ("02/01/2025 19:01", 249.9),
            ("13/03/2025 17:16", 167.43),
            ("20/03/2025 18:01", 249.9),
            ("23/06/2025 17:21", 149.94),
            ("26/06/2025 19:57", 149.94),
            ("10/07/2025 17:11", 249.9),
            ("29/09/2025 17:08", 149.94),
            ("06/10/2025 17:11", 249.9),
            ("20/11/2025 18:01", 149.94),
            ("02/12/2025 18:01", 249.9),
            ("05/12/2025 16:09", 249.9),
        ]
        cursor.executemany('INSERT INTO prices (date, price) VALUES (?, ?)', data)
        conn.commit()
    
    conn.close()

def load_price_data():
    """Load price data from SQLite database and return as DataFrame"""
    init_database()
    conn = sqlite3.connect(DB_PATH)
    
    df = pd.read_sql_query(
        'SELECT date, price FROM prices ORDER BY date ASC',
        conn
    )
    
    conn.close()
    
    # Convert date column to datetime with correct format
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y %H:%M')
    
    # Rename columns for consistency
    df.columns = ['Date', 'Price']
    
    return df

def add_price(date_str, price):
    """Add a new price entry to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO prices (date, price) VALUES (?, ?)', (date_str, price))
    conn.commit()
    conn.close()

def get_all_prices():
    """Get all prices from database"""
    return load_price_data()

def view_raw_table():
    """View raw data directly from the prices table"""
    init_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM prices')
    rows = cursor.fetchall()
    conn.close()
    return rows

# ============================================
# WISHLIST DATABASE FUNCTIONS (NORMALIZED)
# ============================================

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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appid INTEGER NOT NULL,
            name TEXT NOT NULL,
            fetch_date TEXT NOT NULL,
            UNIQUE(appid, fetch_date)
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
    
    # Índices para melhorar performance de consultas
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_game_fetch 
        ON wishlist_games(fetch_date)
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

def save_wishlist_to_db(wishlist_data):
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
    init_wishlist_database()
    conn = sqlite3.connect(WISHLIST_DB_PATH)
    cursor = conn.cursor()
    
    # Data única para todo este fetch
    fetch_date = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    
    for item in wishlist_data:
        try:
            # Passo 1: Inserir jogo na tabela principal
            cursor.execute('''
                INSERT INTO wishlist_games (appid, name, fetch_date)
                VALUES (?, ?, ?)
            ''', (item["appid"], item["name"], fetch_date))
            
            # Passo 2: Recuperar o ID do jogo recém-inserido
            game_id = cursor.lastrowid
            
            # Passo 3: Inserir preço relacionado ao jogo
            cursor.execute('''
                INSERT INTO wishlist_prices (game_id, price, currency, fetch_date)
                VALUES (?, ?, ?, ?)
            ''', (game_id, item.get("price"), item.get("currency"), fetch_date))
            
        except sqlite3.IntegrityError:
            # Se o jogo já existe neste fetch_date, pula
            continue
    
    conn.commit()
    conn.close()

def get_latest_wishlist():
    """
    MUDANÇA 3: Fazer JOIN entre as duas tabelas para recuperar dados completos.
    
    O JOIN conecta:
    - wishlist_games.id = wishlist_prices.game_id
    
    Isso retorna todas as colunas das duas tabelas unidas.
    """
    try:
        conn = sqlite3.connect(WISHLIST_DB_PATH)
        cursor = conn.cursor()
        
        # Buscar a data mais recente
        cursor.execute('''
            SELECT DISTINCT fetch_date 
            FROM wishlist_games 
            ORDER BY fetch_date DESC 
            LIMIT 1
        ''')
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        latest_date = result[0]
        
        # JOIN entre as tabelas para pegar dados completos
        cursor.execute('''
            SELECT 
                g.appid,
                g.name,
                p.price,
                p.currency
            FROM wishlist_games g
            INNER JOIN wishlist_prices p ON g.id = p.game_id
            WHERE g.fetch_date = ?
            ORDER BY g.name
        ''', (latest_date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return {
            "fetch_date": latest_date,
            "items": rows
        }
    except Exception as e:
        print(f"Erro ao buscar wishlist: {e}")
        return None

def get_wishlist_history():
    """
    MUDANÇA 4: JOIN para análise histórica completa.
    
    Retorna um DataFrame com todas as informações unidas,
    útil para gráficos e análises de evolução de preços.
    """
    try:
        conn = sqlite3.connect(WISHLIST_DB_PATH)
        
        # Query com JOIN para unir dados das duas tabelas
        df = pd.read_sql_query('''
            SELECT 
                g.appid,
                g.name,
                p.price,
                p.currency,
                p.fetch_date
            FROM wishlist_games g
            INNER JOIN wishlist_prices p ON g.id = p.game_id
            ORDER BY p.fetch_date DESC
        ''', conn)
        
        conn.close()
        return df
    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        return None

def delete_wishlist_by_fetch_date(fetch_date):
    """
    MUDANÇA 5: Deleção em cascata.
    
    Graças ao 'ON DELETE CASCADE' na foreign key,
    ao deletar um jogo da wishlist_games, todos os
    preços relacionados são automaticamente deletados.
    """
    try:
        conn = sqlite3.connect(WISHLIST_DB_PATH)
        cursor = conn.cursor()
        
        # Deleta da tabela principal
        # Os preços relacionados são deletados automaticamente (CASCADE)
        cursor.execute('DELETE FROM wishlist_games WHERE fetch_date = ?', (fetch_date,))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao deletar: {e}")
        return False

def migrate_old_wishlist_data():
    """
    FUNÇÃO EXTRA: Migração de dados antigos.
    
    Se você já tem dados na tabela antiga 'wishlist',
    esta função transfere tudo para a nova estrutura normalizada.
    
    Execute uma única vez após atualizar o código!
    """
    try:
        conn = sqlite3.connect(WISHLIST_DB_PATH)
        cursor = conn.cursor()
        
        # Verifica se existe a tabela antiga
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='wishlist'
        """)
        
        if not cursor.fetchone():
            print("Tabela antiga 'wishlist' não encontrada. Nada para migrar.")
            conn.close()
            return
        
        # Busca todos os dados antigos
        cursor.execute('SELECT appid, name, price, currency, fetch_date FROM wishlist')
        old_data = cursor.fetchall()
        
        if not old_data:
            print("Nenhum dado para migrar.")
            conn.close()
            return
        
        # Agrupa por fetch_date para manter a organização
        from collections import defaultdict
        grouped = defaultdict(list)
        
        for appid, name, price, currency, fetch_date in old_data:
            grouped[fetch_date].append({
                "appid": appid,
                "name": name,
                "price": price,
                "currency": currency
            })
        
        # Migra cada grupo
        for fetch_date, items in grouped.items():
            for item in items:
                try:
                    # Insere na tabela de jogos
                    cursor.execute('''
                        INSERT INTO wishlist_games (appid, name, fetch_date)
                        VALUES (?, ?, ?)
                    ''', (item["appid"], item["name"], fetch_date))
                    
                    game_id = cursor.lastrowid
                    
                    # Insere o preço relacionado
                    cursor.execute('''
                        INSERT INTO wishlist_prices (game_id, price, currency, fetch_date)
                        VALUES (?, ?, ?, ?)
                    ''', (game_id, item["price"], item["currency"], fetch_date))
                    
                except sqlite3.IntegrityError:
                    # Registro duplicado, pula
                    continue
        
        conn.commit()
        
        # Renomeia a tabela antiga (backup)
        cursor.execute('ALTER TABLE wishlist RENAME TO wishlist_backup_old')
        conn.commit()
        
        print(f"✅ Migração completa! {len(old_data)} registros migrados.")
        print("A tabela antiga foi renomeada para 'wishlist_backup_old'")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erro na migração: {e}")
        return False

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
    
    # Exemplo de JOIN
    print("🔗 Exemplo de dados unidos (JOIN):")
    cursor.execute('''
        SELECT 
            g.id as game_id,
            g.appid,
            g.name,
            p.price,
            p.currency,
            g.fetch_date
        FROM wishlist_games g
        INNER JOIN wishlist_prices p ON g.id = p.game_id
        LIMIT 5
    ''')
    
    print("\n  game_id | appid | nome | preço | moeda | data")
    print("  " + "-" * 70)
    for row in cursor.fetchall():
        print(f"  {row[0]:7} | {row[1]:5} | {row[2][:20]:20} | {row[3]:6} | {row[4]:5} | {row[5]}")
    
    conn.close()