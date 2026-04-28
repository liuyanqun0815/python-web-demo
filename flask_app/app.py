from flask import Flask, jsonify, request

from config import Settings
from service import ServiceValidationError, UserNotFoundError, process_user_message

app = Flask(__name__)


@app.post("/api/user-message/process")
def process_endpoint():
    payload = request.get_json(silent=True) or {}
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


if __name__ == "__main__":
    # threaded 与 processes 不能同时启用；这里固定多进程模式用于并发压测
    app.run(
        host=Settings.host,
        port=Settings.port,
        debug=Settings.debug,
        threaded=False,
        processes=Settings.flask_processes,
    )
