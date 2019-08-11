
class Progress:
    def __init__(self, progress, message="N/A", max_progress=1.0):
        if progress > max_progress:
            raise Exception("Invalid progress: progress was " + str(progress) + " while max progress is " + str(max_progress))
        self.progress = progress / max_progress
        self.message = message
        self.eta_computer = None

    def getProgress(self):
        return self.progress

    def getFormattedProgress(self):
        return '{:3.2} %'.format(self.progress * 100)

    def getMessage(self):
        return self.message

    def __str__(self):
        return '[' + self.getFormattedProgress() + '] : ' + self.getMessage()
