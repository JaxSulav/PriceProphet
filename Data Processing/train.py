#!/usr/bin/env python
# coding: utf-8

# In[787]:


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


# In[409]:


data_path = "./data/lot41_statistical.csv"
df = pd.read_csv(data_path)
df.head(5)


# In[410]:


df.shape


# In[411]:


tfid = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfid.fit_transform(df['name'])
k_means = KMeans(n_clusters=50, random_state=0)
k_means.fit(tfidf_matrix)
df['name'] = k_means.labels_
df.head()


# ##### Binarizing return_policy, money_back, trending

# In[412]:


df['return_policy'] = df['return_policy'].apply(lambda x: 0 if 'no' in x.lower() else 1)
df['money_back'] = df['money_back'].apply(lambda x: 1 if 'yes' in x.lower() else 0)
df['trending'] = df['trending'].apply(lambda x: 1 if 'yes' in x.lower() else 0)
df.head()


# #### Dealing with Category

# In[413]:


enc = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)

df['category'] = enc.fit_transform(df[['category']]).astype(int)
kv_pair_ic = {category: i for i, category in enumerate(enc.categories_[0])}
print(kv_pair_ic)
print(len(enc.categories_[0]))
df.head()


# #### Binarizing the shipping values

# In[414]:


df.loc[~df['shipping'].astype(str).str.contains('\$'), 'shipping'] = 0
df.loc[df['shipping'].astype(str).str.contains('\$'), 'shipping'] = 1
df['shipping'] = df['shipping'].astype(float)
df.head()


# ### Dealing with seller_item_sold

# In[415]:


# For "seller_positive_feedback"
def to_numbers(short):
    if 'K' in short:
        return float(short.replace('K', '')) * 1000
    elif 'M' in short:
        return float(short.replace('M', '')) * 1000000
    else:
        return float(short)

df["seller_item_sold"] = df["seller_item_sold"].apply(to_numbers)


# ### Target Encoder for item_condition

# In[416]:


encoder = TargetEncoder()

encoder.fit(df['item_condition'], df['price_log'])
df['item_condition'] = encoder.transform(df['item_condition'])

encoder.fit(df['brand'], df['price_log'])
df['brand'] = encoder.transform(df['brand'])

encoder.fit(df['located_in'], df['price_log'])
df['located_in'] = encoder.transform(df['located_in'])

df.head()


# In[417]:


df.dtypes


# In[418]:


df.to_csv("./data/lot42_vectorized.csv", index=False)
# In[788]:


data_path = "./data/lot42_vectorized.csv"
df = pd.read_csv(data_path)
df.head(5)


# In[789]:


df.shape


# In[790]:


X = df.drop(['price', 'price_log', 'price_boxcox'], axis=1)
y = df['price_log']


# In[791]:


def calculate_cv_scores(models):
    scores = dict()
    for name, model in models:
       scores[name] = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_squared_error') 
    return scores

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model_rf = RandomForestRegressor(n_estimators = 100, random_state=42)
model_gb = GradientBoostingRegressor(alpha=0.95, learning_rate=0.1, loss="huber", max_depth=9, max_features=0.8500000000000001, min_samples_leaf=10, min_samples_split=18, n_estimators=100, subsample=0.9000000000000001)
model_xg = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, subsample=0.8, random_state=42)
model_lr = LinearRegression()

models = [
    ('Random Forest', model_rf),
    ('Gradient Boosting', model_gb),
    ('XG Boost', model_xg),
    ('Linear Regression', model_lr)
]
scores = calculate_cv_scores(models)
for key, value in scores.items():
    print(f'{key}: {value}')


# In[792]:


def train(models):
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


# In[793]:


log_scores, actual_scores = train(models)
print(log_scores)
print(actual_scores)

