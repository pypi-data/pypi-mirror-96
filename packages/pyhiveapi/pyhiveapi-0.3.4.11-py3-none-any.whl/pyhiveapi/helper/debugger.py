import logging
import sys


class DebugContext:
    """ Debug context to trace any function calls inside the context """

    def __init__(self, name, enabled):
        self.name = name
        self.enabled = enabled
        self.logging = logging.getLogger(__name__)

    def __enter__(self):
        print("Entering Debug Decorated func")
        # Set the trace function to the trace_calls function
        # So all events are now traced
        self.trace_calls

    def trace_calls(self, frame, event, arg):
        # We want to only trace our call to the decorated function
        if event != "call":
            return
        elif frame.f_code.co_name != self.name:
            return
        # return the trace function to use when you go into that
        # function call
        return self.trace_lines

    def trace_lines(self, frame, event, arg):
        # If you want to print local variables each line
        # keep the check for the event 'line'
        # If you want to print local variables only on return
        # check only for the 'return' event
        if event not in ["line", "return"]:
            return
        co = frame.f_code
        func_name = co.co_name
        line_no = frame.f_lineno
        filename = co.co_filename
        local_vars = frame.f_locals
        text = f"  {func_name} {event} {line_no} locals: {local_vars}"
        self.logging.debug(text)


def debug_decorator(enabled=False):
    """ Debug decorator to call the function within the debug context """

    def decorated_func(func):
        def wrapper(*args, **kwargs):
            with DebugContext(func.__name__, enabled):
                return_value = func(*args, **kwargs)
            return return_value

        return wrapper

    return decorated_func
