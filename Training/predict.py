from joblib import load
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from category_encoders import TargetEncoder
import numpy as np



def preprocess_input(input_data):
    tfid = load('./models/tfidf_vectorizer.joblib')
    k_means = load('./models/k_means.joblib')
    encoder_item_condition = load('./models/target_encoder_item_condition.joblib')
    encoder_brand = load('./models/target_encoder_brand.joblib')
    encoder_located_in = load('./models/target_encoder_located_in.joblib')

    tfidf_matrix = tfid.transform([input_data['name']])
    input_data['name'] = k_means.predict(tfidf_matrix)
    
    input_data['item_condition'] = encoder_item_condition.transform(pd.DataFrame([input_data['item_condition']], columns=['item_condition'])).iloc[0,0]
    input_data['brand'] = encoder_brand.transform(pd.DataFrame([input_data['brand']], columns=['brand'])).iloc[0,0]
    input_data['located_in'] = encoder_located_in.transform(pd.DataFrame([input_data['located_in']], columns=['located_in'])).iloc[0,0]
    
    return input_data



def predict_price(input_data):
    model = load('./models/gradient_boosting_model.joblib')
    input_data = preprocess_input(input_data)
    feature_order = ['name', 'brand', 'item_condition', 'shipping', 'located_in', 'return_policy', 'money_back', 'seller_item_sold', 'trending']
    input_list = [input_data[col] for col in feature_order]
    prediction = model.predict([input_list])
    prediction = np.exp(prediction)

    return prediction[0]


input_data = {
    'name': 'Adidas Ultraboost Running Shoes',
    'brand': 'Adidas',
    'item_condition': 'New with tags',
    'located_in': 'United States',
    'shipping': 1.0,  
    'return_policy': 1, 
    'money_back': 0, 
    'seller_item_sold': 300.0, 
    'trending': 1,  
}

print(predict_price(input_data))

