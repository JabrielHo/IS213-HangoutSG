CREATE DATABASE IF NOT EXISTS community_service;
USE community_service;

CREATE TABLE IF NOT EXISTS communities (
    community_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    creator_id VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
