CREATE DATABASE IF NOT EXISTS post_service;
USE post_service;

CREATE TABLE IF NOT EXISTS posts (
    post_id CHAR(36) PRIMARY KEY,
    community_id CHAR(36) NOT NULL,
    author_id CHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'published'
);
