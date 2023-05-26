import sched
import threading
import time

from typing import Any, Callable

class TaskScheduler:

    def __init__(self, task: Callable[[Any], Any], taskArgs=(), delay: int = 5, loop=True) -> None:
        self._task = task
        self._delay = delay
        self._taskArgs = taskArgs
        self._loop = loop

        self._scheduler = sched.scheduler(timefunc=time.time, delayfunc=time.sleep)
        self._event = None
        self._schedThread = threading.Thread(target=self._scheduler.run, daemon=True)

    def _run(self) -> None:
        self._task(*self._taskArgs)

        if self._loop:
            self._event = self._scheduler.enter(delay=self._delay, priority=0, action=self._run)
    
    def start(self) -> None:
        self._event = self._scheduler.enter(delay=self._delay, priority=0, action=self._run)
        self._schedThread.start()
        
    def cancel(self) -> None:
        if not self._scheduler.empty():
            self._scheduler.cancel(self._event)
