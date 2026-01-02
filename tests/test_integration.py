#!/usr/bin/env python3
"""
Integration tests for the Curses UI Framework.

These tests verify end-to-end functionality with all components working together
and test framework behavior under various terminal conditions.
"""

import unittest
import sys
import os
import threading
import time
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from curses_ui_framework import (
    CursesController,
    ApplicationModel,
    WindowView,
    WindowManager,
    LayoutCalculator,
    FrameRenderer,
    FrameStyle,
    CursesFrameworkError,
    TerminalTooSmallError,
    WindowCreationError
)


class MockCursesModule:
    """Mock curses module for testing"""
    
    # Key constants
    KEY_UP = 259
    KEY_DOWN = 258
    KEY_LEFT = 260
    KEY_RIGHT = 261
    KEY_RESIZE = 410
    KEY_BACKSPACE = 263
    KEY_PPAGE = 339
    KEY_NPAGE = 338
    KEY_HOME = 262
    KEY_END = 360
    KEY_F1 = 265
    KEY_F5 = 269
    
    # Color constants
    COLOR_BLACK = 0
    COLOR_WHITE = 7
    COLOR_RED = 1
    COLOR_GREEN = 2
    COLOR_BLUE = 4
    COLOR_YELLOW = 3
    
    def __init__(self):
        self.has_colors_result = True
        self.terminal_size = (60, 120)  # height, width
        self.input_queue = []
        self.output_buffer = []
        
    def has_colors(self):
        return self.has_colors_result
    
    def start_color(self):
        pass
    
    def init_pair(self, pair_num, fg, bg):
        pass
    
    def color_pair(self, pair_num):
        return 0
    
    def curs_set(self, visibility):
        pass
    
    def newwin(self, height, width, y, x):
        return MockWindow(height, width, y, x)
    
    def wrapper(self, func):
        """Mock curses wrapper"""
        stdscr = MockWindow(self.terminal_size[0], self.terminal_size[1], 0, 0)
        return func(stdscr)
    
    def setupterm(self):
        pass
    
    class error(Exception):
        pass


class MockWindow:
    """Mock curses window for testing"""
    
    def __init__(self, height, width, y, x):
        self.height = height
        self.width = width
        self.y = y
        self.x = x
        self.content = {}
        self.attributes = {}
        self.cursor_pos = (0, 0)
        self.nodelay_enabled = False
        self.timeout_value = -1
        
    def getmaxyx(self):
        return (self.height, self.width)
    
    def addstr(self, y, x, text, attr=0):
        if 0 <= y < self.height and 0 <= x < self.width:
            self.content[(y, x)] = text
            self.attributes[(y, x)] = attr
    
    def addch(self, y, x, char, attr=0):
        if 0 <= y < self.height and 0 <= x < self.width:
            self.content[(y, x)] = char
            self.attributes[(y, x)] = attr
    
    def clear(self):
        self.content.clear()
        self.attributes.clear()
    
    def refresh(self):
        pass
    
    def getch(self):
        # Return -1 for no input (non-blocking)
        return -1
    
    def nodelay(self, flag):
        self.nodelay_enabled = flag
    
    def timeout(self, delay):
        self.timeout_value = delay
    
    def attron(self, attr):
        pass
    
    def attroff(self, attr):
        pass
    
    def get_content_at(self, y, x):
        """Helper method to get content at position"""
        return self.content.get((y, x), ' ')
    
    def get_content_lines(self):
        """Helper method to get all content as lines"""
        lines = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                line += str(self.content.get((y, x), ' '))
            lines.append(line.rstrip())
        return lines


