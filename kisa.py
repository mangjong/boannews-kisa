import requests
import urllib3
import re
import os
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://krcert.or.kr/kr/bbs/list.do?menuNo=205020&bbsId=B0000133"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Whale/3.20.182.14 Safari/537.36",
    "Connection": "close"
    }

def get_kisa_list():
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    
    #article_index = [index.text.strip() for index in soup.select("tbody td.num")]
    #article_title = [title.find('a').text.strip() for title in soup.select("tbody td.sbj.tal")]
    article_link = [link.find('a')['href'] for link in soup.select("tbody td.sbj.tal")]
    #article_date = [date.text.strip() for date in soup.select("tbody td.date")]

    saved_kisa_links = set()

    if os.path.isfile("saved_kisa_links.txt"):
        with open("saved_kisa_links.txt", "r") as f:
            saved_kisa_links = set([line.strip() for line in f.readlines()])

    new_kisa_links = []

    for link in article_link:
        full_link = f"https://krcert.or.kr/{link}"

        if full_link not in saved_kisa_links:
            new_kisa_links.append(full_link)
            saved_kisa_links.add(full_link)
    with open("saved_kisa_links.txt", "w") as f:
        f.write("\n".join(saved_kisa_links))

    return new_kisa_links

def crawl(url):
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find('div', class_="b_title").find('h2').get_text()
    date = soup.find('div', class_="b_title").find('span').get_text()
    cve_data = soup.find('div', class_="content_html").get_text().strip()
    cve_list = sorted(set(re.findall(r'CVE\-\d{4}\-\d{4,5}', cve_data)))
    cve_code = ', '.join(cve_list)
    print("보안권고문:", title)
    print("공지일:", date)
    
    if len(cve_list) != 0:
        print(f"CVE 리스트 :\n {cve_code}\n")
        get_cvss(cve_list)
    else:
        pass

def get_cvss(cve_list):
    for list in cve_list:
        nist_url = f'https://nvd.nist.gov/vuln/detail/{list}'
        response = requests.get(nist_url, verify=False)
        if response.status_code == 200:
            if 'CVE ID Not Found' not in response.text:
                soup = BeautifulSoup(response.text, "html.parser")
                try:
                    score = soup.select_one('#Cvss3CnaCalculatorAnchor').text
                    print(f"* Code & Score : {list} & {score}\n")
                except:
                    try:
                        score = soup.select_one('#Cvss3NistCalculatorAnchor').text
                        print(f"* Code & Score : {list} & {score}\n")
                    except:
                        score = soup.select_one('#Cvss3NistCalculatorAnchorNA').text
                        print(f"* Code & Score : {list} & {score}\n")
            else:
                print(f"* Code & Score : {list} is Not Found \n")
        else:  
            print(f'NIST URL of {list} is Not Found\n')
 
new_links = get_kisa_list()
if len(new_links) == 0:
    pass
else:
    for link in new_links:
        crawl(link)
