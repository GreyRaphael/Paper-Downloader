import os
import pikepdf

# 1. pip install pikepdf
# 2. put this file out of directory, which contains pdf files
# 3. run this file

for dir_name in os.listdir():
    if os.path.isdir(dir_name):
        os.makedirs(f'output/{dir_name}', exist_ok=True)
        for file in os.listdir(dir_name):
            pdf=pikepdf.open(f'{dir_name}/{file}', password='P2lyZi')
            pdf.save(f'output/{dir_name}/{file}')
