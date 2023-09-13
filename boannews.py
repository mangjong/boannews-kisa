import requests
import urllib3
import re
import os
from bs4 import BeautifulSoup
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://www.boannews.com/media/t_list.asp"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Whale/3.20.182.14 Safari/537.36",
    "Connection": "close"
    }

response = requests.get(url, headers=headers, verify=False)
soup = BeautifulSoup(response.text, "html.parser")

# 기사 내용 추출
def get_article(article_url):
    response = requests.get(article_url, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")

    article_title = soup.find('div', id='news_title02').find('h1').get_text().strip()
    article_summary = soup.find('div', id ='news_content').find('b').get_text('\n ').strip()
    article_time = soup.find('div', id='news_util01').get_text().strip()[5:]    

    print("주소:", article_url)
    print("제목:", article_title)
    print("부제:", "\n", article_summary)
    print("시간:", article_time, "\n")

# 신규 기사 내용 불러오기
def crawl(index):
    article_url = f'https://www.boannews.com/media/view.asp?idx={index}&page=1&kind=1'
    
    try:
        get_article(article_url)
    except AttributeError:
        print("Error : Article not found for index", index)

# 보안뉴스 전체기사 1 페이지 기준으로 전체 링크 수집 및 저장, 신규 링크에 대한 값 반환
def get_news_list():
    article_links = [link['href'] for link in soup.select('div.news_list a')]

    saved_links = set()

    if os.path.isfile("saved_boan_links.txt"):
        with open("saved_boan_links.txt", "r") as f:
            saved_links = set([line.strip() for line in f.readlines()])

    new_links = []

    for link in article_links:
        index = re.search(r'\d+', link).group()
        full_link = f"https://www.boannews.com/{link}"

        if full_link not in saved_links:
            new_links.append((full_link, index))
            saved_links.add(full_link)
    with open("saved_boan_links.txt", "w") as f:
        f.write("\n".join(saved_links))
    return new_links

def main():
    new_links = get_news_list()

    if len(new_links) == 0:
        print("No new links found.")
    else:
        for link, index in new_links:
            crawl(index)

if __name__ == '__main__':
    main()
