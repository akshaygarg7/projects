import time
from threading import Lock

class FixedWindowRateLimiter:
    def __init__(self, limit: int, window_size_seconds: int):
        self.limit = limit
        self.window_size = window_size_seconds
        self.windows = {}  # tracks number of request per window block
        self.lock = Lock()

    def allow_request(self) -> bool:
        current_time = int(time.time())
        
        # divide current time by window size to create a block since current time
        # new block created once time crosses window size
        current_window = current_time // self.window_size
		
        with self.lock:
            
			# Clean up old windows to prevent memory leaks
            self.windows = {
                w: data for w, data in self.windows.items() 
                if w >= current_window - 1
            }

            if current_window not in self.windows:
                self.windows[current_window] = 0

            if self.windows[current_window] < self.limit:
                self.windows[current_window] += 1
                return True
            
            return False

# --- Example Usage ---
limiter = FixedWindowRateLimiter(limit=3, window_size_seconds=10)

for i in range(5):
    allowed = limiter.allow_request()
    print(f"Request {i+1}: 'Allowed' -> {allowed}")
    time.sleep(1)