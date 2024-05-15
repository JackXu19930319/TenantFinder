import html
import json
import random
import time
from datetime import datetime

import requests

import connection
import tow_c

from bs4 import BeautifulSoup
import exception_tool
import logging

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,  # 设置日志级别为DEBUG，记录所有级别的消息
    format="%(asctime)s [%(levelname)s]: %(message)s",  # 消息格式
    datefmt="%Y-%m-%d %H:%M:%S"  # 时间戳格式
)

max_retry = 5  # 驗證碼可能會失敗，最多嘗試


def insert_error(conn, msg):
    cursor = conn.cursor()
    sql = "insert into error_log(e_str) values(%s);"
    cursor.execute(sql, (msg,))
    conn.commit()


def get_page(url, max_retry=10):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
    """下載網頁"""

    page = None
    retry = 0
    while page is None:
        try:
            retry = retry + 1
            if retry >= max_retry:
                break
            requests.packages.urllib3.disable_warnings()
            page = requests.get(url, headers=headers, timeout=10, verify=False)
        except Exception:
            page = None
            print('...retry connection')
            continue
        return page


# 在外通緝
def fugitive(id_, id_card, name, conn):
    message = None
    try:
        logging.info("查緝專刊 %s, %s" % (id_, id_card))
        cursor = conn.cursor()
        sql = "SELECT link, member_id FROM crimes_list WHERE member_name=%s;"
        cursor.execute(sql, (name,))
        result = cursor.fetchone()
        if result is None:
            pass
        else:
            crimes_member_id = result[1]
            link = result[0]
            if crimes_member_id in id_card:
                message = "[外逃通緝犯]有資料符合\n連結： " + link + " \n"

        s = requests.session()
        page = s.get("https://www.thcw.moj.gov.tw/CriminalWanted/#mainPage")
        soup = BeautifulSoup(page.text, 'html.parser')
        RequestVerificationToken = soup.find('input', {'name': '__RequestVerificationToken'})['value']
        img = s.get("https://www.thcw.moj.gov.tw/CriminalWanted/Home/GetValidateCode")
        with open('captcha.jpg', 'wb') as file:
            file.write(img.content)
        code = tow_c.get_tow_c()
        data = {
            'qName': name,
            'qID': id_card,
            'qValidateCode': code,
            '__RequestVerificationToken': RequestVerificationToken
        }
        page = s.post('https://www.thcw.moj.gov.tw/CriminalWanted/Home/Query', data=data)
        data_json = json.loads(page.text)
        if data_json.get('rDataList') is not None:
            result = data_json.get('rDataList')
            if len(result) > 0:
                if message is not None:
                    message += "[通緝查詢]有資料符合\n連結： " + "https://www.thcw.moj.gov.tw/CriminalWanted/Home/Query"
                else:
                    message = "[通緝查詢]有資料符合\n連結： " + "https://www.thcw.moj.gov.tw/CriminalWanted/Home/Query"
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        error_msg = "function: fugitive, line: " + str(lineNum) + ", detail: " + detail
        insert_error(conn, error_msg)
        logging.error(error_msg)
    return message


def ius(_id, id_card, name, conn):
    message = None
    try:
        logging.info("通緝要犯 %s, %s" % (_id, id_card))
        # print("通緝要犯 %s, %s" % (_id, id_card))
        cursor = conn.cursor()
        sql = "SELECT link, member_id FROM cib_list WHERE member_name=%s and member_id=%s;"
        cursor.execute(sql, (name, id_card))
        result = cursor.fetchone()
        if result is None:
            pass
        else:
            link = result[0]
            message = "[重要緊急查緝]有資料符合\n連結： " + link + " \n"
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        error_msg = "function: ius, line: " + str(lineNum) + ", detail: " + detail
        insert_error(conn, error_msg)
    return message


