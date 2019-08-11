from .progress import Progress

class Printer:
    def __init__(self):
        self.previous_length = 0

    def finish(self, message='Done'):
        self(Progress(1, message))
        print('')

    def __call__(self, progress):
        print(self._getMessageWithClearingPrevious(progress), end='\r')

    def _getMessageWithClearingPrevious(self, progress):
        message = self._getPrintMessage(progress)
        fillout = self._getFilloutFromMessageAndPrevious(message)

        return message + fillout

    def _getFilloutFromMessageAndPrevious(self, message):
        message_length = len(message)
        fillout = ' ' * max(0, self.previous_length - message_length)
        self.previous_length = message_length
        return fillout

    def _getPrintMessage(self, progress):
        progress_percentage = self._getFormattedProgress(progress)
        progress_message = progress.getMessage()
        return '[' + progress_percentage + '] : ' + progress_message

    def _getFormattedProgress(self, progress):
        return '{:3.2f} %'.format(progress.getProgress() * 100)
