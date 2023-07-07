#! /usr/bin/env python3
import smtplib
import urllib3
import requests
import os
import re
from email.mime.text import MIMEText
from email.header import Header
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://krcert.or.kr/kr/bbs/list.do?menuNo=205020&bbsId=B0000133"
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

            soup = BeautifulSoup(response.text, "html.parser")

            article_title = soup.find('div', class_="b_title").find('h2').get_text()
            article_time = soup.find('div', class_="b_title").find('span').get_text()
            #cve_data = soup.find('div', class_="content_html").get_text().strip()
            #cve_list = sorted(set(re.findall(r'CVE\-\d{4}\-\d{4,5}', cve_data)))
            
            '''
            if len(cve_list) < 3:
                cve_code = ', '.join(cve_list)
            else:
                cve_code = f'별도 확인'

            if len(cve_list) != 0:
                print(f"CVE 리스트 :\n {cve_code}\n")
            else:
                pass
            '''
            article_html = f"""
                <tr>
                    <td style="border: 1px solid black; text-align: center;">{index}</td>
                    <td style="border: 1px solid black; text-align: center;">{article_time}</td>
                    <td style="border: 1px solid black;">{article_title}</td>
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
        <table style="border-collapse: collapse; border-spacing: 10px; width: 80%">
            <thead>
                <tr bgcolor="#D9E5FF">
                    <th style="border: 1px solid black; width: 3%; text-align: center;">
                        <strong>번호</strong>
                    </th>
                    <th style="border: 1px solid black; width: 10%; text-align: center;">
                        <strong>일자</strong>
                    </th>
                    <th style="border: 1px solid black; width: 25%; text-align: center;">
                        <strong>제목</strong>
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
    
    body = f"""
    <html>
      <body>
        <p style='line-height:normal'; font-size:13px>
          안녕하세요.<br> 
          KISA에 기재된 보안권고문 전달드립니다.<br>
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
    msg['Subject'] = f'[KISA 보안권고문] 신규 게시물 알림 ({index}건)'

    smtp.sendmail(from_mail, to_mail, msg.as_string())
    smtp.quit()

def get_kisa_list():
    response = requests.get(url, headers=headers, verify=False)
    soup = BeautifulSoup(response.text, "html.parser")
    
    article_link = [link.find('a')['href'] for link in soup.select("tbody td.sbj.tal")]    
    
    saved_kisa_links = set()

    if os.path.isfile("saved_kisa_mail.txt"):
        with open("saved_kisa_mail.txt", "r") as f:
            saved_kisa_links = set([line.strip() for line in f.readlines()])
            pass
    
    new_kisa_links = []

    for link in article_link:
        full_link = f"https://krcert.or.kr{link}"

        if full_link not in saved_kisa_links:
            new_kisa_links.append(full_link)
            saved_kisa_links.add(full_link)
    with open("saved_kisa_mail.txt", "w") as f:
        f.write("\n".join(saved_kisa_links))

    return new_kisa_links

def main():
    new_links = get_kisa_list()

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
