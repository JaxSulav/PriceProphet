#!/usr/bin/env python
# coding: utf-8

# In[408]:


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

