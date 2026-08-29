import time
from typing import Dict, List, Tuple
from fastapi import Request, HTTPException, status


class SimpleRateLimiter:
    """
    Lightweight, free-tier-compatible in-memory sliding window rate limiter.
    Does not require external Redis or paid infrastructure.
    """

    def __init__(self, requests_per_minute: int = 10, burst_limit: int = 5):
        self.requests_per_minute = requests_per_minute
        self.burst_limit = burst_limit
        self.window_seconds = 60.0
        self._access_records: Dict[str, List[float]] = {}

    def _cleanup_old_records(self, now: float):
        # Periodically purge IP records older than the window
        expired_ips = []
        for ip, timestamps in self._access_records.items():
            valid_timestamps = [t for t in timestamps if now - t < self.window_seconds]
            if not valid_timestamps:
                expired_ips.append(ip)
            else:
                self._access_records[ip] = valid_timestamps
        for ip in expired_ips:
            del self._access_records[ip]

    def check_rate_limit(self, request: Request):
        now = time.time()
        client_ip = request.client.host if request.client else "unknown"

        # Cleanup occasionally
        if len(self._access_records) > 500:
            self._cleanup_old_records(now)

        timestamps = self._access_records.get(client_ip, [])
        valid_timestamps = [t for t in timestamps if now - t < self.window_seconds]

        if len(valid_timestamps) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute allowed on this endpoint. Please retry in a few moments.",
            )

        valid_timestamps.append(now)
        self._access_records[client_ip] = valid_timestamps


# Pre-configured rate limiters for expensive/sensitive operations
demo_load_limiter = SimpleRateLimiter(requests_per_minute=6)
demo_reset_limiter = SimpleRateLimiter(requests_per_minute=3)
investigation_limiter = SimpleRateLimiter(requests_per_minute=15)
assistant_limiter = SimpleRateLimiter(requests_per_minute=20)
