import pandas as pd
import numpy as np
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
from category_encoders import TargetEncoder

def predict_price(new_data):
    tfid = joblib.load('./models/tfidf_vectorizer.joblib')
    k_means = joblib.load('./models/k_means.joblib')
    encoder_item_condition = joblib.load('./models/target_encoder_item_condition.joblib')
    encoder_brand = joblib.load('./models/target_encoder_brand.joblib')
    encoder_located_in = joblib.load('./models/target_encoder_located_in.joblib')
    model_gb = joblib.load('./models/gradient_boosting_model.joblib')

    df = pd.DataFrame([new_data])

    tfidf_matrix = tfid.transform(df['name'])
    df['name'] = k_means.predict(tfidf_matrix)
    df['item_condition'] = encoder_item_condition.transform(df['item_condition'])
    df['brand'] = encoder_brand.transform(df['brand'])
    df['located_in'] = encoder_located_in.transform(df['located_in'])

    log_price = model_gb.predict(df)
    price = np.expm1(log_price)  

    return price[0]

new_data = {
    "name": "Womens Jogging Bottoms Elasticated Trouser Joggers Casual Pants",
    "brand": "Crazy Girl Ltd",
    "item_condition": "New with tags",
    "shipping": 1.0,
    "located_in": "United States",
    "return_policy": 1,
    "money_back": 1,
    "seller_item_sold": 203000.0,
    "trending": 1
}

predicted_price = predict_price(new_data)

print(f'The predicted price is: {predicted_price}')

