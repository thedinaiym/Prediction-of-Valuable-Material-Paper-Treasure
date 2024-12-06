import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def optima(url, dates=None):
    if dates is None:
        dates = [datetime.now().strftime('%Y-%m-%d')]

    all_data = []

    for date in dates:
        form_data = {
            'option': 'com_nbrates',
            'view': 'default',
            'Itemid': '196',
            'mycalendar': date
        }

        response = requests.post(url, data=form_data)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        cash_tab = soup.find('div', {'id': 'tab-cash'})
        rows = cash_tab.find_all('div', class_='row0') + cash_tab.find_all('div', class_='row1')

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
        rows = cashless_tab.find_all('div', class_='row0') + cashless_tab.find_all('div', class_='row1')

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
