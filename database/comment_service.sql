CREATE DATABASE IF NOT EXISTS comment_service;
USE comment_service;

CREATE TABLE IF NOT EXISTS comments (
    comment_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    post_id CHAR(36) NOT NULL,
    author_id CHAR(36) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'published'
);
