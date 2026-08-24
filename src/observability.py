"""Small dependency-free observability primitives for the HTTP boundary."""

import json
import logging
import time
from collections import Counter
from threading import Lock

logger = logging.getLogger("pos.api")


class Metrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._requests = Counter()

    def observe(self, *, method: str, path: str, status: int, duration_ms: float) -> None:
        with self._lock:
            self._requests[(method, path, status)] += 1
        logger.info(
            json.dumps(
                {
                    "event": "http_request",
                    "method": method,
                    "path": path,
                    "status": status,
                    "duration_ms": round(duration_ms, 3),
                },
                separators=(",", ":"),
                sort_keys=True,
            )
        )

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            requests = [
                {"method": method, "path": path, "status": status, "count": count}
                for (method, path, status), count in sorted(self._requests.items())
            ]
        return {"requests": requests}


metrics = Metrics()
