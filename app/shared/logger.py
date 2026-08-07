# app/logger.py
import structlog
import logging
from structlog.contextvars import bound_contextvars, clear_contextvars
import uuid
from typing import Optional

# Configure structlog
def configure_logging() -> None:
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    # Also set the root logger level if you want
    logging.basicConfig(level=logging.INFO)

def get_logger() -> structlog.stdlib.BoundLogger:
    """Get a logger instance."""
    return structlog.get_logger()

def bind_request_id(request_id: Optional[str] = None):
    """
    Bind a correlation ID to the current async context.
    If no ID is provided, a new UUID is generated.
    """
    if request_id is None:
        request_id = str(uuid.uuid4())
    bound_contextvars(request_id=request_id)
    return request_id

def clear_context():
    """Clear the contextvars at the end of a request."""
    clear_contextvars()