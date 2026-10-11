# Token Bucket Rate Limiter

`TokenBucket` limits how often work can be admitted while allowing short bursts.
It stores up to `capacity` tokens. Each admitted operation consumes tokens, and
the bucket replenishes at `refill_rate` tokens per second, never exceeding its
capacity. The bucket starts full.

```python
from src.rate_limiter.token_bucket import TokenBucket

# Allow a burst of up to 10 operations, then replenish at 2 operations/second.
limiter = TokenBucket(capacity=10, refill_rate=2)

if limiter.consume():
		handle_request()
else:
		reject_request()
```

## Behavior

- `consume(tokens=1)` returns `True` and deducts the requested amount when
	enough tokens are available. Otherwise it returns `False` immediately; it
	does not wait for tokens to refill.
- Fractional token amounts are supported, so callers can charge different
	costs for different operations.
- `available_tokens` returns the current balance after applying any elapsed
	refill.
- The bucket is safe to share between threads. Consumption and refill checks
	are synchronized.
- `capacity` must be positive, and `refill_rate` must be non-negative. A zero
	refill rate creates a bucket that does not replenish.
- `consume()` requires a positive, finite token amount. A request larger than
	the bucket's capacity returns `False`.

The refill rate is expressed in tokens per second. For example, with a rate of
`2`, one token is replenished every half-second, up to the configured capacity.
