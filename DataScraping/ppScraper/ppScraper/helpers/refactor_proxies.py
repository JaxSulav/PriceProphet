import pandas as pd


df = pd.read_csv("./prox.csv")

print("ff, ", df.head())
joined_list = []

for index, row in df.iterrows():
    joined_string = str(row['ip']) + ':' + str(row['port'])
    joined_list.append(joined_string)


def write_list_to_file(filename, string_list):
    with open(filename, 'w') as file:
        for string in string_list:
            file.write(string + '\n')

write_list_to_file("proxies1.txt", joined_list)