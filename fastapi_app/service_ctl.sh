#!/usr/bin/env bash
set -euo pipefail

ACTION="${1:-}"
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="${APP_DIR}/logs"
PID_FILE="${LOG_DIR}/fastapi-gunicorn.pid"
LOG_FILE="${LOG_DIR}/fastapi-gunicorn.out"
GUNICORN_BIN="${APP_DIR}/.venv/bin/gunicorn"

WORKERS="${FASTAPI_WORKERS:-4}"
THREADS="${FASTAPI_THREADS:-4}"
BIND_HOST="${FASTAPI_HOST:-0.0.0.0}"
BIND_PORT="${FASTAPI_PORT:-8000}"

start_service() {
    mkdir -p "${LOG_DIR}"

    if [[ -f "${PID_FILE}" ]] && kill -0 "$(cat "${PID_FILE}")" 2>/dev/null; then
        echo "FastAPI service is already running. pid=$(cat "${PID_FILE}")"
        return 0
    fi

    if [[ ! -x "${GUNICORN_BIN}" ]]; then
        echo "gunicorn not found: ${GUNICORN_BIN}"
        echo "Please run: pip install -r requirements.txt"
        return 1
    fi

    nohup "${GUNICORN_BIN}" \
        -w "${WORKERS}" \
        --threads "${THREADS}" \
        -k uvicorn.workers.UvicornWorker \
        -b "${BIND_HOST}:${BIND_PORT}" \
        main:app >"${LOG_FILE}" 2>&1 &

    echo $! >"${PID_FILE}"
    echo "FastAPI service started. pid=$(cat "${PID_FILE}") log=${LOG_FILE}"
}

stop_service() {
    if [[ ! -f "${PID_FILE}" ]]; then
        echo "FastAPI service is not running (pid file missing)."
        return 0
    fi

    PID="$(cat "${PID_FILE}")"
    if kill -0 "${PID}" 2>/dev/null; then
        kill "${PID}"
        sleep 1
        if kill -0 "${PID}" 2>/dev/null; then
            kill -9 "${PID}"
        fi
        echo "FastAPI service stopped. pid=${PID}"
    else
        echo "FastAPI service process not found. pid=${PID}"
    fi

    rm -f "${PID_FILE}"
}

restart_service() {
    stop_service
    start_service
}

case "${ACTION}" in
start)
    start_service
    ;;
stop)
    stop_service
    ;;
restart)
    restart_service
    ;;
*)
    echo "Usage: $0 {start|stop|restart}"
    exit 1
    ;;
esac
