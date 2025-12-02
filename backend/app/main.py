# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
from app.exceptions import global_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from logging import getLogger

logger = getLogger("policy_ai.main")

app = FastAPI(title="Policy AI Assistant")

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Register global exception handler
app.add_exception_handler(Exception, global_exception_handler)

# Optional: friendly validation error response
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=422, content={"detail": exc.errors(), "body": exc.body})

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Policy AI Assistant on http://0.0.0.0:8000")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
