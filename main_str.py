from core import *
from load import *
from train import *
from predict_scale import *
from evaluate import *
from visual import *

def main():
    st.title("Ежедневное предсказание Optima Продажа USD Безналичные")
    DATA_PATH = 'data//synthetic_data.csv'
    df = load_and_prepare_data(DATA_PATH)
    if df is None:
        return
    
    target_column = 'Optima_Продажа_USD_Безналичные'
    X, y, df_with_target = get_features_and_target(df, target_column)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    
    trained_models, feature_scaler, target_scaler = load_models_and_scalers()
    if trained_models is None:
        trained_models, feature_scaler, target_scaler = train_models_cached(X_train, y_train)
    
    if trained_models is None or feature_scaler is None or target_scaler is None:
        st.error("Не удалось загрузить или обучить модели и масштабировщики.")
        return
    
    st.sidebar.header("Контрольные Пункты")
    st.sidebar.write("Доступные модели:")
    st.sidebar.write(list(trained_models.keys()))
    
    st.header("Визуализация Данных")
    
    st.subheader("Временные Ряды Цен Kyrgyz Altyn Slitok")
    kyrgyz_columns = [col for col in df.columns if 'Kyrgyz_Altyn_Slitok' in col]
    plot_time_series(df, kyrgyz_columns, "Цены Kyrgyz Altyn Slitok")
    
    st.subheader("Временные Ряды Цен NBKR Slitok")
    nbkr_columns = [col for col in df.columns if 'NBKR_Slitok' in col]
    plot_time_series(df, nbkr_columns, "Цены NBKR Slitok")
    
    st.subheader("Временные Ряды Цен Optima Покупка и Продажа")
    optima_columns = [col for col in df.columns if 'Optima' in col]
    plot_time_series(df, optima_columns, "Цены Optima Покупка и Продажа")
    
    st.subheader("Разница Цен")
    diff_columns = ['Цена_разница']
    plot_time_series(df, diff_columns, "Разница Цен")
    
    st.subheader("Распределение Цен")
    selected_columns = st.multiselect("Выберите столбцы для отображения распределения:", df.columns.tolist(), default=['Optima_Продажа_USD_Безналичные'])
    if selected_columns:
        plot_distribution(df, selected_columns, "Распределение Выбранных Цен")
    
    st.subheader("Корреляционная Матрица")
    plot_correlation_matrix(df, "Корреляционная Матрица Цен")
    
    st.header("Оценка Моделей")
    metrics = evaluate_models(trained_models, X_test, y_test, feature_scaler, target_scaler)
    
    st.subheader("Метрики Моделей")
    st.write(metrics)
    
    if not metrics.empty:
        best_model_name = metrics.loc[metrics['MAE'].idxmin(), 'Модель']
        best_model = trained_models[best_model_name]
        st.write(f"**Лучшая модель по MAE:** {best_model_name}")
        
        last_data = X.tail(1)
        if best_model_name == 'FNN_PyTorch':
            last_data_scaled = feature_scaler.transform(last_data)
            last_data_scaled_df = pd.DataFrame(last_data_scaled, columns=last_data.columns, index=last_data.index)
            prediction = predict_pytorch_model(best_model, last_data_scaled_df, target_scaler)[0]
        else:
            last_data_scaled = feature_scaler.transform(last_data)
            last_data_scaled_df = pd.DataFrame(last_data_scaled, columns=X.columns, index=last_data.index)
            prediction_scaled = best_model.predict(last_data_scaled_df)[0]
            prediction = target_scaler.inverse_transform(np.array([[prediction_scaled]]))[0][0]
        next_date = df.index[-1] + timedelta(days=1)
        
        st.subheader("Предсказание на Следующий День")
        st.write(f"Предсказанное значение {target_column} на {next_date.date()}: {prediction:.2f}")
        
        st.subheader("График Фактических Значений и Предсказания")
        plot_actual_vs_predicted(df_with_target, target_column, prediction, next_date, best_model_name)
        
        st.subheader("Прогноз на Будущие Дни")
        plot_future_predictions(df_with_target, target_column, best_model, feature_scaler, target_scaler, future_steps=7)
    
    st.header("Визуализация Результатов для Всех Моделей")
    for name, model in trained_models.items():
        st.subheader(f"Модель: {name}")
        try:
            last_data = X.tail(1)
            if name == 'FNN_PyTorch':
                last_data_scaled = feature_scaler.transform(last_data)
                last_data_scaled_df = pd.DataFrame(last_data_scaled, columns=last_data.columns, index=last_data.index)
                pred = predict_pytorch_model(model, last_data_scaled_df, target_scaler)[0]
            else:
                last_data_scaled = feature_scaler.transform(last_data)
                last_data_scaled_df = pd.DataFrame(last_data_scaled, columns=X.columns, index=last_data.index)
                pred_scaled = model.predict(last_data_scaled_df)[0]
                pred = target_scaler.inverse_transform(np.array([[pred_scaled]]))[0][0]
            
            plot_actual_vs_predicted(df_with_target, target_column, pred, next_date, name)
            plot_future_predictions(df_with_target, target_column, model, feature_scaler, target_scaler, future_steps=7)
        except Exception as e:
            st.error(f"Ошибка при прогнозировании или визуализации модели {name}: {e}")
    
    st.header("Сравнение Метрик Моделей")
    fig, ax = plt.subplots(figsize=(12, 6))
    metrics_melted = metrics.melt(id_vars="Модель", var_name="Метрика", value_name="Значение")
    
    for metric in ['MAE', 'MSE', 'RMSE', 'R2']:
        subset = metrics_melted[metrics_melted['Метрика'] == metric]
        ax.bar(subset['Модель'] + f'_{metric}', subset['Значение'], label=metric)
    
    ax.set_ylabel('Значение Метрики')
    ax.set_title('Сравнение Метрик Моделей')
    ax.legend()
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    st.header("Важность Признаков для CatBoost")
    if 'CatBoost' in trained_models:
        catboost_model = trained_models['CatBoost']
        feature_names = X_train.columns.tolist()
        plot_catboost_feature_importance(catboost_model, feature_names)
    else:
        st.write("Модель CatBoost не была обучена.")

if __name__ == '__main__':
    main()
