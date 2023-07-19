#!/usr/bin/env python3

import requests
import urllib3
import re
import os
from bs4 import BeautifulSoup
import time
import telegram

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://www.boannews.com/media/t_list.asp"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Whale/3.20.182.14 Safari/537.36",
    "Connection": "close"
    }

response = requests.get(url, headers=headers, verify=False)
soup = BeautifulSoup(response.text, "html.parser")

def get_news_list():
    article_links = []  

    for link in soup.select('div.news_list a'):
        article_links.append(link['href'])

    saved_links = set()

    if os.path.isfile("saved_boan_links.txt"):
        with open("saved_boan_links.txt", "r") as f:
            saved_links = set([line.strip() for line in f.readlines()])

    new_links = []

    for link in article_links:
        full_link = f"https://www.boannews.com/{link}"
    
        if full_link not in saved_links:
            new_links.append(full_link)
            saved_links.add(full_link)
    with open("saved_boan_links.txt", "w") as f:
        f.write("\n".join(saved_links))
    return new_links

def telegram(link):
    TOKEN = 'Your Token'
    CHAT_ID = 'Your CHAT_ID'
    bot = telegram.Bot(token=TOKEN)
    cnt = len(link)
    
    INFO = "[★] 보안뉴스에 새로운 뉴스는 {}개 입니다.".format(cnt)
   
    bot.sendMessage(CHAT_ID, text=INFO)

    for url in link:
        BOAN_LINK = "링크 : {}".format(url)
        try:
            response = requests.get(url, headers=headers, verify=False)
            soup = BeautifulSoup(response.text, "html.parser")
            title = soup.find('div', id="news_title02").find('h1').get_text().strip()
        except AttributeError:
            title = "[*] 내용을 확인하기 위해서는 로그인이 필요합니다." 
        
        BOAN_TITLE = "제목 : {}".format(title)
        
        bot.sendMessage(CHAT_ID, text=BOAN_TITLE)
        bot.sendMessage(CHAT_ID, text=BOAN_LINK)
        time.sleep(0.5)

def main():
    new_links = get_news_list()

    if len(new_links) != 0:
        telegram(new_links)
    else:
        pass

if __name__ == '__main__':
    main()
