"""
WindowManager class for the Curses UI Framework.

This module manages the four main windows and their lifecycle,
providing window creation, refresh, and cleanup functionality.
"""

import curses
from enum import Enum
from typing import Dict, Optional
from .exceptions import WindowCreationError
from .frame_renderer import FrameRenderer, FrameStyle


class WindowType(Enum):
    """Enumeration of window types in the framework."""
    TOP = "top"
    LEFT = "left"
    MAIN = "main"
    BOTTOM = "bottom"


class WindowGeometry:
    """Container for window geometry information."""

    def __init__(self, y: int = 0, x: int = 0, height: int = 0, width: int = 0):
        """
        Initialize window geometry.

        Args:
            y: Row position (0-based)
            x: Column position (0-based)
            height: Window height in rows
            width: Window width in columns
        """
        self.y = y
        self.x = x
        self.height = height
        self.width = width

    def __repr__(self) -> str:
        return f"WindowGeometry(y={self.y}, x={self.x}, height={self.height}, width={self.width})"


class LayoutInfo:
    """Container for layout information of all windows."""

    def __init__(self):
        """Initialize layout information with default geometries."""
        self.top_window = WindowGeometry()
        self.left_window = WindowGeometry()
        self.main_window = WindowGeometry()
        self.bottom_window = WindowGeometry()
        self.terminal_height = 0
        self.terminal_width = 0

    def get_window_geometry(self, window_type: WindowType) -> WindowGeometry:
        """
        Get geometry for a specific window type.

        Args:
            window_type: Type of window to get geometry for

        Returns:
            WindowGeometry for the specified window type
        """
        if window_type == WindowType.TOP:
            return self.top_window
        elif window_type == WindowType.LEFT:
            return self.left_window
        elif window_type == WindowType.MAIN:
            return self.main_window
        elif window_type == WindowType.BOTTOM:
            return self.bottom_window
        else:
            raise ValueError(f"Unknown window type: {window_type}")


class WindowManager:
    """
    Manages the four main windows and their lifecycle.

    This class handles window creation, refresh operations, and cleanup
    for all windows in the curses UI framework.
    """

    def __init__(self, stdscr):
        """
        Initialize window manager with main screen.

        Args:
            stdscr: Main curses screen object
        """
        self.stdscr = stdscr
        self.windows: Dict[WindowType, curses.window] = {}
        self.layout_info: Optional[LayoutInfo] = None
        self.frame_renderer = FrameRenderer()
        self.frame_style = FrameStyle.SINGLE

    def create_windows(self, layout: LayoutInfo) -> None:
        """
        Create all four windows based on layout calculations.

        Args:
            layout: Layout information containing window geometries

        Raises:
            WindowCreationError: If window creation fails
        """
        self.layout_info = layout

        try:
            # Create top window
            top_geom = layout.top_window
            self.windows[WindowType.TOP] = curses.newwin(
                top_geom.height, top_geom.width, top_geom.y, top_geom.x
            )

            # Create left window
            left_geom = layout.left_window
            self.windows[WindowType.LEFT] = curses.newwin(
                left_geom.height, left_geom.width, left_geom.y, left_geom.x
            )

            # Create main window
            main_geom = layout.main_window
            self.windows[WindowType.MAIN] = curses.newwin(
                main_geom.height, main_geom.width, main_geom.y, main_geom.x
            )

            # Create bottom window
            bottom_geom = layout.bottom_window
            self.windows[WindowType.BOTTOM] = curses.newwin(
                bottom_geom.height, bottom_geom.width, bottom_geom.y, bottom_geom.x
            )

            # Draw frames for all windows
            self._draw_all_frames()

        except curses.error as e:
            raise WindowCreationError("window creation", str(e))

    def refresh_all(self) -> None:
        """Refresh all windows to display changes."""
        for window in self.windows.values():
            window.refresh()

    def resize_windows(self, new_layout: LayoutInfo) -> None:
        """
        Resize all windows when terminal size changes.

        Args:
            new_layout: New layout information with updated geometries
        """
        # Clear existing windows
        self.cleanup()

        # Create windows with new layout
        self.create_windows(new_layout)

    def get_window(self, window_type: WindowType) -> Optional[curses.window]:
        """
        Get a specific window by type.

        Args:
            window_type: Type of window to retrieve

        Returns:
            The curses window object or None if not found
        """
        return self.windows.get(window_type)

    def cleanup(self) -> None:
        """Clean up all window resources."""
        for window in self.windows.values():
            window.clear()
        self.windows.clear()

    def get_all_windows(self) -> Dict[WindowType, curses.window]:
        """
        Get all windows as a dictionary.

        Returns:
            Dictionary mapping window types to curses window objects
        """
        return self.windows.copy()

    def set_frame_style(self, style: FrameStyle) -> None:
        """
        Set the frame style for all windows.

        Args:
            style: The frame style to use
        """
        self.frame_style = style
        self._draw_all_frames()

    def _draw_all_frames(self) -> None:
        """Draw frames for all windows using the current frame style."""
        for window in self.windows.values():
            if window is not None:
                self.frame_renderer.draw_frame(window, self.frame_style)

    def get_content_area(self, window_type: WindowType) -> Optional[tuple]:
        """
        Get the content area coordinates for a specific window.

        Args:
            window_type: Type of window to get content area for

        Returns:
            Tuple of (start_y, start_x, content_height, content_width) or None
        """
        window = self.get_window(window_type)
        if window is not None:
            return self.frame_renderer.get_content_area(window)
        return None