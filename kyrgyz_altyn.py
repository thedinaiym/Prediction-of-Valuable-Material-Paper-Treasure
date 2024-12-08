import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os

class GoldPriceScraper:
    def __init__(self, url='https://ru.kyrgyzaltyn.kg/gold_bars/', 
                 json_filename='kyrgyz_gold.json', 
                 check_interval=60):

        self.url = url
        self.json_filename = json_filename
        self.check_interval = check_interval
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

    def clean_text(self, text):
        return text.strip().replace('\n', '').replace('\r', '')

    def load_existing_data(self):
        if os.path.exists(self.json_filename):
            with open(self.json_filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def extract_gold_prices(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        tables = soup.find_all('table', {'border': '1', 'cellpadding': '0', 'cellspacing': '0'})
        
        if len(tables) < 2:
            return []
        
        price_table = tables[1]
        rows = price_table.find_all('tr')
        
        gold_prices = []
        
        for row in rows[1:]:
            cols = row.find_all('td')
            
            if len(cols) == 4:
                gold_price = {
                    "Дата": self.clean_text(cols[0].get_text()),
                    "Мерные золотые слитки, г.": self.clean_text(cols[1].get_text()),
                    "Цена обратного выкупа, сом": self.clean_text(cols[2].get_text()),
                    "Цена продажи, сом": self.clean_text(cols[3].get_text())
                }
                gold_prices.append(gold_price)
        
        return gold_prices

    def merge_and_save_data(self, new_prices):
        """Объединение новых данных с существующими и сохранение."""
        existing_data = self.load_existing_data()
        
        existing_entries = {(entry.get("Дата"), entry.get("Мерные золотые слитки, г.")) for entry in existing_data}
        
        for price in new_prices:
            key = (price.get("Дата"), price.get("Мерные золотые слитки, г."))
            if key not in existing_entries:
                existing_data.append(price)
                existing_entries.add(key)
        
        existing_data.sort(key=lambda x: datetime.strptime(x["Дата"], "%d.%m.%Y"), reverse=True)
        
        with open(self.json_filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        
        print(f"Обновлено записей: {len(new_prices)}, Всего записей: {len(existing_data)}")

    def run(self):
        while True:
            try:
                print(f"[{datetime.now()}] Проверка данных...")
                
                response = requests.get(self.url, headers=self.headers)
                
                if response.status_code == 200:
                    new_prices = self.extract_gold_prices(response.content)
                    
                    if new_prices:
                        self.merge_and_save_data(new_prices)
                    else:
                        print("Новых данных не найдено.")
                else:
                    print(f'Ошибка при запросе страницы: {response.status_code}')
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Произошла ошибка: {e}")
                time.sleep(self.check_interval)

if __name__ == "__main__":
    scraper = GoldPriceScraper()
    scraper.run()