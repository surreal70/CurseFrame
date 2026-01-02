"""
ContentManager class for the Curses UI Framework.

This module provides text management functionality including setting,
appending, clearing, wrapping, formatting, and scrolling capabilities
for window content with advanced text styling support.
"""

import curses
import textwrap
import hashlib
from typing import List, Optional, Tuple, Dict, Union
from dataclasses import dataclass
from enum import Enum


class TextStyle(Enum):
    """Text styling options."""
    NORMAL = 0
    BOLD = curses.A_BOLD
    UNDERLINE = curses.A_UNDERLINE
    REVERSE = curses.A_REVERSE
    BLINK = curses.A_BLINK
    DIM = curses.A_DIM


class TextColor(Enum):
    """Text color options."""
    DEFAULT = 0
    BLACK = curses.COLOR_BLACK
    RED = curses.COLOR_RED
    GREEN = curses.COLOR_GREEN
    YELLOW = curses.COLOR_YELLOW
    BLUE = curses.COLOR_BLUE
    MAGENTA = curses.COLOR_MAGENTA
    CYAN = curses.COLOR_CYAN
    WHITE = curses.COLOR_WHITE


@dataclass
class TextFormat:
    """Text formatting specification."""
    style: TextStyle = TextStyle.NORMAL
    fg_color: TextColor = TextColor.DEFAULT
    bg_color: TextColor = TextColor.DEFAULT
    
    def to_curses_attr(self, color_pair: int = 0) -> int:
        """Convert to curses attributes."""
        attr = self.style.value
        if color_pair > 0:
            attr |= curses.color_pair(color_pair)
        return attr


@dataclass
class FormattedText:
    """Text with formatting information."""
    text: str
    format: TextFormat = None
    
    def __post_init__(self):
        if self.format is None:
            self.format = TextFormat()


