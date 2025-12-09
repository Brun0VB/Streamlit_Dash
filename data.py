import sqlite3
import pandas as pd
from pathlib import Path

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
# WISHLIST DATABASE FUNCTIONS
# ============================================

def get_latest_wishlist():
    """Get the latest wishlist data from database"""
    try:
        conn = sqlite3.connect(WISHLIST_DB_PATH)
        cursor = conn.cursor()
        
        # Get the latest fetch_date
        cursor.execute('SELECT DISTINCT fetch_date FROM wishlist ORDER BY fetch_date DESC LIMIT 1')
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
        
        latest_date = result[0]
        
        # Get all items from the latest fetch
        cursor.execute('SELECT appid, name, price, currency FROM wishlist WHERE fetch_date = ? ORDER BY name', (latest_date,))
        rows = cursor.fetchall()
        conn.close()
        
        return {
            "fetch_date": latest_date,
            "items": rows
        }
    except:
        return None

def get_wishlist_history():
    """Get wishlist data as a DataFrame for analysis"""
    try:
        conn = sqlite3.connect(WISHLIST_DB_PATH)
        df = pd.read_sql_query(
            'SELECT appid, name, price, currency, fetch_date FROM wishlist ORDER BY fetch_date DESC',
            conn
        )
        conn.close()
        return df
    except:
        return None

def delete_wishlist_by_fetch_date(fetch_date):
    """Delete all wishlist records for a specific fetch_date"""
    try:
        conn = sqlite3.connect(WISHLIST_DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM wishlist WHERE fetch_date = ?', (fetch_date,))
        conn.commit()
        conn.close()
        return True
    except:
        return False
