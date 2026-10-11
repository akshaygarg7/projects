import math
import time
from threading import Lock
from typing import Callable


class TokenBucket:
	"""A thread-safe token bucket rate limiter.

	Tokens are added at ``refill_rate`` tokens per second, up to ``capacity``.
	The bucket starts full.
	"""

	def __init__(
		self,
		capacity: float,
		refill_rate: float,
		clock: Callable[[], float] = time.monotonic,
	) -> None:
		if capacity <= 0:
			raise ValueError("capacity must be a finite positive number")
		if refill_rate < 0:
			raise ValueError("refill_rate must be a finite non-negative number")

		self._capacity = float(capacity)
		self._refill_rate = float(refill_rate)

		self._clock = clock
		self._tokens = self._capacity
		self._last_refill = clock()
		self._lock = Lock()

	@property
	def available_tokens(self) -> float:
		"""Return the current token balance after applying elapsed refill."""
		with self._lock:
			self._refill()
			return self._tokens

	def consume(self, tokens: float = 1) -> bool:
		"""Consume ``tokens`` if available and report whether it succeeded."""
		if not math.isfinite(tokens) or tokens <= 0:
			raise ValueError("tokens must be a finite positive number")
		if tokens > self._capacity:
			return False

		with self._lock:
			self._refill()
			if self._tokens < tokens:
				return False
			self._tokens -= tokens
			return True

	def _refill(self) -> None:
		now = self._clock()

        # number of elapsed seconds since last refil rate
		elapsed = max(0.0, now - self._last_refill)

        # refil bucket with refil rate for elapsed time, limited to capacity 
		self._tokens = min(
			self._capacity,
			self._tokens + elapsed * self._refill_rate,
		)
		
		self._last_refill = now
