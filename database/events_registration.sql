CREATE DATABASE IF NOT EXISTS event_registrations_database;
USE event_registrations_database;

CREATE TABLE IF NOT EXISTS event_registrations (
    registration_id CHAR(36) NOT NULL PRIMARY KEY DEFAULT (UUID()),
    event_id CHAR(36) NOT NULL,
    user_id VARCHAR(50) NOT NULL,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (event_id, user_id)
);