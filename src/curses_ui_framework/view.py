"""
WindowView class for the Curses UI Framework.

This module implements the View component of the MVC architecture,
handling all visual presentation and UI rendering.
"""

import curses
from typing import List, Dict
from .model import ApplicationModel
from .exceptions import WindowCreationError
from .frame_renderer import FrameRenderer, FrameStyle
from .content_manager import ContentManager


class WindowView:
    """
    Manages all visual presentation for the curses UI framework.

    This class handles rendering of all windows and visual elements,
    implementing the View component of the MVC pattern.
    """

    def __init__(self, stdscr):
        """
        Initialize view with main screen.

        Args:
            stdscr: Main curses screen object
        """
        self.stdscr = stdscr
        self.windows = {}
        self.content_managers: Dict[str, ContentManager] = {}
        self.layout_info = None
        self.frame_renderer = FrameRenderer()
        
        # Track which windows need updates for efficient refresh
        self._dirty_windows = set()
        self._last_render_data = {}

        # Initialize colors if available
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # For highlighting

    def initialize_windows(self, layout_info) -> None:
        """
        Create and initialize all windows based on layout.

        Args:
            layout_info: Layout information containing window geometries
        """
        self.layout_info = layout_info

        try:
            # Create top window
            self.windows['top'] = curses.newwin(
                layout_info.top_window.height,
                layout_info.top_window.width,
                layout_info.top_window.y,
                layout_info.top_window.x
            )

            # Create left window
            self.windows['left'] = curses.newwin(
                layout_info.left_window.height,
                layout_info.left_window.width,
                layout_info.left_window.y,
                layout_info.left_window.x
            )

            # Create main window
            self.windows['main'] = curses.newwin(
                layout_info.main_window.height,
                layout_info.main_window.width,
                layout_info.main_window.y,
                layout_info.main_window.x
            )

            # Create bottom window
            self.windows['bottom'] = curses.newwin(
                layout_info.bottom_window.height,
                layout_info.bottom_window.width,
                layout_info.bottom_window.y,
                layout_info.bottom_window.x
            )

        except curses.error as e:
            raise WindowCreationError("window", str(e))

        # Draw frames for all windows
        self._draw_all_frames()
        
        # Create content managers for windows that need content management
        self._create_content_managers()

    def render_all(self, model: ApplicationModel) -> None:
        """
        Render all windows with current model data using efficient selective updates.

        Args:
            model: Application model containing current state
        """
        # Check what data has changed since last render
        current_data = {
            'title': model.get_title(),
            'author': model.get_author(), 
            'version': model.get_version(),
            'navigation_items': model.get_navigation_items(),
            'selected_navigation': model.get_selected_navigation_index(),
            'main_content': model.get_main_content(),
            'status': model.get_status(),
            'bottom_mode': model.get_bottom_window_mode()
        }
        
        # Mark windows as dirty if their data changed
        if self._last_render_data.get('title') != current_data['title'] or \
           self._last_render_data.get('author') != current_data['author'] or \
           self._last_render_data.get('version') != current_data['version']:
            self.mark_window_dirty('top')
            
        if self._last_render_data.get('navigation_items') != current_data['navigation_items'] or \
           self._last_render_data.get('selected_navigation') != current_data['selected_navigation']:
            self.mark_window_dirty('left')
            
        if self._last_render_data.get('main_content') != current_data['main_content']:
            self.mark_window_dirty('main')
            
        if self._last_render_data.get('status') != current_data['status'] or \
           self._last_render_data.get('bottom_mode') != current_data['bottom_mode']:
            self.mark_window_dirty('bottom')
        
        # Render only dirty windows
        if 'top' in self._dirty_windows:
            self.render_top_window(current_data['title'], current_data['author'], current_data['version'])
            
        if 'left' in self._dirty_windows:
            self.render_left_window(current_data['navigation_items'], current_data['selected_navigation'])
            
        if 'main' in self._dirty_windows:
            self.render_main_window(current_data['main_content'])
            
        if 'bottom' in self._dirty_windows:
            self.render_bottom_window(current_data['status'], current_data['bottom_mode'])

        # Refresh only dirty windows
        self.refresh_dirty_windows()
        
        # Store current data for next comparison
        self._last_render_data = current_data.copy()
        
        # Clear dirty flags
        self._dirty_windows.clear()

    def render_top_window(self, title: str, author: str, version: str) -> None:
        """
        Render top window with application metadata using ContentManager.

        Args:
            title: Application title
            author: Application author
            version: Application version
        """
        if 'top' not in self.windows or 'top' not in self.content_managers:
            return

        # Format metadata for display
        metadata_text = self._format_application_metadata(title, author, version)
        
        # Use ContentManager with centered text for proper formatting
        content_manager = self.content_managers['top']
        content_manager.set_centered_text(metadata_text)

    def _format_application_metadata(self, title: str, author: str, version: str) -> str:
        """
        Format application metadata for display in top window.

        Args:
            title: Application title
            author: Application author  
            version: Application version

        Returns:
            Formatted metadata string
        """
        # Create centered display format
        # Line 1: Title (centered)
        # Line 2: Author - Version (centered)
        
        lines = []
        
        # Add title if provided
        if title:
            lines.append(title)
        
        # Add author and version info if provided
        info_parts = []
        if author:
            info_parts.append(author)
        if version:
            info_parts.append(f"v{version}")
        
        if info_parts:
            lines.append(" - ".join(info_parts))
        
        return '\n'.join(lines)

    def render_left_window(self, items: List[str], selected: int) -> None:
        """
        Render left navigation window with enhanced navigation support.

        Args:
            items: List of navigation items
            selected: Index of selected item
        """
        if 'left' not in self.windows:
            return

        window = self.windows['left']
        
        # Get content area within frame
        start_y, start_x, content_height, content_width = self.frame_renderer.get_content_area(window)
        
        # Clear content area
        for y in range(start_y, start_y + content_height):
            for x in range(start_x, start_x + content_width):
                try:
                    window.addch(y, x, ' ')
                except curses.error:
                    pass

        # Redraw frame
        self.frame_renderer.draw_frame(window)

        # Render navigation items within content area in list format
        if not items:
            # Show placeholder text when no items
            placeholder = "No items"
            if len(placeholder) <= content_width:
                try:
                    window.addstr(start_y, start_x, placeholder)
                except curses.error:
                    pass
            return

        # Calculate scrolling if there are more items than visible space
        visible_items = min(len(items), content_height)
        scroll_offset = 0
        
        # If selected item is outside visible area, scroll to show it
        if selected >= content_height:
            scroll_offset = selected - content_height + 1
        elif selected < 0:
            scroll_offset = 0

        # Ensure we don't scroll past the end
        max_scroll = max(0, len(items) - content_height)
        scroll_offset = min(scroll_offset, max_scroll)

        # Render visible navigation items
        for i in range(visible_items):
            item_index = i + scroll_offset
            if item_index >= len(items):
                break
                
            item = items[item_index]
            y_pos = start_y + i
            
            # Format item with fixed width maintenance
            # Add numbering for better navigation (1-based for user display)
            item_number = f"{item_index + 1:2d}. "
            available_width = content_width - len(item_number)
            
            # Truncate item text to fit available width
            if len(item) > available_width:
                truncated_item = item[:available_width - 3] + "..."
            else:
                truncated_item = item
            
            # Create full display text with consistent width
            display_text = item_number + truncated_item
            # Pad to full content width for consistent appearance
            padded_text = display_text.ljust(content_width)
            
            if item_index == selected:
                # Highlight selected item with visual indicators
                if curses.has_colors():
                    window.attron(curses.color_pair(2))
                
                # Add selection indicator
                selection_indicator = ">"
                highlighted_text = selection_indicator + " " + display_text[2:]
                highlighted_text = highlighted_text[:content_width].ljust(content_width)
                
                try:
                    window.addstr(y_pos, start_x, highlighted_text)
                except curses.error:
                    pass
                    
                if curses.has_colors():
                    window.attroff(curses.color_pair(2))
            else:
                try:
                    window.addstr(y_pos, start_x, padded_text)
                except curses.error:
                    pass

        # Add scroll indicators if needed
        if len(items) > content_height:
            self._add_scroll_indicators(window, start_y, start_x, content_height, 
                                      content_width, scroll_offset, len(items))

    def render_main_window(self, content: str) -> None:
        """
        Render main content window using ContentManager with comprehensive text display.

        Args:
            content: Text content to display
        """
        if 'main' not in self.windows or 'main' not in self.content_managers:
            return

        # Use ContentManager for advanced text management and scrolling
        content_manager = self.content_managers['main']
        content_manager.set_text(content)

    def update_main_content(self, content: str) -> None:
        """
        Update main window content using ContentManager with efficient refresh.

        Args:
            content: New content to display
        """
        if 'main' in self.content_managers:
            self.content_managers['main'].set_text(content)
            self.mark_window_dirty('main')

    def append_main_content(self, content: str) -> None:
        """
        Append content to main window using ContentManager with efficient refresh.

        Args:
            content: Content to append
        """
        if 'main' in self.content_managers:
            self.content_managers['main'].append_line(content)
            self.mark_window_dirty('main')

    def clear_main_content(self) -> None:
        """Clear main window content using ContentManager with efficient refresh."""
        if 'main' in self.content_managers:
            self.content_managers['main'].clear()
            self.mark_window_dirty('main')

    def scroll_main_content(self, direction: str, lines: int = 1) -> None:
        """
        Scroll main window content.

        Args:
            direction: 'up' or 'down'
            lines: Number of lines to scroll
        """
        if 'main' in self.content_managers:
            content_manager = self.content_managers['main']
            if direction == 'up':
                content_manager.scroll_up(lines)
            elif direction == 'down':
                content_manager.scroll_down(lines)

    def can_scroll_main_content(self, direction: str) -> bool:
        """
        Check if main content can be scrolled in the given direction.

        Args:
            direction: 'up' or 'down'

        Returns:
            True if scrolling is possible in that direction
        """
        if 'main' in self.content_managers:
            content_manager = self.content_managers['main']
            if direction == 'up':
                return content_manager.can_scroll_up()
            elif direction == 'down':
                return content_manager.can_scroll_down()
        return False

    def set_main_content_with_status(self, content: str, status: str = "") -> None:
        """
        Set main window content with processing status display.

        Args:
            content: Main text content to display
            status: Processing status to show (optional)
        """
        if 'main' in self.content_managers:
            # Combine content with status if provided
            full_content = content
            if status:
                full_content = f"[Status: {status}]\n\n{content}"
            
            self.content_managers['main'].set_text(full_content)

    def show_processing_status(self, message: str, progress: float = None) -> None:
        """
        Show processing status in main window.

        Args:
            message: Status message to display
            progress: Optional progress value (0.0 to 1.0)
        """
        if 'main' in self.content_managers:
            status_content = f"Processing: {message}\n\n"
            
            if progress is not None:
                # Create a simple progress bar
                bar_width = 40
                filled_width = int(bar_width * max(0.0, min(1.0, progress)))
                bar = "█" * filled_width + "░" * (bar_width - filled_width)
                percentage = int(progress * 100)
                status_content += f"Progress: [{bar}] {percentage}%\n\n"
            
            status_content += "Please wait while the operation completes..."
            
            self.content_managers['main'].set_text(status_content)

    def get_main_content_info(self) -> dict:
        """
        Get information about main window content.

        Returns:
            Dictionary with content information including scroll state
        """
        if 'main' in self.content_managers:
            content_manager = self.content_managers['main']
            scroll_offset, total_lines, visible_lines = content_manager.get_scroll_info()
            
            return {
                'total_lines': total_lines,
                'visible_lines': visible_lines,
                'scroll_offset': scroll_offset,
                'can_scroll_up': content_manager.can_scroll_up(),
                'can_scroll_down': content_manager.can_scroll_down(),
                'content_lines': content_manager.get_content_lines()
            }
        return {}

    def get_content_manager(self, window_name: str) -> ContentManager:
        """
        Get content manager for a specific window.

        Args:
            window_name: Name of the window ('main', 'left', 'top', 'bottom')

        Returns:
            ContentManager instance for the window, or None if not found
        """
        return self.content_managers.get(window_name)

    def render_bottom_window(self, status: str, mode: str) -> None:
        """
        Render bottom status/command window with dual-mode functionality.

        Args:
            status: Status text to display
            mode: Current window mode ("display" or "input")
        """
        if 'bottom' not in self.windows:
            return

        window = self.windows['bottom']
        
        # Get content area within frame
        start_y, start_x, content_height, content_width = self.frame_renderer.get_content_area(window)
        
        # Clear content area
        for y in range(start_y, start_y + content_height):
            for x in range(start_x, start_x + content_width):
                try:
                    window.addch(y, x, ' ')
                except curses.error:
                    pass

        # Redraw frame
        self.frame_renderer.draw_frame(window)

        # Render based on mode within content area
        if content_height > 0 and content_width > 0:
            if mode == "input":
                self._render_input_mode(window, start_y, start_x, content_height, content_width)
            else:
                self._render_display_mode(window, start_y, start_x, content_height, content_width, status)

    def _render_input_mode(self, window, start_y: int, start_x: int, 
                          content_height: int, content_width: int) -> None:
        """
        Render bottom window in input mode.

        Args:
            window: The curses window
            start_y: Starting Y position of content area
            start_x: Starting X position of content area
            content_height: Height of content area
            content_width: Width of content area
        """
        # Show command prompt and input
        prompt = "Command: "
        
        # Get current command input from model if available
        command_input = ""
        if hasattr(self, '_current_command_input'):
            command_input = self._current_command_input
        
        # First line: command prompt and input with echo
        if content_height >= 1:
            prompt_line = prompt + command_input
            # Add cursor indicator
            cursor_pos = len(prompt_line)
            if cursor_pos < content_width:
                prompt_line += "_"  # Simple cursor indicator
            
            # Truncate if too long, but show the end of the input (most recent typing)
            if len(prompt_line) > content_width:
                # Show the prompt and as much of the recent input as possible
                prompt_len = len(prompt)
                available_for_input = content_width - prompt_len - 1  # -1 for cursor
                if available_for_input > 0:
                    # Show the end of the command input (most recent characters)
                    truncated_input = command_input[-(available_for_input):]
                    display_line = prompt + truncated_input + "_"
                else:
                    # If prompt is too long, just show what fits
                    display_line = prompt_line[:content_width]
            else:
                display_line = prompt_line
            
            try:
                window.addstr(start_y, start_x, display_line)
            except curses.error:
                pass

        # Second line: help text if there's space
        if content_height >= 2:
            help_text = "Press Tab to switch to display mode, Enter to execute"
            help_line = help_text[:content_width] if len(help_text) > content_width else help_text
            try:
                window.addstr(start_y + 1, start_x, help_line)
            except curses.error:
                pass

    def _render_display_mode(self, window, start_y: int, start_x: int, 
                           content_height: int, content_width: int, status: str) -> None:
        """
        Render bottom window in display mode with statistics.

        Args:
            window: The curses window
            start_y: Starting Y position of content area
            start_x: Starting X position of content area
            content_height: Height of content area
            content_width: Width of content area
            status: Status text to display
        """
        lines_to_show = []
        
        # First line: status
        if status:
            status_line = f"Status: {status}"
            lines_to_show.append(status_line)
        
        # Get statistics if available
        if hasattr(self, '_current_statistics'):
            stats = self._current_statistics
            
            # Second line: command statistics
            if 'total_commands' in stats and 'last_command' in stats:
                cmd_stats = f"Commands: {stats['total_commands']}"
                if stats['last_command']:
                    cmd_stats += f" | Last: {stats['last_command'][:20]}..."
                lines_to_show.append(cmd_stats)
            
            # Third line: content statistics
            if 'content_lines' in stats:
                content_stats = f"Content lines: {stats['content_lines']}"
                if 'uptime' in stats:
                    content_stats += f" | Uptime: {stats['uptime']}s"
                lines_to_show.append(content_stats)
        
        # If no statistics, show help
        if len(lines_to_show) <= 1:
            lines_to_show.append("Press Tab to switch to input mode")
        
        # Render lines
        for i, line in enumerate(lines_to_show[:content_height]):
            y_pos = start_y + i
            # Truncate line to fit content width
            display_line = line[:content_width] if len(line) > content_width else line
            try:
                window.addstr(y_pos, start_x, display_line)
            except curses.error:
                pass

    def set_bottom_window_command_input(self, text: str) -> None:
        """
        Set the current command input text for display.

        Args:
            text: Command input text
        """
        self._current_command_input = text

    def set_bottom_window_statistics(self, statistics: dict) -> None:
        """
        Set the current statistics for display.

        Args:
            statistics: Dictionary of statistics to display
        """
        self._current_statistics = statistics

    def resize_windows(self, new_layout_info) -> None:
        """
        Resize all windows for new layout.

        Args:
            new_layout_info: New layout information
        """
        self.layout_info = new_layout_info

        # Clear existing windows
        for window in self.windows.values():
            window.clear()

        # Recreate windows with new layout
        self.initialize_windows(new_layout_info)
        
        # Mark all windows as dirty since they were recreated
        self.mark_all_windows_dirty()

    def cleanup(self) -> None:
        """Clean up window resources."""
        for window in self.windows.values():
            window.clear()
        self.windows.clear()
        self.content_managers.clear()
        self._dirty_windows.clear()
        self._last_render_data.clear()

    def mark_window_dirty(self, window_name: str) -> None:
        """
        Mark a window as needing refresh.
        
        Args:
            window_name: Name of the window to mark dirty ('top', 'left', 'main', 'bottom')
        """
        if window_name in self.windows:
            self._dirty_windows.add(window_name)

    def mark_all_windows_dirty(self) -> None:
        """Mark all windows as needing refresh."""
        self._dirty_windows.update(self.windows.keys())

    def refresh_dirty_windows(self) -> None:
        """Refresh only the windows marked as dirty."""
        for window_name in self._dirty_windows:
            if window_name in self.windows:
                self.windows[window_name].refresh()

    def refresh_window(self, window_name: str) -> None:
        """
        Refresh a specific window immediately.
        
        Args:
            window_name: Name of the window to refresh
        """
        if window_name in self.windows:
            self.windows[window_name].refresh()

    def refresh_all_windows(self) -> None:
        """Force refresh of all windows."""
        for window in self.windows.values():
            window.refresh()

    def update_content(self, window_name: str, content: str) -> None:
        """
        Update content in a specific window efficiently.
        
        Args:
            window_name: Name of the window to update
            content: New content to set
        """
        if window_name in self.content_managers:
            self.content_managers[window_name].set_text(content)
            self.mark_window_dirty(window_name)

    def append_content(self, window_name: str, content: str) -> None:
        """
        Append content to a specific window efficiently.
        
        Args:
            window_name: Name of the window to append to
            content: Content to append
        """
        if window_name in self.content_managers:
            self.content_managers[window_name].append_line(content)
            self.mark_window_dirty(window_name)

    def clear_content(self, window_name: str) -> None:
        """
        Clear content in a specific window efficiently.
        
        Args:
            window_name: Name of the window to clear
        """
        if window_name in self.content_managers:
            self.content_managers[window_name].clear()
            self.mark_window_dirty(window_name)

    def _add_scroll_indicators(self, window, start_y: int, start_x: int, 
                             content_height: int, content_width: int, 
                             scroll_offset: int, total_items: int) -> None:
        """
        Add scroll indicators to show there are more items above/below.

        Args:
            window: The curses window
            start_y: Starting Y position of content area
            start_x: Starting X position of content area
            content_height: Height of content area
            content_width: Width of content area
            scroll_offset: Current scroll offset
            total_items: Total number of items
        """
        # Add up arrow if there are items above
        if scroll_offset > 0:
            indicator_pos = start_x + content_width - 1
            try:
                window.addch(start_y, indicator_pos, '^')
            except curses.error:
                pass

        # Add down arrow if there are items below
        if scroll_offset + content_height < total_items:
            indicator_pos = start_x + content_width - 1
            try:
                window.addch(start_y + content_height - 1, indicator_pos, 'v')
            except curses.error:
                pass

    def _draw_all_frames(self) -> None:
        """Draw frames for all windows."""
        for window in self.windows.values():
            if window is not None:
                self.frame_renderer.draw_frame(window)

    def _create_content_managers(self) -> None:
        """Create content managers for windows that support content management."""
        # Create content managers for main window (primary content management)
        if 'main' in self.windows:
            self.content_managers['main'] = ContentManager(self.windows['main'])
        
        # Create content managers for other windows that may need content management
        if 'left' in self.windows:
            self.content_managers['left'] = ContentManager(self.windows['left'])
        
        if 'top' in self.windows:
            self.content_managers['top'] = ContentManager(self.windows['top'])
            
        if 'bottom' in self.windows:
            self.content_managers['bottom'] = ContentManager(self.windows['bottom'])