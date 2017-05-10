from threading import Lock
import collections

# FIFO Queue lock
class QLock:
    def __init__(self):
        self.lock = Lock()
        self.waiters = collections.deque()
        self.count = 0

    def acquire(self):
        self.lock.acquire()
        # Add a lock to the queue
        if self.count:
            new_lock = Lock()
            new_lock.acquire()
            self.waiters.append(new_lock)
            self.lock.release()
            new_lock.acquire()
            self.lock.acquire()
        self.count += 1
        self.lock.release()

    def release(self):
        with self.lock:
            if not self.count:
                raise ValueError("lock not acquired")
            self.count -= 1
            if self.waiters:
                self.waiters.popleft().release()

    def locked(self):
        return self.count > 0
