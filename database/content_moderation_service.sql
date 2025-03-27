CREATE DATABASE IF NOT EXISTS content_moderation_service;
USE content_moderation_service;

CREATE TABLE IF NOT EXISTS flagged (
    flag_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    post_id CHAR(36) NULL,
    comment_id CHAR(36) NULL,
    flagged_by VARCHAR(50) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);