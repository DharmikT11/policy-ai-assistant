# exceptions.py
from fastapi import Request
from fastapi.responses import JSONResponse
from logging import getLogger

logger = getLogger("policy_ai.exceptions")

async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred. Our engineers have been notified.", "detail": str(exc)},
    )
