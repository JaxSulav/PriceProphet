import os
import pandas as pd

# Directory path containing the CSV files
directory = '../data/bak/'

# Get all the CSV files in the directory
csv_files = [file for file in os.listdir(directory) if file.endswith('.csv')]

# Initialize an empty list to store the individual DataFrames
data_frames = []

# Iterate over each CSV file and load it into a DataFrame
for file in csv_files:
    file_path = os.path.join(directory, file)
    data = pd.read_csv(file_path)
    data_frames.append(data)

# Concatenate all the DataFrames into a single DataFrame
combined_data = pd.concat(data_frames, ignore_index=True)

# Write the combined data to a new CSV file
combined_data.to_csv('../data/combined/combinedF.csv', index=False)

