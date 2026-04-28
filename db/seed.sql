-- 预置用户数据（用于压测前初始化）
INSERT INTO users (user_id, birth_date, age)
VALUES
    (1001, '1998-05-20', NULL),
    (1002, '1995-10-01', NULL),
    (1003, '2000-01-15', NULL)
ON CONFLICT (user_id) DO UPDATE SET
    birth_date = EXCLUDED.birth_date;

-- 可选：预置消息数据
INSERT INTO user_messages (user_id, message)
VALUES
    (1001, 'seed message 1001')
ON CONFLICT (user_id) DO UPDATE SET
    message = EXCLUDED.message,
    updated_at = NOW();
