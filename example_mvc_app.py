#!/usr/bin/env python3
"""
Comprehensive MVC Example Application for the Curses UI Framework.

This example demonstrates proper MVC separation with:
- Navigation between different application sections
- Content display with scrolling and formatting
- Command input with history and processing
- Status updates and statistics tracking
- Error handling and resize responsiveness
- Real-time content updates and user interaction

The application simulates a simple file manager / text viewer with
multiple sections accessible through navigation.
"""

import sys
import os
import time
import threading
import curses
from typing import List, Dict, Optional
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from curses_ui_framework import (
    CursesController, 
    ApplicationModel, 
    WindowView,
    CursesFrameworkError
)


class FileManagerModel(ApplicationModel):
    """
    Extended model for the file manager example application.
    
    Demonstrates proper MVC separation by managing all application
    state and business logic independently of the UI.
    """
    
    def __init__(self):
        super().__init__(
            title="MVC File Manager Demo",
            author="Curses UI Framework",
            version="1.0.0"
        )
        
        # Application-specific state
        self._current_section = "home"
        self._file_list = []
        self._current_file_content = ""
        self._current_directory = os.getcwd()
        self._search_results = []
        self._processing_status = ""
        self._last_command_result = ""
        
        # Initialize navigation sections
        self.set_navigation_items([
            "Home",
            "File Browser", 
            "Text Viewer",
            "Search",
            "Settings",
            "Help",
            "About"
        ])
        
        # Initialize with home content
        self._update_content_for_section("home")
        
        # Enhanced statistics
        self._statistics.update({
            'files_viewed': 0,
            'searches_performed': 0,
            'commands_executed': 0,
            'current_section': 'home',
            'session_start': datetime.now().strftime("%H:%M:%S")
        })
    
    def set_current_section(self, section: str) -> None:
        """Set the current application section."""
        self._current_section = section.lower()
        self._statistics['current_section'] = section.lower()
        self._update_content_for_section(section.lower())
    
    def get_current_section(self) -> str:
        """Get the current application section."""
        return self._current_section
    
    def _update_content_for_section(self, section: str) -> None:
        """Update main content based on the selected section."""
        if section == "home":
            self._set_home_content()
        elif section == "file browser":
            self._set_file_browser_content()
        elif section == "text viewer":
            self._set_text_viewer_content()
        elif section == "search":
            self._set_search_content()
        elif section == "settings":
            self._set_settings_content()
        elif section == "help":
            self._set_help_content()
        elif section == "about":
            self._set_about_content()
        else:
            self.set_main_content(f"Unknown section: {section}")
    
    def _set_home_content(self) -> None:
        """Set content for the home section."""
        content = """Welcome to the MVC File Manager Demo!

This comprehensive example demonstrates the Curses UI Framework's
Model-View-Controller architecture in action.

🏠 CURRENT SECTION: Home Dashboard

📊 QUICK STATS:
• Files viewed this session: {files_viewed}
• Searches performed: {searches_performed}  
• Commands executed: {commands_executed}
• Session started: {session_start}
• Current directory: {current_dir}

🧭 NAVIGATION:
Use the arrow keys (↑/↓) to navigate the left panel, then press
Enter to switch to different sections of the application.

⌨️  COMMANDS:
Press Tab to switch to command mode and try these commands:
• help - Show available commands
• status <message> - Set a custom status
• refresh - Refresh current section
• stats - Show detailed statistics
• clear - Clear main content
• time - Show current time

🔄 REAL-TIME FEATURES:
This application demonstrates:
✓ Proper MVC separation of concerns
✓ Navigation between application sections
✓ Command processing with history
✓ Status updates and statistics tracking
✓ Content scrolling (use Page Up/Down, j/k keys)
✓ Error handling and resize responsiveness
✓ Real-time content updates

Navigate to other sections to explore more features!""".format(
            files_viewed=self._statistics.get('files_viewed', 0),
            searches_performed=self._statistics.get('searches_performed', 0),
            commands_executed=self._statistics.get('commands_executed', 0),
            session_start=self._statistics.get('session_start', 'Unknown'),
            current_dir=self._current_directory
        )
        
        self.set_main_content(content)
        self.set_status("Home - Welcome to the MVC Demo Application")
    
    def _set_file_browser_content(self) -> None:
        """Set content for the file browser section."""
        try:
            # Get current directory listing
            files = []
            dirs = []
            
            for item in os.listdir(self._current_directory):
                full_path = os.path.join(self._current_directory, item)
                if os.path.isdir(full_path):
                    dirs.append(item)
                else:
                    files.append(item)
            
            # Sort directories and files
            dirs.sort()
            files.sort()
            
            content = f"""📁 FILE BROWSER

Current Directory: {self._current_directory}

📂 DIRECTORIES ({len(dirs)}):
"""
            
            for directory in dirs[:10]:  # Show first 10 directories
                content += f"  📁 {directory}\n"
            
            if len(dirs) > 10:
                content += f"  ... and {len(dirs) - 10} more directories\n"
            
            content += f"\n📄 FILES ({len(files)}):\n"
            
            for file in files[:15]:  # Show first 15 files
                try:
                    full_path = os.path.join(self._current_directory, file)
                    size = os.path.getsize(full_path)
                    if size < 1024:
                        size_str = f"{size}B"
                    elif size < 1024 * 1024:
                        size_str = f"{size//1024}KB"
                    else:
                        size_str = f"{size//(1024*1024)}MB"
                    
                    content += f"  📄 {file} ({size_str})\n"
                except OSError:
                    content += f"  📄 {file} (size unknown)\n"
            
            if len(files) > 15:
                content += f"  ... and {len(files) - 15} more files\n"
            
            content += f"""

💡 COMMANDS AVAILABLE:
• 'cd <directory>' - Change to directory
• 'view <filename>' - View file content
• 'ls' - Refresh directory listing
• 'pwd' - Show current directory
• 'up' - Go to parent directory

This demonstrates how the Model manages file system data
independently of the View's presentation logic."""
            
            self.set_main_content(content)
            self.set_status(f"File Browser - {len(dirs)} dirs, {len(files)} files")
            
        except PermissionError:
            self.set_main_content("❌ Permission denied accessing current directory")
            self.set_status("File Browser - Permission Error")
        except Exception as e:
            self.set_main_content(f"❌ Error reading directory: {str(e)}")
            self.set_status("File Browser - Error")
    
    def _set_text_viewer_content(self) -> None:
        """Set content for the text viewer section."""
        if self._current_file_content:
            content = f"""📖 TEXT VIEWER

Currently viewing: {getattr(self, '_current_filename', 'Unknown file')}

{self._current_file_content}

💡 Use Page Up/Down or j/k keys to scroll through content.
💡 Use 'view <filename>' command to load a different file."""
        else:
            content = """📖 TEXT VIEWER

No file currently loaded.

To view a file:
1. Navigate to 'File Browser' section
2. Use the 'view <filename>' command to load a file
3. Return to this section to read the content

EXAMPLE FILES TO TRY:
• README.md - Project documentation
• demo.py - Demo application source
• requirements.txt - Python dependencies

This section demonstrates how the Model stores file content
data while the View handles the presentation and scrolling."""
        
        self.set_main_content(content)
        status = "Text Viewer - " + (f"Viewing {getattr(self, '_current_filename', 'file')}" 
                                   if self._current_file_content else "No file loaded")
        self.set_status(status)
    
    def _set_search_content(self) -> None:
        """Set content for the search section."""
        content = """🔍 SEARCH FUNCTIONALITY

This section demonstrates search capabilities within the MVC pattern.

SEARCH COMMANDS:
• 'search <term>' - Search for files containing term
• 'find <pattern>' - Find files matching pattern
• 'grep <text>' - Search file contents for text

RECENT SEARCHES:
"""
        
        # Show recent search results if any
        if self._search_results:
            content += f"Last search found {len(self._search_results)} results:\n"
            for i, result in enumerate(self._search_results[:5]):
                content += f"  {i+1}. {result}\n"
            if len(self._search_results) > 5:
                content += f"  ... and {len(self._search_results) - 5} more results\n"
        else:
            content += "No recent searches performed.\n"
        
        content += """
SEARCH FEATURES:
✓ File name pattern matching
✓ Content text searching  
✓ Result ranking and filtering
✓ Search history tracking

This demonstrates how search functionality can be cleanly
separated into Model (search logic) and View (result display)."""
        
        self.set_main_content(content)
        self.set_status(f"Search - {self._statistics.get('searches_performed', 0)} searches performed")
    
    def _set_settings_content(self) -> None:
        """Set content for the settings section."""
        content = """⚙️  SETTINGS & CONFIGURATION

This section demonstrates configuration management in MVC architecture.

CURRENT SETTINGS:
• Theme: Default Terminal
• Auto-refresh: Enabled
• Command history: Enabled
• Statistics tracking: Enabled
• Error reporting: Verbose

AVAILABLE COMMANDS:
• 'set <option> <value>' - Change a setting
• 'reset' - Reset to defaults
• 'export' - Export current settings
• 'import <file>' - Import settings from file

FRAMEWORK CONFIGURATION:
• Minimum terminal size: 120x60
• Layout: Four-panel (top/left/main/bottom)
• Frame style: Single-line box drawing
• Content management: Scrollable with wrapping
• Input handling: Non-blocking with timeout

MVC BENEFITS DEMONSTRATED:
✓ Settings stored in Model (data persistence)
✓ View updates automatically when settings change
✓ Controller handles setting validation and updates
✓ Clean separation between config logic and display"""
        
        self.set_main_content(content)
        self.set_status("Settings - Configuration Management")
    
    def _set_help_content(self) -> None:
        """Set content for the help section."""
        content = """❓ HELP & DOCUMENTATION

KEYBOARD SHORTCUTS:
• ↑/↓ Arrow Keys - Navigate left panel
• Enter - Activate selected navigation item
• Tab - Switch between display/input mode (bottom panel)
• Page Up/Down - Scroll main content
• j/k - Scroll main content line by line
• g/G - Jump to top/bottom of content
• q/Esc - Quit application

COMMAND REFERENCE:
• help - Show this help
• clear - Clear main content
• status <msg> - Set status message
• refresh - Refresh current section
• stats - Show detailed statistics
• time - Display current time
• quit - Exit application

FILE BROWSER COMMANDS:
• ls - List directory contents
• cd <dir> - Change directory
• pwd - Show current directory
• up - Go to parent directory
• view <file> - Load file for viewing

SEARCH COMMANDS:
• search <term> - Search for files
• find <pattern> - Find files by pattern
• grep <text> - Search file contents

MVC ARCHITECTURE FEATURES:
✓ Model: Manages all application data and state
✓ View: Handles visual presentation and user interface
✓ Controller: Coordinates between Model and View
✓ Clean separation of concerns
✓ Testable components
✓ Extensible design

FRAMEWORK CAPABILITIES:
✓ Automatic layout management
✓ Responsive window resizing
✓ Frame rendering with box-drawing characters
✓ Content scrolling and text wrapping
✓ Command processing with history
✓ Error handling and recovery
✓ Property-based testing integration"""
        
        self.set_main_content(content)
        self.set_status("Help - Documentation and Command Reference")
    
    def _set_about_content(self) -> None:
        """Set content for the about section."""
        content = f"""ℹ️  ABOUT THIS APPLICATION

{self.get_title()}
Version: {self.get_version()}
Author: {self.get_author()}

This comprehensive example application demonstrates the Curses UI
Framework's Model-View-Controller architecture in a real-world
scenario.

🏗️  ARCHITECTURE OVERVIEW:

MODEL (Data & Business Logic):
• FileManagerModel - Extends ApplicationModel
• Manages file system data, search results, settings
• Handles business logic for file operations
• Maintains application state independently

VIEW (User Interface):
• WindowView - Handles all visual presentation
• Renders four-panel layout with frames
• Manages content scrolling and formatting
• Updates display based on Model changes

CONTROLLER (Application Logic):
• FileManagerController - Extends CursesController  
• Coordinates between Model and View
• Handles user input and command processing
• Manages application lifecycle and events

🎯 DEMONSTRATION FEATURES:

✓ Navigation between application sections
✓ File browsing with directory listings
✓ Text file viewing with scrolling
✓ Search functionality with results
✓ Settings and configuration management
✓ Command processing with history
✓ Real-time status updates
✓ Statistics tracking and display
✓ Error handling and recovery
✓ Responsive layout and resizing

📊 SESSION STATISTICS:
• Files viewed: {self._statistics.get('files_viewed', 0)}
• Searches performed: {self._statistics.get('searches_performed', 0)}
• Commands executed: {self._statistics.get('commands_executed', 0)}
• Session started: {self._statistics.get('session_start', 'Unknown')}
• Current section: {self._statistics.get('current_section', 'unknown')}

This application showcases how the MVC pattern enables:
• Clean separation of concerns
• Testable and maintainable code
• Extensible architecture
• Professional terminal applications"""
        
        self.set_main_content(content)
        self.set_status("About - Application Information")
    
    def load_file_content(self, filename: str) -> bool:
        """
        Load file content for viewing.
        
        Args:
            filename: Name of file to load
            
        Returns:
            True if file was loaded successfully, False otherwise
        """
        try:
            file_path = os.path.join(self._current_directory, filename)
            
            # Check if file exists and is readable
            if not os.path.isfile(file_path):
                self._current_file_content = f"❌ File not found: {filename}"
                return False
            
            # Try to read file content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Limit content size for display
            if len(content) > 50000:  # 50KB limit
                content = content[:50000] + "\n\n[Content truncated - file too large for display]"
            
            self._current_file_content = content
            self._current_filename = filename
            self._statistics['files_viewed'] += 1
            
            return True
            
        except PermissionError:
            self._current_file_content = f"❌ Permission denied reading file: {filename}"
            return False
        except UnicodeDecodeError:
            self._current_file_content = f"❌ Cannot display binary file: {filename}"
            return False
        except Exception as e:
            self._current_file_content = f"❌ Error reading file {filename}: {str(e)}"
            return False
    
    def change_directory(self, directory: str) -> bool:
        """
        Change current directory.
        
        Args:
            directory: Directory to change to
            
        Returns:
            True if directory changed successfully, False otherwise
        """
        try:
            if directory == "..":
                new_dir = os.path.dirname(self._current_directory)
            elif directory == "~":
                new_dir = os.path.expanduser("~")
            elif os.path.isabs(directory):
                new_dir = directory
            else:
                new_dir = os.path.join(self._current_directory, directory)
            
            # Normalize and validate path
            new_dir = os.path.abspath(new_dir)
            
            if os.path.isdir(new_dir):
                self._current_directory = new_dir
                # Refresh file browser content if we're in that section
                if self._current_section == "file browser":
                    self._set_file_browser_content()
                return True
            else:
                return False
                
        except Exception:
            return False
    
    def perform_search(self, search_term: str) -> List[str]:
        """
        Perform a search operation.
        
        Args:
            search_term: Term to search for
            
        Returns:
            List of search results
        """
        try:
            results = []
            
            # Search for files containing the term in their name
            for item in os.listdir(self._current_directory):
                if search_term.lower() in item.lower():
                    results.append(f"📄 {item} (filename match)")
            
            # Search for files containing the term in their content (text files only)
            for item in os.listdir(self._current_directory):
                if item.endswith(('.txt', '.py', '.md', '.json', '.yaml', '.yml', '.cfg', '.ini')):
                    try:
                        file_path = os.path.join(self._current_directory, item)
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if search_term.lower() in content.lower():
                                results.append(f"📄 {item} (content match)")
                    except Exception:
                        continue
            
            self._search_results = results
            self._statistics['searches_performed'] += 1
            
            return results
            
        except Exception:
            return []