def zez_npa(_id, id_card, name, conn):
    message = None
    try:
        # print("查捕中逃犯 %s, %s" % (_id, id_card))
        logging.info("查捕中逃犯 %s, %s" % (_id, id_card))
        main_url = 'https://eze8.npa.gov.tw/NpaE8ServerRWD/CE_Query.jsp'
        RequestVerificationToken = ""
        s = requests.session()
        page = s.get(main_url)
        soup = BeautifulSoup(page.text, 'html.parser')
        img_url = "https://eze8.npa.gov.tw/NpaE8ServerRWD/CheckCharImgServlet?"
        # print(img_url)
        img = s.get(img_url)
        with open('captcha.jpg', 'wb') as file:
            file.write(img.content)
        # # 下載圖片到本機
        code = tow_c.get_tow_c()
        data = {
            'ajaxAction': 'ceCheckCaptcha',
            'browser': 'Chrome 118',
            'answer': code,
            'QS_NAME': name,
            'QS_ID': id_card,
            'FUNC_NAME': 'CE'
        }
        page = s.post("https://eze8.npa.gov.tw/NpaE8ServerRWD/CaseQueryServlet", data=data)
        decoded_str = html.unescape(json.loads(page.text).get('formData'))

        # 將解碼後的字串轉換成 JSON
        json_data = json.loads(decoded_str)
        for r in json_data:
            E8_WT_UNIT_NM = r.get("E8_WT_UNIT_NM")
            if E8_WT_UNIT_NM is not None:
                if E8_WT_UNIT_NM == "查無資料":
                    pass
                else:
                    message = "[查捕逃犯]有資料符合\n連結： " + "https://eze8.npa.gov.tw/NpaE8ServerRWD/CE_Query.jsp"
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        error_msg = "function: zez_npa, line: " + str(lineNum) + ", detail: " + detail
        insert_error(conn, error_msg)
        logging.error(error_msg)
    return message


def mvdis(_id, id_card, birthday, conn):
    times = 0
    retry = 0
    money = 0
    soup = None
    try:
        while True:
            time.sleep(3)
            if retry > max_retry:
                break
            retry += 1
            birthday = birthday.replace("-", "")
            # print("查詢欠繳罰單 %s, %s, %s" % (_id, id_card, birthday))
            logging.info("查詢欠繳罰單 %s, %s, %s" % (_id, id_card, birthday))
            headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
                       'Host': 'www.mvdis.gov.tw',
                       'Referer': 'https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay?method=pagination'
                       }

            s = requests.session()
            page = s.get('https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay')
            soup = BeautifulSoup(page.text, 'html.parser')
            img_url = 'https://www.mvdis.gov.tw' + soup.find('img', {'id': 'pickimg1'}).get('src').strip()
            img = s.get(img_url)
            with open('captcha.jpg', 'wb') as file:
                file.write(img.content)
            code = tow_c.get_tow_c()
            data = {
                'stage': 'natural',
                'method': 'queryPerson',
                'uid': id_card,
                'birthday': birthday,
                'validateStr': code.upper()
            }
            # 不可線上繳納
            page = s.post('https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay', data=data)
            soup = BeautifulSoup(page.text, 'html.parser')
            if "查無可線上繳納罰單資料" in soup.text.strip():
                break
            if soup.find('div', {'id': 'disbanner'}) is not None:
                break
        if soup.find('div', {'id': 'disbanner'}) is not None:
            for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='odd'):
                money += int(r.find_all('td')[3].text)
                times += 1
            for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='even'):
                money += int(r.find_all('td')[3].text)
                times += 1

            for i in range(2, 20):
                page = s.get('https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay?d-49440-p=%s&method=pagination' % i, headers=headers)
                soup = BeautifulSoup(page.text, 'html.parser')
                disbanner = soup.find('div', {'id': 'disbanner'})
                if disbanner is None:
                    break
                for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='odd'):
                    times += 1
                    money += int(r.find_all('td')[3].text)
                for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='even'):
                    money += int(r.find_all('td')[3].text)
                    times += 1

            # 不可線上繳納
            page = s.get('https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay?method=nopayPagination')
            soup = BeautifulSoup(page.text, 'html.parser')
            if soup.find('div', {'id': 'disbanner'}) is not None:
                for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='odd'):
                    money += int(r.find_all('td')[3].text)
                    times += 1
                for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='even'):
                    money += int(r.find_all('td')[3].text)
                    times += 1

                for i in range(2, 20):
                    page = s.get(f'https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay?method=nopayPagination&d-2637073-p={i}', headers=headers)
                    soup = BeautifulSoup(page.text, 'html.parser')
                    disbanner = soup.find('div', {'id': 'disbanner'})
                    if disbanner is None:
                        break
                    for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='odd'):
                        money += int(r.find_all('td')[3].text)
                        times += 1
                    for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='even'):
                        money += int(r.find_all('td')[3].text)
                        times += 1
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        error_msg = "function: mvdis, line: " + str(lineNum) + ", detail: " + detail
        insert_error(conn, error_msg)
        logging.error(error_msg)
    if money > 0:
        return "%s筆/%s元" % (str(times), str(money)) + "\n" + "https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay"
    else:
        return None


