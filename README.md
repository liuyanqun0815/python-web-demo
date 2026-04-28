# Flask vs FastAPI 并发对照项目

本目录包含两个独立 API 项目，用于在相同 PostgreSQL 与相同业务逻辑下进行并发与 CPU 占用对比。
两个项目都使用 SQLAlchemy ORM 连接数据库并操作模型：

- Flask：同步 ORM Session（`Session` + `sessionmaker`）
- FastAPI：异步 ORM Session（`AsyncSession` + `async_sessionmaker`）

## 项目结构

- `db/init.sql`：数据库建表脚本
- `db/seed.sql`：初始化测试数据脚本
- `db/reset.sql`：压测前重置并回填基线数据脚本
- `flask_app/`：Flask（同步 SQLAlchemy + psycopg2）
- `fastapi_app/`：FastAPI（异步 SQLAlchemy + asyncpg）

## 业务逻辑（两项目一致）

`POST /api/user-message/process`

请求体：

```json
{
  "user_id": 1003,
  "message": "hello world"
}
```

处理流程：

1. 读取 `users` 表的 `birth_date`（若用户不存在返回 404）
2. 在 `user_messages` 表按 `user_id` 执行插入或更新
3. 按服务器本地日期计算周岁
4. 更新 `users.age`

成功响应示例：

```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "user_id": 1003,
    "action": "inserted",
    "age": 27
  }
}
```

## 数据库准备

1. 创建 PostgreSQL 数据库（示例使用 `postgres` 库）
2. 执行建表脚本：

```bash
psql -h 127.0.0.1 -U postgres -d postgres -f db/init.sql
```

3. 执行初始化数据脚本：

```bash
psql -h 127.0.0.1 -U postgres -d postgres -f db/seed.sql
```

4. 每轮压测前可执行重置脚本（推荐）：

```bash
psql -h 127.0.0.1 -U postgres -d postgres -f db/reset.sql
```

说明：
- `db/seed.sql` 会初始化 `20000` 个用户（`user_id` 从 `1003` 到 `21002`），生日随机。
- `db/reset.sql` 会清空并按同样规则重建这 `20000` 个用户，适合每轮压测前回到统一基线。

## 在 Linux 运行 Flask 项目

```bash
cd flask_app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/postgres
mkdir -p logs
nohup gunicorn -w 4 -k sync -b 0.0.0.0:5000 app:app > logs/flask-gunicorn.out 2>&1 &
echo $! > logs/flask-gunicorn.pid
```

默认端口：`5000`

## 在 Linux 运行 FastAPI 项目

```bash
cd fastapi_app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres
mkdir -p logs
nohup gunicorn -w 4 --threads 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app > logs/fastapi-gunicorn.out 2>&1 &
echo $! > logs/fastapi-gunicorn.pid
```

默认端口：`8000`

查看日志与进程：

```bash
tail -f flask_app/logs/flask-gunicorn.out
tail -f fastapi_app/logs/fastapi-gunicorn.out
cat flask_app/logs/flask-gunicorn.pid
cat fastapi_app/logs/fastapi-gunicorn.pid
```

## 在 Windows 运行（参考）

```bash
cd flask_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/postgres
gunicorn -w 4 -k sync -b 0.0.0.0:5000 app:app
```

```bash
cd fastapi_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres
gunicorn -w 4 --threads 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
```

## Linux 使用 systemd 托管（推荐）

假设项目目录为 `/opt/python_web_test`，运行用户为 `www-data`（请按你的服务器实际情况替换）。

1) 创建 Flask 服务文件 `/etc/systemd/system/flask-app.service`：

```ini
[Unit]
Description=Flask App Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/python_web_test/flask_app
Environment=DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/postgres
ExecStart=/opt/python_web_test/flask_app/.venv/bin/gunicorn -w 4 -k sync -b 0.0.0.0:5000 app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

2) 创建 FastAPI 服务文件 `/etc/systemd/system/fastapi-app.service`：

```ini
[Unit]
Description=FastAPI App Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/python_web_test/fastapi_app
Environment=DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres
ExecStart=/opt/python_web_test/fastapi_app/.venv/bin/gunicorn -w 4 --threads 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

3) 重新加载并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable flask-app fastapi-app
sudo systemctl restart flask-app fastapi-app
sudo systemctl status flask-app fastapi-app
```

4) 查看日志：

```bash
sudo journalctl -u flask-app -f
sudo journalctl -u fastapi-app -f
```

常见错误修复建议：
- `ExecStart` 路径错误：确认虚拟环境存在且路径正确（`.venv/bin/gunicorn`）。
- `Permission denied`：检查 `User/Group` 是否有项目目录读写权限。
- 端口无法访问：检查服务器防火墙与安全组放行 `5000/8000` 端口。

## 压测建议（JMeter）

- 两端使用相同请求体数据集
- 两端保持相同并发用户数、Ramp-Up、持续时间
- 关闭 debug，确保服务运行参数稳定
- 观察 API 响应时间 + 主机 CPU 占用率
