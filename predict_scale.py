from core import *
from load import *
from train import *


def load_models_and_scalers():
    try:
        sk_models_path = os.path.join(MODEL_DIR, 'trained_sk_models.joblib')
        pytorch_model_path = os.path.join(MODEL_DIR, 'trained_pytorch_model.pth')
        feature_scaler_path = os.path.join(MODEL_DIR, 'feature_scaler.joblib')
        target_scaler_path = os.path.join(MODEL_DIR, 'target_scaler.joblib')
        
        st.write("Список файлов в директории models:")
        if os.path.exists(MODEL_DIR):
            st.write(os.listdir(MODEL_DIR))
        else:
            st.write("Директория models не существует.")
            return None, None, None
        
        sk_models = joblib.load(sk_models_path)
        st.write("Scikit-learn модели загружены успешно.")
        
        if os.path.exists(pytorch_model_path):
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            if 'Случайный лес' in sk_models:
                input_dim = sk_models['Случайный лес'].n_features_in_
            else:
                input_dim = next(iter(sk_models.values())).n_features_in_
            
            fnn_model = FNNRegressor(input_dim).to(device)
            fnn_model.load_state_dict(torch.load(pytorch_model_path, map_location=device))
            sk_models['FNN_PyTorch'] = fnn_model
            st.write("Модель FNN_PyTorch загружена успешно.")
        else:
            st.warning(f"Файл '{pytorch_model_path}' не найден. Модель FNN_PyTorch не загружена.")
        
        feature_scaler = joblib.load(feature_scaler_path)
        target_scaler = joblib.load(target_scaler_path)
        st.write("Масштабировщики загружены успешно.")
        
        return sk_models, feature_scaler, target_scaler
    except FileNotFoundError:
        st.warning("Файлы моделей или масштабировщиков не найдены.")
        return None, None, None
    except Exception as e:
        st.error(f"Ошибка при загрузке моделей и масштабировщиков: {e}")
        return None, None, None

def train_models_cached(X_train, y_train):
    feature_scaler = StandardScaler()
    target_scaler = StandardScaler()
    models, X_train_scaled_df = train_models(X_train, y_train, feature_scaler, target_scaler)
    return models, feature_scaler, target_scaler
