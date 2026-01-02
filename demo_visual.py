#!/usr/bin/env python3
"""
Visual layout demonstration for the Curses UI Framework.

This script creates a text-based representation of the framework layout
to show how windows are positioned and sized.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from curses_ui_framework.layout_calculator import LayoutCalculator


def draw_layout_ascii(layout, terminal_width, terminal_height):
    """Draw an ASCII representation of the window layout."""
    
    # Create a grid to represent the terminal
    grid = [[' ' for _ in range(terminal_width)] for _ in range(terminal_height)]
    
    # Fill in each window area with its identifier
    windows = [
        ('T', layout.top_window),     # Top
        ('L', layout.left_window),    # Left  
        ('M', layout.main_window),    # Main
        ('B', layout.bottom_window)   # Bottom
    ]
    
    for char, window in windows:
        for y in range(window.y, window.y + window.height):
            for x in range(window.x, window.x + window.width):
                if 0 <= y < terminal_height and 0 <= x < terminal_width:
                    grid[y][x] = char
    
    # Draw borders around each window
    for char, window in windows:
        # Top and bottom borders
        for x in range(window.x, window.x + window.width):
            if 0 <= window.y < terminal_height and 0 <= x < terminal_width:
                grid[window.y][x] = '─'
            if 0 <= window.y + window.height - 1 < terminal_height and 0 <= x < terminal_width:
                grid[window.y + window.height - 1][x] = '─'
        
        # Left and right borders
        for y in range(window.y, window.y + window.height):
            if 0 <= y < terminal_height and 0 <= window.x < terminal_width:
                grid[y][window.x] = '│'
            if 0 <= y < terminal_height and 0 <= window.x + window.width - 1 < terminal_width:
                grid[y][window.x + window.width - 1] = '│'
        
        # Corners
        corners = [
            (window.y, window.x, '┌'),
            (window.y, window.x + window.width - 1, '┐'),
            (window.y + window.height - 1, window.x, '└'),
            (window.y + window.height - 1, window.x + window.width - 1, '┘')
        ]
        
        for y, x, corner_char in corners:
            if 0 <= y < terminal_height and 0 <= x < terminal_width:
                grid[y][x] = corner_char
    
    # Add labels inside each window
    labels = [
        (layout.top_window, "TOP WINDOW"),
        (layout.left_window, "LEFT"),
        (layout.main_window, "MAIN CONTENT AREA"),
        (layout.bottom_window, "BOTTOM WINDOW")
    ]
    
    for window, label in labels:
        # Calculate center position for label
        center_y = window.y + window.height // 2
        center_x = window.x + (window.width - len(label)) // 2
        
        # Place label if it fits
        if (center_y > window.y and center_y < window.y + window.height - 1 and
            center_x > window.x and center_x + len(label) < window.x + window.width):
            for i, char in enumerate(label):
                if center_x + i < terminal_width:
                    grid[center_y][center_x + i] = char
    
    # Convert grid to string
    result = []
    for row in grid:
        result.append(''.join(row))
    
    return '\n'.join(result)


def main():
    """Demonstrate visual layout representation."""
    print("CURSES UI FRAMEWORK - VISUAL LAYOUT DEMONSTRATION")
    print("=" * 70)
    
    calculator = LayoutCalculator()
    
    # Test different sizes
    test_sizes = [
        (60, 120, "Minimum Size"),
        (30, 80, "Compact View"),
        (25, 60, "Very Compact")
    ]
    
    for height, width, description in test_sizes:
        print(f"\n{description}: {width} x {height}")
        print("-" * 50)
        
        if calculator.validate_terminal_size(height, width):
            layout = calculator.calculate_layout(height, width)
            
            print("Window Details:")
            print(f"  Top:    {layout.top_window.width:3d}x{layout.top_window.height:2d} at ({layout.top_window.x:2d},{layout.top_window.y:2d})")
            print(f"  Left:   {layout.left_window.width:3d}x{layout.left_window.height:2d} at ({layout.left_window.x:2d},{layout.left_window.y:2d})")
            print(f"  Main:   {layout.main_window.width:3d}x{layout.main_window.height:2d} at ({layout.main_window.x:2d},{layout.main_window.y:2d})")
            print(f"  Bottom: {layout.bottom_window.width:3d}x{layout.bottom_window.height:2d} at ({layout.bottom_window.x:2d},{layout.bottom_window.y:2d})")
            print()
            
            # Only draw ASCII for reasonable sizes
            if width <= 80 and height <= 30:
                print("ASCII Layout:")
                ascii_layout = draw_layout_ascii(layout, width, height)
                print(ascii_layout)
            else:
                print("(Layout too large for ASCII representation)")
                
        else:
            print("✗ Terminal size too small")
        
        print()
    
    print("=" * 70)
    print("LEGEND:")
    print("  ┌─┐ = Window borders (drawn with box-drawing characters)")
    print("  │ │")
    print("  └─┘")
    print("  T = Top window area")
    print("  L = Left window area") 
    print("  M = Main window area")
    print("  B = Bottom window area")
    print()
    print("The actual framework uses proper curses box-drawing characters")
    print("and renders content within each window area.")


if __name__ == "__main__":
    main()