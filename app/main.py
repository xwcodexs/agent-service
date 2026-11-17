from contextlib import asynccontextmanager


from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request


from app.core.config import settings
from app.core.exceptions import ApplicationError
from app.core.logging import configure_logging, get_logger
import uvicorn
configure_logging(settings.logging.level)
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"【{settings.app.name}】应用启动中...")
    from app.infra.database import check_database, close_database
    try:
        await check_database()
        yield
    finally:
        logger.info("应用关闭中... ")
        await close_database()





app = FastAPI(
    title=settings.app.name,
    debug=settings.app.debug,
    lifespan=lifespan,
)
from app.modules.chat_threads.router import router as chat_thread_router
from app.modules.product.router import router as product_router
app.include_router(product_router)
app.include_router(chat_thread_router)


# @app.get("/health",summary="Health Check")
# async def health_check() -> dict[str, str]:
#     return {"status": "healthy"}
@app.exception_handler(ApplicationError)
async def http_exception_handler(request: Request, exc: ApplicationError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.code,
            "detail": exc.message
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=False
    )
