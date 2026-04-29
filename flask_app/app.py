import time
import logging

from flask import Flask, jsonify, request

from config import Settings
from service import ServiceValidationError, UserNotFoundError, process_user_message

app = Flask(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")


def cpu_burn(iterations: int) -> int:
    """
    执行纯 CPU 计算：累计质数判定结果，避免被轻易优化。
    """
    checksum = 0
    for number in range(2, iterations + 2):
        is_prime = True
        divisor = 2
        while divisor * divisor <= number:
            if number % divisor == 0:
                is_prime = False
                break
            divisor += 1
        if is_prime:
            checksum += number
    return checksum


@app.post("/api/user-message/process")
def process_endpoint():
    payload = request.get_json(silent=True) or {}
    logger.info("Request /api/user-message/process payload=%s", payload)
    user_id = payload.get("user_id")
    message = payload.get("message")

    try:
        result = process_user_message(user_id=user_id, message=message)
        return (
            jsonify(
                {
                    "code": 0,
                    "message": "ok",
                    "data": {
                        "user_id": result.user_id,
                        "action": result.action,
                        "age": result.age,
                    },
                }
            ),
            200,
        )
    except ServiceValidationError as exc:
        return jsonify({"code": 1000, "message": str(exc), "data": None}), 400
    except UserNotFoundError as exc:
        return jsonify({"code": 1001, "message": str(exc), "data": None}), 404
    except RuntimeError:
        return jsonify({"code": 1002, "message": "database error", "data": None}), 500
    except Exception:
        return jsonify({"code": 1003, "message": "internal server error", "data": None}), 500


@app.post("/api/cpu-burn")
def cpu_burn_endpoint():
    payload = request.get_json(silent=True) or {}
    logger.info("Request /api/cpu-burn payload=%s", payload)
    iterations = payload.get("iterations", 5000)

    if not isinstance(iterations, int) or iterations <= 0:
        return jsonify({"code": 1000, "message": "iterations must be a positive integer", "data": None}), 400

    start = time.perf_counter()
    checksum = cpu_burn(iterations)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    return (
        jsonify(
            {
                "code": 0,
                "message": "ok",
                "data": {
                    "iterations": iterations,
                    "checksum": checksum,
                    "elapsed_ms": elapsed_ms,
                },
            }
        ),
        200,
    )


if __name__ == "__main__":
    # threaded 与 processes 不能同时启用；这里固定多进程模式用于并发压测
    app.run(
        host=Settings.host,
        port=Settings.port,
        debug=Settings.debug,
        threaded=False,
        processes=Settings.flask_processes,
    )