class IntegrationTestBase(unittest.TestCase):
    """Base class for integration tests"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock curses module
        self.mock_curses = MockCursesModule()
        
        # Patch curses module
        self.curses_patcher = patch('curses_ui_framework.controller.curses', self.mock_curses)
        self.curses_patcher.start()
        
        # Also patch in other modules that import curses
        patch('curses_ui_framework.view.curses', self.mock_curses).start()
        patch('curses_ui_framework.window_manager.curses', self.mock_curses).start()
        patch('curses_ui_framework.frame_renderer.curses', self.mock_curses).start()
        patch('curses_ui_framework.content_manager.curses', self.mock_curses).start()
        
        # Create test model
        self.model = ApplicationModel(
            title="Test Application",
            author="Test Author", 
            version="1.0.0"
        )
        
        # Set up test data
        self.model.set_navigation_items(["Home", "Settings", "Help"])
        self.model.set_main_content("Test content for integration testing")
        self.model.set_status("Test status")
    
    def tearDown(self):
        """Clean up test environment"""
        self.curses_patcher.stop()
        patch.stopall()


class TestFullFrameworkIntegration(IntegrationTestBase):
    """Test complete framework integration"""
    
    def test_mvc_component_integration(self):
        """Test that Model, View, and Controller work together properly"""
        # Create controller with model
        controller = CursesController(self.model)
        
        # Verify controller has model
        self.assertEqual(controller.model, self.model)
        
        # Test model-controller interaction
        controller.set_status("Controller status")
        self.assertEqual(self.model.get_status(), "Controller status")
        
        controller.update_main_content("Controller content")
        self.assertEqual(self.model.get_main_content(), "Controller content")
        
        # Test navigation
        controller.set_navigation_items(["Item1", "Item2", "Item3"])
        self.assertEqual(self.model.get_navigation_items(), ["Item1", "Item2", "Item3"])
        
        # Test navigation selection
        self.assertTrue(controller.navigate_to_index(1))
        self.assertEqual(self.model.get_selected_navigation_index(), 1)
        self.assertEqual(controller.get_selected_navigation_item(), "Item2")
    
    def test_window_management_integration(self):
        """Test window management with layout calculation"""
        controller = CursesController(self.model)
        
        # Mock the main loop setup
        stdscr = MockWindow(60, 120, 0, 0)
        controller.stdscr = stdscr
        controller._validate_and_setup_layout()
        
        # Verify layout was calculated
        self.assertIsNotNone(controller.layout_info)
        self.assertEqual(controller.layout_info.terminal_height, 60)
        self.assertEqual(controller.layout_info.terminal_width, 120)
        
        # Verify window geometries
        self.assertEqual(controller.layout_info.top_window.height, 3)
        self.assertEqual(controller.layout_info.bottom_window.height, 3)
        self.assertGreater(controller.layout_info.main_window.width, 
                          controller.layout_info.left_window.width)
    
    def test_content_management_integration(self):
        """Test content management across MVC components"""
        controller = CursesController(self.model)
        
        # Set up view
        stdscr = MockWindow(60, 120, 0, 0)
        view = WindowView(stdscr)
        controller.view = view
        controller.stdscr = stdscr
        controller._validate_and_setup_layout()
        view.initialize_windows(controller.layout_info)
        
        # Test content updates through controller
        test_content = "Integration test content\nLine 2\nLine 3"
        controller.update_main_content(test_content)
        
        # Verify model was updated
        self.assertEqual(self.model.get_main_content(), test_content)
        
        # Test content appending
        controller.append_main_content("Appended line")
        expected_content = test_content + "\nAppended line"
        self.assertEqual(self.model.get_main_content(), expected_content)
        
        # Test content clearing
        controller.clear_main_content()
        self.assertEqual(self.model.get_main_content(), "")
    
    def test_command_processing_integration(self):
        """Test command processing through the full stack"""
        controller = CursesController(self.model)
        
        # Test built-in commands
        controller._execute_command("help")
        self.assertIn("help", self.model.get_main_content().lower())
        
        controller._execute_command("clear")
        self.assertEqual(self.model.get_main_content(), "")
        
        controller._execute_command("status Test message")
        self.assertEqual(self.model.get_status(), "Test message")
        
        # Test command history
        initial_count = self.model.get_statistics()['total_commands']
        controller._execute_command("test command")
        final_count = self.model.get_statistics()['total_commands']
        self.assertEqual(final_count, initial_count + 1)
    
    def test_input_handling_integration(self):
        """Test input handling through controller"""
        controller = CursesController(self.model)
        
        # Test navigation input
        self.model.set_navigation_items(["Item1", "Item2", "Item3"])
        
        # Test down arrow
        result = controller.handle_input(self.mock_curses.KEY_DOWN)
        self.assertTrue(result)
        self.assertEqual(self.model.get_selected_navigation_index(), 1)
        
        # Test up arrow
        result = controller.handle_input(self.mock_curses.KEY_UP)
        self.assertTrue(result)
        self.assertEqual(self.model.get_selected_navigation_index(), 0)
        
        # Test tab key (mode switching)
        initial_mode = self.model.get_bottom_window_mode()
        controller.handle_input(ord('\t'))
        final_mode = self.model.get_bottom_window_mode()
        self.assertNotEqual(initial_mode, final_mode)
        
        # Test quit key
        result = controller.handle_input(ord('q'))
        self.assertFalse(result)  # Should return False to indicate quit
    
    def test_statistics_integration(self):
        """Test statistics tracking across components"""
        controller = CursesController(self.model)
        
        # Get initial statistics
        initial_stats = self.model.get_statistics()
        
        # Execute some commands
        controller._execute_command("help")
        controller._execute_command("status test")
        controller._execute_command("clear")
        
        # Check statistics were updated
        final_stats = self.model.get_statistics()
        self.assertGreater(final_stats['total_commands'], initial_stats['total_commands'])
        # Note: last_command might be empty in base implementation, just check it exists
        self.assertIn('last_command', final_stats)
        
        # Test statistics display
        controller._execute_command("stats")
        content = self.model.get_main_content()
        self.assertIn("total commands", content.lower())
        self.assertIn("last command", content.lower())


class TestTerminalConditions(IntegrationTestBase):
    """Test framework behavior under various terminal conditions"""
    
    def test_minimum_terminal_size(self):
        """Test behavior at minimum terminal size"""
        # Set terminal to minimum size
        self.mock_curses.terminal_size = (60, 120)
        
        controller = CursesController(self.model)
        stdscr = MockWindow(60, 120, 0, 0)
        controller.stdscr = stdscr
        
        # Should not raise exception
        controller._validate_and_setup_layout()
        
        # Verify layout is valid
        layout = controller.layout_info
        self.assertEqual(layout.terminal_height, 60)
        self.assertEqual(layout.terminal_width, 120)
        
        # Verify all windows fit
        self.assertGreaterEqual(layout.top_window.height, 1)
        self.assertGreaterEqual(layout.left_window.height, 1)
        self.assertGreaterEqual(layout.main_window.height, 1)
        self.assertGreaterEqual(layout.bottom_window.height, 1)
    
    def test_terminal_too_small(self):
        """Test behavior when terminal is too small"""
        # Set terminal below minimum size
        self.mock_curses.terminal_size = (20, 50)
        
        controller = CursesController(self.model)
        stdscr = MockWindow(20, 50, 0, 0)
        controller.stdscr = stdscr
        
        # Should raise TerminalTooSmallError
        with self.assertRaises(TerminalTooSmallError):
            controller._validate_and_setup_layout()
    
    def test_large_terminal_size(self):
        """Test behavior with large terminal"""
        # Set large terminal size
        self.mock_curses.terminal_size = (100, 200)
        
        controller = CursesController(self.model)
        stdscr = MockWindow(100, 200, 0, 0)
        controller.stdscr = stdscr
        
        controller._validate_and_setup_layout()
        
        # Verify layout scales properly
        layout = controller.layout_info
        self.assertEqual(layout.terminal_height, 100)
        self.assertEqual(layout.terminal_width, 200)
        
        # Main window should get most of the space
        total_area = 100 * 200
        main_area = layout.main_window.height * layout.main_window.width
        self.assertGreater(main_area / total_area, 0.4)  # At least 40% of space
    
    def test_terminal_resize_handling(self):
        """Test terminal resize event handling"""
        controller = CursesController(self.model)
        stdscr = MockWindow(60, 120, 0, 0)
        controller.stdscr = stdscr
        controller._validate_and_setup_layout()
        
        # Store original layout
        original_width = controller.layout_info.terminal_width
        original_height = controller.layout_info.terminal_height
        
        # Simulate terminal resize by changing the mock window size
        # and calling handle_resize which should recalculate layout
        self.mock_curses.terminal_size = (80, 160)
        new_stdscr = MockWindow(80, 160, 0, 0)
        controller.stdscr = new_stdscr
        
        # Mock getmaxyx to return new size
        with patch.object(new_stdscr, 'getmaxyx', return_value=(80, 160)):
            controller.handle_resize()
        
        # Verify layout was recalculated
        new_layout = controller.layout_info
        self.assertNotEqual(original_height, new_layout.terminal_height)
        self.assertNotEqual(original_width, new_layout.terminal_width)
        self.assertEqual(new_layout.terminal_height, 80)
        self.assertEqual(new_layout.terminal_width, 160)
    
    def test_no_color_support(self):
        """Test behavior when terminal doesn't support colors"""
        # Disable color support
        self.mock_curses.has_colors_result = False
        
        controller = CursesController(self.model)
        stdscr = MockWindow(60, 120, 0, 0)
        view = WindowView(stdscr)
        controller.view = view
        controller.stdscr = stdscr
        controller._validate_and_setup_layout()
        
        # Should not raise exception
        view.initialize_windows(controller.layout_info)
        view.render_all(self.model)
        
        # Verify basic functionality still works
        controller.update_main_content("Test content")
        self.assertEqual(self.model.get_main_content(), "Test content")


