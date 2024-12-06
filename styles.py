class DarkTheme:
    MAIN_STYLE = """
        * {
            font-family: 'Segoe UI', Arial;
        }
        QMainWindow, QWidget {
            background-color: #1a1a1a;
            color: #ffffff;
        }
        QDockWidget {
            border: 1px solid #2d2d2d;
        }
        QDockWidget::title {
            text-align: left;
            background: #2d2d2d;
            padding: 5px;
        }
        QDockWidget::close-button, QDockWidget::float-button {
            background: transparent;
        }
        QLabel {
            color: #ffffff;
            padding: 2px;
        }
        QPushButton {
            background-color: #2d2d2d;
            color: #ffffff;
            border: none;
            padding: 8px;
            border-radius: 4px;
            min-width: 100px;
        }
        QPushButton:hover {
            background-color: #3d3d3d;
        }
        QSlider {
            background: transparent;
        }
        QSlider::groove:horizontal {
            height: 4px;
            background: #3d3d3d;
            border-radius: 2px;
        }
        QSlider::handle:horizontal {
            background: #007acc;
            width: 16px;
            height: 16px;
            margin: -6px 0;
            border-radius: 8px;
        }
        QMenuBar {
            background-color: #1a1a1a;
            color: #ffffff;
            border-bottom: 1px solid #2d2d2d;
        }
        QMenuBar::item:selected {
            background-color: #2d2d2d;
        }
        QMenu {
            background-color: #1a1a1a;
            color: #ffffff;
            border: 1px solid #2d2d2d;
        }
        QMenu::item:selected {
            background-color: #2d2d2d;
        }
        QSpinBox, QDoubleSpinBox {
            background-color: #2d2d2d;
            color: #ffffff;
            border: none;
            padding: 4px;
            border-radius: 4px;
        }
        QComboBox {
            background-color: #2d2d2d;
            color: #ffffff;
            border: none;
            padding: 6px;
            border-radius: 4px;
        }
        QComboBox::drop-down {
            border: none;
        }
        QComboBox::down-arrow {
            width: 12px;
            height: 12px;
            background: #ffffff;
        }
    """