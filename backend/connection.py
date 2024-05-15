import os

import mysql.connector

host = os.environ.get("MYSQL_HOST", '')
port = int(os.environ.get("MYSQL_PORT", '3306'))
username = os.environ.get("MYSQL_USER", 'root')
password = os.environ.get("MYSQL_PASSWORD", '')
database = os.environ.get("MYSQL_DATABASE", '')


def connect_to_mysql():
    try:
        # 建立連線
        connection = mysql.connector.connect(
            host=host,
            port=port,
            user=username,
            password=password,
            database=database
        )

        if connection.is_connected():
            # 顯示連線資訊
            # print("已成功連接至MySQL資料庫")
            # print("主機:", host)
            # print("資料庫:", database)

            # 回傳連線物件
            return connection

    except mysql.connector.Error as error:
        # 連線失敗時顯示錯誤訊息
        print("連接失敗:", error)

    # 若連線失敗則回傳None
    return None


def close_connection(connection):
    # 關閉連線
    if connection.is_connected():
        connection.close()
        # print("已關閉MySQL資料庫連線")
