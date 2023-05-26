import queue
from typing import Any


class Buffer:

    def __init__(self, maxSize=5) -> None:
        self._buffer = queue.Queue(maxSize)

    def enqueue(self, value: Any) -> None:
        if self._buffer.full():
            self._buffer.get_nowait()
        self._buffer.put_nowait(value)

    def dequeue(self) -> Any:
        if not self._buffer.empty():
            return self._buffer.get_nowait()
        else:
            return None

    def peek(self) -> Any:
        if not self._buffer.empty():
            return self._buffer.queue[0]
        else:
            return None

    def isFull(self) -> bool:
        return self._buffer.full()

    def isEmpty(self) -> bool:
        return self._buffer.empty()