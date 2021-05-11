import os
import requests

'''
下载北大图书馆买的书:
1. 获取所有链接
2. 利用Chrome插件Tab copy/paste+IDM下载所有文件
3. 根据顺序重命名pdf文件
'''

HEADERS={
'Host':'www.sciencedirect.com',
'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
'Accept':'application/json, text/plain, */*',
'Accept-Language':'en-US,en;q=0.5',
'Accept-Encoding':'gzip, deflate, br',
'Connection':'keep-alive',
'Referer':'https://www.sciencedirect.com/referencework/9780081028667/comprehensive-nuclear-materials',
'Cookie':r'EUID=6570c1f2-df63-4cf6-bdb9-32fc085e7e6f; id_ab=AEG; mbox=session%2357edcf6926394cd68ce2efa05c44b13a%231620718822%7CPC%2336ddb3989581415d8c301f4c55fdb1e7.34_0%231683961762; mboxes=%7B%7D; AMCV_4D6368F454EC41940A4C98A6%40AdobeOrg=-1124106680%7CMCIDTS%7C18759%7CMCMID%7C04632463758883178193106101450788796676%7CMCAID%7CNONE%7CMCOPTOUT-1620726706s%7CNONE%7CvVersion%7C5.2.0; ANONRA_COOKIE=DE0439D3870A21293C1F7556C50836BDCCA5363369CD2AA9A7E070366C9711D625A9A0698555F06529B306765B43761270F41F8C37FAD0C4; SD_REMOTEACCESS=eyJhY2NvdW50SWQiOiI1MzY2MiIsInRpbWVzdGFtcCI6MTYyMDcxOTUwNDIzMn0=; __cfduid=d1da386944680b03723b770133b74d30c1618196532; sd_session_id=9207f4d99ac8104645394e29a3ccfcd8d38egxrqa; acw=9207f4d99ac8104645394e29a3ccfcd8d38egxrqa%7C%24%7CF4270B12F3F59C1E46D9E4488CFEA4D66FFE79AD25490BBC8FF2291F192448DF1479ABDB602E0F8685032A1C3016527CA545B04E27F73C053FBA44D1BD4E4F2EAFE9C31A29ED2080B6DA1F7CB1786ABB; has_multiple_organizations=false; MIAMISESSION=68b46559-d490-4fdc-9861-a454c1e4f766:3798172304; AMCVS_4D6368F454EC41940A4C98A6%40AdobeOrg=1; fingerPrintToken=b10f6608a553a07b40d7493c1cb36f2a; __cf_bm=8257f1dff08c1cc3bf0b4aa829a25ce5017fba32-1620719615-1800-ARXDadCUKpqyFYcfu+VIX77qWQHWEe6aVl+lQBRrzPwLACv6+lCr1H3BkNaueiC7CgWQU5CKaIwZIfbylrJHPuE=',
'TE':'Trailers',
}

piis=[]
for pg in range(7):
    pii=[]
    url=f'https://www.sciencedirect.com/book/api/mrw/9780081028667/table-of-contents/index/{pg}'
    data=requests.get(url, headers=HEADERS).json()
    for paper in data['data']['content']:
        pii.append(paper['pii'])
    piis.append(pii)

# generate url for Chrom Tab copy/paste extension

# download all pdf

# rename pdf

for i, pii in enumerate(piis):
    for ii, pi in enumerate(pii):
        os.rename(f'{i}/3-s2.0-{pi}-main.pdf', f'{i}/{ii:02d}.pdf', )
