# Hayward Tech Suite - PyQt6 Migration

## Project Overview

Hayward Tech Suite is a comprehensive Windows system maintenance tool. This project is currently undergoing a major framework migration from CustomTkinter to PyQt6 to provide better performance, modern UI capabilities, and enhanced Windows 11 integration.

## Current Status

### ✅ Completed Components

#### Phase 1: Infrastructure (100%)
- **Application Entry**: Migrated to QApplication with proper initialization
- **Main Window**: Completely rewritten as QMainWindow with QTabWidget
- **Theme System**: Created QSS-based theming with hot-reload support
  - `hacker_dark.qss` - Matrix-inspired green-on-black theme
  - `hacker_light.qss` - Light variant with green accents
- **Theme Manager**: Dynamic theme loading and application
- **High DPI Support**: Enabled for 4K displays
- **Custom Widgets**: TerminalOutputWidget with typewriter effect

#### Phase 2: Tab Migration (12.5% - 1/8 tabs)
- **Monitoring Tab** ✅ - Fully migrated with signal/slot pattern
  - Real-time CPU, RAM, Disk, Battery, Network monitoring
  - Thread-safe updates using PyQt6 signals
  - QGroupBox-based layout for clean sectioning
  - Start/Stop monitoring controls

### 🔄 In Progress

#### Phase 2: Tab Migration (87.5% remaining)
- [ ] Diagnostics Tab (Network tools: ping, traceroute, speedtest)
- [ ] Maintenance Tab (Disk cleanup, SFC, DISM)
- [ ] Security Tab (Vulnerability scanning, risk scoring)
- [ ] Registry Hacks Tab (Registry tweaks with red accent theme)
- [ ] Debloat Tab (Bloatware removal with category filtering)
- [ ] System Tools Tab (Install system utilities)
- [ ] Settings Tab (Configuration management)

### 📋 Planned

#### Phase 3: Advanced Features
- System tray integration with live monitoring
- Global keyboard shortcuts
- Export to PDF/HTML
- QUndoStack for registry operations

#### Phase 4: Build & Deployment
- PyInstaller build configuration
- Single EXE creation
- Performance optimization
- Windows 11 compatibility testing

## Why PyQt6?

### Benefits Over CustomTkinter

1. **Performance**: Native Qt rendering is significantly faster
2. **Professional UI**: More polished, Windows-native appearance
3. **Advanced Features**: Built-in support for:
   - System tray integration
   - Rich text formatting
   - Complex layouts
   - Animations
   - High DPI scaling
4. **Better Threading**: Signal/slot mechanism for thread-safe GUI updates
5. **Styling**: Powerful QSS (CSS-like) styling system
6. **Maintainability**: Larger community, better documentation

### Technical Improvements

- **Threading Model**: Replaced `parent.after(0, callback)` with PyQt6 signals/slots
- **Layout System**: More flexible QLayout managers vs CustomTkinter's grid
- **Memory Management**: Qt's parent-child ownership model prevents memory leaks
- **Native Integration**: Better Windows API integration

## Architecture

### Application Structure
```
src/
├── main.py              # QApplication entry point
├── gui/
│   ├── main_window.py   # QMainWindow with QTabWidget
│   ├── styles/          # QSS stylesheets and theme manager
│   │   ├── hacker_dark.qss
│   │   ├── hacker_light.qss
│   │   └── theme_manager.py
│   ├── widgets/         # Custom PyQt6 widgets
│   │   ├── terminal_output.py
│   │   └── ...
│   └── tabs/            # Tab implementations
│       ├── monitoring_tab_pyqt6.py  ✅ MIGRATED
│       └── ...
├── core/                # Business logic (UNCHANGED)
└── utils/               # Utilities (UNCHANGED)
```

### Migration Pattern

Each tab follows this pattern:

```python
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal

class MyTab(QWidget):
    # Signals for thread-safe updates
    data_updated = pyqtSignal(dict)
    
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window
        
        # Create UI
        self._create_ui()
        
        # Connect signals
        self.data_updated.connect(self._update_display)
    
    def _create_ui(self):
        # Build UI using QLayouts
        layout = QVBoxLayout(self)
        # ...
    
    def _update_display(self, data):
        # Thread-safe GUI update
        self.label.setText(str(data))
```

## Theme System

### Available Themes

1. **hacker_dark** (default)
   - Matrix-inspired green on black
   - Ideal for the "hacker" aesthetic
   - Easy on the eyes in dark environments

2. **hacker_light**
   - Green-tinted light theme
   - Better for bright environments
   - Maintains the tech aesthetic

### Switching Themes

```python
from src.gui.styles.theme_manager import get_theme_manager

theme_manager = get_theme_manager()
theme_manager.apply_theme("hacker_dark")
```

### Customizing Styles

QSS files support CSS-like syntax:

```css
QPushButton {
    background-color: #1a1a1a;
    color: #00ff00;
    border: 2px solid #00ff00;
    border-radius: 4px;
    padding: 8px 16px;
}

QPushButton:hover {
    background-color: #2a2a2a;
    border: 2px solid #00ffff;
}
```

## Development

### Requirements

```bash
pip install PyQt6>=6.6.0
pip install psutil>=5.9.8
# See requirements.txt for full list
```

### Running the Application

```bash
python src/main.py
```

### Testing (Local Windows Environment Required)

Since PyQt6 requires GUI libraries, testing must be done on Windows:

```bash
# On Windows with display
python src/main.py
```

### Code Quality

```bash
# Format code
black src/

# Lint
pylint src/

# Type checking
mypy src/
```

## Migration Progress Tracking

### Metrics
- **Lines of Code**: ~6,000 GUI lines to migrate
- **Tabs Completed**: 1/8 (12.5%)
- **Overall Progress**: ~15% (including infrastructure)

### Commits
Track migration progress with:
```bash
git log --oneline --grep="Phase"
```

## Documentation

- **Migration Guide**: `docs/PYQT6_MIGRATION_GUIDE.md` - Detailed migration patterns
- **API Docs**: (To be generated with Sphinx)
- **User Guide**: (To be updated after migration complete)

## Known Issues

1. **CI Environment**: PyQt6 GUI cannot run in headless CI (expected)
2. **Performance Profiling**: Placeholder in Monitoring tab (to be completed)
3. **Registry Tab**: Special red styling needs testing

## Contributing to Migration

If continuing this migration:

1. Read `docs/PYQT6_MIGRATION_GUIDE.md`
2. Follow the established signal/slot pattern
3. Use QLayouts instead of grid system
4. Test on Windows environment
5. Update this README with progress

## Future Enhancements

### Planned Features
- [ ] Draggable/resizable monitoring widgets
- [ ] Command palette (Ctrl+P) for quick actions
- [ ] Activity log viewer
- [ ] Plugin system for extensibility
- [ ] Animated transitions between tabs
- [ ] Custom window frame (frameless with custom title bar)

### Build System
- [ ] PyInstaller spec file with QSS bundling
- [ ] Auto-updater integration
- [ ] Portable vs installed mode detection
- [ ] Digital signature for EXE

## Support

For issues or questions:
- Check `docs/PYQT6_MIGRATION_GUIDE.md`
- Review completed Monitoring Tab implementation
- Reference PyQt6 documentation

## License

[Existing license remains unchanged]

---

**Migration Start Date**: 2026-02-09  
**Last Updated**: 2026-02-09  
**Current Phase**: 2 - Tab Migration  
**Target Completion**: TBD
