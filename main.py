import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = '/app/data/database.db'
SUMMARY_PATH = '/app/data/summary.txt'

CSV_FILES = {
    'products': 'products.csv',
    'stores': 'stores.csv',
    'sales': 'sales.csv'
}

for file_name in CSV_FILES.values():
    if not os.path.exists(file_name):
        raise FileNotFoundError(f"Le fichier {file_name} est introuvable dans le dossier du projet.")

# Connect to SQLite db
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create tables
cursor.execute('''CREATE TABLE IF NOT EXISTS products (product_ref TEXT PRIMARY KEY, name TEXT, price REAL, stock INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS stores (store_id INTEGER PRIMARY KEY, city TEXT, employees INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS sales (sale_id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, product_ref TEXT, quantity INTEGER, store_id INTEGER, FOREIGN KEY (product_ref) REFERENCES products(product_ref), FOREIGN KEY (store_id) REFERENCES stores(store_id))''')
cursor.execute('''CREATE TABLE IF NOT EXISTS analysis_results (result_id INTEGER PRIMARY KEY AUTOINCREMENT, analysis_type TEXT, result_value TEXT, timestamp TEXT)''')

# Import data from csv files
products_df = pd.read_csv(CSV_FILES['products'])
products_data = [tuple(row) for row in products_df[['ID Référence produit', 'Nom', 'Prix', 'Stock']].values]
cursor.executemany("INSERT OR IGNORE INTO products (product_ref, name, price, stock) VALUES (?, ?, ?, ?)", products_data)

stores_df = pd.read_csv(CSV_FILES['stores'])
stores_data = [tuple(row) for row in stores_df[['ID Magasin', 'Ville', 'Nombre de salariés']].values]
cursor.executemany("INSERT OR IGNORE INTO stores (store_id, city, employees) VALUES (?, ?, ?)", stores_data)

sales_df = pd.read_csv(CSV_FILES['sales'])
sales_data = [tuple(row) for row in sales_df[['Date', 'ID Référence produit', 'Quantité', 'ID Magasin']].values]
new_sales = 0
for sale in sales_data:
    date, product_ref, quantity, store_id = sale
    cursor.execute("SELECT COUNT(*) FROM sales WHERE date=? AND product_ref=? AND store_id=?", 
                   (date, product_ref, store_id))
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO sales (date, product_ref, quantity, store_id) VALUES (?, ?, ?, ?)", 
                       (date, product_ref, quantity, store_id))
        new_sales += 1

# SQL analysis
cursor.execute('''SELECT SUM(s.quantity * p.price) as total_revenue FROM sales s JOIN products p ON s.product_ref = p.product_ref''')
total_revenue = cursor.fetchone()[0] or 0.0

cursor.execute('''SELECT p.name, SUM(s.quantity) as total_quantity FROM sales s JOIN products p ON s.product_ref = p.product_ref GROUP BY p.name''')
sales_by_product = cursor.fetchall()

cursor.execute('''SELECT st.city, SUM(s.quantity * p.price) as total_sales FROM sales s JOIN stores st ON s.store_id = st.store_id JOIN products p ON s.product_ref = p.product_ref GROUP BY st.city''')
sales_by_region = cursor.fetchall()

# Store SQL analysis results in analysis_results table in db
timestamp = datetime.now().isoformat()
cursor.execute("INSERT INTO analysis_results (analysis_type, result_value, timestamp) VALUES (?, ?, ?)", 
               ("total_revenue", f"Chiffre d'affaires total: {total_revenue:.2f}", timestamp))
for product, qty in sales_by_product:
    cursor.execute("INSERT INTO analysis_results (analysis_type, result_value, timestamp) VALUES (?, ?, ?)", 
                   ("sales_by_product", f"{product}: {qty} unités", timestamp))
for city, sales in sales_by_region:
    cursor.execute("INSERT INTO analysis_results (analysis_type, result_value, timestamp) VALUES (?, ?, ?)", 
                   ("sales_by_region", f"{city}: {sales:.2f}", timestamp))

# Génération de la fiche synthèse dans un fichier texte
with open(SUMMARY_PATH, 'w') as f:
    f.write(f"Fiche Synthèse des Résultats d'Analyse\n")
    f.write(f"Date : {datetime.now().strftime('%d/%m/%Y')}\n\n")
    f.write(f"1. Chiffre d'affaires total : {total_revenue:.2f} €\n")
    f.write("2. Ventes par produit :\n")
    for product, qty in sales_by_product:
        f.write(f"   - {product} : {qty} unités\n")
    f.write("3. Ventes par région :\n")
    for city, sales in sales_by_region:
        f.write(f"   - {city} : {sales:.2f} €\n")

# Sauvegarde et fermeture
conn.commit()
conn.close()

print("Base de données créée, données importées, analyses effectuées, et fiche synthèse générée dans summary.txt.")