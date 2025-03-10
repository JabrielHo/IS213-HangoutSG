CREATE DATABASE IF NOT EXISTS inbox_service;
USE inbox_service;

CREATE TABLE IF NOT EXISTS inbox (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    receiver_id VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'unread'
);