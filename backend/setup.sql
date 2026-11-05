CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    hashed_password TEXT NOT NULL
);

CREATE TABLE lesson_progress (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    lesson_id TEXT NOT NULL,
    exercise_id TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    code TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);