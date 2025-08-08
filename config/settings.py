from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "model.pkl"
VECTORIZER_PATH = BASE_DIR / "models" / "vectorizer.pkl"
SCALER_PATH = BASE_DIR / "models" / "scaler.pkl"
TFLITE_MODEL_PATH = BASE_DIR / "models" / "all-MiniLM-L6-v2.tflite"

RECIPE_DB_PATH = BASE_DIR / "database" / "tarifler.db"
PRODUCT_DB_PATH = BASE_DIR / "database" / "urunler.db"

#--- USER_AGENTS Ayarları ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 13; Mobile; rv:109.0) Gecko/109.0 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
]

# --- Market Ayarları ---
from selenium.webdriver.common.by import By
MARKETS = [
    {
        "name": "Migros",
        "url": "https://www.migros.com.tr/arama?q={query}",
        "cookie_id":"31cd32c1-b03e-4463-948d-1347667e64a4",
        "name_selector":"a.product-name",
        "price_selector":"div.sale-price",
        "card_selector": None,
        "url_func": lambda e, base_url: e.get_attribute("href")
    },
    {
        "name": "A101",
        "url": "https://www.a101.com.tr/arama?k={query}&kurumsal=1&platform_name=kapida",
        "cookie_id": "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
        "name_selector": "h3.text-xs.font-medium.leading-4.tablet\\:mb-3.mobile\\:mb-1.cursor-pointer.tablet\\:line-clamp-3.mobile\\:line-clamp-2",
        "price_selector": "section.mt-2\\.5 span.text-base",
        "card_selector": "a[rel='bookmark'][title]",
        "url_func": lambda e, base_url: base_url + e.get_attribute("href")
    },
    {
        "name": "Şok",
        "url": "https://www.sokmarket.com.tr/arama?q={query}",
        "cookie_id": "onetrust-accept-btn-handler",
        "name_selector": "h2.CProductCard-module_title__u8bMW",
        "price_selector": "span.CPriceBox-module_price__bYk-c",
        "card_selector": "div[class*='PLPProductListing_PLPCardParent'] a",
        "url_func": lambda e, base_url: base_url + e.get_attribute("href")
    }


]


#conda activate tf_gpu_env