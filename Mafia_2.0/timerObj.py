from typing import Optional
import asyncio

class TimerHandle:
    def __init__(self, message, end_time, task):
        self.message = message
        self.end_time = end_time
        self.task: Optional[asyncio.Task[None]] = task
        self.cancelled = False
