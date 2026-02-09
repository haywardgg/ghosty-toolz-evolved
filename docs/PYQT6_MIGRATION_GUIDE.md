# CustomTkinter to PyQt6 Migration Guide

## Overview

This document provides guidance for completing the migration of Hayward Tech Suite from CustomTkinter to PyQt6.

## Migration Progress

### Completed ✅
- **Core Infrastructure**: QApplication, MainWindow, Theme System, QSS Stylesheets
- **Tab 1 - Monitoring**: Full migration with real-time updates using signals/slots

### In Progress 🔄
- **Tab 2-8**: Remaining tabs to be migrated

## Architecture Changes

### Application Entry Point (main.py)
**Before (CustomTkinter):**
```python
from src.gui.main_window import MainWindow
app = MainWindow()
app.mainloop()
```

**After (PyQt6):**
```python
from PyQt6.QtWidgets import QApplication
from src.gui.main_window import MainWindow
app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
sys.exit(app.exec())
```

### Main Window Structure
**Before (CustomTkinter):**
```python
class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.tabview = ctk.CTkTabview(self.main_container)
```

**After (PyQt6):**
```python
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tab_widget = QTabWidget()
        self.setCentralWidget(central_widget)
```

## Tab Migration Pattern

### 1. Class Declaration

**CustomTkinter:**
```python
class MyTab:
    def __init__(self, parent: ctk.CTkFrame, main_window=None):
        self.parent = parent
        self.main_window = main_window
```

**PyQt6:**
```python
class MyTab(QWidget):
    # Define signals for thread-safe updates
    data_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Connect signals
        self.data_updated.connect(self._update_display)
```

### 2. Widget Conversions

| CustomTkinter | PyQt6 | Notes |
|---------------|-------|-------|
| `ctk.CTkFrame` | `QGroupBox` or `QWidget` | Use QGroupBox for titled sections |
| `ctk.CTkLabel` | `QLabel` | |
| `ctk.CTkButton` | `QPushButton` | |
| `ctk.CTkEntry` | `QLineEdit` | |
| `ctk.CTkTextbox` | `QTextEdit` | |
| `ctk.CTkProgressBar` | `QProgressBar` | Use setMinimum(0), setMaximum(100) |
| `ctk.CTkComboBox` | `QComboBox` | |
| `ctk.CTkCheckBox` | `QCheckBox` | |
| `ctk.CTkRadioButton` | `QRadioButton` | |
| `ctk.CTkSwitch` | `QCheckBox` | Style differently in QSS |
| `ctk.CTkSlider` | `QSlider` | |
| `ctk.CTkOptionMenu` | `QComboBox` | |
| `ctk.CTkTabview` | `QTabWidget` | |

### 3. Layout Management

**CustomTkinter (Grid-based):**
```python
widget.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
parent.grid_rowconfigure(0, weight=1)
parent.grid_columnconfigure(0, weight=1)
```

**PyQt6 (Layout Managers):**
```python
# VBox Layout (vertical)
layout = QVBoxLayout(self)
layout.addWidget(widget)
layout.addStretch()  # For spacing

# HBox Layout (horizontal)
layout = QHBoxLayout()
layout.addWidget(widget)
layout.addSpacing(10)

# Grid Layout
grid = QGridLayout()
grid.addWidget(widget, row, col)
grid.setRowStretch(0, 1)
grid.setColumnStretch(0, 1)
```

### 4. Button Connections

**CustomTkinter:**
```python
button = ctk.CTkButton(parent, text="Click", command=self.on_click)
```

**PyQt6:**
```python
button = QPushButton("Click")
button.clicked.connect(self.on_click)
```

### 5. Text Updates

**CustomTkinter:**
```python
label.configure(text="New text")
button.configure(text="New text", state="disabled")
```

**PyQt6:**
```python
label.setText("New text")
button.setText("New text")
button.setEnabled(False)
```

### 6. Thread-Safe GUI Updates

**CustomTkinter:**
```python
def callback(data):
    def update_ui():
        self.label.configure(text=str(data))
    self.parent.after(0, update_ui)
```

**PyQt6 (Using Signals/Slots):**
```python
class MyTab(QWidget):
    data_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.data_updated.connect(self._update_display)
        
    def callback(self, data):
        # Emit signal (thread-safe)
        self.data_updated.emit(data)
    
    def _update_display(self, data):
        # Runs in GUI thread
        self.label.setText(str(data))
```

### 7. Message Boxes

**CustomTkinter:**
```python
from tkinter import messagebox
messagebox.showinfo("Title", "Message")
messagebox.showwarning("Title", "Warning")
messagebox.showerror("Title", "Error")
result = messagebox.askyesno("Title", "Question?")
```

**PyQt6:**
```python
from PyQt6.QtWidgets import QMessageBox

QMessageBox.information(self, "Title", "Message")
QMessageBox.warning(self, "Title", "Warning")
QMessageBox.critical(self, "Title", "Error")

msg_box = QMessageBox()
msg_box.setWindowTitle("Title")
msg_box.setText("Question?")
msg_box.setStandardButtons(
    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
)
result = msg_box.exec()
if result == QMessageBox.StandardButton.Yes:
    # User clicked Yes
```

### 8. Timers and Scheduled Tasks

**CustomTkinter:**
```python
self.parent.after(1000, self.update_function)  # One-time after 1 second
self.parent.after(1000, self.periodic_update)  # Must be called repeatedly
```

**PyQt6:**
```python
from PyQt6.QtCore import QTimer

# One-time timer
QTimer.singleShot(1000, self.update_function)

# Periodic timer
self.timer = QTimer()
self.timer.timeout.connect(self.periodic_update)
self.timer.start(1000)  # Every 1 second

# Stop timer
self.timer.stop()
```

