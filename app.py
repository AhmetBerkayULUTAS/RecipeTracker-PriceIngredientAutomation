from flask import Flask, request, render_template
import traceback

from scraper.product_scraper import get_ingredient 
from database import recipe_db
from scraper import recipe_scraper
from scraper.utils_scraper import setup_driver


app = Flask(__name__)
# --- Flask Uygulama Rotaları ---

@app.route("/", methods=["GET", "POST"])
def index():
    tarifler = []

    if request.method == "POST":
        search_term = request.form.get("search_term")
        if search_term:
            tarifler = recipe_db.get_recipes(search_term)
            if not tarifler: # Veritabanında yoksa internetten çek
                print(f"'{search_term}' veritabanında bulunamadı. İnternetten aranıyor...")    
                try:
                    driver = setup_driver()
                    all_results = recipe_scraper.scrape_all_search_results(driver, search_term)

                    for url, ad in all_results:
                        if url and "tarifleri" in url: # Sadece tarif URL'lerini işle
                            print(f"Tarif işleniyor: {ad} - {url}")
                            data = recipe_scraper.scrape_recipe_details(driver, url)
                            if data["Tarif Adı"] != "Tarif Adı Bulunamadı" and data["Malzemeler"] != "Malzemeler Bulunamadı":
                                recipe_db.save_recipe(search_term, data["Tarif Adı"], url, data["Malzemeler"])
                            else:
                                print(f"Uygun veri bulunamadığı için tarif atlandı: {url}")
                    driver.quit()
                    print("Veri çekme işlemi tamamlandı.")
                    
                    # Veritabanından çekilen tarifleri al ve göster
                    tarifler = recipe_db.get_recipes(search_term)
                    for tarif in tarifler:   
                        get_ingredient(tarif[2])
                    return render_template("index.html", search_term=search_term, tarifler=tarifler, search_done=True)

                except Exception as e:
                    print(f"Veri çekme sırasında bir hata oluştu: {e}")
                    traceback.print_exc() # Hata detaylarını yazdır
                    return render_template("index.html", error_message="Arama sırasında bir hata oluştu.", search_term=search_term)
            else:
                for tarif in tarifler:   
                    get_ingredient(tarif[2])   
                return render_template("index.html", search_term=search_term, tarifler=tarifler, search_done=True)
        else:
            return render_template("index.html", error_message="Lütfen bir arama terimi girin.")
    
    # GET isteği veya POST'ta arama yapılmazsa
    return render_template("index.html")

# Veritabanını uygulama başlangıcında oluştur
with app.app_context():
    recipe_db.create_recipe_db()

if __name__ == "__main__":
    app.run(debug=True, threaded=True) 