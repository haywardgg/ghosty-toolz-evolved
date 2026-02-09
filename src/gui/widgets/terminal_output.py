"""
Terminal-style output widget for Hayward Tech Suite.

Provides a hacker-themed terminal display with typewriter effect.
"""

from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QTextCursor
from src.utils.logger import get_logger

logger = get_logger("terminal_widget")


class TerminalOutputWidget(QTextEdit):
    """Terminal-style text output widget with hacker styling."""
    
    def __init__(self, parent=None):
        """Initialize terminal output widget."""
        super().__init__(parent)
        
        # Set object name for QSS styling
        self.setObjectName("terminal")
        
        # Configure as read-only
        self.setReadOnly(True)
        
        # Set monospace font
        font = QFont("Consolas", 10)
        if not font.exactMatch():
            font = QFont("Courier New", 10)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.setFont(font)
        
        # Configure text wrapping
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Typewriter effect support
        self._typewriter_enabled = False
        self._typewriter_text = ""
        self._typewriter_index = 0
        self._typewriter_timer = QTimer()
        self._typewriter_timer.timeout.connect(self._typewriter_step)
        
        logger.debug("Terminal output widget initialized")
    
    def append_text(self, text: str, typewriter: bool = False):
        """
        Append text to the terminal.
        
        Args:
            text: Text to append
            typewriter: If True, display text with typewriter effect
        """
        if typewriter and not self._typewriter_enabled:
            self._start_typewriter(text)
        else:
            self.append(text)
            # Auto-scroll to bottom
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)
    
    def clear_terminal(self):
        """Clear all terminal content."""
        self.clear()
        self._stop_typewriter()
    
    def _start_typewriter(self, text: str, speed: int = 10):
        """
        Start typewriter effect for text.
        
        Args:
            text: Text to display
            speed: Characters per timer tick
        """
        self._typewriter_text = text
        self._typewriter_index = 0
        self._typewriter_enabled = True
        self._typewriter_timer.start(speed)
    
    def _typewriter_step(self):
        """Display next character in typewriter effect."""
        if self._typewriter_index < len(self._typewriter_text):
            char = self._typewriter_text[self._typewriter_index]
            self.insertPlainText(char)
            self._typewriter_index += 1
            
            # Auto-scroll to bottom
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)
        else:
            self._stop_typewriter()
    
    def _stop_typewriter(self):
        """Stop typewriter effect."""
        self._typewriter_timer.stop()
        self._typewriter_enabled = False
        self._typewriter_text = ""
        self._typewriter_index = 0
    
    def set_typewriter_speed(self, speed: int):
        """
        Set typewriter effect speed.
        
        Args:
            speed: Milliseconds between characters
        """
        if self._typewriter_timer.isActive():
            self._typewriter_timer.setInterval(speed)
