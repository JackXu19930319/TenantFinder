import time

import requests
from bs4 import BeautifulSoup

from app import connection

headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
           }


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
        for i in range(0, 100):
            try:
                url = 'https://www.cib.npa.gov.tw/ch/app/wanted/list?module=wanted&id=1889&page=%s&pageSize=99' % str(i)
                page = requests.get(url, headers=headers)
                soup = BeautifulSoup(page.text, 'html.parser')
                peoples = soup.find_all('li', class_='col-lg-3 col-md-4 col-sm-6 col-12')
                if len(peoples) == 0:
                    break
                for people in peoples:
                    link = 'https://www.cib.npa.gov.tw' + people.find('a').get('href')
                    name = people.find('div', class_='info').find_all('p', class_='text02')[0].text.strip()
                    people_id = people.find('div', class_='info').find_all('p', class_='text02')[1].text.strip()
                    sql = "select * from cib_list where member_id=%s and member_name=%s ;"
                    cursor.execute(sql, (people_id, name))
                    result = cursor.fetchone()
                    if result is None:
                        sql = "insert into cib_list (member_id, member_name, link) values (%s, %s, %s);"
                        cursor.execute(sql, (people_id, name, link))
                        conn.commit()
            except:
                pass
            time.sleep(6)
        time.sleep(60 * 60)


if __name__ == '__main__':
    execute()
