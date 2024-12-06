from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction
from PyQt6.QtCore import pyqtSignal

class MenuBar(QMenuBar):
    """Ana menü barı"""
    
    # Sinyaller
    load_requested = pyqtSignal()
    save_requested = pyqtSignal()
    undo_requested = pyqtSignal()
    redo_requested = pyqtSignal()
    batch_process_requested = pyqtSignal()
    preferences_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_menus()
        
    def setup_menus(self):
        # Dosya Menüsü
        file_menu = self.create_file_menu()
        self.addMenu(file_menu)
        
        # Düzenle Menüsü
        edit_menu = self.create_edit_menu()
        self.addMenu(edit_menu)
        
        # Görünüm Menüsü
        self.view_menu = self.create_view_menu()
        self.addMenu(self.view_menu)
        
        # Araçlar Menüsü
        tools_menu = self.create_tools_menu()
        self.addMenu(tools_menu)
        
    def create_file_menu(self) -> QMenu:
        menu = QMenu("Dosya", self)
        
        actions = [
            ("Aç", "Ctrl+O", self.load_requested),
            ("Kaydet", "Ctrl+S", self.save_requested),
            ("Farklı Kaydet", "Ctrl+Shift+S", self.save_requested),
            None,  # Ayraç için None
            ("Toplu İşlem", "Ctrl+B", self.batch_process_requested),
            None,
            ("Çıkış", "Alt+F4", self.parent().close if self.parent() else None)
        ]
        
        for action_info in actions:
            if action_info is None:
                menu.addSeparator()
            else:
                text, shortcut, handler = action_info
                action = QAction(text, self)
                action.setShortcut(shortcut)
                if handler:
                    action.triggered.connect(handler.emit if hasattr(handler, 'emit') else handler)
                menu.addAction(action)
        
        return menu
        
    def create_edit_menu(self) -> QMenu:
        menu = QMenu("Düzenle", self)
        
        actions = [
            ("Geri Al", "Ctrl+Z", self.undo_requested),
            ("Yinele", "Ctrl+Y", self.redo_requested),
            None,
            ("Ayarlar", None, self.preferences_requested)
        ]
        
        for action_info in actions:
            if action_info is None:
                menu.addSeparator()
            else:
                text, shortcut, handler = action_info
                action = QAction(text, self)
                if shortcut:
                    action.setShortcut(shortcut)
                if handler:
                    action.triggered.connect(handler.emit if hasattr(handler, 'emit') else handler)
                menu.addAction(action)
        
        return menu
        
    def create_view_menu(self) -> QMenu:
        """Görünüm menüsü - Panelleri göster/gizle için kullanılacak"""
        menu = QMenu("Görünüm", self)
        return menu
        
    def create_tools_menu(self) -> QMenu:
        menu = QMenu("Araçlar", self)
        
        actions = [
            ("Toplu İşlem", None, self.batch_process_requested),
            ("Ayarlar", None, self.preferences_requested)
        ]
        
        for text, shortcut, handler in actions:
            action = QAction(text, self)
            if shortcut:
                action.setShortcut(shortcut)
            if handler:
                action.triggered.connect(handler.emit if hasattr(handler, 'emit') else handler)
            menu.addAction(action)
        
        return menu
        
    def add_view_toggle(self, text: str, handler, checked: bool = True) -> QAction:
        """Görünüm menüsüne panel göster/gizle seçeneği ekle"""
        action = QAction(text, self)
        action.setCheckable(True)
        action.setChecked(checked)
        action.triggered.connect(handler)
        self.view_menu.addAction(action)
        return action
        
    def update_undo_redo_state(self, can_undo: bool, can_redo: bool):
        """Geri al/yinele menü öğelerinin durumunu güncelle"""
        for action in self.actions():
            if isinstance(action, QAction):
                if action.text() == "Geri Al":
                    action.setEnabled(can_undo)
                elif action.text() == "Yinele":
                    action.setEnabled(can_redo)