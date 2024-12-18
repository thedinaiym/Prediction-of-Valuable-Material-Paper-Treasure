import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import os

def optima(url, date):
    form_data = {
        'option': 'com_nbrates',
        'view': 'default',
        'Itemid': '196',
        'mycalendar': date
    }
    
    all_data = []
    try:
        response = requests.post(url, data=form_data)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        cash_tab = soup.find('div', {'id': 'tab-cash'})
        rows = cash_tab.find_all('div', class_=['row0', 'row1'])
        
        for row in rows:
            currency = row.find('div', class_='code').text.strip()
            buy_rate = row.find('div', class_='rate buy').text.strip()
            sell_rate = row.find('div', class_='rate sell').text.strip()
            all_data.append({
                'date': date,
                'currency': currency,
                'buy': buy_rate,
                'sell': sell_rate,
                'type': 'Наличные'
            })
        
        cashless_tab = soup.find('div', {'id': 'tab-cashless'})
        rows = cashless_tab.find_all('div', class_=['row0', 'row1'])
        
        for row in rows:
            currency = row.find('div', class_='code').text.strip()
            buy_rate = row.find('div', class_='rate buy').text.strip()
            sell_rate = row.find('div', class_='rate sell').text.strip()
            all_data.append({
                'date': date,
                'currency': currency,
                'buy': buy_rate,
                'sell': sell_rate,
                'type': 'Безналичные'
            })
        
        df = pd.DataFrame(all_data)
        df['bank_name'] = 'Оптима'
        return df
    
    except Exception as e:
        print(f"Error fetching data for {date}: {e}")
        return pd.DataFrame()

def update_exchange_rates():
    """
    Update exchange rates daily, preserving continuous index
    """
    optima_url = 'https://www.optimabank.kg/index.php?option=com_nbrates&view=default&lang=ru'
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    os.makedirs('data', exist_ok=True)
    filename = 'data/optima.csv'
    
    if os.path.exists(filename):
        existing_df = pd.read_csv(filename)
        
        if not existing_df[existing_df['Дата'] == today].empty:
            print(f"Data for {today} already exists. Skipping.")
            return
        
        last_index = existing_df.index.max()
    else:
        existing_df = pd.DataFrame(columns=['Индекс', 'Дата', 'Валюта', 'Покупка', 'Продажа', 'Курс', 'Банк'])
        last_index = -1
    
    new_df = optima(optima_url, today)
    
    if not new_df.empty:
        new_df.rename(columns={
            'currency': 'Валюта', 
            'buy': 'Покупка', 
            'sell': 'Продажа', 
            'date': 'Дата', 
            'bank_name': 'Банк', 
            'type': 'Курс'
        }, inplace=True)
        
        new_df['Индекс'] = range(last_index + 1, last_index + len(new_df) + 1)
        
        new_df = new_df[['Индекс', 'Дата', 'Валюта', 'Покупка', 'Продажа', 'Курс', 'Банк']]
        
        updated_df = pd.concat([existing_df, new_df], ignore_index=False)
        
        updated_df.to_csv(filename, index=False)
        print(f"Data for {today} added to {filename}")
    else:
        print("No data fetched today.")

def main():
    """Main function to run the script"""
    update_exchange_rates()

if __name__ == '__main__':
    main()