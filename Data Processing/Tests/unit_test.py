import unittest
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from consolidate import load_data, preprocess_data, to_numbers, split_data, calculate_cv_scores, train
from sklearn.model_selection import train_test_split

class TestConsolidate(unittest.TestCase):
    df = load_data('../data/lot41_statistical.csv')
    def test_load_data(self):
        # Test for instance and shape
        self.assertIsInstance(self.df, pd.DataFrame)
        self.assertEqual(self.df.shape[0], 17893)
        self.assertEqual(self.df.shape[1], 13)

    def test_preprocess_data(self):
        df = self.df.head(1000)
        df_op = preprocess_data(df)
        # Check for instance, shape and columns
        self.assertIsInstance(self.df, pd.DataFrame)
        self.assertEqual(self.df.shape[0], 17893)
        self.assertEqual(self.df.shape[1], 13)
        self.assertListEqual(df.columns.tolist(), df_op.columns.tolist())

        # Making sure, target variable has not changed
        self.assertListEqual(df["price_log"].tolist(), df_op["price_log"].tolist())

    def test_to_numbers(self):
        # Check on number conversions
        self.assertEqual(to_numbers('5K'), 5000)
        self.assertEqual(to_numbers('5M'), 5000000)
        self.assertEqual(to_numbers('5'), 5)

    def test_split_data(self):
        # check if the testing and training data are coming in desired ratio
        df = self.df.head(1000)
        X_train, X_test, _, _ = split_data(df)
        self.assertEqual(len(X_train), 800)
        self.assertEqual(len(X_test), 200)
    
    def test_calculate_cv_scores(self):
        # Make sure cv_scores function produces desired result
        df = load_data('../data/lot42_vectorized.csv')
        models = [('RandomForestRegressor', RandomForestRegressor(n_estimators = 100, random_state=42))]
        X = df.drop(['price', 'price_log', 'price_boxcox'], axis=1)
        y = df['price_log']
        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
        scores = calculate_cv_scores(models, X_train, y_train)
        self.assertTrue('RandomForestRegressor' in scores)
        

if __name__ == '__main__':
    unittest.main()