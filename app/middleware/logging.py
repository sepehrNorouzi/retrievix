import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.shared.logger import get_logger, bind_request_id, clear_context

logger = get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. Generate correlation ID and bind to context
        request_id = bind_request_id()

        # 2. Log request start
        start_time = time.perf_counter()
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
            client_ip=request.client.host if request.client else None,
        )

        try:
            # 3. Process the request
            response = await call_next(request)
            process_time = time.perf_counter() - start_time

            # 4. Log successful response
            logger.info(
                "Request completed",
                status_code=response.status_code,
                duration_ms=round(process_time * 1000, 2),
                method=request.method,
                path=request.url.path,
            )
            # Add correlation ID header (optional)
            response.headers["X-Request-ID"] = request_id
            return response

        except Exception as exc:
            # 5. Log any unhandled exception
            process_time = time.perf_counter() - start_time
            logger.error(
                "Request failed",
                error=str(exc),
                exc_info=True,
                duration_ms=round(process_time * 1000, 2),
                method=request.method,
                path=request.url.path,
            )
            raise

        finally:
            clear_context()