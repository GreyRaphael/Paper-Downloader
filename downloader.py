import os
import sys
import re
import json
import requests
from lxml import etree
import random

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


class SciHub():
    def __init__(self):
        self.sess=requests.session()
        self.pat=re.compile(r"location.href=\'(.+?)\'")
    
    def _get_pdf_url(self, paper_url, path):
        pg=''
        try:
            pg=self.sess.get(f'https://sci-hub.tw/{paper_url}', headers=random_headers()).text
        except Exception as e:
            print('[网络问题]无法访问sci-hub.tw，下次重启再试', e, paper_url, path)
        
        if pg:
            match=self.pat.search(pg)
            if isinstance(match, re.Match):
                pdf_url=match.group(1)
                if not pdf_url.startswith('https'):
                    pdf_url=f'https:{pdf_url}'
                return pdf_url
            else:
                print('[网络问题]存在验证码，下次重启再试', paper_url, path)
    
    def download(self, paper_url, path):
        pdf_url=self._get_pdf_url(paper_url, path)
        try:
            if pdf_url:
                pdf=self.sess.get(pdf_url, headers=random_headers()).content
                with open(path, 'wb') as file:
                    file.write(pdf)
        except FileNotFoundError as e:
            print(f'本地无法保存文件{path}', e, paper_url, path)
        except Exception as e:
            print('[网络问题]无法下载pdf，下次重启再试', e, paper_url, path)

def get_volume_issue_urls(start_year, end_year):
    '''get volume-issues of every year'''
    all_vi_urls={}
    for year in range(start_year, end_year+1):
        os.makedirs(str(year), exist_ok=True)
        url=f'https://www.sciencedirect.com/journal/00223115/year/{year}/issues'
        j_urls=requests.get(url, headers=random_headers()).json()
        all_vi_urls[year]=[f"https://www.sciencedirect.com/journal/journal-of-nuclear-materials{url['uriLookup']}" for url in j_urls['data']]
    
    print('Success to get all volume-issue urls')
    return all_vi_urls

def get_all_paper_urls(all_vi_urls):
    all_paper_urls=[]
    for year in all_vi_urls:
        for vi_url in all_vi_urls[year]:
            vi_page=requests.get(vi_url, headers=random_headers()).text
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

    hub=SciHub()
    all_vi_urls=get_volume_issue_urls(start_year, end_year)
    all_paper_urls=get_all_paper_urls(all_vi_urls)

    for url, title, year, volume, issue in all_paper_urls:
        filename=f'{year}/volume{volume}-issue{issue}/{url[50:]}.pdf'
        if not os.path.exists(filename):
            hub.download(url, path=filename)
        print(f'finished--->{url}, {title[:60]}')
    print(f'finishe all paper from {start_year} to {end_year}')



