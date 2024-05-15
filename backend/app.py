# coding=UTF-8
import datetime
import json
import re
import subprocess
import threading
import time

import requests

import connection
import os
from crawler import crimes_list_crawler as crimes_list_crawler
from crawler import cib_list as cib_list_crawler
import check_people_work
from flask_cors import CORS
from flask import Flask, jsonify, request
from gevent.pywsgi import WSGIServer

# import exception_tool

# reader = easyocr.Reader(['ch_tra', 'en'], gpu=True)  # 選擇語言

app = Flask(__name__)
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(seconds=86400)
app.config['JSON_AS_ASCII'] = False  # UTF-8 support
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'SECRET_KEY')

LISTEN_PORT = os.environ.get("LISTEN_PORT", '8888')  # 監聽默认8888
CORS(app)

# 定義需要啟動和監控的程序列表
programs_to_monitor = [
    "python check_people_work.py",
]


def validate_taiwan_id(id_number):
    # 定義地區英文轉換成對應的數字的字典
    region_dict = {'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15,
                   'G': 16, 'H': 17, 'J': 18, 'K': 19, 'L': 20, 'M': 21,
                   'N': 22, 'P': 23, 'Q': 24, 'R': 25, 'S': 26, 'T': 27,
                   'U': 28, 'V': 29, 'X': 30, 'Y': 31, 'W': 32, 'Z': 33,
                   'I': 34, 'O': 35}

    # 檢查身分證字號是否符合規則
    if len(id_number) == 10:
        # 將地區英文轉換成對應的數字
        region_num = region_dict.get(id_number[0], None)
        # print(region_num)
        if region_num is not None:
            id_str = str(region_num) + str(id_number[1:])
            weights = [1, 9, 8, 7, 6, 5, 4, 3, 2, 1]
            sum = 0
            for index, v in enumerate(id_str):
                if index == 10:
                    break
                sum += int(v) * weights[index]
                print(index, v)
            if (sum + int(id_str[-1])) % 10 == 0:
                return True
    return False


def check_format(input_str):
    pattern = re.compile(r'^[A-Za-z]\d{9}$')
    return bool(pattern.match(input_str))


def ocr_space_file(filename, overlay=False, api_key='helloworld', language='eng'):
    payload = {'isOverlayRequired': False,
               'apikey': api_key,
               'language': language,
               'FileType': '.Auto',
               'IsCreateSearchablePDF': False,
               'isSearchablePdfHideTextLayer': True,
               'detectOrientation': False,
               'isTable': False,
               'scale': True,
               'OCREngine': '1',
               'detectCheckbox': False,
               'checkboxTemplate': '0'
               }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )
    return r.content.decode()


@app.route('/api', methods=['GET'])
def index():
    result = "test04"
    return jsonify(status=True, message=result), 200
    # return Response(result), 200


@app.route('/api/ocr', methods=['POST'])
def ocr():
    # 檢查請求中是否有檔案
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    # 檢查檔案名稱是否有效
    if file.filename == '':
        return jsonify({'error': 'Invalid file name'}), 400
    file.save(file.filename)
    text = ocr_space_file(filename=file.filename, language='cht')
    os.remove(file.filename)
    text = text.replace(' ', '').strip()
    ocr_data = json.loads(text)
    text = ocr_data['ParsedResults'][0].get('ParsedText').replace(' ', '').replace('\r\n', '').strip()
    print(text)
    name_pattern = re.compile(r'姓名([^\d]+)')
    bd_pattern = re.compile(r'出生民國(\d+)年(\d+)月(\d+)日')
    id_pattern = r'([A-Z]\d{9})'  # 匹配身分證號
    dob_match = bd_pattern.search(text)
    name_match = name_pattern.search(text)
    id_match = re.search(id_pattern, text)
    # 提取匹配到的資訊
    name = name_match.group(1)[:3] if name_match else "未找到姓名"
    year, month, day = dob_match.groups() if dob_match else ("", "", "")
    id_number = id_match.group(1) if id_match else "未找到身分證號"
    # 格式化生日為六位數字
    formatted_dob = f"{year.zfill(3)}-{month.zfill(2)}-{day.zfill(2)}"
    # 構建輸出訊息
    output_message = {
        "message": {
            "birthday_y": formatted_dob.split('-')[0],
            "birthday_m": formatted_dob.split('-')[1],
            "birthday_d": formatted_dob.split('-')[2],
            "birthday": formatted_dob,
            "id": id_number,
            "name": name
        }
    }
    return jsonify(status=True, message=output_message), 200


@app.route('/api/upload', methods=['POST'])
def upload():
    req_data = json.loads(request.data)
    name = req_data.get('name', None)
    birthday = req_data.get('birthday', None)
    identity_id = req_data.get('identity_id', None)
    if not check_format(identity_id):
        return jsonify(status=False, message='身分證號格式錯誤'), 400
    if name is None or birthday is None or identity_id is None:
        return jsonify(status=False, message='缺少必要參數'), 400
    if not validate_taiwan_id(identity_id):
        return jsonify(status=False, message='身分證號錯誤'), 400
    conn = connection.connect_to_mysql()
    cursor = conn.cursor()
    sql = "SELECT * FROM member WHERE Identity_id = %s;"
    cursor.execute(sql, (identity_id,))
    result = cursor.fetchone()
    if result is not None:
        sql = "update member set name= %s, birthday= %s, crawler_status=0 where Identity_id = %s;"
        cursor.execute(sql, (name, birthday, identity_id))
    else:
        sql = "INSERT INTO member (name, birthday, Identity_id) VALUES (%s, %s, %s)"
        cursor.execute(sql, (name, birthday, identity_id))
    conn.commit()
    return jsonify(status=True, message='上傳成功'), 200


