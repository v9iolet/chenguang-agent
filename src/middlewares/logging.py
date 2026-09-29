import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        日志中间件
        """
        #记录请求时间
        start = time.perf_counter()
        logger.info(f"--> {request.method} {request.url.path}")
        #调用下一个中间件或路由处理函数
        response = await call_next(request)
        #记录响应时间
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            f"<-- {request.method} {request.url.path} "
            f"status={response.status_code} {elapsed:.2f}ms"
        )
        return response