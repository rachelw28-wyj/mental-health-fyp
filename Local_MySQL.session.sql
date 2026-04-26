USE mental_health_db;

CREATE TABLE User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('Patient', 'Professional') NOT NULL DEFAULT 'Patient',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Chat_History (
    msg_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    sender ENUM('User', 'Bot') NOT NULL,
    message_text TEXT NOT NULL,
    sentiment_score FLOAT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

CREATE TABLE Mood_Logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    mood_rating INT NOT NULL CHECK (mood_rating BETWEEN 1 AND 5),
    primary_emotion VARCHAR(50) NOT NULL,
    note TEXT,
    log_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

CREATE TABLE Journal_Entries (
    journal_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(100),
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);

CREATE TABLE Crisis_Events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    trigger_word VARCHAR(50) NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    action_taken VARCHAR(100) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);