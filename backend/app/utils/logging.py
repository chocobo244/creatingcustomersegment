"""
Logging configuration and utilities for Multi-Touch Attribution Platform.
"""
import logging
import logging.handlers
import sys
from typing import Any, Dict, Optional
from pathlib import Path
import structlog
from config.settings import get_logging_settings


def setup_logging() -> None:
    """Setup application logging configuration."""
    settings = get_logging_settings()
    
    # Ensure log directory exists
    log_path = Path(settings.file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, settings.level.upper()),
        format=settings.format,
        handlers=[
            # Console handler
            logging.StreamHandler(sys.stdout),
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                filename=settings.file_path,
                maxBytes=_parse_file_size(settings.max_file_size),
                backupCount=settings.backup_count,
                encoding="utf-8"
            )
        ]
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def _parse_file_size(size_str: str) -> int:
    """Parse file size string to bytes."""
    size_str = size_str.upper()
    if size_str.endswith('KB'):
        return int(size_str[:-2]) * 1024
    elif size_str.endswith('MB'):
        return int(size_str[:-2]) * 1024 * 1024
    elif size_str.endswith('GB'):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    else:
        return int(size_str)


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggerMixin:
    """Mixin class to add logging capabilities to any class."""
    
    @property
    def logger(self) -> structlog.BoundLogger:
        """Get logger for this class."""
        return get_logger(self.__class__.__module__ + "." + self.__class__.__name__)


def log_function_call(
    func_name: str,
    args: tuple = (),
    kwargs: Optional[Dict[str, Any]] = None,
    result: Any = None,
    error: Optional[Exception] = None,
    execution_time: Optional[float] = None
) -> None:
    """Log function call details."""
    logger = get_logger("function_calls")
    
    log_data = {
        "function": func_name,
        "args_count": len(args) if args else 0,
        "kwargs_keys": list(kwargs.keys()) if kwargs else [],
    }
    
    if execution_time is not None:
        log_data["execution_time_ms"] = round(execution_time * 1000, 2)
    
    if error:
        logger.error(
            "Function call failed",
            **log_data,
            error=str(error),
            error_type=type(error).__name__
        )
    else:
        logger.info(
            "Function call completed",
            **log_data,
            result_type=type(result).__name__ if result is not None else None
        )


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    execution_time: float,
    user_id: Optional[str] = None,
    request_id: Optional[str] = None,
    error: Optional[str] = None
) -> None:
    """Log API request details."""
    logger = get_logger("api_requests")
    
    log_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "execution_time_ms": round(execution_time * 1000, 2),
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if request_id:
        log_data["request_id"] = request_id
    
    if error:
        log_data["error"] = error
        logger.error("API request failed", **log_data)
    else:
        logger.info("API request completed", **log_data)


def log_attribution_calculation(
    model_name: str,
    touchpoint_count: int,
    conversion_count: int,
    execution_time: float,
    user_id: Optional[str] = None,
    error: Optional[str] = None
) -> None:
    """Log attribution calculation details."""
    logger = get_logger("attribution_calculations")
    
    log_data = {
        "model_name": model_name,
        "touchpoint_count": touchpoint_count,
        "conversion_count": conversion_count,
        "execution_time_ms": round(execution_time * 1000, 2),
    }
    
    if user_id:
        log_data["user_id"] = user_id
    
    if error:
        log_data["error"] = error
        logger.error("Attribution calculation failed", **log_data)
    else:
        logger.info("Attribution calculation completed", **log_data)


def log_data_ingestion(
    source: str,
    records_processed: int,
    records_failed: int,
    execution_time: float,
    batch_id: Optional[str] = None,
    error: Optional[str] = None
) -> None:
    """Log data ingestion details."""
    logger = get_logger("data_ingestion")
    
    log_data = {
        "source": source,
        "records_processed": records_processed,
        "records_failed": records_failed,
        "success_rate": (records_processed / (records_processed + records_failed)) * 100 
                       if (records_processed + records_failed) > 0 else 0,
        "execution_time_ms": round(execution_time * 1000, 2),
    }
    
    if batch_id:
        log_data["batch_id"] = batch_id
    
    if error:
        log_data["error"] = error
        logger.error("Data ingestion failed", **log_data)
    else:
        logger.info("Data ingestion completed", **log_data)


class AttributionLogger:
    """Specialized logger for attribution-related operations."""
    
    def __init__(self, context: Optional[Dict[str, Any]] = None):
        self.logger = get_logger("attribution")
        self.context = context or {}
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with context."""
        self.logger.info(message, **self.context, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with context."""
        self.logger.error(message, **self.context, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with context."""
        self.logger.warning(message, **self.context, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with context."""
        self.logger.debug(message, **self.context, **kwargs)
    
    def with_context(self, **kwargs) -> "AttributionLogger":
        """Create new logger instance with additional context."""
        new_context = {**self.context, **kwargs}
        return AttributionLogger(context=new_context)


# Performance monitoring
class PerformanceLogger:
    """Logger for performance monitoring."""
    
    def __init__(self):
        self.logger = get_logger("performance")
    
    def log_slow_query(
        self,
        query: str,
        execution_time: float,
        threshold: float = 1.0,
        parameters: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log slow database queries."""
        if execution_time >= threshold:
            self.logger.warning(
                "Slow query detected",
                query=query[:200] + "..." if len(query) > 200 else query,
                execution_time_ms=round(execution_time * 1000, 2),
                threshold_ms=round(threshold * 1000, 2),
                parameters=parameters
            )
    
    def log_memory_usage(
        self,
        operation: str,
        memory_before: float,
        memory_after: float,
        peak_memory: Optional[float] = None
    ) -> None:
        """Log memory usage for operations."""
        memory_delta = memory_after - memory_before
        
        log_data = {
            "operation": operation,
            "memory_before_mb": round(memory_before / 1024 / 1024, 2),
            "memory_after_mb": round(memory_after / 1024 / 1024, 2),
            "memory_delta_mb": round(memory_delta / 1024 / 1024, 2),
        }
        
        if peak_memory:
            log_data["peak_memory_mb"] = round(peak_memory / 1024 / 1024, 2)
        
        self.logger.info("Memory usage tracked", **log_data)


# Initialize global loggers
performance_logger = PerformanceLogger()
attribution_logger = AttributionLogger()


def configure_uvicorn_logging() -> None:
    """Configure uvicorn logging to use our structured logging."""
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    
    # Use our structured logging format
    for logger in [uvicorn_logger, uvicorn_access_logger]:
        logger.handlers.clear()
        logger.addHandler(logging.StreamHandler(sys.stdout))
        logger.setLevel(logging.INFO)