import sys


class QuietError(Exception):
    pass


class CommandError(QuietError):
    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.message = message
        self.code = code


class EventTimeout(QuietError):
    pass