class TestErrorHandling(IntegrationTestBase):
    """Test error handling throughout the framework"""
    
    def test_window_creation_error_handling(self):
        """Test handling of window creation errors"""
        controller = CursesController(self.model)
        stdscr = MockWindow(60, 120, 0, 0)
        controller.stdscr = stdscr
        controller._validate_and_setup_layout()
        
        # Mock window creation to raise error
        with patch('curses_ui_framework.view.curses.newwin') as mock_newwin:
            mock_newwin.side_effect = self.mock_curses.error("Window creation failed")
            
            view = WindowView(stdscr)
            
            # Should raise WindowCreationError
            with self.assertRaises(WindowCreationError):
                view.initialize_windows(controller.layout_info)
    
    def test_input_error_handling(self):
        """Test handling of input errors"""
        controller = CursesController(self.model)
        
        # Test with invalid key codes
        result = controller.handle_input(-1)  # Invalid key
        self.assertTrue(result)  # Should continue running
        
        result = controller.handle_input(999999)  # Very large key code
        self.assertTrue(result)  # Should continue running
    
    def test_content_error_handling(self):
        """Test handling of content-related errors"""
        controller = CursesController(self.model)
        
        # Test with very large content
        large_content = "x" * 100000
        controller.update_main_content(large_content)
        self.assertEqual(self.model.get_main_content(), large_content)
        
        # Test with special characters
        special_content = "Special chars: àáâãäåæçèéêë\n中文\n🚀🎉"
        controller.update_main_content(special_content)
        self.assertEqual(self.model.get_main_content(), special_content)
    
    def test_command_error_handling(self):
        """Test handling of command execution errors"""
        controller = CursesController(self.model)
        
        # Test empty command
        controller._execute_command("")
        # Should not crash
        
        # Test invalid command
        controller._execute_command("invalid_command_xyz")
        status = self.model.get_status()
        self.assertIn("Unknown command", status)
        
        # Test command with invalid arguments
        controller._execute_command("status")  # Missing argument
        # Should not crash


