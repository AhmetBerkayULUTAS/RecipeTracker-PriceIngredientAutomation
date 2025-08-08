import sqlite3
from datetime import datetime, timedelta

from config.settings import PRODUCT_DB_PATH

def save_product_data(veriler):
    try:
        conn = sqlite3.connect(PRODUCT_DB_PATH)
        cursor = conn.cursor()


        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urunler (
                market TEXT,
                aranan_urun TEXT,
                urun_adi TEXT,
                fiyat REAL,
                link TEXT,
                alindigi_tarih TEXT,
                miktar REAL,
                birim_tipi TEXT,
                birim_fiyat REAL,
                UNIQUE(market, aranan_urun, alindigi_tarih) ON CONFLICT IGNORE
            )
        """)

        now = datetime.now().strftime("%Y-%m-%d")
        for row in veriler:
            fiyat_degeri = row["fiyat"]
            if isinstance(fiyat_degeri, str):
                fiyat_degeri = fiyat_degeri.replace(',', '.').replace('₺', '')
                fiyat_degeri = float(fiyat_degeri) if fiyat_degeri.replace('.', '', 1).isdigit() else None
            elif isinstance(fiyat_degeri, (float, int)):
                fiyat_degeri = float(fiyat_degeri)
            else:
                fiyat_degeri = None

            birim_fiyat = fiyat_degeri / row["miktar"] if fiyat_degeri and row["miktar"] else None

            cursor.execute("""
                INSERT INTO urunler (market, aranan_urun, urun_adi, fiyat, link, alindigi_tarih, miktar, birim_tipi, birim_fiyat)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["market"],
                row["aranan_urun"],
                row["urun_adi"],
                fiyat_degeri,
                row["link"],
                now,
                row["miktar"],
                row["birim_tipi"],
                birim_fiyat,
            ))

        conn.commit()
        conn.close()
        print(f"{len(veriler)} ürün SQLite veritabanına kaydedildi.")

    except (NameError, ValueError) as e:
        print(f"Hata: Ürün listesi oluşturulamadı. Lütfen 'malzemeler' değişkenini kontrol edin. Detay: {e}")
    except Exception as e:
        print(f"Beklenmedik bir hata oluştu: {e}")


def has_recent_data_for_product(product_name, days=7):
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()

    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    cursor.execute("""
        SELECT COUNT(*) FROM urunler
        WHERE aranan_urun = ? AND alindigi_tarih >= ?
    """, (product_name, cutoff_date))

    count = cursor.fetchone()[0]
    conn.close()
    return count > 0
