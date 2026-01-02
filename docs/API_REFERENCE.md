# Curses UI Framework - API Reference

## Overview

The Curses UI Framework provides a structured approach to building terminal-based user interfaces in Python using the Model-View-Controller (MVC) architecture. This reference documents all public APIs and provides usage examples.

## Table of Contents

- [Core Classes](#core-classes)
- [MVC Architecture](#mvc-architecture)
- [Window Management](#window-management)
- [Layout System](#layout-system)
- [Content Management](#content-management)
- [Error Handling](#error-handling)
- [Usage Examples](#usage-examples)

## Core Classes

### ApplicationModel

The Model component of the MVC architecture, managing application state and data.

```python
class ApplicationModel:
    def __init__(self, title: str, author: str, version: str)
```

#### Methods

##### Basic Metadata
```python
def get_title(self) -> str
def get_author(self) -> str  
def get_version(self) -> str
```

##### Navigation Management
```python
def set_navigation_items(self, items: List[str]) -> None
def get_navigation_items(self) -> List[str]
def get_selected_navigation_index(self) -> int
def set_selected_navigation_index(self, index: int) -> None
```

##### Content Management
```python
def set_main_content(self, content: str) -> None
def get_main_content(self) -> str
def set_status(self, status: str) -> None
def get_status(self) -> str
```

##### Bottom Window Mode
```python
def set_bottom_window_mode(self, mode: str) -> None  # "display" or "input"
def get_bottom_window_mode(self) -> str
def get_command_input(self) -> str
def set_command_input(self, text: str) -> None
def clear_command_input(self) -> None
```

##### Command History
```python
def add_command_to_history(self, command: str) -> None
def get_command_history(self) -> List[str]
```

##### Statistics
```python
def get_statistics(self) -> dict
def update_statistics(self, key: str, value) -> None
def increment_statistic(self, key: str, amount: int = 1) -> None
```

#### Example Usage

```python
# Create application model
model = ApplicationModel(
    title="My Terminal App",
    author="Developer Name", 
    version="1.0.0"
)

# Set up navigation
model.set_navigation_items(["Home", "Settings", "Help"])

# Set content
model.set_main_content("Welcome to my application!")
model.set_status("Ready")

# Handle command input
model.set_bottom_window_mode("input")
model.set_command_input("help")
```

### WindowView

The View component handling all visual presentation and UI rendering.

```python
class WindowView:
    def __init__(self, stdscr)
```

#### Methods

##### Window Initialization
```python
def initialize_windows(self, layout_info) -> None
def resize_windows(self, new_layout_info) -> None
def cleanup(self) -> None
```

##### Rendering
```python
def render_all(self, model: ApplicationModel) -> None
def render_top_window(self, title: str, author: str, version: str) -> None
def render_left_window(self, items: List[str], selected: int) -> None
def render_main_window(self, content: str) -> None
def render_bottom_window(self, status: str, mode: str) -> None
```

##### Content Management
```python
def update_main_content(self, content: str) -> None
def append_main_content(self, content: str) -> None
def clear_main_content(self) -> None
def scroll_main_content(self, direction: str, lines: int = 1) -> None
def can_scroll_main_content(self, direction: str) -> bool
```

##### Efficient Updates
```python
def mark_window_dirty(self, window_name: str) -> None
def refresh_dirty_windows(self) -> None
def refresh_all_windows(self) -> None
```

#### Example Usage

```python
# Create view (usually done by controller)
view = WindowView(stdscr)

# Initialize with layout
view.initialize_windows(layout_info)

# Render with model data
view.render_all(model)

# Update specific content
view.update_main_content("New content")
view.scroll_main_content("down", 3)
```

### CursesController

The Controller component coordinating between Model and View.

```python
class CursesController:
    def __init__(self, model: ApplicationModel, view: Optional[WindowView] = None)
```

#### Methods

##### Application Lifecycle
```python
def run(self) -> None
def shutdown(self) -> None
def handle_input(self, key: int) -> bool
def handle_resize(self) -> None
```

##### Content Management
```python
def update_main_content(self, content: str) -> None
def append_main_content(self, content: str) -> None
def clear_main_content(self) -> None
def set_main_content_with_status(self, content: str, status: str = "") -> None
def show_processing_status(self, message: str, progress: float = None) -> None
```

##### Navigation
```python
def set_navigation_items(self, items: List[str]) -> None
def get_selected_navigation_item(self) -> str
def navigate_to_item(self, item_name: str) -> bool
def navigate_to_index(self, index: int) -> bool
```

##### Command Processing
```python
def execute_command(self, command: str) -> None
def get_command_history(self) -> List[str]
```

##### Status and Statistics
```python
def set_status(self, status: str) -> None
def get_application_statistics(self) -> dict
```

#### Example Usage

```python
# Create model
model = ApplicationModel("My App", "Author", "1.0")

# Create and run controller
controller = CursesController(model)
controller.run()  # Starts the application loop
```

## MVC Architecture

### Separation of Concerns

The framework enforces clean separation between:

- **Model**: Data and business logic
- **View**: User interface and presentation  
- **Controller**: Application flow and user interaction

### Example MVC Implementation

```python
class MyAppModel(ApplicationModel):
    """Extended model with app-specific data"""
    
    def __init__(self):
        super().__init__("My App", "Author", "1.0")
        self.app_data = {}
    
    def process_data(self, data):
        """Business logic in the model"""
        self.app_data = self.validate_and_transform(data)
        return self.app_data

class MyAppController(CursesController):
    """Extended controller with app-specific logic"""
    
    def _execute_command(self, command: str) -> None:
        """Override to add custom commands"""
        if command.startswith("mycommand"):
            # Process command and update model
            result = self.model.process_data(command)
            self.update_main_content(f"Result: {result}")
        else:
            # Call parent for built-in commands
            super()._execute_command(command)
    
    def _activate_navigation_item(self) -> None:
        """Override to add custom navigation"""
        selected = self.get_selected_navigation_item()
        if selected == "Custom Section":
            self.model.set_main_content("Custom content here")
        else:
            super()._activate_navigation_item()

# Usage
model = MyAppModel()
controller = MyAppController(model)
controller.run()
```

## Window Management

### Window Types

The framework provides four window types:

- **Top Window**: Application metadata (title, author, version)
- **Left Window**: Navigation menu
- **Main Window**: Primary content area
- **Bottom Window**: Commands and status

### Layout Configuration

```python
# Minimum terminal size
MIN_WIDTH = 120
MIN_HEIGHT = 60

# Window proportions (calculated automatically)
# Top: 3 rows, full width
# Bottom: 3 rows, full width  
# Left: 25% width, remaining height
# Main: Remaining space
```

### Window Geometry

```python
@dataclass
class WindowGeometry:
    y: int          # Row position
    x: int          # Column position  
    height: int     # Height in rows
    width: int      # Width in columns
```

## Layout System

### LayoutCalculator

Handles automatic window positioning and sizing.

```python
class LayoutCalculator:
    def calculate_layout(self, terminal_height: int, terminal_width: int) -> LayoutInfo
    def validate_terminal_size(self, height: int, width: int) -> bool
    def get_minimum_terminal_size(self) -> Tuple[int, int]
```

### Layout Information

```python
@dataclass
class LayoutInfo:
    top_window: WindowGeometry
    left_window: WindowGeometry
    main_window: WindowGeometry
    bottom_window: WindowGeometry
    terminal_height: int
    terminal_width: int
```

## Content Management

### ContentManager

Handles text content within windows with scrolling and formatting.

```python
class ContentManager:
    def set_text(self, text: str, row: int = 0, col: int = 0) -> None
    def append_line(self, text: str) -> None
    def clear(self) -> None
    def scroll_up(self, lines: int = 1) -> None
    def scroll_down(self, lines: int = 1) -> None
    def can_scroll_up(self) -> bool
    def can_scroll_down(self) -> bool
```

### Text Formatting

```python
# Basic text formatting
content = "Line 1\nLine 2\nLine 3"
content_manager.set_text(content)

# Scrolling
content_manager.scroll_down(2)
content_manager.scroll_up(1)

# Status with progress
controller.show_processing_status("Loading...", 0.5)
```

## Error Handling

### Exception Hierarchy

```python
class CursesFrameworkError(Exception):
    """Base exception for framework errors"""

class TerminalTooSmallError(CursesFrameworkError):
    """Terminal below minimum size"""

class WindowCreationError(CursesFrameworkError):
    """Window creation failed"""

class TerminalCompatibilityError(CursesFrameworkError):
    """Terminal lacks required features"""

class CursesInitializationError(CursesFrameworkError):
    """Curses initialization failed"""
```

### Error Handling Patterns

```python
try:
    controller = CursesController(model)
    controller.run()
except TerminalTooSmallError as e:
    print(f"Terminal too small: {e}")
    print("Please resize to at least 120x60")
except TerminalCompatibilityError as e:
    print(f"Terminal not supported: {e}")
except CursesFrameworkError as e:
    print(f"Framework error: {e}")
```

## Usage Examples

### Basic Application

```python
#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, 'src')

from curses_ui_framework import CursesController, ApplicationModel

def main():
    # Create model
    model = ApplicationModel(
        title="Basic App",
        author="Developer",
        version="1.0.0"
    )
    
    # Set up navigation
    model.set_navigation_items(["Home", "Settings", "Help"])
    
    # Set initial content
    model.set_main_content("Welcome to the basic application!")
    model.set_status("Ready")
    
    # Create and run controller
    controller = CursesController(model)
    controller.run()

if __name__ == "__main__":
    main()
```

### Extended Application with Custom Commands

```python
class CustomController(CursesController):
    def _execute_command(self, command: str) -> None:
        parts = command.split()
        cmd = parts[0].lower() if parts else ""
        
        if cmd == "hello":
            self.update_main_content("Hello, World!")
            self.set_status("Hello command executed")
        elif cmd == "count" and len(parts) > 1:
            try:
                num = int(parts[1])
                content = "\n".join(f"Line {i+1}" for i in range(num))
                self.update_main_content(content)
                self.set_status(f"Generated {num} lines")
            except ValueError:
                self.set_status("Invalid number")
        else:
            super()._execute_command(command)

# Usage
model = ApplicationModel("Custom App", "Dev", "1.0")
controller = CustomController(model)
controller.run()
```

### File Browser Example

```python
class FileBrowserModel(ApplicationModel):
    def __init__(self):
        super().__init__("File Browser", "Framework", "1.0")
        self.current_dir = os.getcwd()
        self.update_file_list()
    
    def update_file_list(self):
        try:
            files = os.listdir(self.current_dir)
            content = f"Directory: {self.current_dir}\n\n"
            content += "\n".join(f"📄 {f}" for f in sorted(files))
            self.set_main_content(content)
        except PermissionError:
            self.set_main_content("Permission denied")

class FileBrowserController(CursesController):
    def _execute_command(self, command: str) -> None:
        parts = command.split()
        cmd = parts[0].lower() if parts else ""
        
        if cmd == "cd" and len(parts) > 1:
            new_dir = parts[1]
            try:
                if new_dir == "..":
                    new_path = os.path.dirname(self.model.current_dir)
                else:
                    new_path = os.path.join(self.model.current_dir, new_dir)
                
                if os.path.isdir(new_path):
                    self.model.current_dir = new_path
                    self.model.update_file_list()
                    self.set_status(f"Changed to {new_path}")
                else:
                    self.set_status("Directory not found")
            except Exception as e:
                self.set_status(f"Error: {e}")
        else:
            super()._execute_command(command)

# Usage
model = FileBrowserModel()
controller = FileBrowserController(model)
controller.run()
```

### Real-time Data Application

```python
import threading
import time

class DataModel(ApplicationModel):
    def __init__(self):
        super().__init__("Data Monitor", "Framework", "1.0")
        self.data_points = []
        self.running = False
    
    def start_data_collection(self):
        self.running = True
        thread = threading.Thread(target=self._collect_data, daemon=True)
        thread.start()
    
    def _collect_data(self):
        import random
        while self.running:
            # Simulate data collection
            value = random.randint(1, 100)
            timestamp = time.strftime("%H:%M:%S")
            self.data_points.append((timestamp, value))
            
            # Keep only last 20 points
            if len(self.data_points) > 20:
                self.data_points.pop(0)
            
            # Update display
            content = "Real-time Data Monitor\n\n"
            for ts, val in self.data_points:
                content += f"{ts}: {val:3d} {'█' * (val // 5)}\n"
            
            self.set_main_content(content)
            time.sleep(1)

class DataController(CursesController):
    def __init__(self, model):
        super().__init__(model)
        model.start_data_collection()

# Usage
model = DataModel()
controller = DataController(model)
controller.run()
```

## Configuration Options

### Terminal Requirements

- Minimum size: 120 columns × 60 rows
- Curses support required
- Box-drawing character support recommended
- Color support optional but enhanced experience

### Customization Points

```python
# Override minimum size (not recommended)
class CustomController(CursesController):
    MIN_TERMINAL_WIDTH = 100
    MIN_TERMINAL_HEIGHT = 40

# Custom frame styles
from curses_ui_framework import FrameStyle
frame_renderer.draw_frame(window, FrameStyle.DOUBLE)

# Custom layout proportions (requires extending LayoutCalculator)
class CustomLayoutCalculator(LayoutCalculator):
    def _calculate_layout(self, height, width):
        # Custom layout logic
        pass
```

### Performance Considerations

- Use efficient content updates with `mark_window_dirty()`
- Limit content size for large text displays
- Use background threads for data collection
- Implement proper cleanup in `shutdown()`

## Best Practices

### MVC Separation

1. **Model**: Keep all data and business logic here
2. **View**: Only handle visual presentation
3. **Controller**: Coordinate between Model and View

### Error Handling

1. Always handle terminal compatibility issues
2. Provide graceful degradation for small terminals
3. Use try-catch blocks around curses operations
4. Implement proper cleanup in shutdown methods

### Performance

1. Use selective window updates when possible
2. Limit content size for large displays
3. Implement efficient scrolling for large content
4. Use background threads for long-running operations

### User Experience

1. Provide clear navigation instructions
2. Show helpful status messages
3. Implement responsive resize handling
4. Offer comprehensive help documentation

This API reference provides the foundation for building professional terminal applications with the Curses UI Framework's MVC architecture.