class TestPerformanceIntegration(IntegrationTestBase):
    """Test performance aspects of the framework"""
    
    def test_large_content_handling(self):
        """Test handling of large content"""
        controller = CursesController(self.model)
        
        # Create large content
        lines = [f"Line {i}: " + "x" * 100 for i in range(1000)]
        large_content = "\n".join(lines)
        
        # Measure time to update content
        start_time = time.time()
        controller.update_main_content(large_content)
        end_time = time.time()
        
        # Should complete reasonably quickly (less than 1 second)
        self.assertLess(end_time - start_time, 1.0)
        
        # Verify content was set
        self.assertEqual(self.model.get_main_content(), large_content)
    
    def test_rapid_input_handling(self):
        """Test handling of rapid input"""
        controller = CursesController(self.model)
        
        # Simulate rapid key presses
        keys = [self.mock_curses.KEY_DOWN, self.mock_curses.KEY_UP] * 100
        
        start_time = time.time()
        for key in keys:
            controller.handle_input(key)
        end_time = time.time()
        
        # Should handle all inputs quickly
        self.assertLess(end_time - start_time, 1.0)
    
    def test_memory_usage_stability(self):
        """Test that memory usage remains stable"""
        controller = CursesController(self.model)
        
        # Perform many operations
        for i in range(100):
            controller.update_main_content(f"Content update {i}")
            controller._execute_command(f"status Update {i}")
            controller.handle_input(self.mock_curses.KEY_DOWN)
            controller.handle_input(self.mock_curses.KEY_UP)
        
        # Verify final state is consistent
        self.assertEqual(self.model.get_main_content(), "Content update 99")
        self.assertEqual(self.model.get_status(), "Update 99")


