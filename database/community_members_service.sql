CREATE DATABASE IF NOT EXISTS community_members_service;
USE community_members_service;

CREATE TABLE IF NOT EXISTS community_members (
    community_id CHAR(36) NOT NULL,
    user_id char(36) NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status VARCHAR(20) DEFAULT 'is_in',
    PRIMARY KEY (community_id, user_id)
);
