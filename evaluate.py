from core import *
from load import *
from train import *
from predict_scale import *

def evaluate_models(trained_models, X_test, y_test, feature_scaler, target_scaler):
    X_test_scaled = feature_scaler.transform(X_test)
    X_test_scaled_df = pd.DataFrame(X_test_scaled, columns=X_test.columns, index=X_test.index)
    
    y_test_scaled = target_scaler.transform(y_test.values.reshape(-1, 1)).flatten()
    
    metrics_list = []
    
    for name, model in trained_models.items():
        try:
            if name == 'FNN_PyTorch':
                y_pred = predict_pytorch_model(model, X_test_scaled_df, target_scaler)
                y_true = y_test.values
            else:
                y_pred_scaled = model.predict(X_test_scaled_df)
                y_pred = target_scaler.inverse_transform(y_pred_scaled.reshape(-1, 1)).flatten()
                y_true = y_test.values
            mae = mean_absolute_error(y_true, y_pred)
            mse = mean_squared_error(y_true, y_pred)
            rmse = np.sqrt(mse)
            r2 = r2_score(y_true, y_pred)
            metrics_list.append({
                'Модель': name,
                'MAE': mae,
                'MSE': mse,
                'RMSE': rmse,
                'R2': r2
            })
        except Exception as e:
            st.error(f"Ошибка при оценке модели {name}: {e}")
    
    metrics_df = pd.DataFrame(metrics_list)
    return metrics_df
