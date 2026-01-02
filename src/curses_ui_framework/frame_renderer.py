"""
FrameRenderer class for the Curses UI Framework.

This module handles visual styling and frame drawing for windows,
providing different frame styles and proper corner connections.
"""

import curses
from enum import Enum
from typing import Dict, Optional


class FrameStyle(Enum):
    """Enumeration of available frame styles."""
    SINGLE = "single"      # Single-line box drawing
    DOUBLE = "double"      # Double-line box drawing
    THICK = "thick"        # Thick line box drawing
    ROUNDED = "rounded"    # Rounded corners


class FrameRenderer:
    """
    Manages visual styling and frame drawing for windows.

    This class provides functionality to draw frames around windows
    using various box-drawing character styles with proper corner
    connections and frame integrity.
    """

    def __init__(self):
        """Initialize the frame renderer with character mappings."""
        # Define box-drawing characters for different styles
        self._frame_chars = {
            FrameStyle.SINGLE: {
                'horizontal': '─',      # U+2500
                'vertical': '│',        # U+2502
                'top_left': '┌',        # U+250C
                'top_right': '┐',       # U+2510
                'bottom_left': '└',     # U+2514
                'bottom_right': '┘',    # U+2518
            },
            FrameStyle.DOUBLE: {
                'horizontal': '═',      # U+2550
                'vertical': '║',        # U+2551
                'top_left': '╔',        # U+2554
                'top_right': '╗',       # U+2557
                'bottom_left': '╚',     # U+255A
                'bottom_right': '╝',    # U+255D
            },
            FrameStyle.THICK: {
                'horizontal': '━',      # U+2501
                'vertical': '┃',        # U+2503
                'top_left': '┏',        # U+250F
                'top_right': '┓',       # U+2513
                'bottom_left': '┗',     # U+2517
                'bottom_right': '┛',    # U+251B
            },
            FrameStyle.ROUNDED: {
                'horizontal': '─',      # U+2500
                'vertical': '│',        # U+2502
                'top_left': '╭',        # U+256D
                'top_right': '╮',       # U+256E
                'bottom_left': '╰',     # U+2570
                'bottom_right': '╯',    # U+256F
            }
        }

        # Fallback to ASCII characters if Unicode is not supported
        self._ascii_chars = {
            'horizontal': '-',
            'vertical': '|',
            'top_left': '+',
            'top_right': '+',
            'bottom_left': '+',
            'bottom_right': '+',
        }

    def draw_frame(self, window: curses.window, style: FrameStyle = FrameStyle.SINGLE) -> None:
        """
        Draw a frame around the specified window.

        Args:
            window: The curses window to draw a frame around
            style: The frame style to use (default: SINGLE)

        Raises:
            curses.error: If drawing operations fail
        """
        try:
            height, width = window.getmaxyx()
            
            # Don't draw frame if window is too small
            if height < 3 or width < 3:
                return

            # Get character set for the style
            chars = self._get_frame_chars(style)

            # Clear the window first
            window.clear()

            # Draw corners
            window.addch(0, 0, chars['top_left'])
            window.addch(0, width - 1, chars['top_right'])
            window.addch(height - 1, 0, chars['bottom_left'])
            window.addch(height - 1, width - 1, chars['bottom_right'])

            # Draw horizontal lines (top and bottom)
            for x in range(1, width - 1):
                window.addch(0, x, chars['horizontal'])
                window.addch(height - 1, x, chars['horizontal'])

            # Draw vertical lines (left and right)
            for y in range(1, height - 1):
                window.addch(y, 0, chars['vertical'])
                window.addch(y, width - 1, chars['vertical'])

        except curses.error:
            # If Unicode characters fail, try with ASCII fallback
            self._draw_ascii_frame(window)

    def _draw_ascii_frame(self, window: curses.window) -> None:
        """
        Draw a frame using ASCII characters as fallback.

        Args:
            window: The curses window to draw a frame around
        """
        try:
            height, width = window.getmaxyx()
            
            if height < 3 or width < 3:
                return

            chars = self._ascii_chars

            # Draw corners
            window.addch(0, 0, chars['top_left'])
            window.addch(0, width - 1, chars['top_right'])
            window.addch(height - 1, 0, chars['bottom_left'])
            window.addch(height - 1, width - 1, chars['bottom_right'])

            # Draw horizontal lines
            for x in range(1, width - 1):
                window.addch(0, x, chars['horizontal'])
                window.addch(height - 1, x, chars['horizontal'])

            # Draw vertical lines
            for y in range(1, height - 1):
                window.addch(y, 0, chars['vertical'])
                window.addch(y, width - 1, chars['vertical'])

        except curses.error:
            # If even ASCII fails, use curses.box() as last resort
            window.box()

    def clear_frame(self, window: curses.window) -> None:
        """
        Clear the frame from a window.

        Args:
            window: The curses window to clear the frame from
        """
        try:
            height, width = window.getmaxyx()
            
            # Clear border area
            for x in range(width):
                window.addch(0, x, ' ')
                if height > 1:
                    window.addch(height - 1, x, ' ')
            
            for y in range(1, height - 1):
                window.addch(y, 0, ' ')
                if width > 1:
                    window.addch(y, width - 1, ' ')

        except curses.error:
            # If clearing fails, just clear the entire window
            window.clear()

    def update_frames(self, windows: Dict[str, curses.window], style: FrameStyle = FrameStyle.SINGLE) -> None:
        """
        Update frames for all windows.

        Args:
            windows: Dictionary of window names to curses window objects
            style: The frame style to use for all windows
        """
        for window in windows.values():
            if window is not None:
                self.draw_frame(window, style)

    def _get_frame_chars(self, style: FrameStyle) -> Dict[str, str]:
        """
        Get the character set for a specific frame style.

        Args:
            style: The frame style to get characters for

        Returns:
            Dictionary mapping character names to Unicode characters
        """
        return self._frame_chars.get(style, self._frame_chars[FrameStyle.SINGLE])

    def get_content_area(self, window: curses.window) -> tuple:
        """
        Get the content area coordinates within a framed window.

        Args:
            window: The framed window

        Returns:
            Tuple of (start_y, start_x, content_height, content_width)
        """
        height, width = window.getmaxyx()
        
        # Content area excludes the frame border
        content_start_y = 1
        content_start_x = 1
        content_height = max(0, height - 2)
        content_width = max(0, width - 2)
        
        return (content_start_y, content_start_x, content_height, content_width)

    def is_frame_supported(self, style: FrameStyle) -> bool:
        """
        Check if a frame style is supported in the current terminal.

        Args:
            style: The frame style to check

        Returns:
            True if the style is supported, False otherwise
        """
        # For now, assume all styles are supported
        # In a more sophisticated implementation, this could test
        # if the terminal supports the specific Unicode characters
        return style in self._frame_chars