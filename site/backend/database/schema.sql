CREATE TABLE IF NOT EXISTS suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (length(trim(name)) BETWEEN 2 AND 80),
    email TEXT NOT NULL CHECK (length(email) <= 254),
    suggestion TEXT NOT NULL CHECK (length(trim(suggestion)) BETWEEN 10 AND 2000),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
