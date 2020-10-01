import sys
import traceback as tb


class QuietError(Exception):
    pass


class CommandError(QuietError):
    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.message = message
        self.code = code


class EventTimeout(QuietError):
    pass


def quiet_hook(kind, message, traceback):
    if QuietError in kind.__bases__:
        stack = tb.extract_tb(traceback)
        last_file = stack[-1].filename

        def filter_func(x) -> bool:
            for v in (last_file, "asyncio/base_events.py", "asyncio/runners.py"):
                if v in x.filename:
                    return False
            return True

        modified_stack = [x for x in stack if filter_func(x)]

        sys.stderr.write("Traceback (most recent call last):\n")

        for l in tb.format_list(modified_stack):
            sys.stderr.write(l)

        err = ""
        if isinstance(message, CommandError):
            err = f"{message.message} (error code {message.code})"
        elif isinstance(message, EventTimeout):
            err = "Event timed out."

        sys.stderr.write(f"pymine.exceptions.{kind.__name__}: {err}")

        sys.stderr.flush()
    else:
        sys.__excepthook__(
            kind, message, traceback
        )  # Print Error Type, Message and Traceback


sys.excepthook = quiet_hook
