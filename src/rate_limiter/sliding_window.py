import time
from collections import deque
from threading import Lock

class SlidingWindowLogRateLimiter:
    def __init__(self, limit: int, window_size_seconds: int):
        self.limit = limit
        self.window_size = window_size_seconds
        self.request_logs = deque()  # Track request ts.
        self.lock = Lock()

    def allow_request(self) -> bool:
        current_time = time.time()
        window_start = current_time - self.window_size

        with self.lock:
            log = self.request_logs

            # Becase start time has shifted, 
            # Remove timestamps outside the current sliding window
            while log and log[0] < window_start:
                log.popleft()

            # Check if adding the new request exceeds the limit
            if len(log) < self.limit:
                log.append(current_time)
                return True

            return False

# --- Example Usage ---
limiter = SlidingWindowLogRateLimiter(limit=3, window_size_seconds=10)

for i in range(5):
    allowed = limiter.allow_request()
    print(f"Request {i+1}: {'Allowed' if allowed else 'Blocked'}")
    time.sleep(1)