### 9. Progress Bars

**CustomTkinter:**
```python
progress = ctk.CTkProgressBar(parent)
progress.set(0.75)  # 75%
```

**PyQt6:**
```python
progress = QProgressBar()
progress.setMinimum(0)
progress.setMaximum(100)
progress.setValue(75)  # 75%
progress.setTextVisible(True)  # Show percentage
```

### 10. Text Boxes (Multiline)

**CustomTkinter:**
```python
textbox = ctk.CTkTextbox(parent)
textbox.insert("1.0", "Text content")
textbox.configure(state="disabled")  # Read-only
```

**PyQt6:**
```python
textbox = QTextEdit()
textbox.setPlainText("Text content")
textbox.setReadOnly(True)  # Read-only
```

## Tab-Specific Migration Notes

### Monitoring Tab ✅ (COMPLETED)
- **Pattern**: Signal/slot for thread-safe updates
- **Complexity**: Medium
- **Key Challenge**: MonitoringService callbacks needed signal emission
- **Lines**: 646 → 550 (simplified with PyQt6 layouts)

### Diagnostics Tab
- **Pattern**: Similar to Monitoring (network callbacks)
- **Complexity**: Medium
- **Key Features**: 
  - Ping/Traceroute output (use QTextEdit)
  - Speedtest integration
  - Common host dropdown (QComboBox)
- **Special Widgets**: Terminal-style output (already created)

### Maintenance Tab
- **Pattern**: Long-running operations with progress
- **Complexity**: Medium-High
- **Key Features**:
  - Disk cleanup
  - SFC/DISM commands
  - Temp file removal
- **Special Considerations**: Use QThread for long operations

### Security Tab
- **Pattern**: Risk indicators and scoring
- **Complexity**: Medium
- **Key Features**:
  - Vulnerability scanning
  - Color-coded risk levels
  - Fix All button
- **Special Widgets**: Risk indicator (to be created)

### Registry Hacks Tab ⚠️ **RED THEME**
- **Pattern**: Similar to Settings tab
- **Complexity**: Medium
- **Key Features**:
  - Registry tweak checkboxes
  - Apply/Restore buttons
  - Backup before changes
- **Special Styling**: Red accent colors in QSS
  ```css
  QPushButton#registry_button {
      border: 2px solid #8B0000;
      color: #ff4444;
  }
  ```

### Debloat Tab
- **Pattern**: Checkbox list with categories
- **Complexity**: High (lots of checkboxes)
- **Key Features**:
  - Category filtering (QComboBox)
  - Bulk selection
  - Safety level indicators
- **Special Considerations**: Use QScrollArea for checkbox list

### System Tools Tab
- **Pattern**: Installation progress tracking
- **Complexity**: Medium
- **Key Features**:
  - Tool list with status
  - Install buttons
  - Progress bars
- **Special Widgets**: Progress dialog (to be created)

### Settings Tab
- **Pattern**: Configuration editor
- **Complexity**: Low-Medium
- **Key Features**:
  - Theme switcher with preview
  - Monitoring intervals
  - Config editing
- **Special Features**: Live theme switching

## Testing Strategy

Since PyQt6 GUI cannot run in CI environment:

1. **Syntax Checking**: Ensure all Python files parse correctly
2. **Import Testing**: Verify all imports resolve
3. **Local Testing**: Test on Windows 11 environment
4. **Screenshots**: Capture UI for visual verification

## Common Pitfalls

### ❌ Don't Do This:
```python
# Directly updating GUI from background thread
def thread_function():
    self.label.setText("Update")  # WRONG - not thread-safe!
```

### ✅ Do This Instead:
```python
# Use signals for thread-safe updates
class MyTab(QWidget):
    update_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.update_signal.connect(self._update_label)
    
    def thread_function(self):
        self.update_signal.emit("Update")  # Thread-safe
    
    def _update_label(self, text):
        self.label.setText(text)  # Runs in GUI thread
```

## QSS Styling Tips

### Accessing Custom Styles
```python
# Set object name for QSS targeting
button.setObjectName("registry_button")
widget.setProperty("heading", True)

# In QSS:
# QPushButton#registry_button { ... }
# QLabel[heading="true"] { ... }
```

### Dynamic Theme Switching
```python
from src.gui.styles.theme_manager import get_theme_manager

theme_manager = get_theme_manager()
theme_manager.apply_theme("hacker_dark")
```

## Build Configuration (Future)

### PyInstaller Spec File
```python
# build.spec
a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/gui/styles/*.qss', 'src/gui/styles'),
        ('images/*', 'images'),
        ('config/*', 'config'),
    ],
    # ...
)
```

## Useful Resources

- PyQt6 Documentation: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- Qt Documentation: https://doc.qt.io/qt-6/
- Signal/Slot Guide: https://doc.qt.io/qt-6/signalsandslots.html
- QSS Reference: https://doc.qt.io/qt-6/stylesheet-reference.html

## Migration Checklist

For each tab to migrate:

- [ ] Create new file: `{tab_name}_pyqt6.py`
- [ ] Convert class to extend QWidget
- [ ] Add necessary signals for data updates
- [ ] Replace CustomTkinter widgets with PyQt6 equivalents
- [ ] Convert grid layout to QLayouts
- [ ] Update button connections (command → clicked.connect)
- [ ] Implement thread-safe updates with signals
- [ ] Test basic functionality locally
- [ ] Update MainWindow to import and use new tab
- [ ] Document any special considerations
- [ ] Commit changes with descriptive message

## Status Update Command
```bash
# See current migration status
git log --oneline --grep="Phase" -10
```

---

**Last Updated**: Session 2026-02-09  
**Completion**: Phase 1 ✅ | Phase 2: 1/8 tabs ✅ | Total: ~15% complete