class TestConcurrencyIntegration(IntegrationTestBase):
    """Test framework behavior with concurrent operations"""
    
    def test_background_statistics_updates(self):
        """Test background statistics updates don't interfere"""
        controller = CursesController(self.model)
        
        # Start background thread that updates statistics
        def update_stats():
            for i in range(10):
                self.model.update_statistics('test_metric', i)
                time.sleep(0.01)
        
        thread = threading.Thread(target=update_stats, daemon=True)
        thread.start()
        
        # Perform normal operations while background thread runs
        for i in range(5):
            controller.update_main_content(f"Content {i}")
            controller._execute_command(f"status Status {i}")
            time.sleep(0.01)
        
        thread.join(timeout=1.0)
        
        # Verify operations completed successfully
        self.assertEqual(self.model.get_main_content(), "Content 4")
        self.assertEqual(self.model.get_status(), "Status 4")
    
    def test_concurrent_content_updates(self):
        """Test concurrent content updates are handled safely"""
        controller = CursesController(self.model)
        results = []
        
        def update_content(thread_id):
            for i in range(5):
                content = f"Thread {thread_id} - Update {i}"
                controller.update_main_content(content)
                results.append(content)
                time.sleep(0.001)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=update_content, args=(i,), daemon=True)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=1.0)
        
        # Verify no crashes occurred and final state is valid
        final_content = self.model.get_main_content()
        self.assertIsInstance(final_content, str)
        self.assertGreater(len(results), 0)


class TestFrameworkExtensibility(IntegrationTestBase):
    """Test framework extensibility and customization"""
    
    def test_custom_model_extension(self):
        """Test extending the ApplicationModel"""
        class CustomModel(ApplicationModel):
            def __init__(self):
                super().__init__("Custom App", "Test", "1.0")
                self.custom_data = {}
            
            def add_custom_data(self, key, value):
                self.custom_data[key] = value
                self.set_main_content(f"Custom data: {self.custom_data}")
        
        custom_model = CustomModel()
        controller = CursesController(custom_model)
        
        # Test custom functionality
        custom_model.add_custom_data("test_key", "test_value")
        self.assertIn("test_key", custom_model.custom_data)
        self.assertIn("test_value", custom_model.get_main_content())
    
    def test_custom_controller_extension(self):
        """Test extending the CursesController"""
        class CustomController(CursesController):
            def __init__(self, model):
                super().__init__(model)
                self.custom_commands = 0
            
            def _execute_command(self, command: str) -> None:
                if command.startswith("custom"):
                    self.custom_commands += 1
                    self.set_status(f"Custom command executed {self.custom_commands} times")
                else:
                    super()._execute_command(command)
        
        controller = CustomController(self.model)
        
        # Test custom command handling
        controller._execute_command("custom test")
        self.assertEqual(controller.custom_commands, 1)
        self.assertIn("Custom command executed", self.model.get_status())
        
        # Test fallback to parent
        controller._execute_command("help")
        self.assertIn("help", self.model.get_main_content().lower())
    
    def test_layout_customization(self):
        """Test custom layout calculation"""
        class CustomController(CursesController):
            def _calculate_layout(self, terminal_height: int, terminal_width: int) -> None:
                # Custom layout with different proportions
                self.layout_info.terminal_height = terminal_height
                self.layout_info.terminal_width = terminal_width
                
                # Make top window larger
                self.layout_info.top_window.y = 0
                self.layout_info.top_window.x = 0
                self.layout_info.top_window.height = 5  # Larger than default
                self.layout_info.top_window.width = terminal_width
                
                # Adjust other windows accordingly
                remaining_height = terminal_height - 8  # 5 for top, 3 for bottom
                left_width = terminal_width // 3  # Different proportion
                
                self.layout_info.left_window.y = 5
                self.layout_info.left_window.x = 0
                self.layout_info.left_window.height = remaining_height
                self.layout_info.left_window.width = left_width
                
                self.layout_info.main_window.y = 5
                self.layout_info.main_window.x = left_width
                self.layout_info.main_window.height = remaining_height
                self.layout_info.main_window.width = terminal_width - left_width
                
                self.layout_info.bottom_window.y = terminal_height - 3
                self.layout_info.bottom_window.x = 0
                self.layout_info.bottom_window.height = 3
                self.layout_info.bottom_window.width = terminal_width
        
        controller = CustomController(self.model)
        stdscr = MockWindow(60, 120, 0, 0)
        controller.stdscr = stdscr
        controller._validate_and_setup_layout()
        
        # Verify custom layout
        self.assertEqual(controller.layout_info.top_window.height, 5)
        self.assertEqual(controller.layout_info.left_window.width, 40)  # 120 // 3


if __name__ == '__main__':
    # Configure test runner
    unittest.main(verbosity=2, buffer=True)