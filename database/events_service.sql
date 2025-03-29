CREATE DATABASE IF NOT EXISTS events_service;
USE events_service;

CREATE TABLE events (
    event_id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    community_id CHAR(36) NOT NULL,
    organizer_id VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    event_date DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    capacity INT
);
