"""
GPU编辑对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class GPUDialog(QDialog):
    """GPU编辑对话框"""
    
    def __init__(self, parent, title, name="", memory=0):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setGeometry(300, 300, 420, 220)
        self.name = name
        self.memory = memory
        self.result_data = None
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        # 设置对话框样式 - 更优雅的背景
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F8F9FA, stop:1 #F0F2F5);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # GPU名称
        name_layout = QHBoxLayout()
        name_label = QLabel("GPU名称:")
        name_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        name_label.setStyleSheet("color: #263238;")
        name_label.setMinimumWidth(100)
        name_layout.addWidget(name_label)
        
        self.name_edit = QLineEdit(self.name)
        self.name_edit.setFont(QFont("Segoe UI", 11))
        self.name_edit.setStyleSheet("""
            QLineEdit {
                background-color: #FFFFFF;
                border: 2px solid #E8ECF0;
                border-radius: 8px;
                padding: 10px 15px;
                min-height: 20px;
            }
            QLineEdit:focus {
                border-color: #5B8DEF;
            }
        """)
        name_layout.addWidget(self.name_edit, stretch=1)
        layout.addLayout(name_layout)
        
        # 总显存
        memory_layout = QHBoxLayout()
        memory_label = QLabel("总显存(GB):")
        memory_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        memory_label.setStyleSheet("color: #263238;")
        memory_label.setMinimumWidth(100)
        memory_layout.addWidget(memory_label)
        
        self.memory_edit = QLineEdit(str(self.memory))
        self.memory_edit.setFont(QFont("Segoe UI", 11))
        self.memory_edit.setStyleSheet(self.name_edit.styleSheet())
        memory_layout.addWidget(self.memory_edit, stretch=1)
        layout.addLayout(memory_layout)
        
        layout.addStretch()
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("确定")
        ok_btn.setStyleSheet(self.get_button_style("#5B8DEF"))
        ok_btn.clicked.connect(self.accept_dialog)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet(self.get_button_style("#90A4AE"))
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def get_button_style(self, color):
        """获取按钮样式"""
        color_map = {
            "#5B8DEF": ("#6B9EFF", "#4A7DD6", "#357ABD"),
            "#90A4AE": ("#A0B4BE", "#78909C", "#6B7D87")
        }
        light, normal, dark = color_map.get(color, (color, color, color))
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {light}, stop:1 {normal});
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                min-height: 20px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {normal}, stop:1 {dark});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {dark}, stop:1 {normal});
            }}
        """
    
    def accept_dialog(self):
        """确定按钮"""
        name = self.name_edit.text().strip()
        try:
            memory = float(self.memory_edit.text())
            if not name:
                msg = QMessageBox(self)
                msg.setWindowTitle("错误")
                msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                msg.setIcon(QMessageBox.Warning)
                msg.setText("请输入GPU名称")
                msg.addButton("确定", QMessageBox.AcceptRole)
                msg.exec_()
                return
            if memory <= 0:
                msg = QMessageBox(self)
                msg.setWindowTitle("错误")
                msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                msg.setIcon(QMessageBox.Warning)
                msg.setText("显存必须大于0")
                msg.addButton("确定", QMessageBox.AcceptRole)
                msg.exec_()
                return
            self.result_data = (name, memory)
            self.accept()
        except ValueError:
            msg = QMessageBox(self)
            msg.setWindowTitle("错误")
            msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            msg.setIcon(QMessageBox.Warning)
            msg.setText("请输入有效的显存数值")
            msg.addButton("确定", QMessageBox.AcceptRole)
            msg.exec_()
    
    def get_result(self):
        """获取结果"""
        return self.result_data
