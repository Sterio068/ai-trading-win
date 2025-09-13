import time, os
from collections import deque

WINDOW_SEC = int(os.getenv("CB_WINDOW_SEC","60"))
MAX_ERRORS = int(os.getenv("CB_MAX_ERRORS","6"))
OPEN_SEC   = int(os.getenv("CB_OPEN_SEC","30"))

class CircuitBreaker:
    def __init__(self):
        self.errors = deque()
        self.open_until = 0
    def allow(self)->bool:
        now=time.time()
        if now < self.open_until: return False
        # 滾動窗口清理
        while self.errors and self.errors[0] < now - WINDOW_SEC:
            self.errors.popleft()
        return True
    def on_error(self):
        now=time.time()
        self.errors.append(now)
        # 超過閾值  打開
        if len(self.errors)>=MAX_ERRORS:
            self.open_until = now + OPEN_SEC
    def on_success(self):
        # 平復
        self.errors.clear()
        self.open_until = 0

cb_okx = CircuitBreaker()
