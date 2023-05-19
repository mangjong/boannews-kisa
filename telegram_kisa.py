#! /usr/bin/env python3
import requests
import urllib3
import re
import os
from bs4 import BeautifulSoup
import time
import telepot

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


url = "https://krcert.or.kr/kr/bbs/list.do?menuNo=205020&bbsId=B0000133"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Whale/3.20.182.14 Safari/537.36",
    "Connection": "close"
    }

def get_kisa_list():
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")        
    article_link = [link.find('a')['href'] for link in soup.select("tbody td.sbj.tal")]

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


def telegram(link):
    TOKEN = 'Your Token'
    CHAT_ID = 'Your Chat ID'
    bot = telepot.Bot(token=TOKEN)
    cnt = len(link)
    
    INFO = "[★] KISA에 공지된 보안권고문은 {}개 입니다.".format(cnt)
   
    bot.sendMessage(CHAT_ID, text=INFO)

    for url in link:
        response = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find('div', class_="b_title").find('h2').get_text()
        
        KISA_TITLE = "제목 : {}".format(title)
        KISA_LINK = "링크 : {}".format(url)

        bot.sendMessage(CHAT_ID, text=KISA_TITLE)
        bot.sendMessage(CHAT_ID, text=KISA_LINK)

def main():
    new_links = get_kisa_list()

    if len(new_links) != 0:
        telegram(new_links)
    else:
        pass

if __name__ == '__main__':
    main()
