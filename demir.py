import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def demir(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        tables = soup.find_all('table')
        
        df_nal = pd.read_html(str(tables[0]))[0]
        df_beznal = pd.read_html(str(tables[1]))[0]
        
        df_nal.columns = ['Currency', 'Buy', 'Sell']
        df_nal = df_nal.dropna().reset_index(drop=True)
        df_nal = df_nal.rename(columns={'Currency': 'currency', 'Buy': 'buy', 'Sell': 'sell'})
        df_nal['bank_name'] = 'Демир'
        df_nal['type'] = 'Наличный'
        
        df_beznal.columns = ['Currency', 'Buy', 'Sell']
        df_beznal = df_beznal.dropna().reset_index(drop=True)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
        df_beznal = df_beznal.rename(columns={'Currency': 'currency', 'Buy': 'buy', 'Sell': 'sell'})
        df_beznal['bank_name'] = 'Демир'
        df_beznal['type'] = 'Безналичный'
        
        today_date = datetime.now().strftime('%Y-%m-%d')
        df_nal['date'] = today_date
        df_beznal['date'] = today_date
        
        df_combined = pd.concat([df_nal, df_beznal], ignore_index=True)
        
        df_combined = df_combined[['bank_name', 'type', 'currency', 'buy', 'sell', 'date']]
        
        print(df_combined)
        return df_combined
    
    except requests.RequestException as e:
        print(f"Request error: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
