from core import *

@st.cache_data
def load_and_prepare_data(file_path):
    try:
        
        df = pd.read_csv(file_path, index_col='Дата', parse_dates=['Дата'])
    except ValueError:
        df = pd.read_csv(file_path, parse_dates=['Дата'])
        df['Дата'] = pd.to_datetime(df['Дата'], format='%Y-%m-%d', errors='coerce')
        df = df.sort_values('Дата')
        df.set_index('Дата', inplace=True)
    
    if 'Unnamed: 0' in df.columns:
        df = df.drop('Unnamed: 0', axis=1)
    
    if df.index.isnull().any():
        st.error("Некоторые значения в столбце 'Дата' не удалось преобразовать в datetime.")
        return None
    
    df = df.ffill()
    
    return df

def get_features_and_target(df, target_column='Optima_Продажа_USD_Безналичные'):
    df = df.copy()
    df['Target'] = df[target_column].shift(-1)  
    df = df.dropna() 
    X = df.drop(['Target'], axis=1)
    y = df['Target']
    return X, y, df  

class FNNRegressor(nn.Module):
    def __init__(self, input_dim):
        super(FNNRegressor, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
    def forward(self, x):
        return self.network(x)
