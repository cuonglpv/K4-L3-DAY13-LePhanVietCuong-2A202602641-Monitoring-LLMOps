from __future__ import annotations

import time
import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from structlog.contextvars import bind_contextvars, clear_contextvars


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Context variables are task-local, but clearing them at the request
        # boundary prevents a worker from carrying request metadata forward.
        clear_contextvars()

        supplied_id = request.headers.get("x-request-id")
        if supplied_id and supplied_id.startswith("req-") and len(supplied_id) == 12:
            try:
                int(supplied_id[4:], 16)
                correlation_id = supplied_id.lower()
            except ValueError:
                correlation_id = f"req-{uuid.uuid4().hex[:8]}"
        else:
            correlation_id = f"req-{uuid.uuid4().hex[:8]}"

        bind_contextvars(correlation_id=correlation_id)
        request.state.correlation_id = correlation_id

        start = time.perf_counter()
        response = await call_next(request)
        response.headers["x-request-id"] = correlation_id
        response.headers["x-response-time-ms"] = str(
            round((time.perf_counter() - start) * 1000, 2)
        )
        return response
