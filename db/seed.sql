-- 初始化 20000 个用户
-- user_id 范围：1003 ~ 21002
-- birth_date：随机日期（1970-01-01 ~ 2005-12-31）
SELECT setseed(0.2026);

INSERT INTO users (user_id, birth_date, age)
SELECT
    gs.user_id,
    DATE '1970-01-01' + (trunc(random() * (DATE '2005-12-31' - DATE '1970-01-01' + 1)))::int,
    NULL
FROM generate_series(1003, 21002) AS gs(user_id)
ON CONFLICT (user_id) DO UPDATE SET
    birth_date = EXCLUDED.birth_date,
    age = NULL;

-- 可选：为首个用户准备一条基线消息
INSERT INTO user_messages (user_id, message)
VALUES
    (1003, 'seed message 1003')
ON CONFLICT (user_id) DO UPDATE SET
    message = EXCLUDED.message,
    updated_at = NOW();
