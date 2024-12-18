import pandas as pd
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import json 

def mbank(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    script_tag = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
    
    if not script_tag:
        print("Ошибка: не найден тег <script> с id '__NEXT_DATA__'")
        return pd.DataFrame()
    
    try:
        data = json.loads(script_tag.string)
    except json.JSONDecodeError as e:
        print(f"Ошибка декодирования JSON: {e}")
        return pd.DataFrame()

    exchange_info = data['props']['pageProps']['mainPage']['exchange']
    cash_exchange = exchange_info.get('cash_exchange', [])

    cash_exchange_dfs = []
    for item in cash_exchange:
        df = pd.DataFrame(item['values'])
        df['type'] = item['operation_type']
        cash_exchange_dfs.append(df)
    
    cash_exchange_df = pd.concat(cash_exchange_dfs, ignore_index=True)
    cash_exchange_df['bank_name'] = 'Кыргызстан'
    today_date = datetime.now().strftime('%Y-%m-%d')
    cash_exchange_df['date'] = today_date

    cash_exchange_df['type'] = cash_exchange_df['type'].replace(
        {'Для операций с наличными': 'Наличный', 'Безналичные курсы': 'Безналичный'}
    )

    columns_to_drop = ['id', 'nbkr']
    cash_exchange_df = cash_exchange_df.drop(columns=[col for col in columns_to_drop if col in cash_exchange_df.columns])

    return cash_exchange_df
