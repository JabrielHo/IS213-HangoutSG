CREATE DATABASE IF NOT EXISTS community_service;
USE community_service;

CREATE TABLE IF NOT EXISTS communities (
    community_id CHAR(36) PRIMARY KEY DEFAULT (UUID()),
    name VARCHAR(21) NOT NULL,
    description TEXT NOT NULL,
    creator_id VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
