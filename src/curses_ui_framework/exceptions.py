"""
Exception classes for the Curses UI Framework.

This module defines custom exceptions used throughout the framework
for proper error handling and user feedback.
"""


class CursesFrameworkError(Exception):
    """Base exception for all framework-related errors."""
    pass


class TerminalTooSmallError(CursesFrameworkError):
    """Raised when terminal is below minimum size requirements."""

    def __init__(self, current_size, minimum_size):
        self.current_size = current_size
        self.minimum_size = minimum_size
        super().__init__(
            f"Terminal size {current_size} is below minimum requirement {minimum_size}"
        )


class WindowCreationError(CursesFrameworkError):
    """Raised when window creation fails."""

    def __init__(self, window_type, reason=None):
        self.window_type = window_type
        self.reason = reason
        message = f"Failed to create {window_type} window"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class TerminalCompatibilityError(CursesFrameworkError):
    """Raised when terminal lacks required curses support."""

    def __init__(self, missing_feature=None):
        self.missing_feature = missing_feature
        message = "Terminal is not compatible with curses framework"
        if missing_feature:
            message += f": {missing_feature}"
        super().__init__(message)


class CursesInitializationError(CursesFrameworkError):
    """Raised when curses initialization fails."""

    def __init__(self, reason=None):
        self.reason = reason
        message = "Failed to initialize curses"
        if reason:
            message += f": {reason}"
        super().__init__(message)