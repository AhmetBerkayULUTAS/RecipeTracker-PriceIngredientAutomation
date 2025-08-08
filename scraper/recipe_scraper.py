from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

import time

def close_popups(driver):
    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".ins-close-button, .close-button, [aria-label='Kapat']"))
        ).click()
        print("Bildirim pop-up'ı kapatıldı.")
        time.sleep(0.5)
    except (NoSuchElementException, TimeoutException):
        pass

    try:
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.fc-cta-consent.fc-primary-button[aria-label='İzin ver']"))
        ).click()
        print("Çerez pop-up'ı (izin ver butonu) kapatıldı.")
        time.sleep(0.5)
    except (NoSuchElementException, TimeoutException):
        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Kabul Et') or contains(text(), 'Tümünü Kabul Et') or contains(@class, 'cc-btn')]"))
            ).click()
            print("Çerez/Kabul et pop-up'ı (genel) kapatıldı.")
            time.sleep(0.5)
        except (NoSuchElementException, TimeoutException):
            pass 
        except Exception as e:
            print(f"Genel çerez butonu kapatılırken hata: {e}")
    except Exception as e:
        print(f"İzin ver butonu kapatılırken hata: {e}")


def scrape_recipe_details(driver, url):
    recipe_data = {
        "Tarif Adı": "Tarif Adı Bulunamadı",
        "Malzemeler": "Malzemeler Bulunamadı",
        "URL": url
    }
    try:
        driver.get(url)
        time.sleep(1.5) 

        try:
            recipe_name_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, 'title') or contains(@class, 'recipe-title')] | (//div[@id='breadcrumb']//span[@itemprop='name'])[last()] | //h1"))
            )
            recipe_data["Tarif Adı"] = recipe_name_element.text.strip()
        except:
            print(f"Tarif adı bulunamadı: {url}")
            pass

    
        try:
            ingredients_list_elements = WebDriverWait(driver, 10).until( 
                EC.presence_of_all_elements_located((By.XPATH, "//ul[@class='recipe-materials']/li[@itemprop='recipeIngredient'] | //div[contains(@class, 'ingredients') or contains(@class, 'malzemeler')]//li"))
            )
            recipe_data["Malzemeler"] = "\n".join([item.text.strip() for item in ingredients_list_elements if item.text.strip()])
        except:
            print(f"Malzemeler bulunamadı: {url}")
            pass
    except TimeoutException:
        print(f"Zaman aşımı hatası: {url}")
    except WebDriverException as e:
        print(f"WebDriver hatası: {url} - {e}")
    except Exception as e:
        print(f"scrape_recipe_details bilinmeyen hata: {url} - {e}")
    return recipe_data

def scrape_all_search_results(driver, arama):
    print(f"'{arama}' için arama yapılıyor...")
    driver.get("https://www.nefisyemektarifleri.com/")
    close_popups(driver)

    try:
        search_icon = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.header-search-icon, .icon-search"))
        )
        search_icon.click()
        time.sleep(0.5)
    except (NoSuchElementException, TimeoutException):
        print("Arama ikonuna tıklanamadı, doğrudan input araması deneniyor.")
        pass

    try:
        search_input = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "top-search-input"))
        )
        search_input.clear()
        search_input.send_keys(arama)
        search_input.send_keys(Keys.ENTER)
        time.sleep(3)
    except (NoSuchElementException, TimeoutException):
        print("Arama input alanı bulunamadı veya etkileşim kurulamadı.")
        return []
        
    try:
        close_popups(driver)

        recipe_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((
                By.XPATH, "//a[contains(@class,'title') and @href and string-length(normalize-space(text())) > 0]"
            ))
        )

        results = []
        for card in recipe_cards:
            href = card.get_attribute('href')
            text = card.text.strip()
            if href and text:
                results.append((href, text))

        print(f"Arama sonuç sayfasında {len(results)} tarif linki bulundu.")
        return results
    except (NoSuchElementException, TimeoutException):
        print("Arama sonuçları bulunamadı.")
        return []
    except Exception as e:
        print(f"Arama sonuçlarını çekerken hata: {e}")
        return []