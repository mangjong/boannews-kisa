#! /usr/bin/env python3
import smtplib
import urllib3
import requests
import os
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://www.boannews.com/media/t_list.asp"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Whale/3.20.182.14 Safari/537.36",
    "Connection": "close"
    }

response = requests.get(url, headers=headers, verify=False)
soup = BeautifulSoup(response.text, "html.parser")

def get_article(new_links):
    articles = []
    index = 1

    for article_url in new_links:
        try:
            response = requests.get(article_url, verify=False)
            response.raise_for_status()

            if "http-equiv='refresh'" in response.text:
                print("Error: Login Error", article_url)
                continue
            
            soup = BeautifulSoup(response.text, "html.parser")
            article_time = soup.find('div', id='news_util01').get_text().strip()[8:]
            article_title = soup.find('div', id='news_title02').find('h1').get_text().strip()

            try:
                article_summary = soup.find('div', id='news_content').find('b').get_text('\n ').strip()
            except AttributeError:
                print("Error: Summary not found for index", article_url)
                article_summary = "요약 내용이 없습니다."

            article_html = f"""
                <tr>
                    <td style="border: 1px solid black; text-align: center;">{index}</td>
                    <td style="border: 1px solid black; text-align: center;">{article_time}</td>
                    <td style="border: 1px solid black;">{article_title}</td>
                    <td style="border: 1px solid black;">{article_summary}</td>
                    <td style="border: 1px solid black; text-align: center;">
                        <a href="{article_url}" target="_blank">링크</a>
                    </td>
                </tr>
            """
            articles.append(article_html)
            index += 1
        except requests.exceptions.RequestException as e:
            print(f"Error: Request failed for index {article_url}: {e}")

    table_html = f"""
        <table style="border-collapse: collapse; border-spacing: 10px; width: 100%">
            <thead>
                <tr bgcolor="#D9E5FF">
                    <th style="border: 1px solid black; width: 3%; text-align: center;">
                        <strong>번호</strong>
                    </th>
                    <th style="border: 1px solid black; width: 15%; text-align: center;">
                        <strong>시간</strong>
                    </th>
                    <th style="border: 1px solid black; width: 35%; text-align: center;">
                        <strong>제목</strong>
                    </th>
                    <th style="border: 1px solid black; width: 43%; text-align: center;">
                        <strong>요약</strong>
                    </th>
                    <th style="border: 1px solid black; width: 7%; text-align: center;">
                        <strong>바로가기</strong>
                    </th>
                </tr>
            </thead>
            <tbody>
                {''.join(articles)}
            </tbody>
        </table>
    """
    return table_html.strip(), index - 1
    
def send_mail(new_links, to_mail):
    
    #Config / Mail List, basic content
    from_name = "YOUR NAME"
    from_mail = 'YOUR FROM MAIL'
    #to_mail = 'YOUR TO MAIL'
    app_key = 'YOUR APP KEY'

    smtp = smtplib.SMTP('smtp.gmail.com', 587)

    smtp.ehlo()
    smtp.starttls()
    smtp.login(from_mail, app_key)
    title, index = get_article(new_links)
    if index !=0:
      body = f"""
      <html>
        <body>
          <p style='line-height:normal'; font-size:13px>
            안녕하세요.<br> 
            보안뉴스에 기재된 새로운 게시물을 전달드립니다.<br>
            업무에 참고해주시기 바랍니다.
          </p>
          {title}
          <p>감사합니다.</p>
        </body>
      </html>
      """
      
      msg = MIMEText(body, 'html', 'utf-8')
      msg['From'] = Header(from_name, 'utf-8')
      msg['To'] = to_mail
      msg['Subject'] = f'[보안뉴스] 신규 게시물 알림 ({index}건)'
  
      smtp.sendmail(from_mail, to_mail, msg.as_string())
      smtp.quit()
    else:
      print("No article\n")
      
def get_news_list():
    article_links = []  

    for link in soup.select('div.news_list a'):
        article_links.append(link['href'])

    saved_links = set()

    if os.path.isfile("./saved_boan_mail.txt"):
        with open("./saved_boan_mail.txt", "r") as f:
            saved_links = set([line.strip() for line in f.readlines()])

    new_links = []

    for link in article_links:
        full_link = f"https://www.boannews.com/{link}"
    
        if full_link not in saved_links:
            new_links.append(full_link)
            saved_links.add(full_link)
    with open("./saved_boan_mail.txt", "w") as f:
        f.write("\n".join(saved_links))
        
    return new_links

def main():
    new_links = get_news_list()
    
    if len(new_links) == 0:
        print("No new links found.")
    else:
        try:
            mail_list = []
            if os.path.isfile("./mail_list.txt"):
                with open("./mail_list.txt", "r") as f:
                    mail_list = set([line.strip() for line in f.readlines()])
            for to_mail in mail_list:
                send_mail(new_links, to_mail)
            #get_article(new_links)
        except AttributeError:
            print("Error")
            
if __name__ == '__main__':
    main()
