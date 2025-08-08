from scraper.product_scraper import get_ingredient

print("--- run_scraper_test.py başlatılıyor ---")

# Test etmek istediğiniz ürün listesi
test_malzemeler_str = """
ton balığı
"""


import sqlite3
from scraper.utils_scraper import extract_quantity_and_unit
from config.settings import PRODUCT_DB_PATH

def test_veritabani_verileri():
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT rowid, urun_adi FROM urunler")
    rows = cursor.fetchall()

    print("\n--- VERİTABANI VERİLERİ TESTİ ---")
    tanımlanamayanlar = []

    for row in rows:
        urun_id, urun_adi = row
        miktar, birim = extract_quantity_and_unit(urun_adi)
        print(f"[ID: {urun_id}] {urun_adi} → Miktar: {miktar}, Birim_tipi: {birim}")

        if miktar is None or birim is None:
            tanımlanamayanlar.append((urun_id, urun_adi))

    conn.close()

    print("\n--- TANIMLANAMAYAN ÜRÜNLER ---")
    if tanımlanamayanlar:
        for uid, ad in tanımlanamayanlar:
            print(f"[ID: {uid}] {ad}")
        print(f"\nToplam tanımlanamayan ürün sayısı: {len(tanımlanamayanlar)}")
    else:
        print("Tüm ürünler başarıyla çözümlendi.")
        


def temizle_eksik_veriler():
    conn = sqlite3.connect(PRODUCT_DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT rowid, urun_adi FROM urunler")
    rows = cursor.fetchall()

    silinecek_idler = []

    for row in rows:
        rowid, urun_adi = row
        miktar, birim = extract_quantity_and_unit(urun_adi)
        if miktar is None or birim is None:
            silinecek_idler.append(rowid)

    print(f"\n{len(silinecek_idler)} adet ürün birim/miktar verisi olmadığı için silinecek.")

    for rowid in silinecek_idler:
        cursor.execute("DELETE FROM urunler WHERE rowid = ?", (rowid,))

    conn.commit()
    conn.close()
    print("Silme işlemi tamamlandı.")

if __name__ == "__main__":
    #test_veritabani_verileri()
    #temizle_eksik_veriler()
    get_ingredient(test_malzemeler_str)

    #print("--- Test tamamlandı ---")



