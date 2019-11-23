from .null_callback import NullCallback
from .progress import Progress

class Callback:
    def __init__(self, progress_callback=NullCallback(), start_at=0, end_at=1, message=None):
        self.progress_callback = progress_callback
        self.start_at = start_at
        self.end_at = end_at
        self.message = message

    def __call__(self, progress):
        scaled_progress = progress.getProgress() * (self.end_at - self.start_at)
        new_progress = self.start_at + scaled_progress
        combined_message = (self.message + ": " or "") + progress.message
        new_progress = Progress(new_progress, combined_message)
        self.progress_callback(new_progress)
