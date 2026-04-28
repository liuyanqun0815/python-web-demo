# Flask vs FastAPI 并发对照项目

本目录包含两个独立 API 项目，用于在相同 PostgreSQL 与相同业务逻辑下进行并发与 CPU 占用对比。
两个项目都使用 SQLAlchemy ORM 连接数据库并操作模型：

- Flask：同步 ORM Session（`Session` + `sessionmaker`）
- FastAPI：异步 ORM Session（`AsyncSession` + `async_sessionmaker`）

## 项目结构

- `db/init.sql`：数据库建表脚本
- `db/seed.sql`：初始化测试数据脚本
- `flask_app/`：Flask（同步 SQLAlchemy + psycopg2）
- `fastapi_app/`：FastAPI（异步 SQLAlchemy + asyncpg）

## 业务逻辑（两项目一致）

`POST /api/user-message/process`

请求体：

```json
{
  "user_id": 1001,
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
    "user_id": 1001,
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

## 运行 Flask 项目

```bash
cd flask_app
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/postgres
python app.py
```

默认端口：`5000`

## 运行 FastAPI 项目

```bash
cd fastapi_app
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
pip install -r requirements.txt
set DATABASE_URL=postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/postgres
python main.py
```

默认端口：`8000`

## 压测建议（JMeter）

- 两端使用相同请求体数据集
- 两端保持相同并发用户数、Ramp-Up、持续时间
- 关闭 debug，确保服务运行参数稳定
- 观察 API 响应时间 + 主机 CPU 占用率
