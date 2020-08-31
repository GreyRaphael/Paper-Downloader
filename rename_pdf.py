import json
import os

with open('index.json') as file:
    data=json.load(file)


for year in os.listdir():
    if os.path.isdir(year):
        for vi in os.listdir(year):
            for pdf in os.listdir(f'{year}/{vi}'):
                paper_id=pdf[:-4]
                page=data[paper_id]
                os.rename(f'{year}/{vi}/{pdf}', f'{year}/{vi}/{page} {pdf}')