def mvdis_two(_id, id_card, birthday, conn):
    soup = None
    times = 0
    retry = 0
    money = 0
    soup = None
    try:
        while True:
            birthday = birthday.replace("-", "")
            # print("查詢燃料費 %s, %s, %s" % (_id, id_card, birthday))
            # logging.info("查詢燃料費 %s, %s, %s" % (_id, id_card, birthday))
            time.sleep(3)
            if retry > max_retry:
                break
            retry += 1
            headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
                       'Host': 'www.mvdis.gov.tw',
                       'Referer': 'https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay'
                       }
            s = requests.session()
            s.get('https://www.mvdis.gov.tw/m3-emv-fee/fee/fuelFee')
            # soup = BeautifulSoup(page.text, 'html.parser')
            img_url = "https://www.mvdis.gov.tw/m3-emv-fee/captchaImg.jpg?"
            img = s.get(img_url)
            with open('captcha.jpg', 'wb') as file:
                file.write(img.content)
            code = tow_c.get_tow_c()
            data = {
                'method': 'queryCheck',
                'queryType': 1,
                'idNo': id_card,
                'birthday': birthday,
                'validateStr': code.upper()
            }
            page = s.post('https://www.mvdis.gov.tw/m3-emv-fee/fee/fuelFee', data=data)
            soup = BeautifulSoup(page.text, 'html.parser')
            if "查無須繳納之汽燃費及罰鍰" in soup.text.strip():
                break
            if soup.find('div', {'id': 'disbanner'}) is not None:
                break
        # 不可線上繳納
        if soup.find('div', {'id': 'disbanner'}) is not None:
            for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='odd'):
                for td in r.find_all('td'):
                    try:
                        money += int(td.text.strip().replace(' ', ''))
                        break
                    except:
                        pass
                # money += int(r.find_all('td')[3].strip().text)
                times += 1
            for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='even'):
                for td in r.find_all('td'):
                    try:
                        money += int(td.text.strip().replace(' ', ''))
                        break
                    except:
                        pass
                # money += int(r.find_all('td')[3].strip().text)
                times += 1

            for i in range(2, 20):
                page = s.get('https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay?d-49440-p=%s&method=pagination' % i, headers=headers)
                soup = BeautifulSoup(page.text, 'html.parser')
                disbanner = soup.find('div', {'id': 'disbanner'})
                if disbanner is None:
                    break
                for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='odd'):
                    for td in r.find_all('td'):
                        try:
                            money += int(td.text.strip().replace(' ', ''))
                            break
                        except:
                            pass
                    # money += int(r.find_all('td')[3].strip().text)
                    times += 1
                for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='even'):
                    for td in r.find_all('td'):
                        try:
                            money += int(td.text.strip().replace(' ', ''))
                            break
                        except:
                            pass
                    # money += int(r.find_all('td')[3].strip().text)
                    times += 1

        # 可線上繳納
        page = s.get('https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay?method=pagination')
        soup = BeautifulSoup(page.text, 'html.parser')
        if soup.find('div', {'id': 'disbanner'}) is not None:
            for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='odd'):
                for td in r.find_all('td'):
                    try:
                        money += int(td.text.strip().replace(' ', ''))
                        break
                    except:
                        pass
                # money += int(r.find_all('td')[3].strip().text)
                times += 1
            for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='even'):
                for td in r.find_all('td'):
                    try:
                        money += int(td.text.strip().replace(' ', ''))
                        break
                    except:
                        pass
                # money += int(r.find_all('td')[3].strip().text)
                times += 1

            for i in range(2, 20):
                page = s.get('https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay?d-49440-p=%s&method=pagination' % i, headers=headers)
                soup = BeautifulSoup(page.text, 'html.parser')
                disbanner = soup.find('div', {'id': 'disbanner'})
                if disbanner is None:
                    break
                for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='odd'):
                    for td in r.find_all('td'):
                        try:
                            money += int(td.text.strip().replace(' ', ''))
                            break
                        except:
                            pass
                    # money += int(r.find_all('td')[3].strip().text)
                    times += 1
                for r in soup.find('div', {'id': 'disbanner'}).find_all('tr', class_='even'):
                    for td in r.find_all('td'):
                        try:
                            money += int(td.text.strip().replace(' ', ''))
                            break
                        except:
                            pass
                    # money += int(r.find_all('td')[3].strip().text)
                    times += 1
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        error_msg = "function: mvdis_two, line: " + str(lineNum) + ", detail: " + detail
        # insert_error(conn, error_msg)
        logging.error(error_msg)
    if money > 0:
        return "%s筆/%s元" % (str(times), str(money)) + "\n" + "https://www.mvdis.gov.tw/m3-emv-fee/fee/fuelFee"
    else:
        return None


