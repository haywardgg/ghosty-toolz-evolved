"""
Main window for Hayward Tech Suite.

Provides the main PyQt6 application window with tabbed interface for different functionality.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QCloseEvent
from typing import Optional
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config import get_config
from src.utils.resource_path import resource_path

logger = get_logger("main_window")
config = get_config()


class MainWindow(QMainWindow):
    """Main application window with tabbed interface."""
    
    # Signal for status bar updates
    status_updated = pyqtSignal(str)

    def __init__(self) -> None:
        """Initialize main window."""
        super().__init__()
        
        # Store tab references
        self.monitoring_tab = None
        self.diagnostics_tab = None
        self.maintenance_tab = None
        self.security_tab = None
        self.registry_hacks_tab = None
        self.debloat_tab = None
        self.system_tools_tab = None
        self.settings_tab = None

        # Window configuration
        app_name = config.get("app.name", "Hayward Tech Suite")
        app_version = config.get("app.version", "1.0.0")
        self.setWindowTitle(f"{app_name} v{app_version}")
        
        # Get window dimensions from config
        width = config.get("ui.window.width", 1200)
        height = config.get("ui.window.height", 800)
        self.resize(width, height)
        
        # Set minimum size
        min_width = config.get("ui.window.min_width", 1000)
        min_height = config.get("ui.window.min_height", 700)
        self.setMinimumSize(min_width, min_height)

        # Set icon if available
        icon_path = Path(resource_path("images/icon.ico"))
        if icon_path.exists():
            try:
                self.setWindowIcon(QIcon(str(icon_path)))
            except Exception as e:
                logger.warning(f"Could not set window icon: {e}")

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(5)

        # Create status bar first (tabs may need to access it during initialization)
        self._create_status_bar()

        # Create tab widget
        self._create_tabview()
        main_layout.addWidget(self.tab_widget)

        # Connect status signal
        self.status_updated.connect(self._update_status_label)

        logger.info("Main window initialized")

    def _create_tabview(self) -> None:
        """Create main tab widget with all tabs."""
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setMovable(False)
        self.tab_widget.setDocumentMode(False)
        
        # We'll add tabs as they are migrated
        # For now, create placeholder tabs to show the structure
        self._add_placeholder_tabs()
        
        logger.info("Tab widget created (with placeholders)")

    def _add_placeholder_tabs(self) -> None:
        """Add placeholder tabs until real tabs are migrated."""
        tab_names = [
            "Monitoring",
            "Diagnostics", 
            "Maintenance",
            "Security",
            "Registry Hacks",
            "Debloat Windows",
            "System Tools",
            "Settings"
        ]
        
        for tab_name in tab_names:
            try:
                # Create placeholder widget
                placeholder = QWidget()
                layout = QVBoxLayout(placeholder)
                
                label = QLabel(f"{tab_name} Tab")
                label.setProperty("heading", True)
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(label)
                
                info_label = QLabel(
                    f"The {tab_name} tab is being migrated to PyQt6.\n"
                    "This is a placeholder that will be replaced with the actual implementation."
                )
                info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                info_label.setWordWrap(True)
                layout.addWidget(info_label)
                
                layout.addStretch()
                
                # Add tab
                self.tab_widget.addTab(placeholder, tab_name)
                
                # Special styling for Registry Hacks tab (will be enhanced later)
                if tab_name == "Registry Hacks":
                    index = self.tab_widget.indexOf(placeholder)
                    # We'll apply special styling via QSS later
                    
                logger.info(f"Created placeholder for {tab_name} tab")
                
            except Exception as e:
                logger.error(f"Failed to create placeholder for {tab_name} tab: {e}")

    def _create_status_bar(self) -> None:
        """Create status bar at bottom."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Create status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label, 1)  # Stretch factor 1
        
        logger.debug("Status bar created")

    def update_status(self, message: str) -> None:
        """
        Update status bar message (thread-safe).

        Args:
            message: Status message to display
        """
        # Emit signal for thread-safe update
        self.status_updated.emit(message)
        logger.debug(f"Status updated: {message}")

    def _update_status_label(self, message: str) -> None:
        """
        Internal method to update status label (runs in GUI thread).
        
        Args:
            message: Status message to display
        """
        self.status_label.setText(message)

    def show_message(self, title: str, message: str, message_type: str = "info") -> None:
        """
        Show a message dialog.

        Args:
            title: Dialog title
            message: Message to display
            message_type: Type of message ('info', 'warning', 'error', 'question')
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if message_type == "info":
            msg_box.setIcon(QMessageBox.Icon.Information)
        elif message_type == "warning":
            msg_box.setIcon(QMessageBox.Icon.Warning)
        elif message_type == "error":
            msg_box.setIcon(QMessageBox.Icon.Critical)
        elif message_type == "question":
            msg_box.setIcon(QMessageBox.Icon.Question)
        else:
            msg_box.setIcon(QMessageBox.Icon.Information)
        
        msg_box.exec()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle window close event.
        
        Args:
            event: Close event
        """
        logger.info("Application closing")

        # Stop monitoring if active
        if self.monitoring_tab:
            try:
                if hasattr(self.monitoring_tab, 'stop_monitoring'):
                    self.monitoring_tab.stop_monitoring()
            except Exception as e:
                logger.error(f"Error stopping monitoring: {e}")

        # Accept the close event
        event.accept()
        logger.info("Close event accepted")


# Example usage for testing
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from src.utils.logger import get_logger
    from src.gui.styles.theme_manager import get_theme_manager

    logger = get_logger("main")
    logger.info("Starting Hayward Tech Suite (test mode)")

    # Create application
    app = QApplication(sys.argv)
    
    # Apply theme
    theme_manager = get_theme_manager()
    theme_manager.apply_theme("hacker_dark", app)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec())
