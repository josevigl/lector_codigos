import time


class Deduplicator:
    def __init__(self, ttl_seconds):
        if ttl_seconds <= 0:
            raise ValueError("El TTL de deduplicación debe ser positivo.")
        self.ttl_seconds = float(ttl_seconds)
        self._seen_at = {}

    def is_duplicate(self, code, now=None):
        current_time = time.monotonic() if now is None else now
        expired = [
            seen_code
            for seen_code, timestamp in self._seen_at.items()
            if current_time - timestamp >= self.ttl_seconds
        ]
        for seen_code in expired:
            del self._seen_at[seen_code]

        previous_time = self._seen_at.get(code)
        if previous_time is not None and current_time - previous_time < self.ttl_seconds:
            return True
        self._seen_at[code] = current_time
        return False
