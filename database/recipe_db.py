import sqlite3
from datetime import datetime

from config.settings import RECIPE_DB_PATH

def create_recipe_db():
    """Tarifler veritabanını oluşturur """
    conn = sqlite3.connect(RECIPE_DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tarifler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aranan_kelime TEXT,
            tarif_adi TEXT,
            tarif_url TEXT UNIQUE,
            malzemeler TEXT,
            eklenme_tarihi TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_recipe(aranan_kelime, tarif_adi, tarif_url, malzemeler):
    """Yeni bir tarif kaydeder"""
    conn = sqlite3.connect(RECIPE_DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT OR IGNORE INTO tarifler (aranan_kelime, tarif_adi, tarif_url, malzemeler, eklenme_tarihi)
            VALUES (?, ?, ?, ?, ?)
        """, (
            aranan_kelime,
            tarif_adi,
            tarif_url,
            malzemeler,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
    except sqlite3.Error as e:
        print("SQLite Hatası:", e)
    finally:
        conn.close()

def get_recipes(search_term=None, limit=10):
    """Tarifleri arama kelimesine göre getirir"""
    conn = sqlite3.connect(RECIPE_DB_PATH)
    c = conn.cursor()
    if search_term:
        c.execute("""
            SELECT tarif_adi, tarif_url, malzemeler 
            FROM tarifler 
            WHERE aranan_kelime LIKE ? 
            ORDER BY eklenme_tarihi DESC
        """, ('%' + search_term + '%',))
    else:
        c.execute("""
            SELECT tarif_adi, tarif_url, malzemeler 
            FROM tarifler 
            ORDER BY eklenme_tarihi DESC 
            LIMIT ?
        """, (limit,))
    results = c.fetchall()
    conn.close()
    return results
