CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    birth_date DATE NOT NULL,
    age INTEGER
);

CREATE TABLE IF NOT EXISTS user_messages (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    message TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_user_messages_user_id
        FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_users_birth_date ON users (birth_date);

COMMENT ON TABLE users IS '用户主表：预置用户出生日期，接口会回写age';
COMMENT ON TABLE user_messages IS '用户消息表：按user_id唯一存储一条消息';
