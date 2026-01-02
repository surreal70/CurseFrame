# MVC Patterns and Best Practices

## Overview

This guide demonstrates common Model-View-Controller patterns and best practices when using the Curses UI Framework. The MVC architecture provides clean separation of concerns, making applications more maintainable, testable, and extensible.

## Table of Contents

- [MVC Fundamentals](#mvc-fundamentals)
- [Model Patterns](#model-patterns)
- [View Patterns](#view-patterns)
- [Controller Patterns](#controller-patterns)
- [Communication Patterns](#communication-patterns)
- [Common Use Cases](#common-use-cases)
- [Testing Strategies](#testing-strategies)

## MVC Fundamentals

### Core Principles

1. **Model**: Manages data and business logic
2. **View**: Handles presentation and user interface
3. **Controller**: Coordinates between Model and View

### Data Flow

```
User Input → Controller → Model → Controller → View → Display
```

### Separation Rules

- **Model** should never directly update the View
- **View** should never contain business logic
- **Controller** should not store application state

## Model Patterns

### Basic Model Extension

```python
class TaskManagerModel(ApplicationModel):
    """Model for a task management application"""
    
    def __init__(self):
        super().__init__("Task Manager", "Developer", "1.0")
        self._tasks = []
        self._completed_tasks = []
        self._current_filter = "all"
    
    def add_task(self, description: str, priority: str = "normal") -> bool:
        """Add a new task (business logic)"""
        if not description.strip():
            return False
        
        task = {
            'id': len(self._tasks) + 1,
            'description': description.strip(),
            'priority': priority,
            'created': datetime.now(),
            'completed': False
        }
        
        self._tasks.append(task)
        self._update_display_content()
        return True
    
    def complete_task(self, task_id: int) -> bool:
        """Mark task as completed"""
        for task in self._tasks:
            if task['id'] == task_id and not task['completed']:
                task['completed'] = True
                self._completed_tasks.append(task)
                self._update_display_content()
                return True
        return False
    
    def get_filtered_tasks(self) -> List[dict]:
        """Get tasks based on current filter"""
        if self._current_filter == "completed":
            return [t for t in self._tasks if t['completed']]
        elif self._current_filter == "pending":
            return [t for t in self._tasks if not t['completed']]
        else:
            return self._tasks
    
    def set_filter(self, filter_type: str) -> None:
        """Change task filter"""
        if filter_type in ["all", "pending", "completed"]:
            self._current_filter = filter_type
            self._update_display_content()
    
    def _update_display_content(self) -> None:
        """Update main content based on current state"""
        tasks = self.get_filtered_tasks()
        
        content = f"📋 TASK MANAGER ({self._current_filter.upper()})\n\n"
        
        if not tasks:
            content += "No tasks found.\n"
        else:
            for task in tasks:
                status = "✅" if task['completed'] else "⏳"
                priority = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(
                    task['priority'], "🟡"
                )
                content += f"{status} {priority} [{task['id']}] {task['description']}\n"
        
        content += f"\nTotal tasks: {len(self._tasks)}"
        content += f"\nCompleted: {len(self._completed_tasks)}"
        content += f"\nPending: {len(self._tasks) - len(self._completed_tasks)}"
        
        self.set_main_content(content)
```

### Data Validation Pattern

```python
class UserModel(ApplicationModel):
    """Model with data validation"""
    
    def __init__(self):
        super().__init__("User Manager", "Framework", "1.0")
        self._users = {}
        self._validation_errors = []
    
    def add_user(self, username: str, email: str, age: int) -> bool:
        """Add user with validation"""
        self._validation_errors.clear()
        
        # Validate input
        if not self._validate_username(username):
            return False
        if not self._validate_email(email):
            return False
        if not self._validate_age(age):
            return False
        
        # Add user if validation passes
        self._users[username] = {
            'email': email,
            'age': age,
            'created': datetime.now()
        }
        
        self._update_user_display()
        return True
    
    def _validate_username(self, username: str) -> bool:
        """Validate username"""
        if not username or len(username) < 3:
            self._validation_errors.append("Username must be at least 3 characters")
            return False
        if username in self._users:
            self._validation_errors.append("Username already exists")
            return False
        return True
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            self._validation_errors.append("Invalid email format")
            return False
        return True
    
    def _validate_age(self, age: int) -> bool:
        """Validate age"""
        if not isinstance(age, int) or age < 0 or age > 150:
            self._validation_errors.append("Age must be between 0 and 150")
            return False
        return True
    
    def get_validation_errors(self) -> List[str]:
        """Get current validation errors"""
        return self._validation_errors.copy()
```

### State Management Pattern

```python
class GameModel(ApplicationModel):
    """Model with complex state management"""
    
    def __init__(self):
        super().__init__("Game Manager", "Framework", "1.0")
        self._game_state = "menu"  # menu, playing, paused, game_over
        self._score = 0
        self._level = 1
        self._lives = 3
        self._state_history = []
    
    def change_state(self, new_state: str) -> bool:
        """Change game state with validation"""
        valid_transitions = {
            "menu": ["playing"],
            "playing": ["paused", "game_over"],
            "paused": ["playing", "menu"],
            "game_over": ["menu"]
        }
        
        if new_state in valid_transitions.get(self._game_state, []):
            self._state_history.append(self._game_state)
            self._game_state = new_state
            self._update_game_display()
            return True
        return False
    
    def update_score(self, points: int) -> None:
        """Update score and check for level up"""
        self._score += points
        
        # Level up every 1000 points
        new_level = (self._score // 1000) + 1
        if new_level > self._level:
            self._level = new_level
            self.set_status(f"Level up! Now at level {self._level}")
        
        self._update_game_display()
    
    def lose_life(self) -> bool:
        """Lose a life, return True if game over"""
        self._lives -= 1
        if self._lives <= 0:
            self.change_state("game_over")
            return True
        return False
    
    def reset_game(self) -> None:
        """Reset game to initial state"""
        self._score = 0
        self._level = 1
        self._lives = 3
        self._game_state = "menu"
        self._state_history.clear()
        self._update_game_display()
```

## View Patterns

### Custom View Components

```python
class DashboardView(WindowView):
    """Extended view with custom rendering"""
    
    def render_dashboard(self, model: ApplicationModel) -> None:
        """Render a custom dashboard layout"""
        # Get statistics from model
        stats = model.get_statistics()
        
        # Create dashboard content
        dashboard_content = self._create_dashboard_content(stats)
        
        # Update main window with dashboard
        self.update_main_content(dashboard_content)
    
    def _create_dashboard_content(self, stats: dict) -> str:
        """Create formatted dashboard content"""
        content = "📊 APPLICATION DASHBOARD\n"
        content += "=" * 40 + "\n\n"
        
        # System info section
        content += "🖥️  SYSTEM INFO:\n"
        content += f"   Uptime: {stats.get('uptime', 0)} seconds\n"
        content += f"   Commands: {stats.get('total_commands', 0)}\n"
        content += f"   Content Lines: {stats.get('content_lines', 0)}\n\n"
        
        # Activity section
        content += "📈 ACTIVITY:\n"
        content += f"   Last Command: {stats.get('last_command', 'None')}\n"
        content += f"   Session Start: {stats.get('session_start', 'Unknown')}\n\n"
        
        # Progress bars for visual appeal
        uptime = stats.get('uptime', 0)
        uptime_bar = self._create_progress_bar(min(uptime, 300), 300, 20)
        content += f"   Uptime Progress: [{uptime_bar}]\n"
        
        return content
    
    def _create_progress_bar(self, current: int, maximum: int, width: int) -> str:
        """Create a text-based progress bar"""
        if maximum == 0:
            return "░" * width
        
        filled = int((current / maximum) * width)
        return "█" * filled + "░" * (width - filled)
    
    def render_status_with_indicators(self, status: str, indicators: dict) -> None:
        """Render status with visual indicators"""
        # Add indicators to status
        indicator_text = ""
        for key, value in indicators.items():
            if key == "connection":
                indicator_text += "🟢" if value else "🔴"
            elif key == "processing":
                indicator_text += "⚡" if value else "⏸️"
            elif key == "errors":
                indicator_text += "⚠️" if value > 0 else "✅"
        
        full_status = f"{status} {indicator_text}"
        
        # Update bottom window with enhanced status
        self.set_bottom_window_statistics({
            'status': full_status,
            'indicators': indicators
        })
```

### Responsive Layout Pattern

```python
class ResponsiveView(WindowView):
    """View that adapts to different terminal sizes"""
    
    def render_all(self, model: ApplicationModel) -> None:
        """Render with responsive layout"""
        # Get terminal dimensions
        if self.layout_info:
            width = self.layout_info.terminal_width
            height = self.layout_info.terminal_height
            
            # Adapt content based on size
            if width < 100:
                self._render_compact_layout(model)
            elif width < 140:
                self._render_standard_layout(model)
            else:
                self._render_expanded_layout(model)
        else:
            super().render_all(model)
    
    def _render_compact_layout(self, model: ApplicationModel) -> None:
        """Render for small terminals"""
        # Simplified content for small screens
        content = model.get_main_content()
        
        # Truncate long lines
        lines = content.split('\n')
        truncated_lines = []
        for line in lines:
            if len(line) > 60:
                truncated_lines.append(line[:57] + "...")
            else:
                truncated_lines.append(line)
        
        compact_content = '\n'.join(truncated_lines)
        self.update_main_content(compact_content)
        
        # Simplified navigation
        nav_items = model.get_navigation_items()
        if len(nav_items) > 5:
            # Show only first 5 items with "More..." indicator
            compact_nav = nav_items[:4] + ["More..."]
            model.set_navigation_items(compact_nav)
    
    def _render_expanded_layout(self, model: ApplicationModel) -> None:
        """Render for large terminals"""
        # Enhanced content for large screens
        content = model.get_main_content()
        
        # Add visual enhancements
        enhanced_content = self._add_visual_enhancements(content)
        self.update_main_content(enhanced_content)
    
    def _add_visual_enhancements(self, content: str) -> str:
        """Add visual enhancements for large screens"""
        # Add borders and spacing
        lines = content.split('\n')
        enhanced_lines = []
        
        for line in lines:
            if line.startswith('#'):
                # Header styling
                enhanced_lines.append("=" * 60)
                enhanced_lines.append(f"  {line}")
                enhanced_lines.append("=" * 60)
            elif line.startswith('*'):
                # Bullet point styling
                enhanced_lines.append(f"  • {line[1:].strip()}")
            else:
                enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
```

## Controller Patterns

### Command Processing Pattern

```python
class AdvancedController(CursesController):
    """Controller with advanced command processing"""
    
    def __init__(self, model: ApplicationModel):
        super().__init__(model)
        self._command_handlers = {
            'add': self._handle_add_command,
            'delete': self._handle_delete_command,
            'edit': self._handle_edit_command,
            'search': self._handle_search_command,
            'export': self._handle_export_command,
            'import': self._handle_import_command,
        }
        self._command_history_index = -1
    
    def _execute_command(self, command: str) -> None:
        """Enhanced command execution with validation"""
        # Parse command
        parts = command.strip().split()
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Check for custom handlers
        if cmd in self._command_handlers:
            try:
                result = self._command_handlers[cmd](args)
                if result:
                    self.set_status(f"Command '{cmd}' executed successfully")
                else:
                    self.set_status(f"Command '{cmd}' failed")
            except Exception as e:
                self.set_status(f"Error executing '{cmd}': {str(e)}")
        else:
            # Fall back to parent implementation
            super()._execute_command(command)
    
    def _handle_add_command(self, args: List[str]) -> bool:
        """Handle add command"""
        if not args:
            self.set_status("Usage: add <item>")
            return False
        
        item = " ".join(args)
        # Delegate to model for business logic
        return self.model.add_item(item)
    
    def _handle_search_command(self, args: List[str]) -> bool:
        """Handle search command"""
        if not args:
            self.set_status("Usage: search <term>")
            return False
        
        search_term = " ".join(args)
        results = self.model.search(search_term)
        
        if results:
            content = f"Search results for '{search_term}':\n\n"
            for i, result in enumerate(results, 1):
                content += f"{i}. {result}\n"
            self.update_main_content(content)
            return True
        else:
            self.set_status(f"No results found for '{search_term}'")
            return False
    
    def handle_input(self, key: int) -> bool:
        """Enhanced input handling"""
        # Handle command history navigation
        if self.model.get_bottom_window_mode() == "input":
            if key == curses.KEY_UP:
                self._navigate_command_history(-1)
                return True
            elif key == curses.KEY_DOWN:
                self._navigate_command_history(1)
                return True
        
        # Call parent implementation
        return super().handle_input(key)
    
    def _navigate_command_history(self, direction: int) -> None:
        """Navigate through command history"""
        history = self.model.get_command_history()
        if not history:
            return
        
        self._command_history_index += direction
        
        # Clamp to valid range
        if self._command_history_index < 0:
            self._command_history_index = 0
        elif self._command_history_index >= len(history):
            self._command_history_index = len(history) - 1
        
        # Set command input to historical command
        if 0 <= self._command_history_index < len(history):
            historical_command = history[self._command_history_index]
            self.model.set_command_input(historical_command)
```

### State Machine Pattern

```python
class StateMachineController(CursesController):
    """Controller implementing state machine pattern"""
    
    def __init__(self, model: ApplicationModel):
        super().__init__(model)
        self._state = "idle"
        self._state_handlers = {
            "idle": self._handle_idle_state,
            "editing": self._handle_editing_state,
            "searching": self._handle_searching_state,
            "confirming": self._handle_confirming_state,
        }
        self._pending_action = None
    
    def handle_input(self, key: int) -> bool:
        """Handle input based on current state"""
        # Get current state handler
        handler = self._state_handlers.get(self._state)
        if handler:
            # Let state handler process input
            if handler(key):
                return True
        
        # Fall back to parent implementation
        return super().handle_input(key)
    
    def _handle_idle_state(self, key: int) -> bool:
        """Handle input in idle state"""
        if key == ord('e'):
            self._transition_to_state("editing")
            return True
        elif key == ord('s'):
            self._transition_to_state("searching")
            return True
        elif key == ord('d'):
            self._pending_action = "delete"
            self._transition_to_state("confirming")
            return True
        return False
    
    def _handle_editing_state(self, key: int) -> bool:
        """Handle input in editing state"""
        if key == 27:  # ESC
            self._transition_to_state("idle")
            return True
        elif key == ord('\n'):
            self._save_changes()
            self._transition_to_state("idle")
            return True
        # Handle other editing keys...
        return False
    
    def _handle_confirming_state(self, key: int) -> bool:
        """Handle input in confirmation state"""
        if key == ord('y') or key == ord('Y'):
            self._execute_pending_action()
            self._transition_to_state("idle")
            return True
        elif key == ord('n') or key == ord('N') or key == 27:
            self._cancel_pending_action()
            self._transition_to_state("idle")
            return True
        return False
    
    def _transition_to_state(self, new_state: str) -> None:
        """Transition to new state"""
        old_state = self._state
        self._state = new_state
        
        # Update UI based on state
        if new_state == "editing":
            self.set_status("EDITING MODE - Press ESC to cancel, Enter to save")
            self.model.set_bottom_window_mode("input")
        elif new_state == "confirming":
            action = self._pending_action or "action"
            self.set_status(f"Confirm {action}? (y/n)")
        else:
            self.set_status("Ready")
            self.model.set_bottom_window_mode("display")
```

## Communication Patterns

### Observer Pattern

```python
class ObservableModel(ApplicationModel):
    """Model with observer pattern for change notifications"""
    
    def __init__(self, title: str, author: str, version: str):
        super().__init__(title, author, version)
        self._observers = []
    
    def add_observer(self, observer) -> None:
        """Add an observer"""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def remove_observer(self, observer) -> None:
        """Remove an observer"""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify_observers(self, event: str, data: any = None) -> None:
        """Notify all observers of a change"""
        for observer in self._observers:
            if hasattr(observer, 'on_model_change'):
                observer.on_model_change(event, data)
    
    def set_main_content(self, content: str) -> None:
        """Override to notify observers"""
        super().set_main_content(content)
        self.notify_observers('content_changed', content)
    
    def set_status(self, status: str) -> None:
        """Override to notify observers"""
        super().set_status(status)
        self.notify_observers('status_changed', status)

class ObserverController(CursesController):
    """Controller that observes model changes"""
    
    def __init__(self, model: ObservableModel):
        super().__init__(model)
        model.add_observer(self)
    
    def on_model_change(self, event: str, data: any) -> None:
        """Handle model change notifications"""
        if event == 'content_changed':
            # Update view immediately when content changes
            if self.view:
                self.view.mark_window_dirty('main')
        elif event == 'status_changed':
            # Update status display
            if self.view:
                self.view.mark_window_dirty('bottom')
```

### Event System Pattern

```python
class EventDrivenModel(ApplicationModel):
    """Model with event system"""
    
    def __init__(self, title: str, author: str, version: str):
        super().__init__(title, author, version)
        self._event_handlers = {}
    
    def on(self, event: str, handler) -> None:
        """Register event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)
    
    def emit(self, event: str, *args, **kwargs) -> None:
        """Emit an event"""
        handlers = self._event_handlers.get(event, [])
        for handler in handlers:
            try:
                handler(*args, **kwargs)
            except Exception as e:
                # Log error but don't stop other handlers
                print(f"Error in event handler: {e}")
    
    def add_item(self, item: str) -> bool:
        """Add item and emit event"""
        # Business logic
        success = self._do_add_item(item)
        
        if success:
            self.emit('item_added', item)
        else:
            self.emit('item_add_failed', item)
        
        return success

class EventDrivenController(CursesController):
    """Controller with event handling"""
    
    def __init__(self, model: EventDrivenModel):
        super().__init__(model)
        
        # Register for model events
        model.on('item_added', self._on_item_added)
        model.on('item_add_failed', self._on_item_add_failed)
    
    def _on_item_added(self, item: str) -> None:
        """Handle item added event"""
        self.set_status(f"Added: {item}")
        # Refresh display
        self._refresh_item_list()
    
    def _on_item_add_failed(self, item: str) -> None:
        """Handle item add failed event"""
        self.set_status(f"Failed to add: {item}")
```

## Common Use Cases

### File Manager Application

```python
class FileManagerModel(ApplicationModel):
    def __init__(self):
        super().__init__("File Manager", "Framework", "1.0")
        self.current_path = os.getcwd()
        self.selected_files = []
    
    def navigate_to(self, path: str) -> bool:
        """Navigate to directory"""
        try:
            if os.path.isdir(path):
                self.current_path = os.path.abspath(path)
                self._update_file_list()
                return True
        except PermissionError:
            pass
        return False
    
    def _update_file_list(self) -> None:
        """Update file listing display"""
        try:
            items = os.listdir(self.current_path)
            content = f"📁 {self.current_path}\n\n"
            
            # Separate directories and files
            dirs = [item for item in items if os.path.isdir(os.path.join(self.current_path, item))]
            files = [item for item in items if os.path.isfile(os.path.join(self.current_path, item))]
            
            # Display directories first
            for directory in sorted(dirs):
                content += f"📂 {directory}/\n"
            
            # Then files
            for file in sorted(files):
                content += f"📄 {file}\n"
            
            self.set_main_content(content)
        except PermissionError:
            self.set_main_content("❌ Permission denied")

class FileManagerController(CursesController):
    def _execute_command(self, command: str) -> None:
        parts = command.split()
        cmd = parts[0].lower() if parts else ""
        
        if cmd == "cd":
            path = parts[1] if len(parts) > 1 else os.path.expanduser("~")
            if self.model.navigate_to(path):
                self.set_status(f"Changed to: {path}")
            else:
                self.set_status(f"Cannot access: {path}")
        else:
            super()._execute_command(command)
```

### Data Dashboard Application

```python
class DashboardModel(ApplicationModel):
    def __init__(self):
        super().__init__("Data Dashboard", "Framework", "1.0")
        self.metrics = {}
        self.alerts = []
        self._start_data_collection()
    
    def _start_data_collection(self) -> None:
        """Start background data collection"""
        import threading
        self.running = True
        thread = threading.Thread(target=self._collect_metrics, daemon=True)
        thread.start()
    
    def _collect_metrics(self) -> None:
        """Collect metrics in background"""
        import random
        import time
        
        while self.running:
            # Simulate metric collection
            self.metrics.update({
                'cpu_usage': random.randint(10, 90),
                'memory_usage': random.randint(30, 80),
                'disk_usage': random.randint(20, 95),
                'network_io': random.randint(0, 100)
            })
            
            # Check for alerts
            if self.metrics['cpu_usage'] > 80:
                self.alerts.append(f"High CPU usage: {self.metrics['cpu_usage']}%")
            
            self._update_dashboard()
            time.sleep(2)
    
    def _update_dashboard(self) -> None:
        """Update dashboard display"""
        content = "📊 SYSTEM DASHBOARD\n\n"
        
        for metric, value in self.metrics.items():
            bar = self._create_bar(value, 100, 20)
            content += f"{metric.replace('_', ' ').title()}: [{bar}] {value}%\n"
        
        if self.alerts:
            content += "\n🚨 ALERTS:\n"
            for alert in self.alerts[-5:]:  # Show last 5 alerts
                content += f"  • {alert}\n"
        
        self.set_main_content(content)
    
    def _create_bar(self, value: int, max_value: int, width: int) -> str:
        """Create progress bar"""
        filled = int((value / max_value) * width)
        return "█" * filled + "░" * (width - filled)
```

## Testing Strategies

### Model Testing

```python
import unittest
from unittest.mock import Mock, patch

class TestTaskManagerModel(unittest.TestCase):
    def setUp(self):
        self.model = TaskManagerModel()
    
    def test_add_task_success(self):
        """Test successful task addition"""
        result = self.model.add_task("Test task", "high")
        self.assertTrue(result)
        self.assertEqual(len(self.model._tasks), 1)
        self.assertEqual(self.model._tasks[0]['description'], "Test task")
    
    def test_add_task_empty_description(self):
        """Test task addition with empty description"""
        result = self.model.add_task("", "normal")
        self.assertFalse(result)
        self.assertEqual(len(self.model._tasks), 0)
    
    def test_complete_task(self):
        """Test task completion"""
        self.model.add_task("Test task", "normal")
        task_id = self.model._tasks[0]['id']
        
        result = self.model.complete_task(task_id)
        self.assertTrue(result)
        self.assertTrue(self.model._tasks[0]['completed'])
    
    def test_filter_tasks(self):
        """Test task filtering"""
        self.model.add_task("Task 1", "normal")
        self.model.add_task("Task 2", "high")
        self.model.complete_task(1)
        
        # Test different filters
        self.model.set_filter("all")
        self.assertEqual(len(self.model.get_filtered_tasks()), 2)
        
        self.model.set_filter("completed")
        self.assertEqual(len(self.model.get_filtered_tasks()), 1)
        
        self.model.set_filter("pending")
        self.assertEqual(len(self.model.get_filtered_tasks()), 1)
```

### Controller Testing

```python
class TestTaskManagerController(unittest.TestCase):
    def setUp(self):
        self.model = TaskManagerModel()
        self.controller = TaskManagerController(self.model)
        self.controller.view = Mock()  # Mock the view
    
    def test_add_command(self):
        """Test add command execution"""
        self.controller._execute_command("add Test task")
        
        # Verify task was added to model
        self.assertEqual(len(self.model._tasks), 1)
        self.assertEqual(self.model._tasks[0]['description'], "Test task")
        
        # Verify view was updated
        self.controller.view.update_main_content.assert_called()
    
    def test_complete_command(self):
        """Test complete command execution"""
        # Add a task first
        self.model.add_task("Test task", "normal")
        task_id = self.model._tasks[0]['id']
        
        # Execute complete command
        self.controller._execute_command(f"complete {task_id}")
        
        # Verify task was completed
        self.assertTrue(self.model._tasks[0]['completed'])
    
    @patch('curses.getch')
    def test_navigation_input(self, mock_getch):
        """Test navigation input handling"""
        # Set up navigation items
        self.model.set_navigation_items(["Item 1", "Item 2", "Item 3"])
        
        # Simulate down arrow key
        result = self.controller.handle_input(curses.KEY_DOWN)
        
        self.assertTrue(result)
        self.assertEqual(self.model.get_selected_navigation_index(), 1)
```

### Integration Testing

```python
class TestMVCIntegration(unittest.TestCase):
    def setUp(self):
        self.model = TaskManagerModel()
        self.controller = TaskManagerController(self.model)
        # Use real view for integration testing
        self.mock_stdscr = Mock()
        self.controller.view = WindowView(self.mock_stdscr)
    
    def test_full_workflow(self):
        """Test complete MVC workflow"""
        # Add task through controller
        self.controller._execute_command("add Integration test task")
        
        # Verify model state
        self.assertEqual(len(self.model._tasks), 1)
        
        # Verify content was updated
        content = self.model.get_main_content()
        self.assertIn("Integration test task", content)
        
        # Complete task
        task_id = self.model._tasks[0]['id']
        self.controller._execute_command(f"complete {task_id}")
        
        # Verify completion
        self.assertTrue(self.model._tasks[0]['completed'])
        
        # Verify updated content
        updated_content = self.model.get_main_content()
        self.assertIn("✅", updated_content)
```

## Best Practices Summary

### Model Best Practices
1. Keep all business logic in the Model
2. Use validation methods for data integrity
3. Implement proper error handling
4. Use events/observers for change notifications
5. Separate data access from business logic

### View Best Practices
1. Only handle presentation logic
2. Use efficient rendering techniques
3. Implement responsive design patterns
4. Separate rendering from data processing
5. Use proper error display mechanisms

### Controller Best Practices
1. Keep controllers thin - delegate to Model
2. Implement proper input validation
3. Use command patterns for complex operations
4. Handle errors gracefully
5. Maintain clean separation from View

### Communication Best Practices
1. Use events for loose coupling
2. Implement observer patterns for notifications
3. Avoid direct Model-View communication
4. Use dependency injection for testability
5. Document interfaces clearly

This guide provides the foundation for building maintainable, testable applications using the MVC pattern with the Curses UI Framework.