class FileManagerController(CursesController):
    """
    Extended controller for the file manager example application.
    
    Demonstrates proper MVC separation by handling application-specific
    logic while delegating data management to the Model and presentation
    to the View.
    """
    
    def __init__(self, model: FileManagerModel):
        super().__init__(model)
        self.model = model  # Type hint for IDE support
        
        # Start background statistics updater
        self._stats_thread = None
        self._stats_running = False
        self._start_statistics_updater()
    
    def _start_statistics_updater(self) -> None:
        """Start background thread to update statistics."""
        self._stats_running = True
        self._stats_thread = threading.Thread(target=self._update_statistics_loop, daemon=True)
        self._stats_thread.start()
    
    def handle_input(self, key: int) -> bool:
        """
        Enhanced input handling with immediate visual feedback for command echo.
        """
        # Call parent implementation for all input handling
        result = super().handle_input(key)
        
        # Force immediate refresh of bottom window for better command echo
        if self.model.get_bottom_window_mode() == "input" and self.view:
            # Ensure the command input is displayed immediately
            current_input = self.model.get_command_input()
            self.view.set_bottom_window_command_input(current_input)
            # Force immediate refresh for responsive typing
            self.view.refresh_window('bottom')
        
        return result
    
    def _update_statistics_loop(self) -> None:
        """Background loop to update statistics."""
        start_time = time.time()
        
        while self._stats_running:
            try:
                # Update uptime
                uptime = int(time.time() - start_time)
                self.model.update_statistics('uptime', uptime)
                
                # Update content line count
                content = self.model.get_main_content()
                line_count = len(content.split('\n')) if content else 0
                self.model.update_statistics('content_lines', line_count)
                
                time.sleep(1)  # Update every second
                
            except Exception:
                # Don't let statistics updates crash the app
                break
    
    def _execute_command(self, command: str) -> None:
        """
        Execute application-specific commands.
        
        Args:
            command: Command string to execute
        """
        # Update statistics
        self.model.increment_statistic('commands_executed')
        
        # Parse command
        parts = command.split()
        if not parts:
            return
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # File browser commands
        if cmd == "ls":
            if self.model.get_current_section() == "file browser":
                self.model._set_file_browser_content()
                self.set_status("Directory listing refreshed")
            else:
                self.set_status("Use 'ls' command in File Browser section")
                
        elif cmd == "cd" and args:
            directory = " ".join(args)
            if self.model.change_directory(directory):
                self.set_status(f"Changed directory to: {directory}")
                # Refresh current section if it's file browser
                if self.model.get_current_section() == "file browser":
                    self.model._set_file_browser_content()
            else:
                self.set_status(f"Cannot change to directory: {directory}")
                
        elif cmd == "pwd":
            current_dir = self.model._current_directory
            self.set_status(f"Current directory: {current_dir}")
            
        elif cmd == "up":
            if self.model.change_directory(".."):
                self.set_status("Moved to parent directory")
                if self.model.get_current_section() == "file browser":
                    self.model._set_file_browser_content()
            else:
                self.set_status("Cannot move to parent directory")
                
        elif cmd == "view" and args:
            filename = " ".join(args)
            if self.model.load_file_content(filename):
                self.set_status(f"Loaded file: {filename}")
                # Switch to text viewer section
                self.model.set_current_section("text viewer")
                # Update navigation selection
                nav_items = self.model.get_navigation_items()
                try:
                    index = nav_items.index("Text Viewer")
                    self.model.set_selected_navigation_index(index)
                except ValueError:
                    pass
            else:
                self.set_status(f"Cannot load file: {filename}")
                
        # Search commands
        elif cmd == "search" and args:
            search_term = " ".join(args)
            results = self.model.perform_search(search_term)
            self.set_status(f"Search for '{search_term}' found {len(results)} results")
            # Switch to search section to show results
            self.model.set_current_section("search")
            nav_items = self.model.get_navigation_items()
            try:
                index = nav_items.index("Search")
                self.model.set_selected_navigation_index(index)
            except ValueError:
                pass
                
        elif cmd == "find" and args:
            pattern = " ".join(args)
            # Simple pattern matching (could be enhanced with regex)
            results = self.model.perform_search(pattern)
            self.set_status(f"Find pattern '{pattern}' found {len(results)} matches")
            
        # Utility commands
        elif cmd == "refresh":
            current_section = self.model.get_current_section()
            self.model._update_content_for_section(current_section)
            self.set_status(f"Refreshed {current_section} section")
            
        elif cmd == "time":
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.set_status(f"Current time: {current_time}")
            
        elif cmd == "stats":
            stats = self.model.get_statistics()
            stats_text = "📊 DETAILED STATISTICS\n\n"
            for key, value in stats.items():
                formatted_key = key.replace('_', ' ').title()
                stats_text += f"{formatted_key}: {value}\n"
            
            stats_text += f"\nDirectory: {self.model._current_directory}\n"
            stats_text += f"Current Section: {self.model.get_current_section()}\n"
            
            self.update_main_content(stats_text)
            self.set_status("Detailed statistics displayed")
            
        # Call parent implementation for built-in commands
        else:
            super()._execute_command(command)
    
    def _activate_navigation_item(self) -> None:
        """
        Handle navigation item activation with section switching.
        """
        items = self.model.get_navigation_items()
        selected_index = self.model.get_selected_navigation_index()
        
        if 0 <= selected_index < len(items):
            selected_item = items[selected_index]
            
            # Switch to the selected section
            self.model.set_current_section(selected_item)
            
            # Update status
            self.model.set_status(f"Switched to: {selected_item}")
    
    def shutdown(self) -> None:
        """Clean shutdown with background thread cleanup."""
        # Stop statistics updater
        self._stats_running = False
        if self._stats_thread and self._stats_thread.is_alive():
            self._stats_thread.join(timeout=1.0)
        
        # Call parent shutdown
        super().shutdown()


