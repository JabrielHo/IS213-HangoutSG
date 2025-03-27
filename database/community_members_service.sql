CREATE DATABASE IF NOT EXISTS community_members_service;
USE community_members_service;

CREATE TABLE IF NOT EXISTS community_members (
    community_id INT NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (community_id, user_id)
);
