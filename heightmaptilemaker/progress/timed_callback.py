from .progress import Progress

import time

from .null_callback import NullCallback
from .progress import Progress
from .callback import Callback

class TimedCallback:
    def __init__(self, progress_callback=NullCallback(), start_at=0, end_at=1, callback_time_seconds=0.5):
        self.internal_callback = Callback(progress_callback, start_at, end_at)
        self.callback_time_seconds = callback_time_seconds
        self.next_callback_time = 0

    def _nextCallbackTimeReached(self):
        return time.time() >= self.next_callback_time

    def _updateNextCallbackTime(self):
        self.next_callback_time = time.time() + self.callback_time_seconds

    def __call__(self, progress):
        if self._nextCallbackTimeReached():
            self._updateNextCallbackTime()
            self.internal_callback(progress)
