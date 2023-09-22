import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import joblib

from category_encoders import TargetEncoder
from sklearn.cluster import KMeans
from sklearn.ensemble import AdaBoostRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_squared_log_error
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor
from xgboost import XGBRegressor


def load_data(path):
    """Loads the data from the given path"""
    return pd.read_csv(path)


def vectorize_and_encode(df):
    """Applies TF-IDF vectorization and encodes the categorical features"""
    # Vectorize 'name' using TF-IDF
    tfid = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfid.fit_transform(df['name'])

    # Cluster 'name' using K-Means
    k_means = KMeans(n_clusters=50, random_state=0)
    k_means.fit(tfidf_matrix)
    df['name'] = k_means.labels_

    # Label encode 'category'
    label_encoder = LabelEncoder()
    df['category'] = label_encoder.fit_transform(df['category'])

    # Target encode 'item_condition', 'brand', and 'located_in'
    encoder = TargetEncoder()
    for col in ['item_condition', 'brand', 'located_in']:
        encoder.fit(df[col], df['price_log'])
        df[col] = encoder.transform(df[col])

    return df


def split_data(df):
    """Splits the data into training and test sets"""
    X = df.drop(['price_log', 'price', 'price_boxcox'], axis=1)
    y = df['price_log']
    return train_test_split(X, y, test_size=0.2, random_state=42)


def get_models():
    """Returns a list of models to be trained"""
    model_rf = RandomForestRegressor(n_estimators=100, random_state=42)
    model_gb = GradientBoostingRegressor(alpha=0.95, learning_rate=0.1, loss="huber", max_depth=9, 
                                         max_features=0.8500000000000001, min_samples_leaf=10, 
                                         min_samples_split=18, n_estimators=100, 
                                         subsample=0.9000000000000001)
    model_xg = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, subsample=0.8, 
                            random_state=42)
    model_lr = LinearRegression()
    model_ada = AdaBoostRegressor(base_estimator=LinearRegression(), n_estimators=50, 
                                  learning_rate=0.001, loss='linear', random_state=42)

    return [
        ('Random Forest', model_rf),
        ('Gradient Boosting', model_gb),
        ('XG Boost', model_xg),
        ('ADA Boost', model_ada),
    ]


def calculate_cv_scores(models, X_train, y_train):
    """Calculates cross-validation scores for each model"""
    scores = {}
    for name, model in models:
        scores[name] = cross_val_score(model, X_train, y_train, cv=5, 
                                       scoring='neg_mean_squared_error')
    return scores


def train_test(models, X_train, X_test, y_train, y_test):
    """Trains each model and calculates the RMSLE for logged and actual prices"""
    scores_log = {}
    scores_actual = {}
    actual_vs_predicted = {}
    trained_models = {}
    for name, model in models:
        model.fit(X_train, y_train)
        trained_models[name] = model
        y_pred = model.predict(X_test)
        test_rmsle = np.sqrt(mean_squared_log_error(y_test, y_pred))
        scores_log[name] = test_rmsle
        actual_vs_predicted[name] = list(zip(y_test[:10], y_pred[:10], 
                                             np.expm1(y_test[:10]), np.expm1(y_pred[:10])))
        y_test_actual = np.expm1(y_test)
        y_pred_actual = np.expm1(y_pred)

        test_rmsle_actual = np.sqrt(mean_squared_log_error(y_test_actual, y_pred_actual))
        scores_actual[name] = test_rmsle_actual

    return scores_log, scores_actual, actual_vs_predicted, trained_models


def print_scores(scores_log, scores_actual):
    """Prints the RMSLE scores for logged and actual prices"""
    print("SCORING FOR LOGGED PRICE:")
    for k, v in scores_log.items():
        print(f'{k}: {v}')
    print("\n")
    print("SCORING FOR ACTUAL PRICE:")
    for k, v in scores_actual.items():
        print(f'{k}: {v}')


def save_models(models, dir_path):
    """Saves trained models to the given directory"""
    for name, model in models.items():
        joblib.dump(model, f'{dir_path}/{name.replace(" ", "_").lower()}.joblib')


def main():
    data_path = "./data/lot51_cleaned.csv"
    models_dir_path = "./trained_models"
    df = load_data(data_path)
    df = vectorize_and_encode(df)
    X_train, X_test, y_train, y_test = split_data(df)
    models = get_models()
    scores_log, scores_actual, actual_vs_predicted, trained_models = train_test(models, X_train, X_test, 
                                                                                y_train, y_test)
    print_scores(scores_log, scores_actual)

    save_models(trained_models, models_dir_path)

    df = pd.DataFrame(actual_vs_predicted["Gradient Boosting"], 
                      columns=['Actual Log', 'Predicted Log', "Actual Price", "Predicted Price"])
    print(df.head(10))


if __name__ == "__main__":
    main()
