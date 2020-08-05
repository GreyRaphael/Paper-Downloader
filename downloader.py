import os
import sys
import re
import json
import requests
from lxml import etree
import random
import scihub


firefox_version=random.randint(50, 80)
HEADERS={
    'User-Agent':f'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{firefox_version}.0) Gecko/20100101 Firefox/{firefox_version}.0',
}

def get_volume_issue_urls(start_year, end_year):
    '''get volume-issues of every year'''
    all_vi_urls={}
    for year in range(start_year, end_year+1):
        os.makedirs(str(year), exist_ok=True)
        url=f'https://www.sciencedirect.com/journal/00223115/year/{year}/issues'
        j_urls=requests.get(url, headers=HEADERS).json()
        all_vi_urls[year]=[f"https://www.sciencedirect.com/journal/journal-of-nuclear-materials{url['uriLookup']}" for url in j_urls['data']]
    
    print('Success to get all volume-issue urls')
    return all_vi_urls

def get_all_paper_urls(all_vi_urls):
    all_paper_urls=[]
    for year in all_vi_urls:
        for vi_url in all_vi_urls[year]:
            vi_page=requests.get(vi_url, headers=HEADERS).text
            tree=etree.HTML(vi_page)
            raw_urls = tree.xpath("//a[contains(@class, 'article-content-title')]/@href")
            raw_titles=tree.xpath("//a[contains(@class, 'article-content-title')]/span")
            assert len(raw_urls)==len(raw_titles), f'raw urls length != raw titles: {vi_url}'

            vi=re.findall(r'\d+', vi_url)
            if len(vi)==2:
                volume, issue=vi
            elif len(vi)==1:
                volume, issue = vi[0], 0
            else:
                raise ValueError(f'vi length must be 1 or 2: {vi_url}')
            path=f'{year}/volume{volume}-issue{issue}'
            os.makedirs(path, exist_ok=True)


            for raw_url, title in zip(raw_urls, raw_titles):
                final_url=f'https://www.sciencedirect.com{raw_url}'
                final_title=title.xpath('string(.)')
                all_paper_urls.append((final_url, final_title, year, volume, issue))
    print('Success to get all paper urls')
    return all_paper_urls


if __name__ == "__main__":
    if len(sys.argv)<3:
        print('usage: python downloader.py 1959 1960')
        sys.exit()

    start_year=int(sys.argv[1])
    end_year=int(sys.argv[2])

    hub=scihub.SciHub()
    all_vi_urls=get_volume_issue_urls(start_year, end_year)
    all_paper_urls=get_all_paper_urls(all_vi_urls)

    for url, title, year, volume, issue in all_paper_urls:
        filename=f'{year}/volume{volume}-issue{issue}/{url[50:]}.pdf'
        if not os.path.exists(filename):
            hub.download(url, path=filename)
        print(f'finished--->{url}, {title}')
    print(f'finishe all paper from {start_year} to {end_year}')



