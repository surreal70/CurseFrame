# Curses UI Framework

A Python framework for creating terminal-based user interfaces using the curses library. The framework provides a structured layout with distinct regions for different UI components, following the Model-View-Controller (MVC) architecture pattern.

## Features

- **MVC Architecture**: Clean separation of concerns with Model, View, and Controller components
- **Four-Panel Layout**: Structured layout with top header, left navigation, main content, and bottom command areas
- **Automatic Layout Management**: Responsive window positioning and sizing
- **Frame Rendering**: Visual separation with box-drawing characters
- **Terminal Compatibility**: Robust error handling and compatibility checks
- **Minimum Size Validation**: Ensures proper display with 120x60 minimum terminal requirements

## Installation

```bash
pip install curses-ui-framework
```

## Quick Start

```python
from curses_ui_framework import CursesController, ApplicationModel

# Create application model
model = ApplicationModel(
    title="My Terminal App",
    author="Your Name", 
    version="1.0.0"
)

# Set up navigation
model.set_navigation_items(["Home", "Settings", "About"])
model.set_main_content("Welcome to my terminal application!")
model.set_status("Ready")

# Create and run controller
controller = CursesController(model)
controller.run()
```

## Requirements

- Python 3.8 or higher
- Terminal with curses support
- Minimum terminal size: 120 columns × 60 rows

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/curses-ui-framework/curses-ui-framework.git
cd curses-ui-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```