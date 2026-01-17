"""
GPU组管理对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTreeWidget, QTreeWidgetItem, QInputDialog, QMessageBox,
                             QWidget, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class SchemeManagerDialog(QDialog):
    """GPU组管理对话框"""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setWindowTitle("GPU组管理")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setGeometry(200, 200, 900, 720)
        self.init_ui()
        self.refresh_list()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(35, 35, 35, 35)
        
        # 列表 - 更现代的设计
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["ID", "GPU组名称", "任务数量"])
        self.tree.setFont(QFont("Segoe UI", 11))
        self.tree.setStyleSheet("""
            QTreeWidget {
                border: 2px solid #E8ECF0;
                border-radius: 10px;
                background-color: #FFFFFF;
                padding: 5px;
            }
            QTreeWidget::item {
                height: 42px;
                padding: 8px;
                border-bottom: 1px solid #F5F6FA;
            }
            QTreeWidget::item:hover {
                background-color: #F8F9FA;
            }
            QTreeWidget::item:selected {
                background-color: #E8EAF6;
                color: #3F51B5;
                border: none;
                border-left: 4px solid #3F51B5;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F8F9FA, stop:1 #F0F2F5);
                padding: 12px;
                border: none;
                border-bottom: 2px solid #E8ECF0;
                font-weight: bold;
                font-size: 11pt;
            }
        """)
        # 启用内联编辑 - 只有GPU组名称列可编辑
        self.tree.setEditTriggers(QTreeWidget.DoubleClicked | QTreeWidget.SelectedClicked)
        # 监听编辑完成事件
        self.tree.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.tree, stretch=1)
        
        # 在表头区域添加按钮（与"任务数量"列对齐）
        self.setup_header_buttons()
    
    def setup_header_buttons(self):
        """在表头区域设置按钮"""
        # 等待布局完成后再设置按钮位置
        self.tree.header().sectionResized.connect(self.update_button_position)
        self.tree.header().geometriesChanged.connect(self.update_button_position)
        
        # 创建按钮容器
        self.button_container = QWidget(self.tree)
        self.button_container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(self.button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(5)
        
        # 添加按钮（+）
        self.add_btn = QPushButton("+")
        self.add_btn.setFont(QFont("Segoe UI", 14))
        self.add_btn.setFixedSize(24, 24)
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #263238;
                border: 1px solid #E8ECF0;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #F8F9FA;
                border-color: #5B8DEF;
            }
            QPushButton:pressed {
                background-color: #E8ECF0;
            }
        """)
        self.add_btn.clicked.connect(self.add_scheme)
        button_layout.addWidget(self.add_btn)
        
        # 删除按钮（-）
        self.delete_btn = QPushButton("−")
        self.delete_btn.setFont(QFont("Segoe UI", 14))
        self.delete_btn.setFixedSize(24, 24)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #263238;
                border: 1px solid #E8ECF0;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #F8F9FA;
                border-color: #FF6B6B;
            }
            QPushButton:pressed {
                background-color: #E8ECF0;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_scheme)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        
        self.button_container.show()
        # 延迟更新位置，确保表头已渲染
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.update_button_position)
    
    def update_button_position(self):
        """更新按钮位置，使其与"任务数量"列对齐"""
        if not hasattr(self, 'button_container'):
            return
        
        header = self.tree.header()
        if header.count() < 3:
            return
        
        # 获取"任务数量"列的位置和宽度
        col_0_width = header.sectionSize(0)
        col_1_width = header.sectionSize(1)
        col_2_x = col_0_width + col_1_width
        col_2_width = header.sectionSize(2)
        
        # 计算按钮位置（在"任务数量"列的右侧）
        header_height = header.height()
        button_x = col_2_x + col_2_width - 60  # 按钮容器宽度约60px，右对齐
        button_y = (header_height - 24) // 2  # 垂直居中
        
        # 设置按钮容器位置
        self.button_container.setGeometry(button_x, button_y, 60, 24)
    
    def refresh_list(self):
        """刷新列表"""
        try:
            self.tree.itemChanged.disconnect(self.on_item_changed)
        except:
            pass
        self.tree.clear()
        schemes = self.data_manager.get_all_schemes()
        for scheme in schemes:
            task_count = len(scheme.get("tasks", []))
            item = QTreeWidgetItem([str(scheme["id"]), scheme["name"], str(task_count)])
            item.setData(0, Qt.UserRole, scheme["id"])
            # 只有GPU组名称列（第1列）可编辑
            flags = item.flags()
            flags |= Qt.ItemIsEditable
            item.setFlags(flags)
            self.tree.addTopLevelItem(item)
        self.tree.itemChanged.connect(self.on_item_changed)
        self.has_unsaved_changes = False
    
    def on_item_changed(self, item, column):
        """项目编辑完成事件"""
        if column == 1:  # 只处理GPU组名称列（第1列）的编辑
            scheme_id = item.data(0, Qt.UserRole)
            if scheme_id:
                new_name = item.text(1).strip()
                if new_name:
                    self.data_manager.update_scheme(scheme_id, new_name)
                    self.has_unsaved_changes = True
                    if self.parent():
                        self.parent().refresh_scheme_combo()
                        self.parent().refresh_chart()
                else:
                    # 如果名称为空，恢复原名称
                    scheme = self.data_manager.get_scheme(scheme_id)
                    if scheme:
                        item.setText(1, scheme["name"])
    
    def add_scheme(self):
        """添加GPU组"""
        dialog = QInputDialog(self)
        dialog.setWindowTitle("添加GPU组")
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setLabelText("请输入GPU组名称:")
        dialog.setOkButtonText("确定")
        dialog.setCancelButtonText("取消")
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.textValue().strip()
            if name:
                self.data_manager.add_scheme(name)
                self.refresh_list()
                # 通知主窗口刷新下拉列表
                if self.parent():
                    self.parent().refresh_scheme_combo()
                    self.parent().refresh_chart()
    
    def edit_scheme(self):
        """编辑GPU组"""
        item = self.tree.currentItem()
        if not item:
            # 如果没有选中项，尝试选中第一个
            if self.tree.topLevelItemCount() > 0:
                item = self.tree.topLevelItem(0)
                self.tree.setCurrentItem(item)
            else:
                return
        
        scheme_id = int(item.text(0))
        scheme = self.data_manager.get_scheme(scheme_id)
        if scheme:
            dialog = QInputDialog(self)
            dialog.setWindowTitle("编辑GPU组")
            dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            dialog.setLabelText("请输入新GPU组名称:")
            dialog.setTextValue(scheme["name"])
            dialog.setOkButtonText("确定")
            dialog.setCancelButtonText("取消")
            if dialog.exec_() == QDialog.Accepted:
                name = dialog.textValue().strip()
                if name:
                    self.data_manager.update_scheme(scheme_id, name)
                    self.refresh_list()
                    # 通知主窗口刷新下拉列表
                    if self.parent():
                        self.parent().refresh_scheme_combo()
                        self.parent().refresh_chart()
    
    def delete_scheme(self):
        """删除GPU组"""
        item = self.tree.currentItem()
        if not item:
            # 如果没有选中项，尝试选中第一个
            if self.tree.topLevelItemCount() > 0:
                item = self.tree.topLevelItem(0)
                self.tree.setCurrentItem(item)
            else:
                return
        
        scheme_id = int(item.text(0))
        scheme = self.data_manager.get_scheme(scheme_id)
        if scheme:
            msg = QMessageBox(self)
            msg.setWindowTitle("确认")
            msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            msg.setIcon(QMessageBox.Question)
            msg.setText(f"确定要删除GPU组 '{scheme['name']}' 吗？\n这将同时删除该GPU组的所有任务和分配。")
            yes_btn = msg.addButton("确定", QMessageBox.YesRole)
            no_btn = msg.addButton("取消", QMessageBox.NoRole)
            msg.exec_()
            if msg.clickedButton() == yes_btn:
                self.data_manager.delete_scheme(scheme_id)
                self.refresh_list()
                # 通知主窗口刷新下拉列表
                if self.parent():
                    self.parent().refresh_scheme_combo()
                    self.parent().refresh_chart()