class ContentManager:
    """
    Manages content within curses windows.

    This class provides comprehensive text management functionality including
    text setting, appending, clearing, wrapping, formatting, and scrolling
    capabilities for content that exceeds window boundaries.
    """

    def __init__(self, window: curses.window):
        """
        Initialize content manager for a window.

        Args:
            window: The curses window to manage content for
        """
        self.window = window
        self._content_lines: List[Union[str, List[FormattedText]]] = []
        self._scroll_offset = 0
        self._max_width = 0
        self._max_height = 0
        self._content_changed = False
        self._last_content_hash = None
        self._color_pairs: Dict[Tuple[TextColor, TextColor], int] = {}
        self._next_color_pair = 1
        self._update_dimensions()
        self._initialize_colors()

    def _update_dimensions(self) -> None:
        """Update internal dimensions based on current window size."""
        try:
            height, width = self.window.getmaxyx()
            # Account for frame borders (1 character on each side)
            self._max_height = max(1, height - 2)
            self._max_width = max(1, width - 2)
        except curses.error:
            self._max_height = 1
            self._max_width = 1

    def _initialize_colors(self) -> None:
        """Initialize color pairs for text formatting."""
        if not curses.has_colors():
            return
            
        try:
            # Initialize basic color pairs
            self._get_color_pair(TextColor.DEFAULT, TextColor.DEFAULT)
            self._get_color_pair(TextColor.RED, TextColor.DEFAULT)
            self._get_color_pair(TextColor.GREEN, TextColor.DEFAULT)
            self._get_color_pair(TextColor.YELLOW, TextColor.DEFAULT)
            self._get_color_pair(TextColor.BLUE, TextColor.DEFAULT)
            self._get_color_pair(TextColor.MAGENTA, TextColor.DEFAULT)
            self._get_color_pair(TextColor.CYAN, TextColor.DEFAULT)
            self._get_color_pair(TextColor.WHITE, TextColor.DEFAULT)
        except curses.error:
            # Color initialization failed, continue without colors
            pass

    def _get_color_pair(self, fg_color: TextColor, bg_color: TextColor) -> int:
        """
        Get or create a color pair for the given colors.
        
        Args:
            fg_color: Foreground color
            bg_color: Background color
            
        Returns:
            Color pair number, or 0 if colors not available
        """
        if not curses.has_colors():
            return 0
            
        color_key = (fg_color, bg_color)
        
        if color_key in self._color_pairs:
            return self._color_pairs[color_key]
        
        # Create new color pair
        try:
            # Check if we have room for more color pairs
            max_color_pairs = getattr(curses, 'COLOR_PAIRS', 64)  # Default to 64 if not available
            if self._next_color_pair < max_color_pairs:
                fg_val = fg_color.value if fg_color != TextColor.DEFAULT else -1
                bg_val = bg_color.value if bg_color != TextColor.DEFAULT else -1
                curses.init_pair(self._next_color_pair, fg_val, bg_val)
                self._color_pairs[color_key] = self._next_color_pair
                self._next_color_pair += 1
                return self._color_pairs[color_key]
        except curses.error:
            pass
        
        return 0

    def set_text(self, text: str, row: int = 0, col: int = 0) -> None:
        """
        Set text at specified position.

        Args:
            text: Text content to set
            row: Row position (0-based, relative to content area)
            col: Column position (0-based, relative to content area)
        """
        # Check if content actually changed
        content_hash = hashlib.md5(text.encode()).hexdigest()
        if content_hash == self._last_content_hash:
            return  # No change, skip update
        
        # Clear existing content
        self.clear()
        
        # Split text into lines and wrap each line
        lines = text.split('\n')
        wrapped_lines = []
        
        for line in lines:
            if len(line) <= self._max_width:
                wrapped_lines.append(line)
            else:
                # Wrap long lines
                wrapped = textwrap.wrap(line, width=self._max_width, 
                                      break_long_words=True, 
                                      break_on_hyphens=True)
                wrapped_lines.extend(wrapped)
        
        # Store wrapped content
        self._content_lines = wrapped_lines
        self._scroll_offset = 0
        self._content_changed = True
        self._last_content_hash = content_hash
        
        # Render the content
        self._render_content()

    def set_centered_text(self, text: str) -> None:
        """
        Set text with center alignment.

        Args:
            text: Text content to set (will be centered)
        """
        # Clear existing content
        self.clear()
        
        # Split text into lines
        lines = text.split('\n')
        centered_lines = []
        
        for line in lines:
            if len(line) <= self._max_width:
                # Center the line
                padding = (self._max_width - len(line)) // 2
                centered_line = ' ' * padding + line
                centered_lines.append(centered_line)
            else:
                # Wrap long lines first, then center each wrapped line
                wrapped = textwrap.wrap(line, width=self._max_width,
                                      break_long_words=True,
                                      break_on_hyphens=True)
                for wrapped_line in wrapped:
                    padding = (self._max_width - len(wrapped_line)) // 2
                    centered_line = ' ' * padding + wrapped_line
                    centered_lines.append(centered_line)
        
        # Store centered content
        self._content_lines = centered_lines
        self._scroll_offset = 0
        
        # Render the content
        self._render_content()

    def append_line(self, text: str) -> None:
        """
        Append a line of text.

        Args:
            text: Text line to append
        """
        # Wrap the new line if necessary
        wrapped = []
        if len(text) <= self._max_width:
            self._content_lines.append(text)
            wrapped = [text]
        else:
            wrapped = textwrap.wrap(text, width=self._max_width,
                                  break_long_words=True,
                                  break_on_hyphens=True)
            self._content_lines.extend(wrapped)
        
        # Mark content as changed
        self._content_changed = True
        self._last_content_hash = None  # Invalidate hash since content changed
        
        # Auto-scroll to show new content if we're at the bottom
        if self._scroll_offset + self._max_height >= len(self._content_lines) - len(wrapped):
            self._scroll_offset = max(0, len(self._content_lines) - self._max_height)
        
        # Render the updated content
        self._render_content()

    def clear(self) -> None:
        """Clear all content."""
        if self._content_lines:  # Only mark as changed if there was content
            self._content_changed = True
            self._last_content_hash = None
        
        self._content_lines.clear()
        self._scroll_offset = 0
        
        # Clear the window content area (preserve frame)
        try:
            height, width = self.window.getmaxyx()
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    try:
                        self.window.addch(y, x, ' ')
                    except curses.error:
                        pass
        except curses.error:
            pass

    def scroll_up(self, lines: int = 1) -> None:
        """
        Scroll content up.

        Args:
            lines: Number of lines to scroll up
        """
        self._scroll_offset = max(0, self._scroll_offset - lines)
        self._render_content()

    def scroll_down(self, lines: int = 1) -> None:
        """
        Scroll content down.

        Args:
            lines: Number of lines to scroll down
        """
        max_scroll = max(0, len(self._content_lines) - self._max_height)
        self._scroll_offset = min(max_scroll, self._scroll_offset + lines)
        self._render_content()

    def scroll_to_top(self) -> None:
        """Scroll to the top of content."""
        self._scroll_offset = 0
        self._render_content()

    def scroll_to_bottom(self) -> None:
        """Scroll to the bottom of content."""
        self._scroll_offset = max(0, len(self._content_lines) - self._max_height)
        self._render_content()

    def can_scroll_up(self) -> bool:
        """Check if content can be scrolled up."""
        return self._scroll_offset > 0

    def can_scroll_down(self) -> bool:
        """Check if content can be scrolled down."""
        return self._scroll_offset + self._max_height < len(self._content_lines)

    def get_content_lines(self) -> List[Union[str, List[FormattedText]]]:
        """Get all content lines."""
        return self._content_lines.copy()

    def get_visible_lines(self) -> List[Union[str, List[FormattedText]]]:
        """Get currently visible lines."""
        start = self._scroll_offset
        end = min(start + self._max_height, len(self._content_lines))
        return self._content_lines[start:end]

    def get_scroll_info(self) -> Tuple[int, int, int]:
        """
        Get scroll information.

        Returns:
            Tuple of (current_offset, total_lines, visible_lines)
        """
        return (self._scroll_offset, len(self._content_lines), self._max_height)

    def has_content_changed(self) -> bool:
        """
        Check if content has changed since last check.
        
        Returns:
            True if content has changed, False otherwise
        """
        return self._content_changed

    def reset_content_changed_flag(self) -> None:
        """Reset the content changed flag."""
        self._content_changed = False

    def force_refresh(self) -> None:
        """Force a refresh of the content display."""
        self._render_content()

    def set_bold_text(self, text: str) -> None:
        """Set text with bold formatting."""
        self.set_text_with_style(text, TextStyle.BOLD)

    def set_underlined_text(self, text: str) -> None:
        """Set text with underline formatting."""
        self.set_text_with_style(text, TextStyle.UNDERLINE)

    def set_colored_text(self, text: str, color: TextColor) -> None:
        """Set text with specific color."""
        self.set_text_with_style(text, TextStyle.NORMAL, color)

    def append_bold_text(self, text: str) -> None:
        """Append text with bold formatting."""
        self.append_text_with_style(text, TextStyle.BOLD)

    def append_colored_text(self, text: str, color: TextColor) -> None:
        """Append text with specific color."""
        self.append_text_with_style(text, TextStyle.NORMAL, color)

    def create_formatted_text(self, text: str, style: TextStyle = TextStyle.NORMAL,
                             fg_color: TextColor = TextColor.DEFAULT,
                             bg_color: TextColor = TextColor.DEFAULT) -> FormattedText:
        """
        Create a FormattedText object with specified formatting.
        
        Args:
            text: Text content
            style: Text style
            fg_color: Foreground color
            bg_color: Background color
            
        Returns:
            FormattedText object
        """
        format = TextFormat(style, fg_color, bg_color)
        return FormattedText(text, format)

    def combine_formatted_texts(self, *formatted_texts: FormattedText) -> List[FormattedText]:
        """
        Combine multiple FormattedText objects into a list.
        
        Args:
            formatted_texts: Variable number of FormattedText objects
            
        Returns:
            List of FormattedText objects
        """
        return list(formatted_texts)

    def resize(self) -> None:
        """Handle window resize by updating dimensions and re-rendering."""
        self._update_dimensions()
        
        # Re-wrap all content with new width
        if self._content_lines:
            # Convert all content back to a format we can re-wrap
            all_formatted_text = []
            
            for line in self._content_lines:
                if isinstance(line, str):
                    # Convert plain string to FormattedText
                    all_formatted_text.append(FormattedText(line + '\n'))
                else:
                    # Add formatted text from this line
                    all_formatted_text.extend(line)
                    all_formatted_text.append(FormattedText('\n'))  # Add line break
            
            # Remove the last newline if it exists
            if all_formatted_text and all_formatted_text[-1].text == '\n':
                all_formatted_text.pop()
            
            # Re-wrap with new dimensions
            self._content_lines = self._wrap_formatted_text(all_formatted_text)
        
        self._render_content()

    def _render_content(self) -> None:
        """Render the current content to the window with formatting support."""
        # Update dimensions in case window was resized
        self._update_dimensions()
        
        # Clear content area (preserve frame)
        try:
            height, width = self.window.getmaxyx()
            for y in range(1, height - 1):
                for x in range(1, width - 1):
                    try:
                        self.window.addch(y, x, ' ')
                    except curses.error:
                        pass
        except curses.error:
            pass

        # Render visible lines
        visible_lines = self.get_visible_lines()
        
        for i, line in enumerate(visible_lines):
            y_pos = 1 + i  # Start after top frame border
            x_pos = 1      # Start after left frame border
            
            if isinstance(line, str):
                # Handle plain string (backward compatibility)
                display_line = line[:self._max_width] if len(line) > self._max_width else line
                try:
                    self.window.addstr(y_pos, x_pos, display_line)
                except curses.error:
                    pass
            else:
                # Handle formatted text
                current_x = x_pos
                for formatted_text in line:
                    if current_x >= x_pos + self._max_width:
                        break  # Line is full
                    
                    # Get color pair for this text
                    color_pair = self._get_color_pair(formatted_text.format.fg_color, 
                                                    formatted_text.format.bg_color)
                    
                    # Calculate attributes
                    attrs = formatted_text.format.to_curses_attr(color_pair)
                    
                    # Truncate text if it exceeds remaining space
                    remaining_space = (x_pos + self._max_width) - current_x
                    text_to_render = formatted_text.text[:remaining_space]
                    
                    try:
                        if attrs != 0:
                            self.window.addstr(y_pos, current_x, text_to_render, attrs)
                        else:
                            self.window.addstr(y_pos, current_x, text_to_render)
                        current_x += len(text_to_render)
                    except curses.error:
                        # Ignore errors from trying to write outside window bounds
                        pass

    def set_formatted_text(self, text: Union[str, List[FormattedText]], format: TextFormat = None) -> None:
        """
        Set text with formatting attributes.

        Args:
            text: Text content to set (string or list of FormattedText)
            format: Default formatting to apply to plain strings
        """
        if format is None:
            format = TextFormat()
            
        # Check if content actually changed
        content_str = self._formatted_text_to_string(text)
        content_hash = hashlib.md5(content_str.encode()).hexdigest()
        if content_hash == self._last_content_hash:
            return  # No change, skip update
        
        # Clear existing content
        self.clear()
        
        # Process formatted text
        if isinstance(text, str):
            # Convert plain string to formatted text
            formatted_lines = self._wrap_formatted_text([FormattedText(text, format)])
        else:
            # Handle list of FormattedText
            formatted_lines = self._wrap_formatted_text(text)
        
        # Store formatted content
        self._content_lines = formatted_lines
        self._scroll_offset = 0
        self._content_changed = True
        self._last_content_hash = content_hash
        
        # Render the content
        self._render_content()

    def append_formatted_line(self, text: Union[str, List[FormattedText]], format: TextFormat = None) -> None:
        """
        Append a line of formatted text.

        Args:
            text: Text line to append (string or list of FormattedText)
            format: Default formatting to apply to plain strings
        """
        if format is None:
            format = TextFormat()
            
        # Process the new line
        if isinstance(text, str):
            formatted_text = [FormattedText(text, format)]
        else:
            formatted_text = text
            
        # Wrap the formatted text
        wrapped_lines = self._wrap_formatted_text(formatted_text)
        
        # Add to content
        self._content_lines.extend(wrapped_lines)
        
        # Mark content as changed
        self._content_changed = True
        self._last_content_hash = None  # Invalidate hash since content changed
        
        # Auto-scroll to show new content if we're at the bottom
        if self._scroll_offset + self._max_height >= len(self._content_lines) - len(wrapped_lines):
            self._scroll_offset = max(0, len(self._content_lines) - self._max_height)
        
        # Render the updated content
        self._render_content()

    def set_text_with_style(self, text: str, style: TextStyle = TextStyle.NORMAL, 
                           fg_color: TextColor = TextColor.DEFAULT, 
                           bg_color: TextColor = TextColor.DEFAULT) -> None:
        """
        Set text with specific styling.

        Args:
            text: Text content to set
            style: Text style (bold, underline, etc.)
            fg_color: Foreground color
            bg_color: Background color
        """
        format = TextFormat(style, fg_color, bg_color)
        self.set_formatted_text(text, format)

    def append_text_with_style(self, text: str, style: TextStyle = TextStyle.NORMAL,
                              fg_color: TextColor = TextColor.DEFAULT,
                              bg_color: TextColor = TextColor.DEFAULT) -> None:
        """
        Append text with specific styling.

        Args:
            text: Text content to append
            style: Text style (bold, underline, etc.)
            fg_color: Foreground color
            bg_color: Background color
        """
        format = TextFormat(style, fg_color, bg_color)
        self.append_formatted_line(text, format)

    def _formatted_text_to_string(self, text: Union[str, List[FormattedText]]) -> str:
        """Convert formatted text to plain string for hashing."""
        if isinstance(text, str):
            return text
        else:
            return ''.join(ft.text for ft in text)

    def _wrap_formatted_text(self, formatted_text: List[FormattedText]) -> List[List[FormattedText]]:
        """
        Wrap formatted text to fit within window boundaries.
        
        Args:
            formatted_text: List of FormattedText objects
            
        Returns:
            List of lines, each containing a list of FormattedText objects
        """
        lines = []
        current_line = []
        current_line_length = 0
        
        for ft in formatted_text:
            # Split text by newlines first
            text_lines = ft.text.split('\n')
            
            for i, line_text in enumerate(text_lines):
                if i > 0:  # New line encountered
                    if current_line:
                        lines.append(current_line)
                    current_line = []
                    current_line_length = 0
                
                if not line_text:  # Empty line
                    if i > 0:  # Only add empty line if it's from a newline
                        lines.append([FormattedText("", ft.format)])
                    continue
                
                # Wrap long text
                while line_text:
                    available_width = self._max_width - current_line_length
                    
                    if len(line_text) <= available_width:
                        # Text fits on current line
                        current_line.append(FormattedText(line_text, ft.format))
                        current_line_length += len(line_text)
                        break
                    else:
                        # Need to wrap
                        if available_width <= 0:
                            # Start new line
                            if current_line:
                                lines.append(current_line)
                            current_line = []
                            current_line_length = 0
                            available_width = self._max_width
                        
                        # Take what fits
                        chunk = line_text[:available_width]
                        current_line.append(FormattedText(chunk, ft.format))
                        line_text = line_text[available_width:]
                        
                        # Start new line
                        lines.append(current_line)
                        current_line = []
                        current_line_length = 0
        
        # Add remaining content
        if current_line:
            lines.append(current_line)
        
        return lines