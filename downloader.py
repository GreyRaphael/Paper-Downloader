import os
import sys
import re
import requests
from lxml import etree
import random
import scihub


firefox_version=random.randint(50, 80)
HEADERS={
    'User-Agent':f'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{firefox_version}.0) Gecko/20100101 Firefox/{firefox_version}.0',
}

def get_volume_issue_urls(start_year, end_year):
    # step1: get all volume-issue urls
    level1_urls={}
    for year in range(start_year, end_year+1):
        os.makedirs(str(year), exist_ok=True)
        url=f'https://www.sciencedirect.com/journal/00223115/year/{year}/issues'
        j_urls=requests.get(url, headers=HEADERS).json()
        for url in j_urls['data']:
            level1_urls[f"https://www.sciencedirect.com/journal/journal-of-nuclear-materials{url['uriLookup']}"]=year
    return level1_urls

def get_paper_urls(volume_issue_url):
    # step2: get all paper  urls
    pg=requests.get(volume_issue_url, headers=HEADERS).text
    tree=etree.HTML(pg)
    raw_urls = tree.xpath("//a[contains(@class, 'article-content-title')]/@href")
    raw_titles=tree.xpath("//a[contains(@class, 'article-content-title')]/span")
    # processing urls
    final_urls= [f'https://www.sciencedirect.com{url}' for url in raw_urls]
    # processing title
    entire_titles=[title.xpath('string(.)') for title in raw_titles]
    final_titles=[' '.join(re.findall(r'\w+', str(title))) for title in entire_titles]
    return zip(final_urls, final_titles)


if __name__ == "__main__":
    if len(sys.argv)<3:
        print('usage: python downloader.py 1959 1960')
        sys.exit()
    
    start_year=int(sys.argv[1])
    end_year=int(sys.argv[2])

    hub=scihub.SciHub()
    
    volume_issue_urls=get_volume_issue_urls(start_year, end_year)
    for url in volume_issue_urls:
        year=volume_issue_urls[url]
        volume, issue= re.findall(r'\d+', url)
        path=f'{year}/{volume}-{issue}'
        os.makedirs(path, exist_ok=True)
        paper_urls=get_paper_urls(url)
        for pl, title in paper_urls:
            print(pl, title)
            filename=f'{path}/{title}.pdf'
            hub.download(pl, path=filename)
        print(f'----->finished {path}')

    