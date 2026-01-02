"""
Curses UI Framework - A Python framework for creating terminal-based user interfaces.

This framework provides a structured approach to building terminal applications
using the curses library with a clean MVC architecture.
"""

__version__ = "0.1.0"
__author__ = "Curses UI Framework Team"

from .controller import CursesController
from .model import ApplicationModel
from .view import WindowView
from .window_manager import WindowManager, WindowType, WindowGeometry, LayoutInfo
from .layout_calculator import LayoutCalculator
from .frame_renderer import FrameRenderer, FrameStyle
from .exceptions import (
    CursesFrameworkError,
    TerminalTooSmallError,
    WindowCreationError
)

__all__ = [
    "CursesController",
    "ApplicationModel",
    "WindowView",
    "WindowManager",
    "WindowType",
    "WindowGeometry",
    "LayoutInfo",
    "LayoutCalculator",
    "FrameRenderer",
    "FrameStyle",
    "CursesFrameworkError",
    "TerminalTooSmallError",
    "WindowCreationError"
]