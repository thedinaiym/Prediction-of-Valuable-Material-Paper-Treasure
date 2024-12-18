import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
from demir import demir
from mbank import mbank
from optima import optima


def main():
    demir_url = 'https://demirbank.kg/ru'
    mbank_url = 'https://mbank.kg/'
    optima_url = 'https://www.optimabank.kg/index.php?option=com_nbrates&view=default&lang=ru'

    demir_df = demir(demir_url)
    mbank_df = mbank(mbank_url)
    optima_df = optima(optima_url) # u can give two variables (url = url, dates = [list of date]) default is current date

    demir_df.rename(columns={'currency': 'Валюта', 'buy': 'Покупка', 'sell': 'Продажа', 'date': 'Дата', 'bank_name': 'Банк', 'type': 'Курс'}, inplace=True)
    mbank_df.rename(columns={'currency': 'Валюта', 'buy': 'Покупка', 'sell': 'Продажа', 'date': 'Дата', 'bank_name': 'Банк', 'type': 'Курс'}, inplace=True)
    optima_df.rename(columns={'currency': 'Валюта', 'buy': 'Покупка', 'sell': 'Продажа', 'date': 'Дата', 'bank_name': 'Банк', 'type': 'Курс'}, inplace=True)

    combined_df = pd.concat([demir_df, mbank_df, optima_df], ignore_index=True)
 
    today_date = datetime.now().strftime('%Y-%m-%d') 
    filename = f'combined_data_{today_date}.csv'
    combined_df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

if __name__ == '__main__':
    main()
