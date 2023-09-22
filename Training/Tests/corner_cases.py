import unittest
import pandas as pd
import numpy as np
from io import StringIO
from consolidate import load_data, preprocess_data, to_numbers, split_data, calculate_cv_scores, train


class TestPreprocessing(unittest.TestCase):

    def test_handle_unexpected(self):
        # Unexpected values corner test for return_policy and trending
        data = 'name,trending,return_policy\nGG,C,Idk\nNotTrending,H,Yes'
        df = pd.read_csv(StringIO(data))
        df = preprocess_data(df)
        self.assertIn(df.loc[0, 'return_policy'], [0, 1])
        self.assertIn(df.loc[0, 'trending'], [0, 1])

    def test_handle_non_numeric_seller_item_sold(self):
        # As items sold in in shortened format, 
        # we need to ensure it is in numerical 
        # format after converting
        self.assertEqual(to_numbers('1000'), 1000.0)
        self.assertEqual(to_numbers('1K'), 1000.0)
        self.assertEqual(to_numbers('1M'), 1000000.0)
        self.assertEqual(to_numbers('A'), None)

    def test_handle_empty_data_file(self):
        # check empty data file
        data = './empty.csv'
        df = load_data(data)
        self.assertIsNone(df)

unittest.main()
