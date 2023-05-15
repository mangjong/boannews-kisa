import requests
import urllib3
import re
import os
from bs4 import BeautifulSoup
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


url = "https://krcert.or.kr/kr/bbs/list.do?menuNo=205020&bbsId=B0000133"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Whale/3.20.182.14 Safari/537.36",
    "Connection": "close"
    }

def get_kisa_list():
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    
    article_index = [index.text.strip() for index in soup.select("tbody td.num")]
    article_title = [title.find('a').text.strip() for title in soup.select("tbody td.sbj.tal")]
    article_link = [link.find('a')['href'] for link in soup.select("tbody td.sbj.tal")]
    article_date = [date.text.strip() for date in soup.select("tbody td.date")]

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
    print("보안권고문:", title)
    print("공지일:", date)

new_links = get_kisa_list()
if len(new_links) == 0:
    pass
else:
    for link in new_links:
        crawl(link)
