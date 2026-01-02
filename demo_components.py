#!/usr/bin/env python3
"""
Component demonstration for the Curses UI Framework.

This script demonstrates the individual components of the framework
without requiring a full curses terminal interface.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from curses_ui_framework import ApplicationModel
from curses_ui_framework.layout_calculator import LayoutCalculator
from curses_ui_framework.window_manager import WindowType
from curses_ui_framework.frame_renderer import FrameStyle


def demo_model():
    """Demonstrate the ApplicationModel (MVC Model component)."""
    print("=" * 60)
    print("DEMO: ApplicationModel (MVC Model Component)")
    print("=" * 60)
    
    # Create model with demo data
    model = ApplicationModel(
        title="Test Application",
        author="John Doe", 
        version="2.1.0"
    )
    
    print(f"Application Title: {model.get_title()}")
    print(f"Application Author: {model.get_author()}")
    print(f"Application Version: {model.get_version()}")
    print()
    
    # Test navigation items
    nav_items = ["Dashboard", "Reports", "Settings", "Help", "Logout"]
    model.set_navigation_items(nav_items)
    print(f"Navigation Items: {model.get_navigation_items()}")
    print()
    
    # Test main content
    content = "This is the main content area.\nIt supports multiple lines.\nAnd can be updated dynamically."
    model.set_main_content(content)
    print("Main Content:")
    print(model.get_main_content())
    print()
    
    # Test status
    model.set_status("System ready | 5 users online | Last update: 2024-01-01")
    print(f"Status: {model.get_status()}")
    print()


def demo_layout_calculator():
    """Demonstrate the LayoutCalculator component."""
    print("=" * 60)
    print("DEMO: LayoutCalculator Component")
    print("=" * 60)
    
    calculator = LayoutCalculator()
    
    # Show minimum requirements
    min_height, min_width = calculator.get_minimum_terminal_size()
    print(f"Minimum Terminal Size: {min_width} x {min_height}")
    print()
    
    # Test different terminal sizes
    test_sizes = [
        (60, 120),   # Minimum size
        (80, 160),   # Medium size
        (100, 200),  # Large size
        (50, 100),   # Too small
    ]
    
    for height, width in test_sizes:
        print(f"Testing terminal size: {width} x {height}")
        
        if calculator.validate_terminal_size(height, width):
            print("✓ Size is valid")
            layout = calculator.calculate_layout(height, width)
            
            print(f"  Top Window:    {layout.top_window.width:3d} x {layout.top_window.height:2d} at ({layout.top_window.x:3d}, {layout.top_window.y:2d})")
            print(f"  Left Window:   {layout.left_window.width:3d} x {layout.left_window.height:2d} at ({layout.left_window.x:3d}, {layout.left_window.y:2d})")
            print(f"  Main Window:   {layout.main_window.width:3d} x {layout.main_window.height:2d} at ({layout.main_window.x:3d}, {layout.main_window.y:2d})")
            print(f"  Bottom Window: {layout.bottom_window.width:3d} x {layout.bottom_window.height:2d} at ({layout.bottom_window.x:3d}, {layout.bottom_window.y:2d})")
            
            # Verify no overlaps
            windows = [
                ("Top", layout.top_window),
                ("Left", layout.left_window), 
                ("Main", layout.main_window),
                ("Bottom", layout.bottom_window)
            ]
            
            overlaps = []
            for i, (name1, win1) in enumerate(windows):
                for j, (name2, win2) in enumerate(windows):
                    if i < j:  # Only check each pair once
                        overlap_x = not (win1.x + win1.width <= win2.x or win2.x + win2.width <= win1.x)
                        overlap_y = not (win1.y + win1.height <= win2.y or win2.y + win2.height <= win1.y)
                        if overlap_x and overlap_y:
                            overlaps.append(f"{name1}-{name2}")
            
            if overlaps:
                print(f"  ✗ Overlaps detected: {', '.join(overlaps)}")
            else:
                print("  ✓ No overlaps detected")
                
        else:
            print("✗ Size is too small")
        
        print()


def demo_window_types():
    """Demonstrate WindowType enumeration and minimum sizes."""
    print("=" * 60)
    print("DEMO: Window Types and Minimum Sizes")
    print("=" * 60)
    
    calculator = LayoutCalculator()
    
    for window_type in WindowType:
        min_height, min_width = calculator.get_window_minimum_size(window_type)
        print(f"{window_type.value.title()} Window: minimum {min_width} x {min_height}")
    
    print()


def demo_frame_styles():
    """Demonstrate FrameStyle enumeration."""
    print("=" * 60)
    print("DEMO: Frame Styles")
    print("=" * 60)
    
    print("Available frame styles:")
    for style in FrameStyle:
        print(f"  - {style.value.title()}: {style.name}")
    
    print()
    print("Frame styles provide different visual appearances:")
    print("  - SINGLE: Standard single-line borders")
    print("  - DOUBLE: Double-line borders for emphasis")
    print("  - THICK: Thick borders for strong separation")
    print("  - ROUNDED: Rounded corners for modern look")
    print()


def demo_mvc_architecture():
    """Demonstrate MVC architecture principles."""
    print("=" * 60)
    print("DEMO: MVC Architecture")
    print("=" * 60)
    
    print("The framework follows Model-View-Controller architecture:")
    print()
    print("MODEL (ApplicationModel):")
    print("  - Stores application data and state")
    print("  - Manages title, author, version information")
    print("  - Handles navigation items and content")
    print("  - Independent of UI presentation")
    print()
    print("VIEW (WindowView):")
    print("  - Handles all visual rendering")
    print("  - Manages window creation and display")
    print("  - Renders frames and content")
    print("  - Updates display based on model data")
    print()
    print("CONTROLLER (CursesController):")
    print("  - Coordinates between Model and View")
    print("  - Handles user input and events")
    print("  - Manages application lifecycle")
    print("  - Processes resize events and updates")
    print()
    print("Benefits:")
    print("  ✓ Clear separation of concerns")
    print("  ✓ Easier testing and maintenance")
    print("  ✓ Flexible and extensible design")
    print("  ✓ Reusable components")
    print()


def main():
    """Run all component demonstrations."""
    print("CURSES UI FRAMEWORK - COMPONENT DEMONSTRATION")
    print("=" * 60)
    print("This demo shows the individual components working")
    print("without requiring a full terminal interface.")
    print()
    
    try:
        demo_model()
        demo_layout_calculator()
        demo_window_types()
        demo_frame_styles()
        demo_mvc_architecture()
        
        print("=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("All components are working correctly!")
        print("The framework is ready for the next implementation phase.")
        print()
        print("To run the full interactive demo:")
        print("1. Resize your terminal to at least 120x60")
        print("2. Run: python demo.py")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()