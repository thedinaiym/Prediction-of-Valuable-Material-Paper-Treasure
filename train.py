from core import *
from load import *

def train_pytorch_model(X_train, y_train, input_dim, epochs=100, learning_rate=0.001, patience=20):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = FNNRegressor(input_dim).to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32).to(device)
    y_train_tensor = torch.tensor(y_train, dtype=torch.float32).view(-1, 1).to(device)
    
    best_loss = float('inf')
    patience_counter = 0
    
    model.train()
    for epoch in range(epochs):
        optimizer.zero_grad()
        outputs = model(X_train_tensor)
        loss = criterion(outputs, y_train_tensor)
        loss.backward()
        optimizer.step()
        
        if loss.item() < best_loss:
            best_loss = loss.item()
            patience_counter = 0
        else:
            patience_counter += 1
        
        if (epoch+1) % 20 == 0:
            st.write(f"Epoch [{epoch+1}/{epochs}], Loss: {loss.item():.4f}")
        
        if patience_counter >= patience:
            st.write(f"Early stopping at epoch {epoch+1}")
            break
    
    return model

def predict_pytorch_model(model, X, target_scaler):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.eval()
    with torch.no_grad():
        X_tensor = torch.tensor(X.values, dtype=torch.float32).to(device)
        predictions = model(X_tensor).cpu().numpy().flatten()
    predictions = target_scaler.inverse_transform(predictions.reshape(-1, 1)).flatten()
    return predictions

def train_models(X_train, y_train, feature_scaler, target_scaler):
    X_train_scaled = feature_scaler.fit_transform(X_train)
    y_train_scaled = target_scaler.fit_transform(y_train.values.reshape(-1, 1)).flatten()
    
    X_train_scaled_df = pd.DataFrame(X_train_scaled, columns=X_train.columns, index=X_train.index)
    
    models = {
        'Случайный лес': RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
        'XGBoost': xgb.XGBRegressor(n_estimators=100, random_state=42, objective='reg:squarederror'),
        'CatBoost': CatBoostRegressor(n_estimators=100, random_state=42, silent=True),
        'LightGBM': lgb.LGBMRegressor(n_estimators=100, random_state=42)
    }
    
    trained_models = {}
    for name, model in models.items():
        try:
            st.write(f"Обучение модели: {name}")
            model.fit(X_train_scaled_df, y_train_scaled)
            trained_models[name] = model
            st.write(f"Модель {name} обучена успешно.")
        except Exception as e:
            st.error(f"Ошибка при обучении модели {name}: {e}")
    
    try:
        input_dim = X_train_scaled_df.shape[1]
        st.write("Обучение модели FNN на PyTorch...")
        fnn_model = train_pytorch_model(X_train_scaled_df, y_train_scaled, input_dim, epochs=200, learning_rate=0.001)
        trained_models['FNN_PyTorch'] = fnn_model
        st.write("Модель FNN_PyTorch обучена успешно.")
    except Exception as e:
        st.error(f"Ошибка при обучении модели FNN_PyTorch: {e}")
    
    feature_scaler_path = os.path.join(MODEL_DIR, 'feature_scaler.joblib')
    target_scaler_path = os.path.join(MODEL_DIR, 'target_scaler.joblib')
    joblib.dump(feature_scaler, feature_scaler_path)
    joblib.dump(target_scaler, target_scaler_path)
    st.write("Масштабировщики сохранены успешно.")
    
    sk_models_path = os.path.join(MODEL_DIR, 'trained_sk_models.joblib')
    joblib.dump({name: model for name, model in trained_models.items() if name != 'FNN_PyTorch'}, sk_models_path)
    st.write("Scikit-learn модели сохранены успешно.")
    
    if 'FNN_PyTorch' in trained_models:
        pytorch_model_path = os.path.join(MODEL_DIR, 'trained_pytorch_model.pth')
        torch.save(trained_models['FNN_PyTorch'].state_dict(), pytorch_model_path)
        st.write("Модель FNN_PyTorch сохранена успешно.")
    
    return trained_models, X_train_scaled_df