@app.route('/api/people', methods=['POST'])
def people():
    req_data = json.loads(request.data)
    id_ = req_data.get('id_', None)
    is_bad = int(req_data.get('is_bad', None))
    cus = req_data.get('cus', None)
    if id_ is None or is_bad is None:
        return jsonify(status=False, message='缺少必要參數'), 400
    if is_bad == 1 and cus is None:
        return jsonify(status=False, message='缺少必要參數'), 400
    conn = connection.connect_to_mysql()
    cursor = conn.cursor()
    if is_bad == 1:
        sql = "UPDATE member SET is_bad = %s, cus=%s WHERE id = %s"
        cursor.execute(sql, (True, cus, id_))
    else:
        sql = "UPDATE member SET is_bad = %s WHERE id = %s"
        cursor.execute(sql, (False, id_))
    conn.commit()
    return jsonify(status=True, message='更新成功'), 200


@app.route('/api/list', methods=['GET'])
def people_list():
    type_ = request.args.get('type', None)
    if type_ is not None:
        type_ = int(type_)
    page = int(request.args.get('page', 1))
    if page < 1:
        page = 1
    page_limit = int(request.args.get('page_limit', 20))
    if page_limit is not None:
        page_limit = int(page_limit)
    # 計算起始索引
    start_index = (page - 1) * page_limit
    # if type_ is None:
    #     return jsonify(status=False, message='缺少必要參數'), 400
    # if type_ != 0 and type_ != 1:
    #     return jsonify(status=False, message='參數錯誤'), 400
    conn = connection.connect_to_mysql()
    cursor = conn.cursor()
    if type_ is None:
        sql = "SELECT id, name, birthday, Identity_id, is_bad, crawler_status, cus FROM member ORDER BY updated_at DESC LIMIT %s OFFSET %s;"
        cursor.execute(sql, (page_limit, start_index))
        results = cursor.fetchall()
    else:
        sql = "SELECT id, name, birthday, Identity_id, is_bad, crawler_status, cus FROM member where is_bad=%s ORDER BY updated_at DESC LIMIT %s OFFSET %s;"
        cursor.execute(sql, (type_, page_limit, start_index))
        results = cursor.fetchall()
    if results is not None:
        datas = []
        for result in results:
            data = {}
            data['id_'] = result[0]
            data['姓名'] = result[1]
            data['生日'] = result[2]
            data['身份字號'] = result[3]
            if result[4] == 1:
                data['是否黑名單'] = True
            else:
                data['是否黑名單'] = False
            if result[6] is None:
                data['黑名單原因'] = ""
            else:
                data['黑名單原因'] = result[6]
            crawler_status = result[5]
            if crawler_status == 0:
                data['爬蟲狀態'] = '未執行'
            elif crawler_status == 1:
                data['爬蟲狀態'] = '執行中'
            elif crawler_status == 2:
                data['爬蟲狀態'] = '已完成'
            elif crawler_status == 3:
                data['爬蟲狀態'] = '失敗'
            sql = "SELECT result_data FROM search_history WHERE member_id=%s;"
            cursor.execute(sql, (result[0],))
            result = cursor.fetchone()
            if result is None:
                data['detail_data'] = None
            else:
                data['detail_data'] = json.loads(result[0])
            datas.append(data)
        return jsonify(status=True, message=datas), 200
    else:
        return jsonify(status=False, message='查無資料'), 400


@app.route('/api/del', methods=['POST'])
def del_people():
    req_data = json.loads(request.data)
    id_ = req_data.get('id_', None)
    if id_ is None:
        return jsonify(status=False, message='缺少必要參數'), 400
    conn = connection.connect_to_mysql()
    cursor = conn.cursor()
    sql = "DELETE FROM search_history WHERE member_id=%s;"
    cursor.execute(sql, (id_,))
    # conn.commit()
    sql = "DELETE FROM member WHERE id=%s;"
    cursor.execute(sql, (id_,))
    conn.commit()
    return jsonify(status=True, message='刪除成功'), 200


def run_script(script_name, *args):
    subprocess.Popen(["python", script_name, *args])


if __name__ == '__main__':
    while True:
        conn = None
        try:
            conn = connection.connect_to_mysql()
        except:
            pass
        if conn is not None:
            break
        time.sleep(5)
        # 啟動 schedule_tool.py 並傳遞程序列表作為參數
    subprocess.Popen(["python", "scheduler_tool.py"] + programs_to_monitor)
    # run_script('crawler/crimes_list_crawler.py')
    # run_script('crawler/cib_list.py')
    # run_script('check_people_work.py')
    # threading.Thread(target=crimes_list_crawler.execute).start()
    # threading.Thread(target=cib_list_crawler.execute).start()
    # threading.Thread(target=check_people_work.execute).start()
    # 啟動flask(套接Gevent高效能WSGI Server)
    http_server = WSGIServer(('0.0.0.0', int(LISTEN_PORT)), app)
    print('★★★★★★ 啟動Flask... port num : ' + LISTEN_PORT)
    http_server.serve_forever()
