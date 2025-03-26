CREATE DATABASE IF NOT EXISTS content_moderation;
USE content_moderation;

CREATE TABLE IF NOT EXISTS flagged (
    flag_id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NULL,
    comment_id INT NULL,
    flagged_by VARCHAR(50) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);