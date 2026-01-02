# Configuration and Customization Guide

## Overview

This guide covers configuration options and customization points for the Curses UI Framework. Learn how to adapt the framework to your specific needs while maintaining the MVC architecture.

## Table of Contents

- [Basic Configuration](#basic-configuration)
- [Layout Customization](#layout-customization)
- [Visual Styling](#visual-styling)
- [Input Handling](#input-handling)
- [Content Management](#content-management)
- [Error Handling](#error-handling)
- [Performance Tuning](#performance-tuning)
- [Advanced Customization](#advanced-customization)

## Basic Configuration

### Terminal Requirements

The framework has specific terminal requirements that can be configured:

```python
class CustomController(CursesController):
    # Override minimum terminal size
    MIN_TERMINAL_WIDTH = 100   # Default: 120
    MIN_TERMINAL_HEIGHT = 40   # Default: 60
    
    def __init__(self, model: ApplicationModel):
        super().__init__(model)
        # Additional initialization
```

### Application Metadata

Configure basic application information:

```python
model = ApplicationModel(
    title="My Custom Application",
    author="Your Name",
    version="2.1.0"
)

# Update metadata dynamically
controller.update_application_metadata(
    title="Updated Title",
    version="2.1.1"
)
```

### Initial State Configuration

```python
class ConfiguredModel(ApplicationModel):
    def __init__(self):
        super().__init__("App", "Author", "1.0")
        
        # Configure initial navigation
        self.set_navigation_items([
            "Dashboard",
            "Data View", 
            "Settings",
            "Help"
        ])
        
        # Set initial content
        self.set_main_content("Welcome! Select a section from the left panel.")
        self.set_status("Ready - Use Tab to switch to command mode")
        
        # Configure bottom window mode
        self.set_bottom_window_mode("display")  # or "input"
        
        # Initialize custom statistics
        self._statistics.update({
            'custom_metric': 0,
            'feature_enabled': True,
            'theme': 'default'
        })
```

## Layout Customization

### Custom Layout Calculator

Create custom window layouts by extending the LayoutCalculator:

```python
class CustomLayoutCalculator(LayoutCalculator):
    def __init__(self):
        super().__init__()
        # Custom minimum sizes
        self._min_sizes = {
            'top': (2, 30),      # (height, width)
            'left': (10, 20),
            'main': (10, 40),
            'bottom': (2, 30)
        }
    
    def calculate_layout(self, terminal_height: int, terminal_width: int) -> LayoutInfo:
        """Custom layout calculation"""
        layout = LayoutInfo()
        
        # Custom proportions
        top_height = 4  # Larger top window
        bottom_height = 4  # Larger bottom window
        left_width = terminal_width // 3  # 1/3 width instead of 1/4
        
        # Calculate positions
        layout.top_window = WindowGeometry(0, 0, top_height, terminal_width)
        layout.bottom_window = WindowGeometry(
            terminal_height - bottom_height, 0, 
            bottom_height, terminal_width
        )
        
        remaining_height = terminal_height - top_height - bottom_height
        layout.left_window = WindowGeometry(
            top_height, 0, 
            remaining_height, left_width
        )
        layout.main_window = WindowGeometry(
            top_height, left_width,
            remaining_height, terminal_width - left_width
        )
        
        layout.terminal_height = terminal_height
        layout.terminal_width = terminal_width
        
        return layout

# Use custom layout
class CustomController(CursesController):
    def _calculate_layout(self, terminal_height: int, terminal_width: int) -> None:
        """Use custom layout calculator"""
        calculator = CustomLayoutCalculator()
        
        if not calculator.validate_terminal_size(terminal_height, terminal_width):
            raise TerminalTooSmallError(
                (terminal_height, terminal_width),
                calculator.get_minimum_terminal_size()
            )
        
        layout = calculator.calculate_layout(terminal_height, terminal_width)
        self.layout_info = layout
```

### Dynamic Layout Switching

Switch between different layouts based on context:

```python
class AdaptiveController(CursesController):
    def __init__(self, model: ApplicationModel):
        super().__init__(model)
        self._layout_mode = "standard"  # standard, compact, expanded
    
    def switch_layout_mode(self, mode: str) -> None:
        """Switch between layout modes"""
        if mode in ["standard", "compact", "expanded"]:
            self._layout_mode = mode
            self.handle_resize()  # Trigger layout recalculation
    
    def _calculate_layout(self, terminal_height: int, terminal_width: int) -> None:
        """Calculate layout based on current mode"""
        if self._layout_mode == "compact":
            self._calculate_compact_layout(terminal_height, terminal_width)
        elif self._layout_mode == "expanded":
            self._calculate_expanded_layout(terminal_height, terminal_width)
        else:
            super()._calculate_layout(terminal_height, terminal_width)
    
    def _calculate_compact_layout(self, height: int, width: int) -> None:
        """Compact layout for small screens"""
        # Smaller top/bottom windows
        top_height = 2
        bottom_height = 2
        left_width = width // 5  # Narrower left panel
        
        # Apply compact layout...
```

## Visual Styling

### Frame Styles

Customize window frame appearance:

```python
from curses_ui_framework import FrameStyle

class StyledView(WindowView):
    def __init__(self, stdscr):
        super().__init__(stdscr)
        # Configure frame styles for different windows
        self._frame_styles = {
            'top': FrameStyle.DOUBLE,
            'left': FrameStyle.SINGLE,
            'main': FrameStyle.SINGLE,
            'bottom': FrameStyle.THICK
        }
    
    def initialize_windows(self, layout_info) -> None:
        """Initialize with custom frame styles"""
        super().initialize_windows(layout_info)
        
        # Apply custom frame styles
        for window_name, style in self._frame_styles.items():
            if window_name in self.windows:
                self.frame_renderer.draw_frame(
                    self.windows[window_name], 
                    style
                )

# Custom frame style definition
class CustomFrameStyle:
    CUSTOM = {
        'horizontal': '═',
        'vertical': '║',
        'top_left': '╔',
        'top_right': '╗',
        'bottom_left': '╚',
        'bottom_right': '╝'
    }

class CustomFrameRenderer(FrameRenderer):
    def draw_custom_frame(self, window, style_dict: dict) -> None:
        """Draw frame with custom characters"""
        height, width = window.getmaxyx()
        
        # Draw horizontal lines
        for x in range(1, width - 1):
            window.addch(0, x, style_dict['horizontal'])
            window.addch(height - 1, x, style_dict['horizontal'])
        
        # Draw vertical lines
        for y in range(1, height - 1):
            window.addch(y, 0, style_dict['vertical'])
            window.addch(y, width - 1, style_dict['vertical'])
        
        # Draw corners
        window.addch(0, 0, style_dict['top_left'])
        window.addch(0, width - 1, style_dict['top_right'])
        window.addch(height - 1, 0, style_dict['bottom_left'])
        window.addch(height - 1, width - 1, style_dict['bottom_right'])
```

### Color Schemes

Configure color schemes for enhanced visual appeal:

```python
import curses

class ColoredView(WindowView):
    def __init__(self, stdscr):
        super().__init__(stdscr)
        self._setup_colors()
    
    def _setup_colors(self) -> None:
        """Setup color pairs"""
        if curses.has_colors():
            curses.start_color()
            
            # Define color pairs
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Normal
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Highlighted
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)   # Success
            curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)     # Error
            curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Warning
            curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Info
    
    def render_top_window(self, title: str, author: str, version: str) -> None:
        """Render top window with colors"""
        if 'top' not in self.windows:
            return
        
        window = self.windows['top']
        
        # Use color for title
        if curses.has_colors():
            window.attron(curses.color_pair(6))  # Blue for title
        
        # Render content with colors
        metadata_text = self._format_application_metadata(title, author, version)
        
        if 'top' in self.content_managers:
            self.content_managers['top'].set_centered_text(metadata_text)
        
        if curses.has_colors():
            window.attroff(curses.color_pair(6))
    
    def render_status_with_color(self, status: str, status_type: str = "normal") -> None:
        """Render status with appropriate color"""
        color_map = {
            "normal": 1,
            "success": 3,
            "error": 4,
            "warning": 5,
            "info": 6
        }
        
        color_pair = color_map.get(status_type, 1)
        
        if 'bottom' in self.windows and curses.has_colors():
            window = self.windows['bottom']
            window.attron(curses.color_pair(color_pair))
            # Render status...
            window.attroff(curses.color_pair(color_pair))
```

### Theme System

Implement a comprehensive theme system:

```python
class Theme:
    def __init__(self, name: str):
        self.name = name
        self.colors = {}
        self.frame_style = FrameStyle.SINGLE
        self.spacing = 1
    
    def set_color(self, element: str, fg_color: int, bg_color: int) -> None:
        """Set color for UI element"""
        self.colors[element] = (fg_color, bg_color)
    
    def get_color_pair(self, element: str) -> int:
        """Get color pair for element"""
        return self.colors.get(element, (curses.COLOR_WHITE, curses.COLOR_BLACK))

class ThemeManager:
    def __init__(self):
        self.themes = {}
        self.current_theme = None
        self._setup_default_themes()
    
    def _setup_default_themes(self) -> None:
        """Setup default themes"""
        # Default theme
        default = Theme("default")
        default.set_color("normal", curses.COLOR_WHITE, curses.COLOR_BLACK)
        default.set_color("highlight", curses.COLOR_BLACK, curses.COLOR_WHITE)
        default.set_color("success", curses.COLOR_GREEN, curses.COLOR_BLACK)
        default.set_color("error", curses.COLOR_RED, curses.COLOR_BLACK)
        self.themes["default"] = default
        
        # Dark theme
        dark = Theme("dark")
        dark.set_color("normal", curses.COLOR_WHITE, curses.COLOR_BLACK)
        dark.set_color("highlight", curses.COLOR_YELLOW, curses.COLOR_BLACK)
        dark.set_color("success", curses.COLOR_GREEN, curses.COLOR_BLACK)
        dark.set_color("error", curses.COLOR_RED, curses.COLOR_BLACK)
        dark.frame_style = FrameStyle.DOUBLE
        self.themes["dark"] = dark
    
    def set_theme(self, theme_name: str) -> bool:
        """Set current theme"""
        if theme_name in self.themes:
            self.current_theme = self.themes[theme_name]
            return True
        return False
    
    def get_current_theme(self) -> Theme:
        """Get current theme"""
        return self.current_theme or self.themes["default"]

class ThemedView(WindowView):
    def __init__(self, stdscr, theme_manager: ThemeManager):
        super().__init__(stdscr)
        self.theme_manager = theme_manager
        self._setup_theme_colors()
    
    def _setup_theme_colors(self) -> None:
        """Setup colors based on current theme"""
        theme = self.theme_manager.get_current_theme()
        
        if curses.has_colors():
            curses.start_color()
            
            # Initialize color pairs based on theme
            for i, (element, (fg, bg)) in enumerate(theme.colors.items(), 1):
                curses.init_pair(i, fg, bg)
```

## Input Handling

### Custom Key Bindings

Configure custom keyboard shortcuts:

```python
class CustomInputController(CursesController):
    def __init__(self, model: ApplicationModel):
        super().__init__(model)
        
        # Define custom key bindings
        self._key_bindings = {
            ord('h'): self._show_help,
            ord('r'): self._refresh_content,
            ord('/'): self._start_search,
            curses.KEY_F1: self._toggle_help,
            curses.KEY_F5: self._refresh_all,
            ord('\t'): self._cycle_focus,  # Override default Tab behavior
        }
    
    def handle_input(self, key: int) -> bool:
        """Handle input with custom key bindings"""
        # Check custom bindings first
        if key in self._key_bindings:
            handler = self._key_bindings[key]
            return handler()
        
        # Fall back to parent implementation
        return super().handle_input(key)
    
    def _show_help(self) -> bool:
        """Show help content"""
        help_content = """KEYBOARD SHORTCUTS:
        
h - Show this help
r - Refresh current content
/ - Start search
F1 - Toggle help panel
F5 - Refresh all windows
Tab - Cycle focus between panels
q/Esc - Quit application

NAVIGATION:
↑/↓ - Navigate menu items
Enter - Select menu item
Page Up/Down - Scroll content
j/k - Scroll line by line
g/G - Jump to top/bottom"""
        
        self.update_main_content(help_content)
        self.set_status("Help displayed - Press any key to continue")
        return True
    
    def _refresh_content(self) -> bool:
        """Refresh current content"""
        # Implement content refresh logic
        self.set_status("Content refreshed")
        return True
    
    def _start_search(self) -> bool:
        """Start search mode"""
        self.model.set_bottom_window_mode("input")
        self.model.set_command_input("/")
        self.set_status("Search mode - Enter search term")
        return True

# Configurable key bindings
class ConfigurableController(CursesController):
    def __init__(self, model: ApplicationModel, key_config: dict = None):
        super().__init__(model)
        self._load_key_config(key_config or {})
    
    def _load_key_config(self, config: dict) -> None:
        """Load key configuration"""
        default_config = {
            'quit': ['q', 'ESC'],
            'help': ['h', 'F1'],
            'refresh': ['r', 'F5'],
            'search': ['/'],
            'navigate_up': ['UP', 'k'],
            'navigate_down': ['DOWN', 'j'],
            'scroll_up': ['PAGE_UP', 'u'],
            'scroll_down': ['PAGE_DOWN', 'd'],
        }
        
        # Merge with user config
        self._key_config = {**default_config, **config}
        
        # Build reverse lookup
        self._key_actions = {}
        for action, keys in self._key_config.items():
            for key in keys:
                key_code = self._get_key_code(key)
                if key_code:
                    self._key_actions[key_code] = action
    
    def _get_key_code(self, key_name: str) -> int:
        """Convert key name to key code"""
        key_map = {
            'ESC': 27,
            'UP': curses.KEY_UP,
            'DOWN': curses.KEY_DOWN,
            'PAGE_UP': curses.KEY_PPAGE,
            'PAGE_DOWN': curses.KEY_NPAGE,
            'F1': curses.KEY_F1,
            'F5': curses.KEY_F5,
        }
        
        if key_name in key_map:
            return key_map[key_name]
        elif len(key_name) == 1:
            return ord(key_name)
        return None
```

### Input Validation

Configure input validation and filtering:

```python
class ValidatedController(CursesController):
    def __init__(self, model: ApplicationModel):
        super().__init__(model)
        self._input_validators = {
            'command': self._validate_command,
            'search': self._validate_search,
            'filename': self._validate_filename,
        }
        self._current_input_type = 'command'
    
    def _validate_command(self, input_text: str) -> tuple[bool, str]:
        """Validate command input"""
        if not input_text.strip():
            return False, "Command cannot be empty"
        
        # Check for dangerous commands
        dangerous = ['rm', 'del', 'format', 'shutdown']
        first_word = input_text.split()[0].lower()
        if first_word in dangerous:
            return False, f"Command '{first_word}' is not allowed"
        
        return True, ""
    
    def _validate_search(self, input_text: str) -> tuple[bool, str]:
        """Validate search input"""
        if len(input_text) < 2:
            return False, "Search term must be at least 2 characters"
        
        # Check for regex patterns that might be problematic
        import re
        try:
            re.compile(input_text)
            return True, ""
        except re.error:
            return False, "Invalid search pattern"
    
    def _validate_filename(self, input_text: str) -> tuple[bool, str]:
        """Validate filename input"""
        import os
        
        if not input_text.strip():
            return False, "Filename cannot be empty"
        
        # Check for invalid characters
        invalid_chars = '<>:"|?*'
        if any(char in input_text for char in invalid_chars):
            return False, f"Filename contains invalid characters: {invalid_chars}"
        
        return True, ""
    
    def handle_input(self, key: int) -> bool:
        """Handle input with validation"""
        if self.model.get_bottom_window_mode() == "input":
            # Validate input as user types
            current_input = self.model.get_command_input()
            validator = self._input_validators.get(self._current_input_type)
            
            if validator:
                is_valid, error_msg = validator(current_input)
                if not is_valid:
                    self.set_status(f"Input error: {error_msg}")
                else:
                    self.set_status("Input valid")
        
        return super().handle_input(key)
```

## Content Management

### Custom Content Formatters

Create custom content formatting:

```python
class ContentFormatter:
    def __init__(self):
        self.formatters = {
            'table': self._format_table,
            'list': self._format_list,
            'json': self._format_json,
            'log': self._format_log,
        }
    
    def format(self, content: any, format_type: str) -> str:
        """Format content based on type"""
        formatter = self.formatters.get(format_type, str)
        return formatter(content)
    
    def _format_table(self, data: list) -> str:
        """Format data as table"""
        if not data or not isinstance(data, list):
            return "No data to display"
        
        # Assume first row contains headers
        headers = data[0] if data else []
        rows = data[1:] if len(data) > 1 else []
        
        # Calculate column widths
        col_widths = [len(str(header)) for header in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Format table
        result = []
        
        # Header
        header_row = " | ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
        result.append(header_row)
        result.append("-" * len(header_row))
        
        # Rows
        for row in rows:
            row_str = " | ".join(str(cell).ljust(col_widths[i]) 
                               for i, cell in enumerate(row))
            result.append(row_str)
        
        return "\n".join(result)
    
    def _format_json(self, data: any) -> str:
        """Format data as JSON"""
        import json
        try:
            return json.dumps(data, indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(data)
    
    def _format_log(self, entries: list) -> str:
        """Format log entries"""
        if not entries:
            return "No log entries"
        
        result = []
        for entry in entries:
            if isinstance(entry, dict):
                timestamp = entry.get('timestamp', 'Unknown')
                level = entry.get('level', 'INFO')
                message = entry.get('message', '')
                result.append(f"[{timestamp}] {level}: {message}")
            else:
                result.append(str(entry))
        
        return "\n".join(result)

class FormattedModel(ApplicationModel):
    def __init__(self, title: str, author: str, version: str):
        super().__init__(title, author, version)
        self.formatter = ContentFormatter()
    
    def set_formatted_content(self, data: any, format_type: str) -> None:
        """Set content with formatting"""
        formatted_content = self.formatter.format(data, format_type)
        self.set_main_content(formatted_content)
```

### Content Caching

Implement content caching for performance:

```python
class CachedContentManager:
    def __init__(self, max_cache_size: int = 100):
        self._cache = {}
        self._cache_order = []
        self._max_cache_size = max_cache_size
    
    def get_content(self, key: str, generator_func) -> str:
        """Get content from cache or generate"""
        if key in self._cache:
            # Move to end (most recently used)
            self._cache_order.remove(key)
            self._cache_order.append(key)
            return self._cache[key]
        
        # Generate new content
        content = generator_func()
        self._cache_content(key, content)
        return content
    
    def _cache_content(self, key: str, content: str) -> None:
        """Cache content with LRU eviction"""
        # Remove oldest if cache is full
        if len(self._cache) >= self._max_cache_size:
            oldest_key = self._cache_order.pop(0)
            del self._cache[oldest_key]
        
        # Add new content
        self._cache[key] = content
        self._cache_order.append(key)
    
    def clear_cache(self) -> None:
        """Clear all cached content"""
        self._cache.clear()
        self._cache_order.clear()

class CachedModel(ApplicationModel):
    def __init__(self, title: str, author: str, version: str):
        super().__init__(title, author, version)
        self.content_cache = CachedContentManager()
    
    def get_expensive_content(self, section: str) -> str:
        """Get content that's expensive to generate"""
        def generate_content():
            # Simulate expensive operation
            import time
            time.sleep(0.1)  # Simulate processing time
            return f"Generated content for {section} at {time.time()}"
        
        return self.content_cache.get_content(section, generate_content)
```

## Error Handling

### Custom Error Handlers

Configure custom error handling:

```python
class CustomErrorHandler:
    def __init__(self):
        self.error_handlers = {
            TerminalTooSmallError: self._handle_terminal_too_small,
            PermissionError: self._handle_permission_error,
            FileNotFoundError: self._handle_file_not_found,
            KeyboardInterrupt: self._handle_keyboard_interrupt,
        }
    
    def handle_error(self, error: Exception) -> bool:
        """Handle error with appropriate handler"""
        error_type = type(error)
        handler = self.error_handlers.get(error_type)
        
        if handler:
            return handler(error)
        else:
            return self._handle_generic_error(error)
    
    def _handle_terminal_too_small(self, error: TerminalTooSmallError) -> bool:
        """Handle terminal too small error"""
        print(f"Terminal too small: {error}")
        print("Please resize your terminal and try again.")
        return True
    
    def _handle_permission_error(self, error: PermissionError) -> bool:
        """Handle permission errors"""
        print(f"Permission denied: {error}")
        print("Please check file permissions and try again.")
        return True
    
    def _handle_generic_error(self, error: Exception) -> bool:
        """Handle generic errors"""
        print(f"An error occurred: {error}")
        import traceback
        traceback.print_exc()
        return False

class ErrorHandlingController(CursesController):
    def __init__(self, model: ApplicationModel):
        super().__init__(model)
        self.error_handler = CustomErrorHandler()
    
    def run(self) -> None:
        """Run with custom error handling"""
        try:
            super().run()
        except Exception as e:
            if not self.error_handler.handle_error(e):
                raise  # Re-raise if not handled
```

## Performance Tuning

### Rendering Optimization

Configure rendering performance:

```python
class OptimizedView(WindowView):
    def __init__(self, stdscr):
        super().__init__(stdscr)
        self._render_throttle = 0.016  # ~60 FPS
        self._last_render_time = 0
        self._pending_updates = set()
    
    def render_all(self, model: ApplicationModel) -> None:
        """Throttled rendering"""
        import time
        current_time = time.time()
        
        if current_time - self._last_render_time < self._render_throttle:
            # Too soon, queue for later
            self._pending_updates.add('all')
            return
        
        super().render_all(model)
        self._last_render_time = current_time
        self._pending_updates.clear()
    
    def process_pending_updates(self) -> None:
        """Process any pending updates"""
        if self._pending_updates:
            import time
            current_time = time.time()
            
            if current_time - self._last_render_time >= self._render_throttle:
                # Process pending updates
                if 'all' in self._pending_updates:
                    super().render_all(self.model)
                else:
                    for window_name in self._pending_updates:
                        self.refresh_window(window_name)
                
                self._last_render_time = current_time
                self._pending_updates.clear()

class PerformanceController(CursesController):
    def __init__(self, model: ApplicationModel):
        super().__init__(model)
        self._performance_stats = {
            'render_count': 0,
            'input_count': 0,
            'command_count': 0,
        }
    
    def _main_loop(self, stdscr) -> None:
        """Main loop with performance monitoring"""
        # Override to add performance monitoring
        super()._main_loop(stdscr)
        
        # Log performance stats
        print(f"Performance stats: {self._performance_stats}")
```

## Advanced Customization

### Plugin System

Implement a plugin system for extensibility:

```python
class Plugin:
    def __init__(self, name: str):
        self.name = name
    
    def initialize(self, controller) -> None:
        """Initialize plugin with controller"""
        pass
    
    def handle_command(self, command: str, args: list) -> bool:
        """Handle plugin-specific commands"""
        return False
    
    def cleanup(self) -> None:
        """Cleanup plugin resources"""
        pass

class FileManagerPlugin(Plugin):
    def __init__(self):
        super().__init__("file_manager")
    
    def handle_command(self, command: str, args: list) -> bool:
        if command == "ls":
            # Handle file listing
            return True
        elif command == "cd":
            # Handle directory change
            return True
        return False

class PluginManager:
    def __init__(self):
        self.plugins = {}
    
    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin"""
        self.plugins[plugin.name] = plugin
    
    def initialize_plugins(self, controller) -> None:
        """Initialize all plugins"""
        for plugin in self.plugins.values():
            plugin.initialize(controller)
    
    def handle_command(self, command: str, args: list) -> bool:
        """Try to handle command with plugins"""
        for plugin in self.plugins.values():
            if plugin.handle_command(command, args):
                return True
        return False

class PluginController(CursesController):
    def __init__(self, model: ApplicationModel):
        super().__init__(model)
        self.plugin_manager = PluginManager()
    
    def _execute_command(self, command: str) -> None:
        """Execute command with plugin support"""
        parts = command.split()
        cmd = parts[0].lower() if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        
        # Try plugins first
        if self.plugin_manager.handle_command(cmd, args):
            return
        
        # Fall back to parent implementation
        super()._execute_command(command)
```

### Configuration Files

Support external configuration files:

```python
import json
import yaml
from pathlib import Path

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.config = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                if self.config_path.suffix == '.json':
                    with open(self.config_path, 'r') as f:
                        self.config = json.load(f)
                elif self.config_path.suffix in ['.yml', '.yaml']:
                    with open(self.config_path, 'r') as f:
                        self.config = yaml.safe_load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                self.config = {}
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_path, 'w') as f:
                if self.config_path.suffix == '.json':
                    json.dump(self.config, f, indent=2)
                elif self.config_path.suffix in ['.yml', '.yaml']:
                    yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value) -> None:
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value

class ConfigurableApplication:
    def __init__(self, config_path: str = "config.json"):
        self.config = ConfigManager(config_path)
        self.model = self._create_model()
        self.controller = self._create_controller()
    
    def _create_model(self) -> ApplicationModel:
        """Create model with configuration"""
        title = self.config.get('app.title', 'Default App')
        author = self.config.get('app.author', 'Unknown')
        version = self.config.get('app.version', '1.0.0')
        
        return ApplicationModel(title, author, version)
    
    def _create_controller(self) -> CursesController:
        """Create controller with configuration"""
        controller = CursesController(self.model)
        
        # Apply configuration
        min_width = self.config.get('terminal.min_width', 120)
        min_height = self.config.get('terminal.min_height', 60)
        
        controller.MIN_TERMINAL_WIDTH = min_width
        controller.MIN_TERMINAL_HEIGHT = min_height
        
        return controller
    
    def run(self) -> None:
        """Run the application"""
        self.controller.run()

# Example configuration file (config.json):
"""
{
  "app": {
    "title": "My Custom Application",
    "author": "Developer Name",
    "version": "2.0.0"
  },
  "terminal": {
    "min_width": 100,
    "min_height": 40
  },
  "ui": {
    "theme": "dark",
    "frame_style": "double",
    "colors": {
      "normal": ["white", "black"],
      "highlight": ["black", "white"]
    }
  },
  "features": {
    "auto_save": true,
    "command_history": true,
    "statistics": true
  }
}
"""
```

This configuration guide provides comprehensive customization options while maintaining the framework's MVC architecture and design principles.