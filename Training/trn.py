import pandas as pd
from category_encoders import TargetEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_log_error
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
import joblib

data_path = "./data/lot51_cleaned.csv"
df = pd.read_csv(data_path)

tfid = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfid.fit_transform(df['name'])
joblib.dump(tfid, './models/tfidf_vectorizer.joblib')

k_means = KMeans(n_clusters=50, random_state=0)
k_means.fit(tfidf_matrix)
joblib.dump(k_means, './models/k_means.joblib')

df['name'] = k_means.labels_

encoder_item_condition = TargetEncoder()
encoder_item_condition.fit(df['item_condition'], df['price_log'])
df['item_condition'] = encoder_item_condition.transform(df['item_condition'])
joblib.dump(encoder_item_condition, './models/target_encoder_item_condition.joblib')

encoder_brand = TargetEncoder()
encoder_brand.fit(df['brand'], df['price_log'])
df['brand'] = encoder_brand.transform(df['brand'])
joblib.dump(encoder_brand, './models/target_encoder_brand.joblib')

encoder_located_in = TargetEncoder()
encoder_located_in.fit(df['located_in'], df['price_log'])
df['located_in'] = encoder_located_in.transform(df['located_in'])
joblib.dump(encoder_located_in, './models/target_encoder_located_in.joblib')

X = df.drop(['price_log', 'price', 'price_boxcox', 'category'], axis=1)
y = df['price_log']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model_gb = GradientBoostingRegressor(alpha=0.95, learning_rate=0.1, loss="huber", max_depth=9, max_features=0.8500000000000001, min_samples_leaf=10, min_samples_split=18, n_estimators=100, subsample=0.9000000000000001)

model_gb.fit(X_train, y_train)
joblib.dump(model_gb, './models/gradient_boosting_model.joblib')