def jud(name, conn):
    hitSize = 0
    times = 0
    try:
        logging.info(f'{name} 查詢判書')
        main_url = "https://judgment.judicial.gov.tw/FJUD/default.aspx"
        state_dict = {}
        main_page = get_page(main_url)
        if main_page is not None:
            soup = BeautifulSoup(main_page.content, 'html.parser')
            __VIEWSTATE = soup.find('input', {'name': '__VIEWSTATE'}).get('value')
            __VIEWSTATEGENERATOR = soup.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value')
            __EVENTVALIDATION = soup.find('input', {'name': '__EVENTVALIDATION'}).get('value')
            state_dict['VIEWSTATE'] = __VIEWSTATE
            state_dict['VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
            state_dict['EVENTVALIDATION'] = __EVENTVALIDATION

            judtype = "JUDBOOK"
            whosub = 0
            SimpleQry = "送出查詢"
            req_data = {
                '__VIEWSTATE': state_dict['VIEWSTATE'],
                '__VIEWSTATEGENERATOR': state_dict['VIEWSTATEGENERATOR'],
                '__EVENTVALIDATION': state_dict['EVENTVALIDATION'],
                'judtype': judtype,
                'whosub': whosub,
                'jud_kw': name,
                'ctl00$cp_content$btnSimpleQry': SimpleQry
            }
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
            page = requests.post("https://judgment.judicial.gov.tw/FJUD/default.aspx", data=req_data, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            hitSize = int(soup.select('.badge')[0].text)
            if hitSize > 20:
                query = soup.select('#iframe-data')[0]['src']
                r = requests.get('https://judgment.judicial.gov.tw/FJUD/%s' % query, headers=headers)
                soup = BeautifulSoup(r.content, features="html.parser")
                allPage = int(soup.find('div', class_='pull-right').find('span').text.split()[7])
                if hitSize > 499:
                    allPage = 24
                nextPage = soup.find('a', class_='page')['href']
                # 第一頁往第二頁連結
                nextPage = nextPage.replace('page=2', '%s')
                for page_index in range(1, allPage):
                    nextPageUrl = nextPage % ('page=%s' % (page_index))
                    page = requests.get('https://judgment.judicial.gov.tw/%s' % nextPageUrl, headers=headers)
                    if page is not None:
                        soup = BeautifulSoup(page.content, 'html.parser')
                        link_objs = soup.find('table', class_='jub-table').find_all('tr', class_='summary')
                        if link_objs is not None:
                            for link_obj in link_objs:
                                parser_str = link_obj.text.strip()
                                if "被告" + name in parser_str:
                                    times += 1
                    time.sleep(4)
            elif hitSize < 21 and hitSize != 0:
                query = soup.select('#iframe-data')[0]['src']
                page = requests.get('https://judgment.judicial.gov.tw/FJUD/%s' % query, headers=headers)
                if page is not None:
                    soup = BeautifulSoup(page.content, 'html.parser')
                    link_objs = soup.find('table', class_='jub-table').find_all('tr', class_='summary')
                    if link_objs is not None:
                        for link_obj in link_objs:
                            parser_str = link_obj.text.strip()
                            if "被告" + name in parser_str:
                                times += 1
            time.sleep(random.randint(3, 6))
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        error_msg = "function: jud, line: " + str(lineNum) + ", detail: " + detail
        insert_error(conn, error_msg)
        logging.error(error_msg)
    if times > 0:
        return "[裁判書判決]有資料符合[被告]\n總數:" + str(times) + "\n連結: https://judgment.judicial.gov.tw/FJUD/default.aspx"
    else:
        return None


def jud_money(name, conn):
    hitSize = 0
    try:
        logging.info(f'{name} 查詢判決金額')
        main_url = "https://judgment.judicial.gov.tw/FJUD/default.aspx"
        state_dict = {}
        main_page = get_page(main_url)
        if main_page is not None:
            soup = BeautifulSoup(main_page.content, 'html.parser')
            __VIEWSTATE = soup.find('input', {'name': '__VIEWSTATE'}).get('value')
            __VIEWSTATEGENERATOR = soup.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value')
            __EVENTVALIDATION = soup.find('input', {'name': '__EVENTVALIDATION'}).get('value')
            state_dict['VIEWSTATE'] = __VIEWSTATE
            state_dict['VIEWSTATEGENERATOR'] = __VIEWSTATEGENERATOR
            state_dict['EVENTVALIDATION'] = __EVENTVALIDATION

            judtype = "JUDBOOK"
            whosub = 0
            SimpleQry = "送出查詢"
            req_data = {
                '__VIEWSTATE': state_dict['VIEWSTATE'],
                '__VIEWSTATEGENERATOR': state_dict['VIEWSTATEGENERATOR'],
                '__EVENTVALIDATION': state_dict['EVENTVALIDATION'],
                'judtype': judtype,
                'whosub': whosub,
                'jud_kw': name,
                'jud_jmain': '消債',
                'ctl00$cp_content$btnSimpleQry': SimpleQry
            }
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36'}
            page = requests.post("https://judgment.judicial.gov.tw/FJUD/default.aspx", data=req_data, headers=headers)
            soup = BeautifulSoup(page.content, 'html.parser')
            hitSize = int(soup.select('.badge')[0].text)
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        error_msg = "function: jud_money, line: " + str(lineNum) + ", detail: " + str(detail)
        print(error_msg)
        insert_error(conn, error_msg)
        logging.error(error_msg)
    if hitSize > 0:
        return "[裁判書消債判決]有資料符合\n總數:" + str(hitSize) + "\n連結: https://judgment.judicial.gov.tw/FJUD/default.aspx"
    else:
        return None


def get_age(birthday):
    # 取得當前日期時間
    current_date = datetime.now()
    provided_date = datetime.strptime(str(int(birthday.split('-')[0]) + 1911) + '-' + birthday.split('-')[1] + '-' + birthday.split('-')[2], "%Y-%m-%d")
    # 計算年齡
    age = current_date.year - provided_date.year - ((current_date.month, current_date.day) < (provided_date.month, provided_date.day))
    return age


def execute():
    conn = None
    cursor = None
    try:
        print("check start")
        conn = connection.connect_to_mysql()
        cursor = conn.cursor()
        sql = "SELECT name, Identity_id, birthday, id FROM member WHERE crawler_status=0 or crawler_status=1 limit 1;"
        cursor.execute(sql)
        row = cursor.fetchone()
        if row is not None:
            all_msg = ""
            all_money = 0  # 總欠繳金額
            name = row[0]
            id_card = row[1]
            birthday = row[2]
            _id = row[3]

            sql = "UPDATE member SET crawler_status=1 WHERE Identity_id=%s;"
            cursor.execute(sql, (id_card,))
            conn.commit()

            fugitive_msg = fugitive(_id, id_card, name, conn)  # 查緝專刊
            ius_msg = ius(_id, id_card, name, conn)  # 通緝要犯
            zez_npa_msg = zez_npa(_id, id_card, name, conn)  # 查捕中逃犯
            mvdis_msg = mvdis(_id, id_card, birthday, conn)  # 查欠繳交通罰單
            if mvdis_msg is not None:
                all_money += int(mvdis_msg.split("/")[1].split('元')[0])
            mvdis_two_msg = mvdis_two(_id, id_card, birthday, conn)  # 查個人汽燃費查詢
            if mvdis_two_msg is not None:
                all_money += int(mvdis_two_msg.split("/")[1].split('元')[0])
            jud_msg = jud(name, conn)  # 裁判書判決
            jud_money_msg = jud_money(name, conn)  # 裁判書消債判決
            if fugitive_msg is not None:
                fugitive_msg = fugitive_msg.rstrip("\n")
            else:
                fugitive_msg = "查無資料"
            if ius_msg is not None:
                ius_msg = ius_msg.rstrip("\n")
            else:
                ius_msg = "查無資料"
            if zez_npa_msg is not None:
                zez_npa_msg = zez_npa_msg.rstrip("\n")
            else:
                zez_npa_msg = "查無資料"
            if mvdis_msg is not None:
                mvdis_msg = mvdis_msg.rstrip("\n")
            else:
                mvdis_msg = "查無資料"
            if mvdis_two_msg is not None:
                mvdis_two_msg = mvdis_two_msg.rstrip("\n")
            else:
                mvdis_two_msg = "查無資料"
            if jud_msg is not None:
                jud_msg = jud_msg.rstrip("\n")
                all_msg += "「疑似有刑事紀錄，詳見下列連結，應進一步驗證」\n"
            else:
                jud_msg = "查無資料"
            if jud_money_msg is not None:
                jud_money_msg = jud_money_msg.rstrip("\n")
                all_msg += "「疑似有消債紀錄，詳見下列連結，應進一步驗證」\n"
            else:
                jud_money_msg = "查無資料"
            if all_money > 0:
                all_msg += "「有欠繳%s元，應注意繳款能力」\n" % all_money
            member_age = get_age(birthday)
            if member_age > 80:
                all_msg += "「%s歲，年齡偏高，應提供親友為租約保人及緊急聯絡人」\n" % str(get_age(birthday))
            if 64 < member_age < 80:
                all_msg += "「%s歲，年齡偏高，應提供親友為租約保人及緊急聯絡人」\n" % str(get_age(birthday))
            if all_msg == "":
                all_msg = "查無資料"
            else:
                all_msg = all_msg.rstrip("\n")
            json_data = {
                "黑名單": jud_msg,
                "交通罰緩": mvdis_msg,
                "查緝專刊": fugitive_msg,
                "消債事件": jud_money_msg,
                "通緝要犯": ius_msg,
                "查捕中逃犯": zez_npa_msg,
                "汽車燃料稅": mvdis_two_msg,
                "公司內部黑名單": "查無資料",
                "綜合評分": all_msg
            }
            sql = "select * from search_history where member_id=%s;"
            cursor.execute(sql, (_id,))
            result = cursor.fetchall()
            if len(result) > 0:
                sql = "UPDATE search_history SET result_data= %s WHERE member_id=%s;"
                cursor.execute(sql, (json.dumps(json_data), _id))
            else:
                sql = "insert into search_history (result_data, member_id) values (%s, %s) ;"
                cursor.execute(sql, (json.dumps(json_data), _id))
            sql = "UPDATE member SET crawler_status=2 WHERE Identity_id=%s;"
            cursor.execute(sql, (id_card,))
            conn.commit()
        conn.close()
    except Exception as e:
        lineNum, detail = exception_tool.exception_tool(e)
        error_msg = "function: check_people_work_execute, line: " + str(lineNum) + ", detail: " + str(detail)
        print(error_msg)
        insert_error(conn, error_msg)
    finally:
        if conn is not None:
            conn.close()
        if cursor is not None:
            cursor.close()
    time.sleep(10)


if __name__ == '__main__':
    while True:
        try:
            execute()
        except Exception as e:
            pass
            # lineNum, detail = exception_tool.exception_tool(e)
            # error_msg = "function: check_people_work, line: " + str(lineNum) + ", detail: " + str(detail)
            # print(error_msg)
