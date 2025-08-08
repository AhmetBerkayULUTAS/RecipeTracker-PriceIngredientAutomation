from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import random
import sys
import re

from config import settings 

def setup_driver():

    chrome_options = Options()

    chrome_options.add_argument("--start-maximized") 
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--log-level=3") 
    #chrome_options.add_argument("--no-sandbox")
    #chrome_options.add_argument("--disable-dev-shm-usage")
    #chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument("--headless") # bu aktif edildikten sonrar diğrleride açılıcak 
    chrome_options.add_argument(f"user-agent={random.choice(settings.USER_AGENTS)}")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
    except WebDriverException as e:
        print(f"WebDriver başlatılamadı: {e}")
        print("Lütfen ChromeDriver yolunu kontrol edin veya PATH'inize ekleyin.")
        sys.exit(1)
        
    driver.set_page_load_timeout(60) 
    return driver


def normalize_unit(miktar: float, birim: str):
    birim = birim.lower()
    if birim in ["gr", "g"]:
        return miktar, "g"
    elif birim == "kg":
        return miktar * 1000, "g"
    elif birim == "ml":
        return miktar, "ml"
    elif birim == "l":
        return miktar * 1000, "ml"
    elif birim == "cl":
        return miktar * 10, "ml"
    elif birim in ["lı", "li", "lu", "'lu", "'li", "'lı", "adet"]:
        return miktar, "adet"
    elif birim == "demet" or birim == "bağ":
        return miktar * 5.0, "adet"
    else:
        return miktar, birim

def extract_quantity_and_unit(urun_adi: str):
    urun_adi = urun_adi.lower()

    # 1. 4x100 g gibi formatlar
    multi_match = re.search(r"(\d+)\s*[xX]\s*(\d+[.,]?\d*)\s*(g|gr|kg|ml|l|litre|cl)", urun_adi)
    if multi_match:
        count = int(multi_match.group(1))
        per_unit = float(multi_match.group(2).replace(",", "."))
        birim = multi_match.group(3)
        toplam = count * per_unit
        return normalize_unit(toplam, birim)

    # 2. Adet bazlı: 10lu, 20li gibi
    adet_match = re.search(r"(\d+)[’']?[lL][ıİiIuUüÜ]", urun_adi)
    if adet_match:
        adet = int(adet_match.group(1))
        return normalize_unit(adet, "adet")

    # 3. Standart gramaj/miktar formatı: 500 g, 1.5kg vb.
    match = re.search(r"(\d+[.,]?\d*)\s*(g|gr|kg|ml|l|litre|cl|lı|li|lu|’lu|’li|adet)", urun_adi)
    if match:
        miktar = float(match.group(1).replace(",", "."))
        birim = match.group(2)
        return normalize_unit(miktar, birim)

    # 4. Sadece birim varsa, miktarı 1 varsay
    unit_only = re.search(r"\b(kg|g|gr|ml|l|litre|cl|lı|li|lu|’lu|’li|adet|demet|bağ)\b", urun_adi)
    if unit_only:
        birim = unit_only.group(1)
        return normalize_unit(1.0, birim)

    return None, None