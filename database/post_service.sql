CREATE DATABASE IF NOT EXISTS post_service;
USE post_service;

CREATE TABLE IF NOT EXISTS posts (
    post_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    community_id CHAR(36) NOT NULL,
    author_id VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'published'
);
