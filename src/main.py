"""
Main entry point for Hayward Tech Suite.

This module initializes the PyQt6 application and starts the main GUI.
"""

import sys
from pathlib import Path

# Add src to path if running from repository root
if __name__ == "__main__":
    root_dir = Path(__file__).parent.parent
    if root_dir not in sys.path:
        sys.path.insert(0, str(root_dir))

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from src.utils.logger import get_logger, Logger
from src.utils.config import get_config
from src.utils.admin_state import AdminState
from src.core.system_operations import SystemOperations
from src.gui.main_window import MainWindow
from src.gui.styles.theme_manager import get_theme_manager
from src.utils.resource_path import resource_path

logger = get_logger("main")


def setup_logging() -> None:
    """Set up application logging."""
    logger_instance = Logger()

    # Get configuration
    config = get_config()
    log_level = config.get("logging.level", "INFO")

    # Map string to logging level
    import logging

    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    level = level_map.get(log_level.upper(), logging.INFO)

    # Configure main logger
    main_logger = logger_instance.get_logger(
        "hayward_techsuite", log_file="hayward_techsuite.log", level=level
    )

    logger.info("Logging initialized")


def check_requirements() -> bool:
    """
    Check if all requirements are met.

    Returns:
        True if requirements are met
    """
    logger.info("Checking requirements...")

    # Check Python version
    if sys.version_info < (3, 8):
        logger.error(f"Python 3.8+ required, got {sys.version_info.major}.{sys.version_info.minor}")
        return False

    # Check platform
    if sys.platform != "win32":
        logger.error(f"Windows platform required, got {sys.platform}")
        return False

    logger.info("Requirements check passed")
    return True


def show_welcome_message() -> None:
    """Show welcome message in console."""
    config = get_config()
    app_name = config.get("app.name", "Hayward Tech Suite")
    app_version = config.get("app.version", "1.0.0")

    welcome_msg = f"""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║                  {app_name}                       ║
║                    Version {app_version}                          ║
║                                                           ║
║      Professional Windows System Maintenance Tool         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Starting application...
"""

    print(welcome_msg)
    logger.info(f"{app_name} v{app_version} starting")


def check_admin_privileges(app: QApplication) -> bool:
    """
    Check admin privileges and prompt user if not admin.
    
    Args:
        app: QApplication instance for showing dialogs
    
    Returns:
        True if app should continue, False if user wants to exit
    """
    is_admin = SystemOperations.is_admin()
    
    if is_admin:
        logger.info("Running with administrator privileges")
        AdminState.set_admin_mode(is_admin=True, declined=False)
        return True
    
    # Not admin - show dialog
    logger.warning("Not running as administrator")
    
    # Create message box
    msg_box = QMessageBox()
    msg_box.setWindowTitle("Administrator Privileges Required")
    msg_box.setIcon(QMessageBox.Icon.Warning)
    msg_box.setText("Administrator privileges are required for advanced features:")
    msg_box.setInformativeText(
        "• Some tweaks and maintenance operations require admin rights\n"
        "• Registry modifications need elevated permissions\n"
        "• System maintenance tools (SFC, DISM) require admin access\n\n"
        "Run without admin? (Limited functionality)"
    )
    msg_box.setStandardButtons(
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    msg_box.setDefaultButton(QMessageBox.StandardButton.No)
    
    # Make window stay on top
    msg_box.setWindowFlags(msg_box.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
    
    result = msg_box.exec()
    
    if result == QMessageBox.StandardButton.Yes:  # User chose YES - continue without admin
        logger.info("User chose to continue without admin privileges")
        AdminState.set_admin_mode(is_admin=False, declined=True)
        return True
    else:  # User chose NO - request elevation
        logger.info("User requested admin elevation")
        try:
            SystemOperations.request_admin_elevation()
            # If we reach here, elevation failed
            logger.error("Admin elevation failed or was cancelled")
            return False
        except Exception as e:
            logger.error(f"Failed to request admin elevation: {e}")
            return False


def main() -> int:
    """
    Main entry point for the PyQt6 application.

    Returns:
        Exit code (0 for success)
    """
    try:
        # Set up logging
        setup_logging()

        # Show welcome message
        show_welcome_message()

        # Check requirements
        if not check_requirements():
            logger.error("Requirements check failed")
            return 1

        # Create QApplication
        app = QApplication(sys.argv)
        app.setApplicationName("Hayward Tech Suite")
        app.setOrganizationName("Hayward")
        
        # Load configuration
        config = get_config()
        logger.info("Configuration loaded")
        
        # Set application metadata
        app_version = config.get("app.version", "1.0.0")
        app.setApplicationVersion(app_version)
        
        # Enable High DPI scaling
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Set application icon if available
        icon_path = Path(resource_path("images/icon.ico"))
        if icon_path.exists():
            try:
                app.setWindowIcon(QIcon(str(icon_path)))
                logger.info(f"Application icon set: {icon_path}")
            except Exception as e:
                logger.warning(f"Could not set application icon: {e}")
        
        # Load and apply theme
        theme_manager = get_theme_manager()
        theme_name = config.get("ui.theme", "hacker_dark")
        if theme_manager.apply_theme(theme_name, app):
            logger.info(f"Applied theme: {theme_name}")
        else:
            logger.warning(f"Failed to apply theme: {theme_name}, using default")

        # Check admin privileges
        if not check_admin_privileges(app):
            logger.info("Application startup cancelled by user")
            return 0

        # Create and show main window
        logger.info("Creating main window...")
        main_window = MainWindow()
        main_window.show()

        logger.info("Application started successfully")
        
        # Start event loop
        exit_code = app.exec()
        
        logger.info(f"Application closed normally with exit code: {exit_code}")
        return exit_code

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        return 0

    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
