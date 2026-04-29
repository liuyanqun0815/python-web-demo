import os
import logging
import time

from fastapi import Depends, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from schemas import ApiResponse, CpuBurnRequest, CpuBurnResponse, ProcessRequest
from service import ServiceValidationError, UserNotFoundError, process_user_message

app = FastAPI()
debug_api_errors = os.getenv("DEBUG_API_ERRORS", "false").lower() == "true"
logger = logging.getLogger(__name__)


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


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request, exc):  # noqa: ANN001
    return JSONResponse(
        status_code=400,
        content={"code": 1000, "message": "invalid request body", "data": None},
    )


@app.post("/api/user-message/process", response_model=ApiResponse)
async def process_endpoint(payload: ProcessRequest, session: AsyncSession = Depends(get_session)):
    try:
        result = await process_user_message(
            session=session,
            user_id=payload.user_id,
            message=payload.message,
        )
        return {
            "code": 0,
            "message": "ok",
            "data": {
                "user_id": result.user_id,
                "action": result.action,
                "age": result.age,
            },
        }
    except ServiceValidationError as exc:
        return JSONResponse(status_code=400, content={"code": 1000, "message": str(exc), "data": None})
    except UserNotFoundError as exc:
        return JSONResponse(status_code=404, content={"code": 1001, "message": str(exc), "data": None})
    except RuntimeError as exc:
        error_message = "database error"
        if debug_api_errors:
            error_message = f"database error: {exc}"
        return JSONResponse(status_code=500, content={"code": 1002, "message": error_message, "data": None})
    except Exception as exc:
        logger.exception("Unhandled exception in process_endpoint")
        error_message = "internal server error"
        if debug_api_errors:
            error_message = f"internal server error: {exc.__class__.__name__}: {exc}"
        return JSONResponse(status_code=500, content={"code": 1003, "message": error_message, "data": None})


@app.post("/api/cpu-burn", response_model=CpuBurnResponse)
async def cpu_burn_endpoint(payload: CpuBurnRequest):
    start = time.perf_counter()
    checksum = cpu_burn(payload.iterations)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    return {
        "code": 0,
        "message": "ok",
        "data": {
            "iterations": payload.iterations,
            "checksum": checksum,
            "elapsed_ms": elapsed_ms,
        },
    }


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host=host, port=port)
