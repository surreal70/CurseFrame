"""
ApplicationModel class for the Curses UI Framework.

This module implements the Model component of the MVC architecture,
managing application state and data independently of the UI.
"""

from typing import List


class ApplicationModel:
    """
    Manages application state and data for the curses UI framework.

    This class stores all application data including metadata (title, author, version),
    navigation items, main content, and status information. It provides a clean
    interface for the controller to manage application state.
    """

    def __init__(self, title: str, author: str, version: str):
        """
        Initialize application model with metadata.

        Args:
            title: Application title to display in top window
            author: Application author information
            version: Application version string
        """
        self._title = title
        self._author = author
        self._version = version
        self._navigation_items: List[str] = []
        self._selected_navigation_index = 0
        self._main_content = ""
        self._status = ""
        self._bottom_window_mode = "display"  # "display" or "input"
        self._command_input = ""
        self._command_history: List[str] = []
        self._statistics = {
            'total_commands': 0,
            'last_command': '',
            'uptime': 0,
            'content_lines': 0
        }

    def get_title(self) -> str:
        """Get application title."""
        return self._title

    def get_author(self) -> str:
        """Get application author."""
        return self._author

    def get_version(self) -> str:
        """Get application version."""
        return self._version

    def set_navigation_items(self, items: List[str]) -> None:
        """
        Set navigation menu items.

        Args:
            items: List of navigation item strings
        """
        self._navigation_items = items.copy()
        # Reset selection if current index is out of bounds
        if self._selected_navigation_index >= len(self._navigation_items):
            self._selected_navigation_index = 0

    def get_navigation_items(self) -> List[str]:
        """Get current navigation items."""
        return self._navigation_items.copy()

    def get_navigation_item_count(self) -> int:
        """Get the number of navigation items."""
        return len(self._navigation_items)

    def has_navigation_items(self) -> bool:
        """Check if there are any navigation items."""
        return len(self._navigation_items) > 0

    def get_selected_navigation_index(self) -> int:
        """Get currently selected navigation item index."""
        return self._selected_navigation_index

    def set_selected_navigation_index(self, index: int) -> None:
        """
        Set selected navigation item index.

        Args:
            index: Index of navigation item to select
        """
        if 0 <= index < len(self._navigation_items):
            self._selected_navigation_index = index

    def set_main_content(self, content: str) -> None:
        """
        Set main window content.

        Args:
            content: Text content to display in main window
        """
        self._main_content = content

    def get_main_content(self) -> str:
        """Get current main content."""
        return self._main_content

    def set_status(self, status: str) -> None:
        """
        Set bottom window status.

        Args:
            status: Status text to display
        """
        self._status = status

    def get_status(self) -> str:
        """Get current status."""
        return self._status

    def set_bottom_window_mode(self, mode: str) -> None:
        """
        Set bottom window mode.

        Args:
            mode: Either "display" or "input"
        """
        if mode in ("display", "input"):
            self._bottom_window_mode = mode

    def get_bottom_window_mode(self) -> str:
        """Get current bottom window mode."""
        return self._bottom_window_mode

    def get_command_input(self) -> str:
        """Get current command input text."""
        return self._command_input

    def set_command_input(self, text: str) -> None:
        """
        Set command input text.

        Args:
            text: Command input text
        """
        self._command_input = text

    def add_command_to_history(self, command: str) -> None:
        """
        Add a command to the command history.

        Args:
            command: Command to add to history
        """
        if command.strip():
            self._command_history.append(command.strip())
            self._statistics['total_commands'] += 1
            self._statistics['last_command'] = command.strip()

    def get_command_history(self) -> List[str]:
        """Get command history."""
        return self._command_history.copy()

    def clear_command_input(self) -> None:
        """Clear the current command input."""
        self._command_input = ""

    def get_statistics(self) -> dict:
        """Get current application statistics."""
        return self._statistics.copy()

    def update_statistics(self, key: str, value) -> None:
        """
        Update a specific statistic.

        Args:
            key: Statistic key to update
            value: New value for the statistic
        """
        if key in self._statistics:
            self._statistics[key] = value

    def increment_statistic(self, key: str, amount: int = 1) -> None:
        """
        Increment a numeric statistic.

        Args:
            key: Statistic key to increment
            amount: Amount to increment by (default 1)
        """
        if key in self._statistics and isinstance(self._statistics[key], (int, float)):
            self._statistics[key] += amount