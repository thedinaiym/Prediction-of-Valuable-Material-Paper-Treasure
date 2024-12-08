import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def parse_nbkr_data():
    url = 'https://www.nbkr.kg/index1.jsp?item=2747&lang=RUS'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                      'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                      'Chrome/58.0.3029.110 Safari/537.3'
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f'Ошибка при запросе страницы: {response.status_code}')
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    # Создаем таблицу с правильной структурой
    table = soup.find('table', class_='content-table')
    if not table:
        print('Таблица не найдена в предоставленном HTML.')
        return []

    data = []
    start_date = datetime(2024, 10, 1)

    # Пропускаем первую строку с заголовками
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        
        # Проверяем, что строка содержит нужное количество столбцов
        if len(cols) < 4:
            continue

        try:
            # Извлекаем данные
            date_str = cols[0].get_text(strip=True)
            gold_weight = cols[1].get_text(strip=True)
            buyback_price = cols[2].get_text(strip=True)
            sale_price = cols[3].get_text(strip=True)

            # Пропускаем строки с заголовками или некорректными данными
            if date_str == 'Дата' or not date_str:
                continue

            # Преобразуем дату
            current_date = datetime.strptime(date_str, '%d.%m.%Y')
            
            # Фильтруем по дате
            if current_date >= start_date:
                row_data = {
                    "Дата": date_str,
                    "Мерные золотые слитки, г.": gold_weight,
                    "Цена обратного выкупа, сом": buyback_price,
                    "Цена продажи, сом": sale_price
                }
                data.append(row_data)

        except (ValueError, IndexError) as e:
            print(f'Ошибка обработки строки: {e}')

    return data

def update_json_data():
    # Create directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    json_filename = 'data/nbkr.json'
    
    # Load existing data
    existing_data = []
    if os.path.exists(json_filename):
        with open(json_filename, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    
    # Get new data
    new_data = parse_nbkr_data()
    
    # Filter out header row
    new_data = [entry for entry in new_data if entry['Дата'] != 'Дата']
    
    # Add only unique entries
    unique_entries = {(entry.get("Дата"), entry.get("Мерные золотые слитки, г."), entry.get("Цена продажи, сом")) for entry in existing_data}
    
    for entry in new_data:
        key = (entry.get("Дата"), entry.get("Мерные золотые слитки, г."), entry.get("Цена продажи, сом"))
        if key not in unique_entries:
            existing_data.append(entry)
            unique_entries.add(key)
    
    # Sort by date
    existing_data.sort(key=lambda x: datetime.strptime(x['Дата'], '%d.%m.%Y'), reverse=True)
    
    # Save updated data
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
    
    print(f'Данные таблицы обновлены. Всего записей: {len(existing_data)}')
    
if __name__ == "__main__":
    update_json_data()