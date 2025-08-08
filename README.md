# RecipeTracker-PriceIngredientAutomation
Recipe Scraper App (Flask + Selenium)
A simple web app that lets users search for recipes, scrapes the details (name, ingredients, URL) from nefisyemektarifleri.com, and saves them into an SQLite database.

# 🔧 Tech Stack
Python 3.x

Flask

Selenium (with ChromeDriver)

SQLite

# ⚙️ Setup
Install dependencies

bash
Copy code
pip install flask selenium pandas
Download ChromeDriver
Update the driver_path in app.py to match your local path.

# 🚀 How It Works
User enters a recipe keyword.

The app uses Selenium to search the site and collect recipe data.

Scraped data is saved into tarifler.db.

Results are displayed on the web page.

# 💡 Usage
bash
Copy code
python app.py
Visit: http://127.0.0.1:5000
 
