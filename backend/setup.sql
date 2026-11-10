CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    hashed_password TEXT NOT NULL
);

-- Usernames are unique regardless of case, so "Ada" and "ada" are the same account.
CREATE UNIQUE INDEX users_username_lower_key ON users (LOWER(username));

CREATE TABLE lesson_progress (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    lesson_id TEXT NOT NULL,
    exercise_id TEXT NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    code TEXT DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (user_id, lesson_id, exercise_id)
);