def main():
    """Run the comprehensive MVC example application."""
    print("Curses UI Framework - Comprehensive MVC Example")
    print("=" * 60)
    print()
    print("This example demonstrates:")
    print("✓ Proper MVC architecture separation")
    print("✓ Navigation between application sections")
    print("✓ File browsing and text viewing")
    print("✓ Command processing with history")
    print("✓ Real-time status updates")
    print("✓ Error handling and resize responsiveness")
    print()
    
    try:
        # Check terminal size
        import shutil
        terminal_size = shutil.get_terminal_size()
        print(f"Terminal size: {terminal_size.columns}x{terminal_size.lines}")
        
        if terminal_size.columns >= 120 and terminal_size.lines >= 60:
            print("✓ Terminal size meets requirements")
            print()
            print("Starting MVC example application...")
            print("Press Ctrl+C to cancel startup")
            
            # Brief countdown
            for i in range(3, 0, -1):
                print(f"Starting in {i}...", end='\r')
                time.sleep(1)
            print("Starting now!     ")
            
            # Create model and controller
            model = FileManagerModel()
            controller = FileManagerController(model)
            
            # Run the application
            controller.run()
            
        else:
            print("✗ Terminal too small - need at least 120x60")
            print("Please resize your terminal and try again")
            
    except KeyboardInterrupt:
        print("\nStartup cancelled by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()