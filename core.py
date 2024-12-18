import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
import numpy as np
import xgboost as xgb
from catboost import CatBoostRegressor
import lightgbm as lgb
import torch
import torch.nn as nn
import torch.optim as optim
import os

st.set_page_config(page_title="USD Безналичные Предсказание", layout="wide")

MODEL_DIR = os.path.join(os.getcwd(), 'models')
os.makedirs(MODEL_DIR, exist_ok=True)
