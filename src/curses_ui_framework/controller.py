"""
CursesController class for the Curses UI Framework.

This module implements the Controller component of the MVC architecture,
coordinating between the model and view and handling application logic.
"""

import curses
from typing import Optional, List
from .model import ApplicationModel
from .view import WindowView
from .exceptions import (
    CursesFrameworkError, 
    TerminalTooSmallError, 
    TerminalCompatibilityError,
    CursesInitializationError
)


class LayoutInfo:
    """Container for layout information."""

    def __init__(self):
        self.top_window = WindowGeometry()
        self.left_window = WindowGeometry()
        self.main_window = WindowGeometry()
        self.bottom_window = WindowGeometry()
        self.terminal_height = 0
        self.terminal_width = 0


class WindowGeometry:
    """Container for window geometry information."""

    def __init__(self, y=0, x=0, height=0, width=0):
        self.y = y
        self.x = x
        self.height = height
        self.width = width


class CursesController:
    """
    Main controller class that coordinates the entire curses application.

    This class implements the Controller component of the MVC pattern,
    managing the application lifecycle and coordinating between model and view.
    """

    # Minimum terminal requirements (120x60 as per requirements)
    MIN_TERMINAL_WIDTH = 120
    MIN_TERMINAL_HEIGHT = 60

    def __init__(self, model: ApplicationModel, view: Optional[WindowView] = None):
        """
        Initialize the controller with model and view.

        Args:
            model: Application model instance
            view: Window view instance (will be created if None)
        """
        self.model = model
        self.view = view
        self.stdscr = None
        self.running = False
        self.layout_info = LayoutInfo()

    def run(self) -> None:
        """Start the application main loop with comprehensive error handling."""
        try:
            # Validate terminal compatibility before starting
            self._validate_terminal_compatibility()
            
            # Start the curses application
            curses.wrapper(self._main_loop)
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            pass
        except TerminalCompatibilityError as e:
            # Handle terminal compatibility issues
            self._handle_compatibility_error(e)
        except CursesInitializationError as e:
            # Handle curses initialization failures
            self._handle_initialization_error(e)
        except Exception as e:
            # Handle any other unexpected errors
            raise CursesFrameworkError(f"Application error: {e}")

    def _validate_terminal_compatibility(self) -> None:
        """
        Validate terminal compatibility with curses framework.
        
        Raises:
            TerminalCompatibilityError: If terminal lacks required features
        """
        try:
            # Check if curses module is available and functional
            import curses
            
            # Test basic curses functionality
            try:
                # Try to get terminal capabilities
                curses.setupterm()
            except curses.error:
                raise TerminalCompatibilityError("Terminal does not support curses")
            
            # Check for required terminal capabilities
            if not hasattr(curses, 'newwin'):
                raise TerminalCompatibilityError("Terminal does not support window creation")
            
            if not hasattr(curses, 'KEY_RESIZE'):
                raise TerminalCompatibilityError("Terminal does not support resize events")
            
            # Check if terminal supports minimum required features
            try:
                # Test if we can create a basic window (this will be cleaned up by wrapper)
                test_result = curses.wrapper(self._test_basic_curses_functionality)
                if not test_result:
                    raise TerminalCompatibilityError("Basic curses functionality test failed")
            except Exception as e:
                raise TerminalCompatibilityError(f"Curses functionality test failed: {e}")
                
        except ImportError:
            raise TerminalCompatibilityError("Curses module not available")

    def _test_basic_curses_functionality(self, stdscr) -> bool:
        """
        Test basic curses functionality in a safe wrapper.
        
        Args:
            stdscr: Test screen from curses.wrapper
            
        Returns:
            True if basic functionality works, False otherwise
        """
        try:
            # Test basic screen operations
            height, width = stdscr.getmaxyx()
            if height < 1 or width < 1:
                return False
            
            # Test window creation
            test_win = curses.newwin(1, 1, 0, 0)
            if test_win is None:
                return False
            
            # Test basic drawing
            stdscr.addstr(0, 0, "T")
            stdscr.refresh()
            
            # Test color support (optional but preferred)
            if curses.has_colors():
                curses.start_color()
            
            return True
        except Exception:
            return False

    def _handle_compatibility_error(self, error: TerminalCompatibilityError) -> None:
        """
        Handle terminal compatibility errors with informative messages.
        
        Args:
            error: The compatibility error that occurred
        """
        print(f"Terminal Compatibility Error: {error}")
        print("\nYour terminal does not support the required curses features.")
        print("Please try one of the following solutions:")
        print("1. Use a different terminal emulator (xterm, gnome-terminal, etc.)")
        print("2. Update your terminal software to a newer version")
        print("3. Check that your TERM environment variable is set correctly")
        print("4. Ensure you're not running in a minimal environment")
        
        # Additional specific advice based on the error
        if error.missing_feature:
            if "resize" in error.missing_feature.lower():
                print("5. Your terminal may not support dynamic resizing")
            elif "window" in error.missing_feature.lower():
                print("5. Your terminal may not support advanced window management")

    def _handle_initialization_error(self, error: CursesInitializationError) -> None:
        """
        Handle curses initialization errors with informative messages.
        
        Args:
            error: The initialization error that occurred
        """
        print(f"Curses Initialization Error: {error}")
        print("\nFailed to initialize the curses library.")
        print("This may be due to:")
        print("1. Running in a non-interactive environment")
        print("2. Terminal permissions issues")
        print("3. Corrupted terminal database")
        print("4. Missing terminal capabilities")
        print("\nTry running the application in a standard terminal window.")

    def _main_loop(self, stdscr) -> None:
        """
        Main application loop (called by curses.wrapper) with robust error handling.

        Args:
            stdscr: Main curses screen object
        """
        try:
            self.stdscr = stdscr

            # Initialize curses settings with error handling
            self._initialize_curses_settings()

            # Create view if not provided
            if self.view is None:
                self.view = WindowView(stdscr)

            # Validate terminal size and calculate layout
            self._validate_and_setup_layout()

            # Initialize windows with error handling
            try:
                self.view.initialize_windows(self.layout_info)
            except Exception as e:
                raise CursesInitializationError(f"Window initialization failed: {e}")

            self.running = True

            # Main event loop with comprehensive error handling
            while self.running:
                try:
                    # Handle input
                    try:
                        key = stdscr.getch()
                        if key != -1:  # Key was pressed
                            # Check for resize event first
                            if key == curses.KEY_RESIZE:
                                self.handle_resize()
                                continue
                            
                            if not self.handle_input(key):
                                break
                    except curses.error:
                        # Handle curses input errors gracefully
                        pass

                    # Additional resize detection (some terminals may not send KEY_RESIZE)
                    try:
                        current_height, current_width = stdscr.getmaxyx()
                        if (current_height != self.layout_info.terminal_height or 
                            current_width != self.layout_info.terminal_width):
                            self.handle_resize()
                    except curses.error:
                        # Handle terminal size query errors
                        pass

                    # Update statistics with error handling
                    try:
                        self.model.update_statistics('content_lines', len(self.model.get_main_content().split('\n')))
                    except Exception:
                        # Don't let statistics updates crash the app
                        pass

                    # Update view with current command input and statistics
                    try:
                        if self.view:
                            self.view.set_bottom_window_command_input(self.model.get_command_input())
                            self.view.set_bottom_window_statistics(self.model.get_statistics())
                    except Exception:
                        # Don't let view updates crash the app
                        pass

                    # Render current state with error handling
                    try:
                        if self.view:
                            self.view.render_all(self.model)
                    except curses.error:
                        # Handle rendering errors (e.g., terminal too small)
                        self._handle_rendering_error()
                    except Exception as e:
                        # Handle other rendering errors
                        self.model.set_status(f"Rendering error: {str(e)[:50]}")

                except KeyboardInterrupt:
                    # Handle Ctrl+C in main loop
                    self.running = False
                    break
                except Exception as e:
                    # Handle unexpected errors in main loop
                    self._handle_main_loop_error(e)

        except TerminalTooSmallError as e:
            # Handle terminal too small during initialization
            self._handle_terminal_too_small_during_init(e)
        except Exception as e:
            # Handle any other initialization errors
            raise CursesInitializationError(f"Main loop initialization failed: {e}")
        finally:
            # Ensure cleanup happens
            self.shutdown()

    def _initialize_curses_settings(self) -> None:
        """
        Initialize curses settings with error handling.
        
        Raises:
            CursesInitializationError: If curses settings cannot be initialized
        """
        try:
            # Hide cursor
            curses.curs_set(0)
        except curses.error:
            # Some terminals don't support cursor visibility control
            pass
        
        try:
            # Non-blocking input
            self.stdscr.nodelay(1)
        except curses.error:
            raise CursesInitializationError("Cannot set non-blocking input")
        
        try:
            # 100ms timeout for input
            self.stdscr.timeout(100)
        except curses.error:
            # Fallback to blocking input if timeout not supported
            pass

    def _handle_rendering_error(self) -> None:
        """Handle rendering errors gracefully."""
        try:
            # Try to clear screen and show error
            self.stdscr.clear()
            height, width = self.stdscr.getmaxyx()
            
            error_msg = "Rendering error - terminal may be too small"
            if len(error_msg) <= width and height > 0:
                self.stdscr.addstr(0, 0, error_msg[:width])
            
            self.stdscr.refresh()
        except curses.error:
            # If we can't even show an error, just continue
            pass

    def _handle_main_loop_error(self, error: Exception) -> None:
        """
        Handle unexpected errors in the main loop.
        
        Args:
            error: The exception that occurred
        """
        # Update status with error information
        error_msg = f"Error: {str(error)[:50]}"
        try:
            self.model.set_status(error_msg)
        except Exception:
            # If we can't update the model, just continue
            pass
        
        # Try to continue running unless it's a critical error
        if isinstance(error, (MemoryError, SystemExit)):
            self.running = False

    def _handle_terminal_too_small_during_init(self, error: TerminalTooSmallError) -> None:
        """
        Handle terminal too small error during initialization.
        
        Args:
            error: The TerminalTooSmallError that occurred
        """
        try:
            # Show error message in whatever space we have
            self.stdscr.clear()
            height, width = self.stdscr.getmaxyx()
            
            error_lines = [
                "Terminal too small!",
                f"Need: {self.MIN_TERMINAL_WIDTH}x{self.MIN_TERMINAL_HEIGHT}",
                f"Have: {width}x{height}",
                "Resize terminal or press 'q'"
            ]
            
            for i, line in enumerate(error_lines):
                if i < height and len(line) <= width:
                    try:
                        self.stdscr.addstr(i, 0, line[:width])
                    except curses.error:
                        pass
            
            self.stdscr.refresh()
            
            # Wait for user input or resize
            while True:
                try:
                    key = self.stdscr.getch()
                    if key == ord('q') or key == 27:  # 'q' or ESC
                        break
                    elif key == curses.KEY_RESIZE:
                        # Try to reinitialize with new size
                        try:
                            self._validate_and_setup_layout()
                            # If successful, continue with main loop
                            return
                        except TerminalTooSmallError:
                            # Still too small, continue waiting
                            continue
                except curses.error:
                    pass
        except Exception:
            # If error handling fails, just exit
            pass

    def handle_input(self, key: int) -> bool:
        """
        Handle user input and update model/view accordingly.

        Args:
            key: Key code from curses

        Returns:
            True to continue running, False to exit
        """
        # Basic navigation handling
        if key == ord('q') or key == 27:  # 'q' or ESC to quit
            return False

        elif key == curses.KEY_UP:
            # Navigate up in left window
            current = self.model.get_selected_navigation_index()
            if current > 0:
                self.model.set_selected_navigation_index(current - 1)

        elif key == curses.KEY_DOWN:
            # Navigate down in left window
            current = self.model.get_selected_navigation_index()
            items = self.model.get_navigation_items()
            if current < len(items) - 1:
                self.model.set_selected_navigation_index(current + 1)

        elif key == curses.KEY_HOME:
            # Jump to first navigation item
            if self.model.get_navigation_items():
                self.model.set_selected_navigation_index(0)

        elif key == curses.KEY_END:
            # Jump to last navigation item
            items = self.model.get_navigation_items()
            if items:
                self.model.set_selected_navigation_index(len(items) - 1)

        elif key == ord('\t'):  # Tab to switch bottom window mode
            current_mode = self.model.get_bottom_window_mode()
            new_mode = "input" if current_mode == "display" else "display"
            self.model.set_bottom_window_mode(new_mode)
            
            # Clear command input when switching to display mode
            if new_mode == "display":
                self.model.clear_command_input()
                if self.view:
                    self.view.set_bottom_window_command_input("")
            
            # Update view immediately to show mode change
            if self.view:
                self.view.mark_window_dirty('bottom')

        elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:  # Backspace in input mode
            if self.model.get_bottom_window_mode() == "input":
                current_input = self.model.get_command_input()
                if current_input:
                    new_input = current_input[:-1]
                    self.model.set_command_input(new_input)
                    
                    # Update view immediately to show the change
                    if self.view:
                        self.view.set_bottom_window_command_input(new_input)
                        self.view.mark_window_dirty('bottom')

        elif key == ord('\n') or key == ord('\r'):  # Enter key
            if self.model.get_bottom_window_mode() == "input":
                # Execute command in input mode
                command = self.model.get_command_input()
                if command.strip():
                    self._execute_command(command.strip())
                    self.model.add_command_to_history(command.strip())
                    self.model.clear_command_input()
                    
                    # Update view to clear the input display
                    if self.view:
                        self.view.set_bottom_window_command_input("")
                        self.view.mark_window_dirty('bottom')
            else:
                # In display mode, Enter activates selected navigation item
                self._activate_navigation_item()

        elif 32 <= key <= 126:  # Printable characters in input mode
            if self.model.get_bottom_window_mode() == "input":
                current_input = self.model.get_command_input()
                new_input = current_input + chr(key)
                self.model.set_command_input(new_input)
                
                # Update view immediately to show the echo
                if self.view:
                    self.view.set_bottom_window_command_input(new_input)
                    self.view.mark_window_dirty('bottom')

        elif key == curses.KEY_PPAGE:  # Page Up - scroll main content up
            if self.view and self.view.can_scroll_main_content('up'):
                self.view.scroll_main_content('up', 5)

        elif key == curses.KEY_NPAGE:  # Page Down - scroll main content down
            if self.view and self.view.can_scroll_main_content('down'):
                self.view.scroll_main_content('down', 5)

        elif key == ord('k'):  # 'k' key - scroll main content up one line
            if self.view and self.view.can_scroll_main_content('up'):
                self.view.scroll_main_content('up', 1)

        elif key == ord('j'):  # 'j' key - scroll main content down one line
            if self.view and self.view.can_scroll_main_content('down'):
                self.view.scroll_main_content('down', 1)

        elif key == ord('g'):  # 'g' key - scroll to top of main content
            self.scroll_main_content_to_top()

        elif key == ord('G'):  # 'G' key - scroll to bottom of main content
            self.scroll_main_content_to_bottom()

        return True

    def _execute_command(self, command: str) -> None:
        """
        Execute a command entered in the bottom window input mode.
        
        This method can be overridden by subclasses to provide specific
        command handling. By default, it provides basic built-in commands.

        Args:
            command: The command string to execute
        """
        # Update statistics
        self.model.increment_statistic('total_commands')
        
        # Parse command
        parts = command.split()
        if not parts:
            return
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Built-in commands
        if cmd == "help":
            help_text = "Available commands:\n\n"
            help_text += "help - Show this help message\n"
            help_text += "clear - Clear main window content\n"
            help_text += "status <message> - Set status message\n"
            help_text += "nav <item> - Navigate to item by name\n"
            help_text += "quit - Exit application\n"
            help_text += "stats - Show application statistics\n"
            self.update_main_content(help_text)
            self.set_status("Help displayed")
            
        elif cmd == "clear":
            self.clear_main_content()
            self.set_status("Main content cleared")
            
        elif cmd == "status" and args:
            status_msg = " ".join(args)
            self.set_status(status_msg)
            
        elif cmd == "nav" and args:
            item_name = " ".join(args)
            if self.navigate_to_item(item_name):
                self.set_status(f"Navigated to: {item_name}")
            else:
                self.set_status(f"Navigation item not found: {item_name}")
                
        elif cmd == "quit":
            self.running = False
            
        elif cmd == "stats":
            stats = self.model.get_statistics()
            stats_text = "Application Statistics:\n\n"
            for key, value in stats.items():
                stats_text += f"{key.replace('_', ' ').title()}: {value}\n"
            self.update_main_content(stats_text)
            self.set_status("Statistics displayed")
            
        else:
            self.set_status(f"Unknown command: {command}")

    def _activate_navigation_item(self) -> None:
        """
        Activate the currently selected navigation item.
        
        This method can be overridden by subclasses to provide specific
        navigation behavior. By default, it updates the status to show
        which item was selected.
        """
        items = self.model.get_navigation_items()
        selected_index = self.model.get_selected_navigation_index()
        
        if 0 <= selected_index < len(items):
            selected_item = items[selected_index]
            # Update status to show selection
            self.model.set_status(f"Selected: {selected_item}")
            
            # Update main content to show selection details
            content = f"Navigation Item Selected\n\n"
            content += f"Item: {selected_item}\n"
            content += f"Index: {selected_index + 1} of {len(items)}\n\n"
            content += "This is a placeholder for navigation item content.\n"
            content += "Override _activate_navigation_item() in your controller\n"
            content += "to provide specific behavior for each navigation item."
            
            self.model.set_main_content(content)

    def handle_resize(self) -> None:
        """
        Handle terminal resize events comprehensively.
        
        This method implements comprehensive resize event handling including:
        - Terminal resize detection using curses.KEY_RESIZE
        - Automatic window recalculation and repositioning
        - Ensuring all windows maintain proper layout after resize
        """
        try:
            # Get new terminal dimensions
            new_height, new_width = self.stdscr.getmaxyx()
            
            # Check if size actually changed (avoid unnecessary work)
            if (self.layout_info.terminal_height == new_height and 
                self.layout_info.terminal_width == new_width):
                return
            
            # Store old layout for comparison
            old_layout = self.layout_info
            
            # Validate new terminal size and recalculate layout
            self._validate_and_setup_layout()
            
            # Clear the entire screen to prevent artifacts
            self.stdscr.clear()
            
            # Resize all windows with new layout
            if self.view:
                self.view.resize_windows(self.layout_info)
            
            # Force complete refresh of all windows
            self.stdscr.refresh()
            if self.view:
                self.view.render_all(self.model)
            
            # Update status to indicate successful resize
            self.model.set_status(f"Resized to {new_width}x{new_height}")
            
        except TerminalTooSmallError as e:
            # Handle terminal too small gracefully
            self._handle_terminal_too_small_error(e)
        except Exception as e:
            # Handle any other resize-related errors
            self._handle_resize_error(e)

    def _handle_terminal_too_small_error(self, error: TerminalTooSmallError) -> None:
        """
        Handle terminal too small error during resize.
        
        Args:
            error: The TerminalTooSmallError that occurred
        """
        # Clear screen and show error message
        self.stdscr.clear()
        
        # Get current terminal size
        height, width = self.stdscr.getmaxyx()
        
        # Create error message
        error_lines = [
            "TERMINAL TOO SMALL",
            "",
            f"Current size: {width} x {height}",
            f"Minimum required: {self.MIN_TERMINAL_WIDTH} x {self.MIN_TERMINAL_HEIGHT}",
            "",
            "Please resize your terminal window",
            "Press 'q' to quit or resize terminal"
        ]
        
        # Display error message centered if possible
        start_y = max(0, height // 2 - len(error_lines) // 2)
        
        for i, line in enumerate(error_lines):
            y_pos = start_y + i
            if y_pos < height:
                # Center the line horizontally
                x_pos = max(0, (width - len(line)) // 2)
                try:
                    self.stdscr.addstr(y_pos, x_pos, line[:width])
                except curses.error:
                    pass
        
        self.stdscr.refresh()
        
        # Update model status
        self.model.set_status(f"Terminal too small: {width}x{height} < {self.MIN_TERMINAL_WIDTH}x{self.MIN_TERMINAL_HEIGHT}")

    def _handle_resize_error(self, error: Exception) -> None:
        """
        Handle general resize errors.
        
        Args:
            error: The exception that occurred during resize
        """
        # Log error and update status
        error_msg = f"Resize error: {str(error)}"
        self.model.set_status(error_msg)
        
        # Try to recover by reinitializing windows
        try:
            if self.view:
                self.view.cleanup()
                self._validate_and_setup_layout()
                self.view.initialize_windows(self.layout_info)
        except Exception:
            # If recovery fails, set error status
            self.model.set_status("Resize recovery failed - restart may be needed")

    def shutdown(self) -> None:
        """Clean shutdown of the application."""
        self.running = False
        if self.view:
            self.view.cleanup()

    def _validate_and_setup_layout(self) -> None:
        """Validate terminal size and calculate layout."""
        height, width = self.stdscr.getmaxyx()

        # Check minimum size requirements
        if height < self.MIN_TERMINAL_HEIGHT or width < self.MIN_TERMINAL_WIDTH:
            raise TerminalTooSmallError(
                (height, width),
                (self.MIN_TERMINAL_HEIGHT, self.MIN_TERMINAL_WIDTH)
            )

        # Calculate layout
        self._calculate_layout(height, width)

    def _calculate_layout(self, terminal_height: int, terminal_width: int) -> None:
        """
        Calculate window positions and sizes.

        Args:
            terminal_height: Terminal height in rows
            terminal_width: Terminal width in columns
        """
        self.layout_info.terminal_height = terminal_height
        self.layout_info.terminal_width = terminal_width

        # Top window: Fixed height of 3 rows, full width
        self.layout_info.top_window.y = 0
        self.layout_info.top_window.x = 0
        self.layout_info.top_window.height = 3
        self.layout_info.top_window.width = terminal_width

        # Bottom window: Fixed height of 3 rows, full width
        self.layout_info.bottom_window.y = terminal_height - 3
        self.layout_info.bottom_window.x = 0
        self.layout_info.bottom_window.height = 3
        self.layout_info.bottom_window.width = terminal_width

        # Remaining height for left and main windows
        remaining_height = terminal_height - 6  # Subtract top and bottom

        # Left window: Fixed width of 25% of terminal width
        left_width = max(25, terminal_width // 4)  # At least 25 columns
        self.layout_info.left_window.y = 3
        self.layout_info.left_window.x = 0
        self.layout_info.left_window.height = remaining_height
        self.layout_info.left_window.width = left_width

        # Main window: Remaining space
        self.layout_info.main_window.y = 3
        self.layout_info.main_window.x = left_width
        self.layout_info.main_window.height = remaining_height
        self.layout_info.main_window.width = terminal_width - left_width

    # Content management methods for MVC integration

    def update_main_content(self, content: str) -> None:
        """
        Update main window content through MVC pattern.

        Args:
            content: New content to display
        """
        # Update model
        self.model.set_main_content(content)
        
        # Update view through content manager
        if self.view:
            self.view.update_main_content(content)

    def append_main_content(self, content: str) -> None:
        """
        Append content to main window through MVC pattern.

        Args:
            content: Content to append
        """
        # Update model (append to existing content)
        current_content = self.model.get_main_content()
        new_content = current_content + '\n' + content if current_content else content
        self.model.set_main_content(new_content)
        
        # Update view through content manager
        if self.view:
            self.view.append_main_content(content)

    def clear_main_content(self) -> None:
        """Clear main window content through MVC pattern."""
        # Update model
        self.model.set_main_content("")
        
        # Update view through content manager
        if self.view:
            self.view.clear_main_content()

    def set_main_content_with_status(self, content: str, status: str = "") -> None:
        """
        Set main window content with processing status through MVC pattern.

        Args:
            content: Main text content to display
            status: Processing status to show (optional)
        """
        # Update model
        full_content = content
        if status:
            full_content = f"[Status: {status}]\n\n{content}"
        self.model.set_main_content(full_content)
        
        # Update view
        if self.view:
            self.view.set_main_content_with_status(content, status)

    def show_processing_status(self, message: str, progress: float = None) -> None:
        """
        Show processing status in main window through MVC pattern.

        Args:
            message: Status message to display
            progress: Optional progress value (0.0 to 1.0)
        """
        # Create status content
        status_content = f"Processing: {message}\n\n"
        
        if progress is not None:
            # Create a simple progress bar
            bar_width = 40
            filled_width = int(bar_width * max(0.0, min(1.0, progress)))
            bar = "█" * filled_width + "░" * (bar_width - filled_width)
            percentage = int(progress * 100)
            status_content += f"Progress: [{bar}] {percentage}%\n\n"
        
        status_content += "Please wait while the operation completes..."
        
        # Update model and view
        self.model.set_main_content(status_content)
        if self.view:
            self.view.show_processing_status(message, progress)

    def get_main_content_info(self) -> dict:
        """
        Get information about main window content through MVC pattern.

        Returns:
            Dictionary with content information including scroll state
        """
        if self.view:
            return self.view.get_main_content_info()
        return {}

    def scroll_main_content_to_top(self) -> None:
        """Scroll main content to the top."""
        if self.view:
            content_manager = self.view.get_content_manager('main')
            if content_manager:
                content_manager.scroll_to_top()

    def scroll_main_content_to_bottom(self) -> None:
        """Scroll main content to the bottom."""
        if self.view:
            content_manager = self.view.get_content_manager('main')
            if content_manager:
                content_manager.scroll_to_bottom()

    def set_bottom_window_mode(self, mode: str) -> None:
        """
        Set bottom window mode through MVC pattern.

        Args:
            mode: Either "display" or "input"
        """
        self.model.set_bottom_window_mode(mode)

    def get_bottom_window_mode(self) -> str:
        """Get current bottom window mode."""
        return self.model.get_bottom_window_mode()

    def execute_command(self, command: str) -> None:
        """
        Execute a command programmatically.

        Args:
            command: Command string to execute
        """
        self._execute_command(command)

    def get_command_history(self) -> List[str]:
        """Get command history."""
        return self.model.get_command_history()

    def get_application_statistics(self) -> dict:
        """Get current application statistics."""
        return self.model.get_statistics()

    def set_navigation_items(self, items: List[str]) -> None:
        """
        Set navigation items through MVC pattern.

        Args:
            items: List of navigation item strings
        """
        self.model.set_navigation_items(items)

    def get_selected_navigation_item(self) -> str:
        """
        Get the currently selected navigation item.

        Returns:
            The selected navigation item string, or empty string if none selected
        """
        items = self.model.get_navigation_items()
        selected_index = self.model.get_selected_navigation_index()
        
        if 0 <= selected_index < len(items):
            return items[selected_index]
        return ""

    def navigate_to_item(self, item_name: str) -> bool:
        """
        Navigate to a specific item by name.

        Args:
            item_name: Name of the navigation item to select

        Returns:
            True if item was found and selected, False otherwise
        """
        items = self.model.get_navigation_items()
        try:
            index = items.index(item_name)
            self.model.set_selected_navigation_index(index)
            return True
        except ValueError:
            return False

    def navigate_to_index(self, index: int) -> bool:
        """
        Navigate to a specific item by index.

        Args:
            index: Index of the navigation item to select (0-based)

        Returns:
            True if index is valid and item was selected, False otherwise
        """
        items = self.model.get_navigation_items()
        if 0 <= index < len(items):
            self.model.set_selected_navigation_index(index)
            return True
        return False

    def set_status(self, status: str) -> None:
        """
        Set status message through MVC pattern.

        Args:
            status: Status message to display
        """
        self.model.set_status(status)

    def get_content_manager(self, window_name: str):
        """
        Get content manager for a specific window.

        Args:
            window_name: Name of the window ('main', 'left', 'top', 'bottom')

        Returns:
            ContentManager instance for the window, or None if not available
        """
        if self.view:
            return self.view.get_content_manager(window_name)
        return None

    def update_application_metadata(self, title: str = None, author: str = None, version: str = None) -> None:
        """
        Update application metadata through MVC pattern.

        Args:
            title: New application title (if provided)
            author: New application author (if provided)
            version: New application version (if provided)
        """
        # Update model with new metadata (only update provided values)
        if title is not None:
            self.model._title = title
        if author is not None:
            self.model._author = author
        if version is not None:
            self.model._version = version

    def get_application_metadata(self) -> tuple:
        """
        Get current application metadata.

        Returns:
            Tuple of (title, author, version)
        """
        return (self.model.get_title(), self.model.get_author(), self.model.get_version())