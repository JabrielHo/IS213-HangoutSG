CREATE DATABASE IF NOT EXISTS event_registrations_database;
USE event_registrations_database;

CREATE TABLE event_registrations (
    registration_id CHAR(36) NOT NULL PRIMARY KEY,
    event_id CHAR(36) NOT NULL PRIMARY KEY,
    user_id CHAR(36) NOT NULL PRIMARY KEY,
    registered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (event_id, user_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES auth0(user_id) ON DELETE CASCADE
);