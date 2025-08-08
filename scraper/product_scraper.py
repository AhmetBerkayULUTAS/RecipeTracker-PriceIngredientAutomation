import threading
import queue
import time
import random
import urllib.parse

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ml.preprocess import clean_text
from config import settings 
from ml import predict
from scraper.utils_scraper import setup_driver, extract_quantity_and_unit
from database.product_db import save_product_data, has_recent_data_for_product

def wait_random(min_s=1.5, max_s=3.0):
    time.sleep(random.uniform(min_s, max_s))


def accept_cookies(driver, method="id", value=None):
    """
    method: 'id', 'class', 'css' gibi Selenium By parametresi
    value: ilgili ID, class adı veya selector
    """
    if not value:
        return
    try:
        if method == "id":
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, value))
            )
        elif method == "class":
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CLASS_NAME, value))
            )
        elif method == "css":
            element = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, value))
            )
        else:
            print(f"[HATA] Geçersiz yöntem belirtildi: {method}")
            return

        element.click()
        print(f"[{driver.title.split('-')[0].strip()}] Çerez butonu tıklandı: ({method} = {value})")
        wait_random()
    except Exception as e:
        print(f"Çerez butonu bulunamadı veya tıklanamadı ({method}: {value}): {e}")


def scrape_market(market, urun_listesi, results_queue):
    print(f"--- THREAD BAŞLADI: [{market['name']}] ---")
    driver = None
    market_verileri = []
    try:
        driver = setup_driver()
        for urun in urun_listesi:
            if has_recent_data_for_product(urun, days=7):
                print(f"[{market['name']}] '{urun}' için güncel veri zaten var. Atlanıyor.")
                continue
            print(f"[{market['name']}] '{urun}' aranıyor...")
            encoded_urun = urllib.parse.quote(urun)
            search_url = market["url"].format(query=encoded_urun)
            driver.get(search_url)
            wait_random(5.0, 9.0)
            try:
                if market["name"] == "Migros":
                    accept_cookies(driver, method="id", value=market["cookie_id"])
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.product-name"))
                    )
                    isimler = driver.find_elements(By.CSS_SELECTOR, "a.product-name")
                    fiyatlar = driver.find_elements(By.CSS_SELECTOR, "div.price")
                    for isim, fiyat in zip(isimler, fiyatlar):
                        isim_text = isim.text.strip()
                        fiyat_text = fiyat.get_attribute("innerText").replace(" TL", "").replace("₺", "").replace(",", ".").strip()
                        miktar, birim = extract_quantity_and_unit(isim_text)
                        if miktar is not None and birim is not None and urun.lower() in isim_text.lower():
                            if predict.is_relevant(urun, isim_text) == 1:
                                market_verileri.append({
                                    "market": market["name"],
                                    "aranan_urun": urun,
                                    "urun_adi": isim_text,
                                    "fiyat": float(fiyat_text),
                                    "link": isim.get_attribute("href"),
                                    "miktar": miktar,
                                    "birim_tipi": birim
                                })

                elif market["name"] == "A101":
                    accept_cookies(driver, method="id", value="CybotCookiebotDialogBodyLevelButtonCustomize")
                    wait_random(1.0, 2.0)
                    accept_cookies(driver, method="id", value="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, market["card_selector"]))
                    )
                    kartlar = driver.find_elements(By.CSS_SELECTOR, market["card_selector"])
                    for kart in kartlar:
                        try:
                            isim_element = kart.find_element(By.CSS_SELECTOR, market["name_selector"])
                            fiyat_element = kart.find_element(By.CSS_SELECTOR, market["price_selector"])
                            isim_text = isim_element.text.strip()
                            fiyat_text = fiyat_element.text.strip().replace("₺", "").replace(",", ".").split()[-1]
                            miktar, birim = extract_quantity_and_unit(isim_text)
                            if miktar is not None and birim is not None and urun.lower() in isim_text.lower():
                                if predict.is_relevant(urun, isim_text) == 1:
                                    market_verileri.append({
                                        "market": market["name"],
                                        "aranan_urun": urun,
                                        "urun_adi": isim_text,
                                        "fiyat": float(fiyat_text),
                                        "link": kart.get_attribute("href"),
                                        "miktar": miktar,
                                        "birim_tipi": birim
                                    })
                        except Exception as e:
                            print(f"A101 kart hatası: {e}")

                elif market["name"] in ["Şok", "Cepte Şok"]:
                    try:
                        WebDriverWait(driver, 20).until(
                            EC.element_to_be_clickable((By.ID, market["cookie_id"]))
                        ).click()
                        wait_random(2, 4)
                    except Exception as e:
                        print(f"[{market['name']}] Çerez işlemi hatası: {e}")
                    try:
                        WebDriverWait(driver, 30).until(
                            EC.visibility_of_any_elements_located((By.CSS_SELECTOR, market["card_selector"]))
                        )
                    except Exception as e:
                        print(f"[{market['name']}] Sayfa yüklenemedi: {e}")
                        continue
                    kartlar = driver.find_elements(By.CSS_SELECTOR, market["card_selector"])
                    for kart in kartlar:
                        try:
                            isim_element = kart.find_element(By.CSS_SELECTOR, market["name_selector"])
                            fiyat_element = kart.find_element(By.CSS_SELECTOR, market["price_selector"])
                            isim_text = isim_element.text.strip()
                            fiyat_text = fiyat_element.text.strip().replace("₺", "").replace(",", ".").strip()
                            miktar, birim = extract_quantity_and_unit(isim_text)
                            if miktar is not None and birim is not None and urun.lower() in isim_text.lower():
                                if miktar and birim and predict.is_relevant(urun, isim_text) == 1:
                                    link = market["url_func"](kart, market["url"].split("/arama")[0])
                                    market_verileri.append({
                                        "market": market["name"],
                                        "aranan_urun": urun,
                                        "urun_adi": isim_text,
                                        "fiyat": float(fiyat_text),
                                        "link": link,
                                        "miktar": miktar,
                                        "birim_tipi": birim
                                    })
                        except Exception as e:
                            print(f"[{market['name']}] Kart hatası: {e}")
            except Exception as e:
                print(f"[{market['name']}] Genel hata: {e}")
            wait_random(4, 9)
    except Exception as e:
        print(f"!!! THREAD HATASI [{market['name']}]: {e}")
    finally:
        if driver:
            driver.quit()
        results_queue.put(market_verileri)
        print(f"--- THREAD BİTTİ: [{market['name']}] - Toplam {len(market_verileri)} ürün eklendi. ---")
def get_ingredient(malzemeler_str):
    print("Scraping işlemi başlatılıyor...")
    try:
        urun_listesi = [clean_text(malzeme) for malzeme in malzemeler_str.strip().split('\n') if malzeme.strip()]
        if not urun_listesi:
            print("Hata: İşlenecek ürün bulunamadı.")
            return
        print(f"Taranacak ürünler: {urun_listesi}")
        threads = []
        results_queue = queue.Queue()
        for market in settings.MARKETS:
            thread = threading.Thread(target=scrape_market, args=(market, urun_listesi, results_queue))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        print("\nTüm thread'ler tamamlandı. Sonuçlar toplanıyor...")
        tum_veriler = []
        while not results_queue.empty():
            market_sonuclari = results_queue.get()
            if market_sonuclari:
                tum_veriler.extend(market_sonuclari)
        if not tum_veriler:
            print("Hiçbir marketten veri alınamadı.")
            return
        print(f"\nToplam {len(tum_veriler)} adet ürün verisi toplandı. Veritabanına kaydediliyor...")
        save_product_data(tum_veriler)
        print("İşlem başarıyla tamamlandı.")
    except Exception as e:
        print(f"Beklenmedik bir ana hata oluştu: {e}")


