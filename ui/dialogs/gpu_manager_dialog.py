"""
GPU管理对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTreeWidget, QTreeWidgetItem, QMessageBox, QWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.dialogs.gpu_dialog import GPUDialog


class GPUManagerDialog(QDialog):
    """GPU管理对话框"""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent)
        self.data_manager = data_manager
        self.has_unsaved_changes = False  # 标记是否有未保存的更改
        self.setWindowTitle("GPU管理")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setGeometry(200, 200, 950, 720)
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F8F9FA, stop:1 #F0F2F5);
            }
        """)
        self.init_ui()
        self.refresh_list()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(35, 35, 35, 35)
        
        # 列表 - 更现代的设计
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["ID", "GPU名称", "总显存(GB)"])
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
        # 启用内联编辑 - GPU名称和总显存列可编辑（ID列不能编辑）
        self.tree.setEditTriggers(QTreeWidget.NoEditTriggers)  # 禁用默认编辑触发，手动控制
        # 双击事件 - 检查列号，只有非ID列才允许编辑
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        # 监听编辑完成事件
        self.tree.itemChanged.connect(self.on_item_changed)
        layout.addWidget(self.tree, stretch=1)
        
        # 在表头区域添加按钮（与"总显存(GB)"列对齐）
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
        self.add_btn.clicked.connect(self.add_gpu)
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
        self.delete_btn.clicked.connect(self.delete_gpu)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        
        self.button_container.show()
        # 延迟更新位置，确保表头已渲染
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.update_button_position)
    
    def update_button_position(self):
        """更新按钮位置，使其与"总显存(GB)"列对齐"""
        if not hasattr(self, 'button_container'):
            return
        
        header = self.tree.header()
        if header.count() < 3:
            return
        
        # 获取"总显存(GB)"列的位置和宽度
        col_0_width = header.sectionSize(0)
        col_1_width = header.sectionSize(1)
        col_2_x = col_0_width + col_1_width
        col_2_width = header.sectionSize(2)
        
        # 计算按钮位置（在"总显存(GB)"列的右侧）
        header_height = header.height()
        button_x = col_2_x + col_2_width - 60  # 按钮容器宽度约60px，右对齐
        button_y = (header_height - 24) // 2  # 垂直居中
        
        # 设置按钮容器位置
        self.button_container.setGeometry(button_x, button_y, 60, 24)
    
    def refresh_list(self):
        """刷新列表"""
        # 暂时断开信号，避免刷新时触发itemChanged
        try:
            self.tree.itemChanged.disconnect(self.on_item_changed)
        except:
            pass
        self.tree.clear()
        gpus = self.data_manager.get_all_gpus()
        for gpu in gpus:
            item = QTreeWidgetItem([str(gpu["id"]), gpu["name"], f"{gpu['total_memory']:.2f}"])
            # GPU名称（第1列）和总显存（第2列）可编辑
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            # ID列不可编辑
            item.setData(0, Qt.UserRole, gpu["id"])  # 存储ID以便保存时使用
            self.tree.addTopLevelItem(item)
        # 重新连接信号
        self.tree.itemChanged.connect(self.on_item_changed)
        self.has_unsaved_changes = False
    
    def on_item_double_clicked(self, item, column):
        """双击事件 - 只有非ID列才允许编辑"""
        if column == 0:  # ID列不允许编辑
            return
        # 对于其他列，手动触发编辑
        self.tree.editItem(item, column)
    
    def on_item_changed(self, item, column):
        """项目编辑完成事件"""
        # ID列（第0列）不允许编辑，如果被编辑则恢复原值
        if column == 0:
            gpu_id = item.data(0, Qt.UserRole)
            if gpu_id:
                item.setText(0, str(gpu_id))
            return
        
        gpu_id = item.data(0, Qt.UserRole)
        if not gpu_id:
            return
        
        gpu = self.data_manager.get_gpu(gpu_id)
        if not gpu:
            return
        
        if column == 1:  # GPU名称列
            new_name = item.text(1).strip()
            if new_name:
                self.data_manager.update_gpu(gpu_id, new_name, gpu["total_memory"])
                self.has_unsaved_changes = True
                # 通知主窗口刷新图表
                if self.parent():
                    self.parent().refresh_chart()
            else:
                # 如果名称为空，恢复原值
                item.setText(1, gpu["name"])
        elif column == 2:  # 总显存列
            try:
                new_memory = float(item.text(2))
                if new_memory > 0:
                    self.data_manager.update_gpu(gpu_id, gpu["name"], new_memory)
                    self.has_unsaved_changes = True
                    # 通知主窗口刷新图表
                    if self.parent():
                        self.parent().refresh_chart()
                else:
                    # 如果显存为0或负数，恢复原值
                    item.setText(2, f"{gpu['total_memory']:.2f}")
            except ValueError:
                # 如果输入不是有效数字，恢复原值
                item.setText(2, f"{gpu['total_memory']:.2f}")
    
    def add_gpu(self):
        """添加GPU"""
        dialog = GPUDialog(self, "添加GPU")
        if dialog.exec_() == QDialog.Accepted:
            name, memory = dialog.get_result()
            self.data_manager.add_gpu(name, memory)
            self.refresh_list()
            # 通知主窗口刷新图表
            if self.parent():
                self.parent().refresh_chart()
            self.has_unsaved_changes = True
    
    def closeEvent(self, event):
        """关闭事件 - 如果有未保存的更改，确认是否保存"""
        if self.has_unsaved_changes:
            msg = QMessageBox(self)
            msg.setWindowTitle("确认")
            msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            msg.setIcon(QMessageBox.Question)
            msg.setText("有未保存的更改，是否保存？")
            save_btn = msg.addButton("保存", QMessageBox.YesRole)
            discard_btn = msg.addButton("不保存", QMessageBox.NoRole)
            cancel_btn = msg.addButton("取消", QMessageBox.RejectRole)
            msg.exec_()
            
            if msg.clickedButton() == cancel_btn:
                event.ignore()  # 取消关闭
                return
            # save_btn 和 discard_btn 的情况，数据已经在编辑时保存了，直接关闭
        event.accept()
    
    def edit_gpu(self):
        """编辑GPU"""
        item = self.tree.currentItem()
        if not item:
            # 如果没有选中项，尝试选中第一个
            if self.tree.topLevelItemCount() > 0:
                item = self.tree.topLevelItem(0)
                self.tree.setCurrentItem(item)
            else:
                return
        
        gpu_id = int(item.text(0))
        gpu = self.data_manager.get_gpu(gpu_id)
        if gpu:
            dialog = GPUDialog(self, "编辑GPU", gpu["name"], gpu["total_memory"])
            if dialog.exec_() == QDialog.Accepted:
                name, memory = dialog.get_result()
                self.data_manager.update_gpu(gpu_id, name, memory)
                self.refresh_list()
                # 通知主窗口刷新图表（因为图表中显示的是GPU名称）
                if self.parent():
                    self.parent().refresh_chart()
    
    def delete_gpu(self):
        """删除GPU"""
        item = self.tree.currentItem()
        if not item:
            # 如果没有选中项，尝试选中第一个
            if self.tree.topLevelItemCount() > 0:
                item = self.tree.topLevelItem(0)
                self.tree.setCurrentItem(item)
            else:
                return
        
        gpu_id = int(item.text(0))
        gpu = self.data_manager.get_gpu(gpu_id)
        if gpu:
            msg = QMessageBox(self)
            msg.setWindowTitle("确认")
            msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            msg.setIcon(QMessageBox.Question)
            msg.setText(f"确定要删除GPU '{gpu['name']}' 吗？")
            yes_btn = msg.addButton("确定", QMessageBox.YesRole)
            no_btn = msg.addButton("取消", QMessageBox.NoRole)
            msg.exec_()
            if msg.clickedButton() == yes_btn:
                self.data_manager.delete_gpu(gpu_id)
                self.refresh_list()
                # 通知主窗口刷新图表
                if self.parent():
                    self.parent().refresh_chart()
                self.has_unsaved_changes = True
    
    def closeEvent(self, event):
        """关闭事件 - 如果有未保存的更改，确认是否保存"""
        if self.has_unsaved_changes:
            msg = QMessageBox(self)
            msg.setWindowTitle("确认")
            msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            msg.setIcon(QMessageBox.Question)
            msg.setText("有未保存的更改，是否保存？")
            save_btn = msg.addButton("保存", QMessageBox.YesRole)
            discard_btn = msg.addButton("不保存", QMessageBox.NoRole)
            cancel_btn = msg.addButton("取消", QMessageBox.RejectRole)
            msg.exec_()
            
            if msg.clickedButton() == cancel_btn:
                event.ignore()  # 取消关闭
                return
            # save_btn 和 discard_btn 的情况，数据已经在编辑时保存了，直接关闭
        event.accept()