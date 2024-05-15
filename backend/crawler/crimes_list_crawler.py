import time

import requests
from bs4 import BeautifulSoup

from app import connection


def get_conn():
    conn = None
    while True:
        try:
            conn = connection.connect_to_mysql()
        except:
            pass
        if conn is not None:
            break
    time.sleep(5)
    return conn


def execute():
    conn = get_conn()
    cursor = conn.cursor()
    while True:
        # 需要建立表格全站爬蟲後存起來比對
        headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
                   }
        for i in range(1, 100):
            try:
                time.sleep(3)
                data = {
                    "page": i
                }
                page = requests.post("https://www.mjib.gov.tw/Crimes/Crimes_List", headers=headers, data=data)
                soup = BeautifulSoup(page.text, 'html.parser')
                crimess = soup.find_all('div', class_='crimes-card')
                if len(crimess) == 0:
                    break
                for crimes in crimess:
                    link = "https://www.mjib.gov.tw/" + crimes.find('a')['href']
                    c_obj = crimes.find('div', class_='crimes-content').find_all('div')
                    name = c_obj[0].text.strip()
                    people_id = c_obj[2].text.split('****')[0].strip()
                    sql = "select * from crimes_list where member_id=%s and member_name=%s ;"
                    cursor.execute(sql, (people_id, name))
                    result = cursor.fetchone()
                    if result is None:
                        sql = "insert into crimes_list (member_id, member_name, link) values (%s, %s, %s);"
                        cursor.execute(sql, (people_id, name, link))
                        conn.commit()
            except:
                pass
        time.sleep(60 * 60)


if __name__ == '__main__':
    execute()
