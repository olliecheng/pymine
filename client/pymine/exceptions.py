import sys
import traceback as tb


class QuietError(Exception):
    pass


class CommandError(QuietError):
    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.message = message
        self.code = code


def quiet_hook(kind, message, traceback):
    if QuietError in kind.__bases__:
        stack = tb.extract_tb(traceback)
        last_file = stack[-1].filename

        modified_stack = [x for x in stack if x.filename != last_file]

        sys.stderr.write("Traceback (most recent call last):\n")

        for l in tb.format_list(modified_stack):
            sys.stderr.write(l)

        sys.stderr.write(
            "pymine.exceptions.{0}: {1} (error code {2})\n".format(
                kind.__name__, message.message, message.code
            )
        )

        sys.stderr.flush()
    else:
        sys.__excepthook__(
            kind, message, traceback
        )  # Print Error Type, Message and Traceback


sys.excepthook = quiet_hook
