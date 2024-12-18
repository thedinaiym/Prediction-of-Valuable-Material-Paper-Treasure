from core import *
from load import *
from train import *
from predict_scale import *
from evaluate import *

def plot_actual_vs_predicted(df, target_column, prediction, next_date, model_name):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df.index, df[target_column], label='Фактические значения', color='blue')
    ax.plot(next_date, prediction, 'ro', label=f'Предсказание ({model_name})')
    ax.set_xlabel('Дата')
    ax.set_ylabel(target_column)
    ax.set_title(f'Фактические значения и предсказание ({model_name})')
    ax.legend()
    st.pyplot(fig)

def plot_future_predictions(df_with_target, target_column, model, feature_scaler, target_scaler, future_steps=7):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_with_target.index, df_with_target[target_column], label='Фактические значения', color='blue')
    
    future_dates = [df_with_target.index[-1] + timedelta(days=i+1) for i in range(future_steps)]
    future_predictions = []
    current_data = df_with_target.drop('Target', axis=1).copy()  
    
    for _ in range(future_steps):
        current_data_scaled = feature_scaler.transform(current_data.tail(1))
        current_data_scaled_df = pd.DataFrame(current_data_scaled, columns=current_data.columns, index=current_data.tail(1).index)
        
        if isinstance(model, nn.Module):  
            pred = predict_pytorch_model(model, current_data_scaled_df, target_scaler)[0]
        else:
            pred_scaled = model.predict(current_data_scaled_df)[0]
            pred = target_scaler.inverse_transform(np.array([[pred_scaled]]))[0][0]
        future_predictions.append(pred)
        new_row = current_data.tail(1).copy()
        new_row[target_column] = pred
        current_data = pd.concat([current_data, new_row], ignore_index=True)
    
    ax.plot(future_dates, future_predictions, 'ro-', label='Прогнозы')
    ax.set_xlabel('Дата')
    ax.set_ylabel(target_column)
    ax.set_title(f'Прогноз на {future_steps} дней вперед')
    ax.legend()
    st.pyplot(fig)

def plot_catboost_feature_importance(model, feature_names):
    try:
        feature_importances = model.get_feature_importance(type='FeatureImportance')
        
        fi_df = pd.DataFrame({
            'Feature': feature_names,
            'Importance': feature_importances
        }).sort_values(by='Importance', ascending=False)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(x='Importance', y='Feature', data=fi_df, palette='viridis', ax=ax)
        ax.set_title('Важность признаков для CatBoost')
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Ошибка при получении важности признаков для CatBoost: {e}")

def plot_time_series(df, columns, title):
    fig = px.line(df, x=df.index, y=columns, title=title)
    fig.update_layout(xaxis_title='Дата', yaxis_title='Цена', legend_title='Признаки')
    st.plotly_chart(fig, use_container_width=True)

def plot_distribution(df, columns, title):
    fig = plt.figure(figsize=(10, 6))
    for column in columns:
        sns.histplot(df[column], kde=True, label=column, alpha=0.6)
    plt.title(title)
    plt.legend()
    st.pyplot(fig)

def plot_correlation_matrix(df, title):
    corr = df.corr()
    fig, ax = plt.subplots(figsize=(15, 12))
    sns.heatmap(corr, annot=False, cmap='coolwarm', ax=ax)
    ax.set_title(title)
    st.pyplot(fig)
