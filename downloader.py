import os
import sys
import re
import json
import requests
from lxml import etree
import random

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


class SciHub():
    def __init__(self):
        self.sess=requests.session()
        self.pat=re.compile(r"location.href=\'(.+?)\'")
        self.unfinished=[]
        if os.path.exists('unfinished.csv'):
            os.remove('unfinished.csv')
    
    def _get_pdf_url(self, paper_url, path):
        pg=''
        try:
            pg=self.sess.get(f'https://sci-hub.tw/{paper_url}', headers=random_headers(), proxies=G_PROXY, timeout=30).text
        except Exception as e:
            print('[网络问题]无法访问sci-hub.tw，下次重启再试', e, paper_url, path)
            self.unfinished.append((paper_url, path))
        
        if pg:
            match=self.pat.search(pg)
            if isinstance(match, re.Match):
                pdf_url=match.group(1)
                if not pdf_url.startswith('https'):
                    pdf_url=f'https:{pdf_url}'
                return pdf_url
            else:
                print('[网络问题]存在验证码，下次重启再试', paper_url, path)
                self.unfinished.append((paper_url, path))
    
    def download(self, paper_url, path):
        pdf_url=self._get_pdf_url(paper_url, path)
        try:
            if pdf_url:
                pdf=self.sess.get(pdf_url, headers=random_headers(), proxies=G_PROXY, timeout=30).content
                if pdf:
                    with open(path, 'wb') as file:
                        file.write(pdf)
                else:
                    print('[网络问题]pdf为空，下次重启再试', paper_url, path)
                    self.unfinished.append((paper_url, path))
        except FileNotFoundError as e:
            print(f'[本地问题]本地无法保存文件{path}', e, paper_url)
            self.unfinished.append((paper_url, path))
        except Exception as e:
            print('[网络问题]无法下载pdf，下次重启再试', e, paper_url, path)
            self.unfinished.append((paper_url, path))

    def save_finished(self):
        file=open('unfinished.csv', 'w')
        for paper_url, path in self.unfinished:
            file.write(f'{paper_url}\t{path}\n')


def get_volume_issue_urls(start_year, end_year):
    '''get volume-issues of every year'''
    all_vi_urls={}
    for year in range(start_year, end_year+1):
        os.makedirs(str(year), exist_ok=True)
        url=f'https://www.sciencedirect.com/journal/00223115/year/{year}/issues'
        j_urls=requests.get(url, headers=random_headers(), proxies=G_PROXY).json()
        all_vi_urls[year]=[f"https://www.sciencedirect.com/journal/journal-of-nuclear-materials{url['uriLookup']}" for url in j_urls['data']]
    
    print('Success to get all volume-issue urls')
    return all_vi_urls


def get_all_paper_urls(total_vi_urls):
    all_paper_urls=[]
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
            raw_titles=tree.xpath("//a[contains(@class, 'article-content-title')]/span")
            assert len(raw_urls)==len(raw_titles), f'raw urls length != raw titles: {vi_url}'

            vi_url=vi_url.split('?')[0] # 将url中的?分开
            vi=re.findall(r'\d+', vi_url)
            if len(vi)==2:
                volume, issue=vi
            elif len(vi)==1:
                volume, issue = vi[0], 0
            elif len(vi)==3:
                volume, issue=vi[0], f'{vi[1]}-S{vi[2]}'
            else:
                raise ValueError(f'vi length must be 1, 2, 3: {vi_url}')
            path=f'{year}/volume{volume}-issue{issue}'
            os.makedirs(path, exist_ok=True)

            for raw_url, title in zip(raw_urls, raw_titles):
                final_url=f'https://www.sciencedirect.com/science/article/abs/pii/{raw_url[21:]}'
                final_title=title.xpath('string(.)')
                all_paper_urls.append((final_url, final_title, year, volume, issue))
            
        print(f'Success to get paper urls of {year}')
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
        filename=f'{year}/volume{volume}-issue{issue}/{url[54:]}.pdf'
        if not os.path.exists(filename):
            hub.download(url, path=filename)
        print(f'finished--->{url[8:]}, {title[:30]}, {year}-{volume}-{issue}')

    if hub.unfinished:
        print(f'未完成{len(hub.unfinished)}篇文章网址保存到本地文件unfinished.csv, 以便手动下载')
        hub.save_finished()
    else:
        print(f'成功下载所有{start_year}到{end_year}的JNM文章')



