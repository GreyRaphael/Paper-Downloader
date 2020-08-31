import requests
import random
from lxml import etree
import re
import sys
import json
import os


G_PROXY={}
if os.path.exists('proxy.json'):
    G_PROXY=json.load(open('proxy.json'))

def random_headers():
    version=random.randint(70, 83)
    HEADERS={
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh-TW;q=0.7,zh;q=0.6',
        'cache-control': 'max-age=0',
        'cookie': '__ddg1=9ecPxT9UnphsDYkzdiPP; session=ace4fd2a85e617e3b21475d6a75e1626; refresh=1596419755.705; __ddg2=huX54o8URarDaO3R',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.3987.163 Safari/537.36',
    }
    return HEADERS


def get_volume_issue_urls(start_year, end_year):
    '''get volume-issues of every year'''
    all_vi_urls={}
    for year in range(start_year, end_year+1):
        url=f'https://www.sciencedirect.com/journal/00223115/year/{year}/issues'
        j_urls=requests.get(url, headers=random_headers(), proxies=G_PROXY).json()
        all_vi_urls[year]=[f"https://www.sciencedirect.com/journal/journal-of-nuclear-materials{url['uriLookup']}" for url in j_urls['data']]
        print(f'get all volumes of {year}')
    
    print('Success to get all volume-issue urls')
    return all_vi_urls


def get_all_paper_urls(total_vi_urls):
    all_paper_index={}
    for year in total_vi_urls:
        while True:
            if not total_vi_urls[year]:
                break

            vi_url=total_vi_urls[year].pop()
            vi_page=requests.get(vi_url, headers=random_headers(), proxies=G_PROXY).text
            tree=etree.HTML(vi_page)

            pagination=tree.xpath("//span[@class='pagination-pages-label']/text()")
            if pagination and 'page' not in vi_url:
                total_pages=int(pagination[0][-1])
                for pg in range(2, total_pages+1):
                    new_vi_url=f'{vi_url}?page={pg}'
                    all_vi_urls[year].append(new_vi_url)

            raw_urls = tree.xpath("//a[contains(@class, 'article-content-title')]/@href")
            raw_pages=tree.xpath("//dd[contains(@class, 'js-article-page-range')]/text()")
            assert len(raw_urls)==len(raw_pages), f'raw urls length != raw pages: {vi_url}'

            for raw_url, page in zip(raw_urls, raw_pages):
                all_paper_index[raw_url[21:]]=page
            
        print(f'Success to get paper urls of {year}')
    print('Success to get all paper urls')
    return all_paper_index


def write2csv(page_id, page):
    with open('index.csv', 'a') as file:
        file.write(f'{page_id}\t{page}\n')

if __name__ == "__main__":
    if len(sys.argv)<3:
        print('usage: python downloader.py 1959 1960')
        sys.exit()

    start_year=int(sys.argv[1])
    end_year=int(sys.argv[2])

    all_vi_urls=get_volume_issue_urls(start_year, end_year)
    all_paper_index=get_all_paper_urls(all_vi_urls)
    with open('index.json', 'w', encoding='utf8') as file:
        json.dump(all_paper_index, file)
