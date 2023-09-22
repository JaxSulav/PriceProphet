import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OrdinalEncoder
from category_encoders import TargetEncoder
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_log_error
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
import time

def load_data(data_path):
    df = pd.read_csv(data_path)
    if df.empty:
        print("Error: The data file is empty.")
        return None
    return df

def preprocess_data(df):
    tifd = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tifd.fit_transform(df['name'])
    k_means = KMeans(n_clusters=50, random_state=0, n_init="auto")
    k_means.fit(tfidf_matrix)
    df['name'] = k_means.labels_

    df['return_policy'] = df['return_policy'].apply(lambda x: 0 if 'no' in x.lower() else 1)
    df['money_back'] = df['money_back'].apply(lambda x: 1 if 'yes' in x.lower() else 0)
    df['trending'] = df['trending'].apply(lambda x: 1 if 'yes' in x.lower() else 0)
    
    enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    df['category'] = enc.fit_transform(df[['category']]).astype(int)
    
    df.loc[~df['shipping'].astype(str).str.contains('\$'), 'shipping'] = 0
    df.loc[df['shipping'].astype(str).str.contains('\$'), 'shipping'] = 1
    df['shipping'] = df['shipping'].astype(float)
    
    df["seller_item_sold"] = df["seller_item_sold"].apply(to_numbers)
    
    encoder = TargetEncoder()
    encoder.fit(df['item_condition'], df['price_log'])
    df['item_condition'] = encoder.transform(df['item_condition'])
    encoder.fit(df['brand'], df['price_log'])
    df['brand'] = encoder.transform(df['brand'])
    encoder.fit(df['located_in'], df['price_log'])
    df['located_in'] = encoder.transform(df['located_in'])
   
    return df

def to_numbers(val):
    try:
        if 'K' in val:
            return float(val.replace('K', '')) * 1000
        elif 'M' in val:
            return float(val.replace('M', '')) * 1000000
        else:
            return float(val)
    except ValueError:
        print(f"Error: Unable to convert {val}")
        return None

def split_data(df):
    X = df.drop(['price', 'price_log', 'price_boxcox'], axis=1)
    y = df['price_log']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    return X_train, X_test, y_train, y_test

def calculate_cv_scores(models, X_train, y_train):
    scores = dict()
    for name, model in models:
       scores[name] = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_squared_error') 
    return scores

def train(models, X_train, y_train, X_test, y_test):
    scores_log = dict()
    scores_actual = dict()
    for name, model in models:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        test_rmsle = np.sqrt(mean_squared_log_error(y_test, y_pred))
        scores_log[name] = test_rmsle

        y_test_actual = np.expm1(y_test)
        y_pred_actual = np.expm1(y_pred)
        test_rmsle_actual = np.sqrt(mean_squared_log_error(y_test_actual, y_pred_actual))
        scores_actual[name] = test_rmsle_actual
    return scores_log, scores_actual

def train_models(models, X_train, y_train, X_test, y_test):
    models_trained = list()
    for name, model in models:
        model.fit(X_train, y_train)
        models_trained.append((name, model))
    return models_trained

def test_timer(models, df):
    X = df.drop(['price', 'price_log', 'price_boxcox'], axis=1)
    y = df['price_log']
    for name, model in models:
        start = time.perf_counter()
        y_pred = model.predict(X)
        gg = np.exp(y_pred)
        time_taken = time.perf_counter() - start
        print(f"Time take for {name} prediction for {df.shape[0]} items is {time_taken}")



def main():
    data_path = "../data/lot41_statistical.csv"
    df = load_data(data_path)
    df = preprocess_data(df)
    X_train, X_test, y_train, y_test = split_data(df)
    
    model_rf = RandomForestRegressor(n_estimators = 100, random_state=42)
    model_gb = GradientBoostingRegressor(alpha=0.95, learning_rate=0.1, loss="huber", max_depth=9, max_features=0.8500000000000001, min_samples_leaf=10, min_samples_split=18, n_estimators=100, subsample=0.9000000000000001)
    model_xg = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, subsample=0.8, random_state=42)
    model_lr = LinearRegression()
    models = [('Random Forest', model_rf), ('Gradient Boosting', model_gb), ('XG Boost', model_xg), ('Linear Regression', model_lr)]
    
    scores = calculate_cv_scores(models, X_train, y_train)
    for key, value in scores.items():
        print(f'{key}: {value}')
    
    log_scores, actual_scores = train(models, X_train, y_train, X_test, y_test)
    
    # print(log_scores)
    # print(actual_scores)

    df = load_data("../data/lot42_vectorized.csv")
    test_timer(train_models(models, X_train, y_train, X_test, y_test), df)
    
    # log_scores, actual_scores = train(models, X_train, y_train, X_test, y_test)
    
    # # print(log_scores)
    # # print(actual_scores)

    

main()