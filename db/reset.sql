-- 压测前重置脚本
-- 作用：
-- 1) 清理消息与年龄回写结果
-- 2) 回填固定规模基线用户（20000）

BEGIN;

-- 先清理依赖表，再清理用户表
TRUNCATE TABLE user_messages RESTART IDENTITY;
TRUNCATE TABLE users;

-- 回填 20000 个用户：1003 ~ 21002，随机生日
SELECT setseed(0.2026);

INSERT INTO users (user_id, birth_date, age)
SELECT
    gs.user_id,
    DATE '1970-01-01' + (trunc(random() * (DATE '2005-12-31' - DATE '1970-01-01' + 1)))::int,
    NULL
FROM generate_series(1003, 21002) AS gs(user_id);

-- 可选基线消息（可重复执行）
INSERT INTO user_messages (user_id, message)
VALUES
    (1003, 'seed message 1003')
ON CONFLICT (user_id) DO UPDATE SET
    message = EXCLUDED.message,
    updated_at = NOW();

COMMIT;
