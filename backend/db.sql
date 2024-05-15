-- 创建数据库
DROP DATABASE IF EXISTS rgfs;
CREATE DATABASE IF NOT EXISTS rgfs;

-- 使用数据处理工具
USE rgfs;


-- 創建搜尋紀錄（人）
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS member;
CREATE TABLE member
(
    id             INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(255) NOT NULL,
    birthday       TEXT         NOT NULL,
    Identity_id    TEXT         NOT NULL,
    is_bad         BOOLEAN      NOT NULL DEFAULT FALSE,
    cus            TEXT         NUll,
    crawler_status INT          NOT NULL DEFAULT 0,
    created_at     TIMESTAMP    NOt NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP    NOt NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY idx_Identity_id (Identity_id(255)) -- 使用前綴索引
);


-- 創建搜尋紀錄
DROP TABLE IF EXISTS images;
DROP TABLE IF EXISTS search_history;
CREATE TABLE search_history
(
    id          INT AUTO_INCREMENT PRIMARY KEY,
    member_id   INT  NOT NULL,
    result_data JSON NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES member (id)
);

-- 通通緝犯列表
DROP TABLE IF EXISTS crimes_list;
CREATE TABLE crimes_list
(
    id          INT AUTO_INCREMENT PRIMARY KEY,
    member_id   VARCHAR(255) NOT NULL,
    member_name VARCHAR(255) NOT NULL,
    link        VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 通通緝犯列表
DROP TABLE IF EXISTS cib_list;
CREATE TABLE cib_list
(
    id          INT AUTO_INCREMENT PRIMARY KEY,
    member_id   VARCHAR(255) NOT NULL,
    member_name VARCHAR(255) NOT NULL,
    link        VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS error_log;
CREATE TABLE error_log
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    e_str         TEXT         NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);