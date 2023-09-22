import pandas as pd
from category_encoders import TargetEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OrdinalEncoder
from category_encoders import TargetEncoder
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error, mean_squared_log_error
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from xgboost import XGBRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import learning_curve
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import AdaBoostRegressor


data_path = "./data/lot51_cleaned.csv"
df = pd.read_csv(data_path)


tfid = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfid.fit_transform(df['name'])
k_means = KMeans(n_clusters=50, random_state=0)
k_means.fit(tfidf_matrix)
df['name'] = k_means.labels_


# label_encoder = LabelEncoder()
# df['category'] = label_encoder.fit_transform(df['category'])


encoder = TargetEncoder()

encoder.fit(df['item_condition'], df['price_log'])
df['item_condition'] = encoder.transform(df['item_condition'])

encoder.fit(df['brand'], df['price_log'])
df['brand'] = encoder.transform(df['brand'])

encoder.fit(df['located_in'], df['price_log'])
df['located_in'] = encoder.transform(df['located_in'])

X = df.drop(['price_log', 'price', 'price_boxcox', 'category'], axis=1)
# X = df.drop(['price_log'], axis=1)
y = df['price_log']



def calculate_cv_scores(models):
    scores = dict()
    for name, model in models:
       scores[name] = cross_val_score(model, X_train, 
            y_train, cv=5, scoring='neg_mean_squared_error') 
    return scores

X_train, X_test, y_train, y_test = train_test_split(X, y, 
            test_size=0.2, random_state=42)
model_rf = RandomForestRegressor(n_estimators = 100, 
            random_state=42)
model_gb = GradientBoostingRegressor(alpha=0.95, 
            learning_rate=0.1, loss="huber", max_depth=9, 
            max_features=0.8500000000000001, min_samples_leaf=10, 
            min_samples_split=18, n_estimators=100, 
            subsample=0.9000000000000001)
model_xg = XGBRegressor(n_estimators=100, learning_rate=0.1, 
            max_depth=5, subsample=0.8, random_state=42)
model_lr = LinearRegression()
model_ada = AdaBoostRegressor(base_estimator=LinearRegression(), n_estimators = 50, learning_rate = 0.001, loss = 'linear',
    random_state = 42)
ridge_model = Ridge(alpha=1.0, random_state=42)
lasso_model = Lasso(alpha=0.5, max_iter=10000, tol=0.0001)


models = [
    ('Random Forest', model_rf),
    ('Gradient Boosting', model_gb),
    ('XG Boost', model_xg),
    ('ADA Boost', model_ada),
]

def train_test(models):
    scores_log = dict()
    scores_actual = dict()
    actual_vs_predicted = dict()
    for name, model in models:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        test_rmsle = np.sqrt(mean_squared_log_error(y_test, y_pred))
        scores_log[name] = test_rmsle
        actual_vs_predicted[name] = list(zip(y_test[:10], y_pred[:10], np.expm1(y_test[:10]), np.expm1(y_pred[:10])))
        y_test_actual = np.expm1(y_test)
        y_pred_actual = np.expm1(y_pred)
       
        test_rmsle_actual = np.sqrt(mean_squared_log_error(y_test_actual, y_pred_actual))
        scores_actual[name] = test_rmsle_actual
    return scores_log, scores_actual, actual_vs_predicted

log_scores, actual_scores, a = train_test(models)
df = pd.DataFrame(a["Gradient Boosting"], columns=['Actual Log', 'Predicted Log', "Actual Price", "Predicted Price"])

print("SCORING FOR LOGGED PRICE:")
for k, v in log_scores.items():
    print(f'{k}: {v}')
print("\n")
print("SCORING FOR ACTUAL PRICE:")
for k, v in actual_scores.items():
    print(f'{k}: {v}')

print(df.head(10))