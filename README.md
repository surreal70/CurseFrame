# 🖥️ Curses UI Framework

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Framework](https://img.shields.io/badge/Framework-MVC-green.svg)](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller)
[![Terminal](https://img.shields.io/badge/Interface-Terminal-black.svg)](https://en.wikipedia.org/wiki/Text-based_user_interface)
[![Testing](https://img.shields.io/badge/Testing-Property--Based-purple.svg)](https://hypothesis.works/)
[![Code Style](https://img.shields.io/badge/Code%20Style-PEP8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)

A comprehensive Python framework for creating professional terminal-based user interfaces using the curses library. The framework provides a structured Model-View-Controller (MVC) architecture with automatic layout management, frame rendering, and robust error handling for building sophisticated terminal applications.

## Overview

The Curses UI Framework enables developers to create professional terminal applications with minimal boilerplate code. It features a four-panel layout system (top header, left navigation, main content, bottom command/status), comprehensive MVC architecture, and extensive customization options. The framework handles terminal compatibility, resize events, content scrolling, and provides property-based testing integration.

### Key Goals

- **Professional Terminal UIs**: Create sophisticated terminal applications with consistent layouts
- **MVC Architecture**: Clean separation of concerns for maintainable and testable code
- **Developer Experience**: Minimal setup with comprehensive examples and documentation
- **Cross-Platform Compatibility**: Robust terminal compatibility with graceful error handling
- **Extensibility**: Flexible architecture supporting custom controllers and views

## Features

### Core Architecture
- **MVC Pattern**: Complete Model-View-Controller implementation with clean separation
- **Four-Panel Layout**: Structured layout with top header, left navigation, main content, and bottom areas
- **Automatic Layout Management**: Responsive window positioning and sizing with minimum 120x60 terminal support
- **Frame Rendering**: Professional visual separation using box-drawing characters with multiple styles

### Advanced Functionality
- **Content Management**: Text scrolling, wrapping, and formatting with ContentManager
- **Navigation System**: Enhanced navigation with selection highlighting and keyboard controls
- **Command Processing**: Dual-mode bottom window (display/input) with command history
- **Error Handling**: Comprehensive terminal compatibility checks and graceful error recovery
- **Resize Support**: Dynamic layout recalculation and window repositioning on terminal resize

### Testing & Quality
- **Property-Based Testing**: 14 comprehensive property tests using Hypothesis
- **Integration Tests**: End-to-end functionality validation
- **Example Applications**: Multiple demo applications demonstrating MVC patterns
- **Documentation**: Complete API reference and usage guides

## Installation

### From Source (Development)

```bash
# Clone the repository
git clone <repository-url>
cd curses-ui-framework

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

### Dependencies

The framework has minimal dependencies and uses only Python standard library modules:

- **Python 3.8+**: Core language requirement
- **curses**: Terminal interface library (included in Python standard library on Unix systems)

#### Development Dependencies

```bash
# Install development dependencies
pip install -e ".[dev]"
```

Development dependencies include:
- **pytest>=6.0**: Testing framework
- **hypothesis>=6.0**: Property-based testing library
- **flake8>=4.0**: Code linting and style checking

## Quick Start

### Basic Application

```python
from curses_ui_framework import CursesController, ApplicationModel

# Create application model with metadata
model = ApplicationModel(
    title="My Terminal App",
    author="Your Name", 
    version="1.0.0"
)

# Configure navigation and content
model.set_navigation_items(["Home", "Settings", "Help", "About"])
model.set_main_content("Welcome to my terminal application!\n\nUse arrow keys to navigate.")
model.set_status("Application ready")

# Create and run controller
controller = CursesController(model)
controller.run()
```

### Extended MVC Example

```python
from curses_ui_framework import CursesController, ApplicationModel

class MyApplicationModel(ApplicationModel):
    def __init__(self):
        super().__init__("Advanced App", "Developer", "2.0.0")
        self.data = {"counter": 0}
    
    def increment_counter(self):
        self.data["counter"] += 1
        self.set_main_content(f"Counter: {self.data['counter']}")

class MyController(CursesController):
    def _execute_command(self, command: str):
        if command == "increment":
            self.model.increment_counter()
            self.set_status("Counter incremented")
        else:
            super()._execute_command(command)

# Run the application
model = MyApplicationModel()
controller = MyController(model)
controller.run()
```

## Usage Examples

### Running Demo Applications

The framework includes several demonstration applications:

```bash
# Basic framework demo
python demo.py

# Component showcase
python demo_components.py

# Visual layout demo
python demo_visual.py

# Comprehensive MVC file manager example
python example_mvc_app.py
```

### Terminal Requirements

- **Minimum Size**: 120 columns × 60 rows
- **Terminal Support**: xterm, gnome-terminal, or compatible terminal emulator
- **Platform**: Unix-like systems (Linux, macOS) with curses support

### Keyboard Controls

- **Arrow Keys (↑/↓)**: Navigate left panel items
- **Enter**: Activate selected navigation item
- **Tab**: Switch between display/input mode (bottom panel)
- **Page Up/Down**: Scroll main content
- **j/k**: Scroll main content line by line
- **g/G**: Jump to top/bottom of content
- **q/Esc**: Quit application

## Development

### Setting Up Development Environment

```bash
# Clone and setup
git clone <repository-url>
cd curses-ui-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode with dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run property-based tests specifically
pytest tests/test_properties.py -v

# Run integration tests
pytest tests/test_integration.py -v
```

### Code Quality

```bash
# Check code style
flake8 src/

# Run type checking (if mypy installed)
mypy src/

# Format code (if black installed)
black src/ tests/
```

### Project Structure

```
curses-ui-framework/
├── src/curses_ui_framework/     # Main framework code
│   ├── __init__.py              # Package initialization
│   ├── controller.py            # MVC Controller implementation
│   ├── model.py                 # MVC Model implementation
│   ├── view.py                  # MVC View implementation
│   ├── window_manager.py        # Window creation and management
│   ├── layout_calculator.py     # Layout positioning algorithms
│   ├── frame_renderer.py        # Frame drawing and styling
│   ├── content_manager.py       # Text content management
│   └── exceptions.py            # Framework-specific exceptions
├── tests/                       # Test suite
│   ├── test_properties.py       # Property-based tests
│   └── test_integration.py      # Integration tests
├── docs/                        # Documentation
│   ├── API_REFERENCE.md         # Complete API documentation
│   ├── MVC_PATTERNS.md          # MVC architecture guide
│   └── CONFIGURATION.md         # Configuration options
├── demo.py                      # Basic demo application
├── demo_components.py           # Component showcase
├── demo_visual.py               # Visual layout demo
├── example_mvc_app.py           # Comprehensive MVC example
└── README.md                    # This file
```

## Documentation

### API Reference

Complete API documentation is available in [docs/API_REFERENCE.md](docs/API_REFERENCE.md), covering:

- **ApplicationModel**: Data management and state handling
- **CursesController**: Application logic and event handling  
- **WindowView**: UI rendering and visual presentation
- **WindowManager**: Window creation and layout management
- **ContentManager**: Text content and scrolling functionality

### Architecture Guide

Detailed MVC architecture patterns and best practices are documented in [docs/MVC_PATTERNS.md](docs/MVC_PATTERNS.md).

### Configuration

Framework configuration options and customization are covered in [docs/CONFIGURATION.md](docs/CONFIGURATION.md).

## Examples and Demos

### Basic Demo (`demo.py`)
Simple framework demonstration showing basic MVC setup and navigation.

### Component Showcase (`demo_components.py`)
Demonstrates individual framework components and their capabilities.

### Visual Demo (`demo_visual.py`)
Shows layout management and frame rendering features.

### MVC File Manager (`example_mvc_app.py`)
Comprehensive example application demonstrating:
- Extended MVC architecture
- File system navigation
- Command processing
- Real-time statistics
- Section-based navigation
- Background processing

## Testing

The framework includes comprehensive testing with both unit tests and property-based tests:

### Property-Based Tests
- **14 Properties**: Covering terminal resource management, layout integrity, content management
- **Hypothesis Integration**: Automated test case generation
- **Requirements Validation**: Each property validates specific requirements

### Integration Tests
- **End-to-End Testing**: Complete application lifecycle testing
- **Terminal Compatibility**: Various terminal condition testing
- **Error Handling**: Comprehensive error scenario validation

## Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Unix-like systems (Linux, macOS)
- **Terminal**: curses-compatible terminal emulator
- **Display**: Minimum 120 columns × 60 rows

### Python Dependencies
- **Standard Library Only**: No external runtime dependencies
- **Development**: pytest, hypothesis, flake8 (for development only)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the coding standards
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Support

- **Documentation**: See [docs/](docs/) directory for comprehensive guides
- **Examples**: Multiple demo applications in the repository root
- **Issues**: Report bugs and request features via GitHub Issues
- **Testing**: Run `pytest` to validate your environment