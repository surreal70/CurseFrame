"""
LayoutCalculator class for the Curses UI Framework.

This module handles automatic positioning and sizing calculations
for all windows in the framework, including minimum size validation.
"""

from typing import Dict, Tuple
from .window_manager import WindowType, WindowGeometry, LayoutInfo
from .exceptions import TerminalTooSmallError


class LayoutCalculator:
    """
    Handles automatic positioning and sizing calculations for windows.

    This class implements the layout algorithm that positions and sizes
    all four windows based on terminal dimensions and minimum requirements.
    """

    # Minimum terminal requirements (120x60 as per requirements)
    MIN_TERMINAL_WIDTH = 120
    MIN_TERMINAL_HEIGHT = 60

    # Minimum window sizes
    MIN_WINDOW_SIZES = {
        WindowType.TOP: (3, 30),      # (height, width)
        WindowType.LEFT: (15, 25),
        WindowType.MAIN: (15, 50),
        WindowType.BOTTOM: (3, 30)
    }

    def __init__(self, min_sizes: Dict[WindowType, Tuple[int, int]] = None):
        """
        Initialize layout calculator with minimum size constraints.

        Args:
            min_sizes: Optional custom minimum sizes for windows.
                      Format: {WindowType: (height, width)}
                      If None, uses default minimum sizes.
        """
        self.min_sizes = min_sizes or self.MIN_WINDOW_SIZES.copy()

    def calculate_layout(self, terminal_height: int, terminal_width: int) -> LayoutInfo:
        """
        Calculate positions and sizes for all windows.

        Args:
            terminal_height: Terminal height in rows
            terminal_width: Terminal width in columns

        Returns:
            LayoutInfo containing calculated window geometries

        Raises:
            TerminalTooSmallError: If terminal doesn't meet minimum requirements
        """
        # Validate terminal size first
        if not self.validate_terminal_size(terminal_height, terminal_width):
            raise TerminalTooSmallError(
                (terminal_height, terminal_width),
                (self.MIN_TERMINAL_HEIGHT, self.MIN_TERMINAL_WIDTH)
            )

        layout = LayoutInfo()
        layout.terminal_height = terminal_height
        layout.terminal_width = terminal_width

        # Calculate window geometries using fixed layout strategy
        self._calculate_top_window(layout)
        self._calculate_bottom_window(layout)
        self._calculate_left_window(layout)
        self._calculate_main_window(layout)

        # Validate that all windows meet minimum size requirements
        self._validate_window_sizes(layout)

        return layout

    def validate_terminal_size(self, height: int, width: int) -> bool:
        """
        Check if terminal meets minimum requirements (120x60).

        Args:
            height: Terminal height in rows
            width: Terminal width in columns

        Returns:
            True if terminal meets minimum requirements, False otherwise
        """
        return height >= self.MIN_TERMINAL_HEIGHT and width >= self.MIN_TERMINAL_WIDTH

    def detect_size_change(self, current_layout: LayoutInfo, 
                          new_height: int, new_width: int) -> bool:
        """
        Detect if terminal size has changed from current layout.

        Args:
            current_layout: Current layout information
            new_height: New terminal height
            new_width: New terminal width

        Returns:
            True if size has changed, False otherwise
        """
        return (current_layout.terminal_height != new_height or 
                current_layout.terminal_width != new_width)

    def _calculate_top_window(self, layout: LayoutInfo) -> None:
        """
        Calculate top window geometry.

        Args:
            layout: Layout info to update with top window geometry
        """
        # Top window: Fixed height of 3 rows, full width
        layout.top_window.y = 0
        layout.top_window.x = 0
        layout.top_window.height = 3
        layout.top_window.width = layout.terminal_width

    def _calculate_bottom_window(self, layout: LayoutInfo) -> None:
        """
        Calculate bottom window geometry.

        Args:
            layout: Layout info to update with bottom window geometry
        """
        # Bottom window: Fixed height of 3 rows, full width, at bottom
        layout.bottom_window.y = layout.terminal_height - 3
        layout.bottom_window.x = 0
        layout.bottom_window.height = 3
        layout.bottom_window.width = layout.terminal_width

    def _calculate_left_window(self, layout: LayoutInfo) -> None:
        """
        Calculate left window geometry.

        Args:
            layout: Layout info to update with left window geometry
        """
        # Remaining height after top and bottom windows
        remaining_height = layout.terminal_height - 6  # Subtract top (3) and bottom (3)

        # Left window: Fixed width of 25% of terminal width, minimum 25 columns
        left_width = max(25, layout.terminal_width // 4)

        layout.left_window.y = 3  # Below top window
        layout.left_window.x = 0
        layout.left_window.height = remaining_height
        layout.left_window.width = left_width

    def _calculate_main_window(self, layout: LayoutInfo) -> None:
        """
        Calculate main window geometry.

        Args:
            layout: Layout info to update with main window geometry
        """
        # Remaining height after top and bottom windows
        remaining_height = layout.terminal_height - 6  # Subtract top (3) and bottom (3)

        # Main window: Remaining space after left window
        layout.main_window.y = 3  # Below top window
        layout.main_window.x = layout.left_window.width
        layout.main_window.height = remaining_height
        layout.main_window.width = layout.terminal_width - layout.left_window.width

    def _validate_window_sizes(self, layout: LayoutInfo) -> None:
        """
        Validate that all windows meet minimum size requirements.

        Args:
            layout: Layout to validate

        Raises:
            TerminalTooSmallError: If any window is below minimum size
        """
        windows_to_check = [
            (WindowType.TOP, layout.top_window),
            (WindowType.LEFT, layout.left_window),
            (WindowType.MAIN, layout.main_window),
            (WindowType.BOTTOM, layout.bottom_window)
        ]

        for window_type, geometry in windows_to_check:
            min_height, min_width = self.min_sizes[window_type]
            
            if geometry.height < min_height or geometry.width < min_width:
                raise TerminalTooSmallError(
                    (layout.terminal_height, layout.terminal_width),
                    (self.MIN_TERMINAL_HEIGHT, self.MIN_TERMINAL_WIDTH)
                )

    def get_minimum_terminal_size(self) -> Tuple[int, int]:
        """
        Get the minimum required terminal size.

        Returns:
            Tuple of (height, width) minimum requirements
        """
        return (self.MIN_TERMINAL_HEIGHT, self.MIN_TERMINAL_WIDTH)

    def get_window_minimum_size(self, window_type: WindowType) -> Tuple[int, int]:
        """
        Get minimum size for a specific window type.

        Args:
            window_type: Type of window to get minimum size for

        Returns:
            Tuple of (height, width) minimum requirements for the window
        """
        return self.min_sizes.get(window_type, (1, 1))