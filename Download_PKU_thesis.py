import os
import requests
from lxml import etree
import img2pdf

HEADERS={
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
"Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,ja;q=0.6,zh-TW;q=0.5",
"Cache-Control": "max-age=0",
"Connection": "keep-alive",
"Cookie": "JSESSIONID=B9589BA83EA9430BB57F50FFD2EBD466",
"Host": "162.105.134.188",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
}

# make directory if not exist
os.makedirs('thesis', exist_ok=True)

# Basic Input
URL='https://thesis.lib.pku.edu.cn/docinfo.action?learnid=1501110252'
MAX_PAGE=130
PAPER_ID='dB2CJTkh1zFajt0DxG6nJA11'

html=requests.get(URL).text
tree=etree.HTML(html)
THESIS_INFO=[td.xpath('string(.)') for td in tree.xpath('//td[@class="right"]')]
title=THESIS_INFO[0].strip()
author=THESIS_INFO[1].strip()
year=THESIS_INFO[12].strip()[:4]
FILE_NAME=f'{year}-{author}-{title}'
print(FILE_NAME)


for i in range(1, MAX_PAGE+1):
    img_url=f'http://162.105.134.188/store/{PAPER_ID}/P01_00{i:03d}.jpg'
    r=requests.get(img_url, headers=HEADERS)
    with open(f'thesis/P01_00{i:03d}.jpg', 'wb') as file:
        file.write(r.content)
    
    if i%10==0:
        print(f'{i/MAX_PAGE:.2%} downloaded!')

print('100% downloaded!')
print('Merging images to pdf')
with open(f'{FILE_NAME}.pdf', 'wb') as file:
    data=img2pdf.convert([f'thesis/{f}' for f in os.listdir('thesis') if f.endswith('.jpg')])
    file.write(data)

for f in os.listdir('thesis'):
    os.remove(f'thesis/{f}')