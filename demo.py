#!/usr/bin/env python3
"""
Demo script for the Curses UI Framework.

This script demonstrates the current functionality of the framework,
including the MVC architecture, window management, layout calculation,
and frame rendering.
"""

import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from curses_ui_framework import CursesController, ApplicationModel


def main():
    """Run the demo application."""
    print("Curses UI Framework Demo")
    print("=" * 50)
    
    # Create application model with demo data
    model = ApplicationModel(
        title="Curses UI Framework Demo",
        author="Demo User",
        version="1.0.0"
    )
    
    # Add some demo navigation items
    model.set_navigation_items([
        "Home",
        "Settings", 
        "About",
        "Help",
        "Exit"
    ])
    
    # Set some demo content
    model.set_main_content(
        "Welcome to the Curses UI Framework!\n\n"
        "This framework provides:\n"
        "• Four-panel layout (top, left, main, bottom)\n"
        "• Automatic window management\n"
        "• Frame rendering with box-drawing characters\n"
        "• MVC architecture separation\n"
        "• Responsive layout calculation\n"
        "• Minimum size constraints (120x60)\n\n"
        "Current implementation includes:\n"
        "✓ Core MVC classes\n"
        "✓ Window management system\n"
        "✓ Layout calculation with resize handling\n"
        "✓ Frame rendering system\n"
        "✓ Property-based testing\n\n"
        "Press 'q' to quit the demo."
    )
    
    # Set demo status
    model.set_status("Ready | Demo Mode | Press 'q' to quit")
    
    print(f"Title: {model.get_title()}")
    print(f"Author: {model.get_author()}")
    print(f"Version: {model.get_version()}")
    print(f"Navigation Items: {model.get_navigation_items()}")
    print(f"Status: {model.get_status()}")
    print()
    print("Main Content Preview:")
    print("-" * 30)
    print(model.get_main_content()[:200] + "...")
    print("-" * 30)
    print()
    
    # Check terminal size
    try:
        import shutil
        terminal_size = shutil.get_terminal_size()
        print(f"Current terminal size: {terminal_size.columns}x{terminal_size.lines}")
        
        # Import layout calculator to check minimum requirements
        from curses_ui_framework.layout_calculator import LayoutCalculator
        calculator = LayoutCalculator()
        min_height, min_width = calculator.get_minimum_terminal_size()
        
        print(f"Minimum required size: {min_width}x{min_height}")
        
        if terminal_size.columns >= min_width and terminal_size.lines >= min_height:
            print("✓ Terminal size meets requirements")
            
            # Show what the layout would look like
            layout = calculator.calculate_layout(terminal_size.lines, terminal_size.columns)
            print("\nCalculated Layout:")
            print(f"  Top Window: {layout.top_window.width}x{layout.top_window.height} at ({layout.top_window.x}, {layout.top_window.y})")
            print(f"  Left Window: {layout.left_window.width}x{layout.left_window.height} at ({layout.left_window.x}, {layout.left_window.y})")
            print(f"  Main Window: {layout.main_window.width}x{layout.main_window.height} at ({layout.main_window.x}, {layout.main_window.y})")
            print(f"  Bottom Window: {layout.bottom_window.width}x{layout.bottom_window.height} at ({layout.bottom_window.x}, {layout.bottom_window.y})")
            
            print("\nStarting interactive demo in 3 seconds...")
            print("(Press Ctrl+C to cancel)")
            
            try:
                for i in range(3, 0, -1):
                    print(f"Starting in {i}...", end='\r')
                    time.sleep(1)
                print("Starting now!     ")
                
                # Create and run the controller
                controller = CursesController(model)
                controller.run()
                
            except KeyboardInterrupt:
                print("\nDemo cancelled by user.")
                
        else:
            print("✗ Terminal size too small for demo")
            print(f"Please resize your terminal to at least {min_width}x{min_height}")
            
    except ImportError:
        print("Could not determine terminal size")
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()