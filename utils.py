import logging
from PyQt6.QtWidgets import QTextEdit, QVBoxLayout

class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
        """)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

def create_panel_layout():
    layout = QVBoxLayout()
    layout.setSpacing(5)
    layout.setContentsMargins(10, 10, 10, 10)
    return layout