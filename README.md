# 這是一個查詢個人有無污點紀錄的一個程式



技術線
---
- 網路爬蟲
    - 裁判書: https://judgment.judicial.gov.tw/FJUD/default.aspx
    - 通緝查詢: https://www.thcw.moj.gov.tw/CriminalWanted/#mainPage
    - 欠費: https://www.mvdis.gov.tw/m3-emv-vil/vil/penaltyQueryPay
- OCR辨識串接: https://2captcha.com/enterpage
- 後端api
    - flask
- 資料庫:
    - MySql
- 後端套件管理
    - poetry
- 網頁伺服器框架:
    - nginx
- 前端:
    - HTML
    - CSS
    - JavaScript
- 部署:
    - github Action
    - docker 容器化
    - docker compose 腳本

部署
---
- use docker compse > docekr build image > run continer
    - vim docker_compose.yml
    - docker compose -f docker_compose.yml up --build -d
```
version: '3'
services:
  app:
    container_name: flask_app
    build:
      context: ./app
      dockerfile: flask_dockerfile
    restart: always
    networks:
      - rgfs
    environment:
      - MYSQL_HOST=
      - MYSQL_PASSWORD=
      - MYSQL_PORT=
   nginx:
    build:
      context: .
      dockerfile: DockerfileNginx
    container_name: template_nginx
    ports:
      - "80:80"
      - "81:81"
      - "443:443"
    networks:
      - rgfs

networks:
  rgfs:
    driver: bridge
```
