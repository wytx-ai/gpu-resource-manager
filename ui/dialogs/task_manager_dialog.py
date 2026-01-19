"""
任务管理对话框
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTreeWidget, QTreeWidgetItem, QMessageBox,
                             QWidget, QComboBox, QLineEdit, QLabel)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.dialogs.task_dialog import TaskDialog


class TaskManagerDialog(QDialog):
    """任务管理对话框"""
    
    def __init__(self, parent, data_manager):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_task_id = None
        self.has_unsaved_changes = False  # 标记是否有未保存的更改
        self.pending_changes = {}  # 存储待保存的更改 {task_id: new_name}
        self.setWindowTitle("任务管理")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setGeometry(200, 200, 1200, 800)
        self.init_ui()
        self.refresh_list()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(35, 35, 35, 35)
        
        # 主布局 - 左右分栏
        main_layout = QHBoxLayout()
        main_layout.setSpacing(20)
        
        # 左侧：任务列表
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["ID", "任务名称"])
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
        # 选择事件 - 更新右侧分配列表
        self.tree.itemSelectionChanged.connect(self.on_task_selected)
        # 启用内联编辑 - 只有任务名称列可编辑（ID列不能编辑）
        self.tree.setEditTriggers(QTreeWidget.NoEditTriggers)  # 禁用默认编辑触发，手动控制
        # 双击事件 - 检查列号，只有非ID列才允许编辑
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        # 监听编辑完成事件
        self.tree.itemChanged.connect(self.on_task_item_changed)
        left_layout.addWidget(self.tree, stretch=1)
        
        # 在表头区域添加按钮
        self.setup_header_buttons()
        
        main_layout.addWidget(left_widget, stretch=1)
        
        # 右侧：显存分配列表
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        
        # 分配列表
        self.alloc_tree = QTreeWidget()
        self.alloc_tree.setHeaderLabels(["GPU名称", "显存使用(GB)"])
        self.alloc_tree.setFont(QFont("Segoe UI", 11))
        self.alloc_tree.setStyleSheet("""
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
        # 双击事件 - 编辑分配
        self.alloc_tree.itemDoubleClicked.connect(self.on_alloc_double_clicked)
        right_layout.addWidget(self.alloc_tree, stretch=1)
        
        # 在表头区域添加按钮（与"显存使用(GB)"列对齐）
        self.setup_alloc_header_buttons()
        
        main_layout.addWidget(right_widget, stretch=1)
        
        layout.addLayout(main_layout, stretch=1)
        
        # 底部保存按钮
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        self.save_btn = QPushButton("保存")
        self.save_btn.setFont(QFont("Segoe UI", 11))
        self.save_btn.setFixedSize(80, 35)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5B8DEF;
                color: #FFFFFF;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4A7BC8;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #999999;
            }
        """)
        self.save_btn.clicked.connect(self.save_changes)
        self.save_btn.setEnabled(False)
        bottom_layout.addWidget(self.save_btn)
        layout.addLayout(bottom_layout)
    
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
        self.add_btn.clicked.connect(self.add_task)
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
        self.delete_btn.clicked.connect(self.delete_task)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        
        self.button_container.show()
        # 延迟更新位置，确保表头已渲染
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.update_button_position)
    
    def update_button_position(self):
        """更新按钮位置，使其与"任务名称"列对齐"""
        if not hasattr(self, 'button_container'):
            return
        
        header = self.tree.header()
        if header.count() < 2:
            return
        
        # 获取"任务名称"列的位置和宽度
        col_0_width = header.sectionSize(0)
        col_1_x = col_0_width
        col_1_width = header.sectionSize(1)
        
        # 计算按钮位置（在"任务名称"列的右侧）
        header_height = header.height()
        button_x = col_1_x + col_1_width - 60  # 按钮容器宽度约60px，右对齐
        button_y = (header_height - 24) // 2  # 垂直居中
        
        # 设置按钮容器位置
        self.button_container.setGeometry(button_x, button_y, 60, 24)
    
    def setup_alloc_header_buttons(self):
        """在分配列表表头区域设置按钮"""
        # 等待布局完成后再设置按钮位置
        self.alloc_tree.header().sectionResized.connect(self.update_alloc_button_position)
        self.alloc_tree.header().geometriesChanged.connect(self.update_alloc_button_position)
        
        # 创建按钮容器
        self.alloc_button_container = QWidget(self.alloc_tree)
        self.alloc_button_container.setStyleSheet("background: transparent;")
        button_layout = QHBoxLayout(self.alloc_button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(5)
        
        # 添加按钮（+）
        self.add_alloc_btn = QPushButton("+")
        self.add_alloc_btn.setFont(QFont("Segoe UI", 14))
        self.add_alloc_btn.setFixedSize(24, 24)
        self.add_alloc_btn.setStyleSheet("""
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
        self.add_alloc_btn.clicked.connect(self.add_allocation)
        button_layout.addWidget(self.add_alloc_btn)
        
        # 删除按钮（-）
        self.delete_alloc_btn = QPushButton("−")
        self.delete_alloc_btn.setFont(QFont("Segoe UI", 14))
        self.delete_alloc_btn.setFixedSize(24, 24)
        self.delete_alloc_btn.setStyleSheet("""
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
        self.delete_alloc_btn.clicked.connect(self.delete_allocation)
        button_layout.addWidget(self.delete_alloc_btn)
        
        button_layout.addStretch()
        
        self.alloc_button_container.show()
        # 延迟更新位置，确保表头已渲染
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.update_alloc_button_position)
    
    def update_alloc_button_position(self):
        """更新分配列表按钮位置，使其与"显存使用(GB)"列对齐"""
        if not hasattr(self, 'alloc_button_container'):
            return
        
        header = self.alloc_tree.header()
        if header.count() < 2:
            return
        
        # 获取"显存使用(GB)"列的位置和宽度
        col_0_width = header.sectionSize(0)
        col_1_x = col_0_width
        col_1_width = header.sectionSize(1)
        
        # 计算按钮位置（在"显存使用(GB)"列的右侧）
        header_height = header.height()
        button_x = col_1_x + col_1_width - 60  # 按钮容器宽度约60px，右对齐
        button_y = (header_height - 24) // 2  # 垂直居中
        
        # 设置按钮容器位置
        self.alloc_button_container.setGeometry(button_x, button_y, 60, 24)
    
    def refresh_list(self):
        """刷新列表"""
        try:
            self.tree.itemChanged.disconnect(self.on_task_item_changed)
        except:
            pass
        self.tree.clear()
        tasks = self.data_manager.get_all_tasks()
        for task in tasks:
            item = QTreeWidgetItem([str(task["id"]), task["name"]])
            item.setData(0, Qt.UserRole, task["id"])
            # 只有任务名称列（第1列）可编辑
            flags = item.flags()
            flags |= Qt.ItemIsEditable
            item.setFlags(flags)
            self.tree.addTopLevelItem(item)
        self.tree.itemChanged.connect(self.on_task_item_changed)
    
    def on_task_selected(self):
        """任务选择变化时更新分配列表"""
        item = self.tree.currentItem()
        if item:
            self.current_task_id = int(item.text(0))
            self.refresh_allocation_list()
        else:
            self.current_task_id = None
            self.alloc_tree.clear()
    
    def refresh_allocation_list(self):
        """刷新分配列表"""
        self.alloc_tree.clear()
        if not self.current_task_id:
            return
        
        allocations = self.data_manager.get_allocations_by_task(self.current_task_id)
        for alloc in allocations:
            gpu = self.data_manager.get_gpu(alloc["gpu_id"])
            if gpu:
                item = QTreeWidgetItem([gpu["name"], f"{alloc['memory_usage']:.1f}"])
                item.setData(0, Qt.UserRole, alloc["gpu_id"])  # 存储gpu_id
                self.alloc_tree.addTopLevelItem(item)
    
    def on_item_double_clicked(self, item, column):
        """双击事件 - 只有非ID列才允许编辑"""
        if column == 0:  # ID列不允许编辑
            return
        # 对于其他列，手动触发编辑
        self.tree.editItem(item, column)
    
    def on_task_item_changed(self, item, column):
        """任务项目编辑完成事件"""
        # 只处理任务名称列（第1列）的编辑，ID列（第0列）不允许编辑
        if column == 0:
            # ID列被编辑，恢复原值
            task_id = item.data(0, Qt.UserRole)
            if task_id:
                item.setText(0, str(task_id))
            return
        
        if column == 1:
            task_id = item.data(0, Qt.UserRole)
            if task_id:
                new_name = item.text(1).strip()
                if new_name:
                    # 不立即保存，只标记为待保存
                    self.pending_changes[task_id] = new_name
                    self.has_unsaved_changes = True
                    self.save_btn.setEnabled(True)
                else:
                    # 如果名称为空，恢复原名称
                    task = self.data_manager.get_task(task_id)
                    if task:
                        item.setText(1, task["name"])
                        # 移除待保存的更改
                        if task_id in self.pending_changes:
                            del self.pending_changes[task_id]
                        if not self.pending_changes:
                            self.has_unsaved_changes = False
                            self.save_btn.setEnabled(False)
    
    def save_changes(self):
        """保存所有待保存的更改"""
        if not self.pending_changes:
            return
        
        for task_id, new_name in self.pending_changes.items():
            task = self.data_manager.get_task(task_id)
            if task:
                self.data_manager.update_task(task_id, new_name, task.get("description", ""))
        
        self.pending_changes.clear()
        self.has_unsaved_changes = False
        self.save_btn.setEnabled(False)
        
        # 通知主窗口刷新图表
        if self.parent():
            self.parent().refresh_chart()
    
    def closeEvent(self, event):
        """关闭事件 - 如果有未保存的更改，确认是否保存"""
        if self.has_unsaved_changes:
            msg = QMessageBox(self)
            msg.setWindowTitle("未保存的更改")
            msg.setIcon(QMessageBox.Warning)
            msg.setText("有未保存的更改，是否保存？")
            save_btn = msg.addButton("保存", QMessageBox.YesRole)
            discard_btn = msg.addButton("不保存", QMessageBox.NoRole)
            cancel_btn = msg.addButton("取消", QMessageBox.RejectRole)
            msg.exec_()
            
            if msg.clickedButton() == save_btn:
                self.save_changes()
                event.accept()
            elif msg.clickedButton() == discard_btn:
                # 恢复原值
                try:
                    self.tree.itemChanged.disconnect(self.on_task_item_changed)
                except:
                    pass
                for task_id in self.pending_changes:
                    item = None
                    for i in range(self.tree.topLevelItemCount()):
                        if self.tree.topLevelItem(i).data(0, Qt.UserRole) == task_id:
                            item = self.tree.topLevelItem(i)
                            break
                    if item:
                        task = self.data_manager.get_task(task_id)
                        if task:
                            item.setText(1, task["name"])
                self.tree.itemChanged.connect(self.on_task_item_changed)
                self.pending_changes.clear()
                self.has_unsaved_changes = False
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def on_alloc_double_clicked(self, item, column):
        """双击分配行事件 - 编辑显存分配"""
        if not self.current_task_id:
            return
        gpu_id = item.data(1, Qt.UserRole)  # gpu_id存储在GPU名称列（第1列）
        self.edit_allocation(gpu_id)
    
    def add_task(self):
        """添加任务"""
        dialog = TaskDialog(self, "添加任务")
        if dialog.exec_() == QDialog.Accepted:
            name = dialog.get_result()
            task_id = self.data_manager.add_task(name, "")
            self.refresh_list()
            # 通知主窗口刷新图表
            if self.parent():
                self.parent().refresh_chart()
    
    def edit_task(self):
        """编辑任务名称"""
        item = self.tree.currentItem()
        if not item:
            # 如果没有选中项，尝试选中第一个
            if self.tree.topLevelItemCount() > 0:
                item = self.tree.topLevelItem(0)
                self.tree.setCurrentItem(item)
            else:
                return
        
        task_id = int(item.text(0))
        task = self.data_manager.get_task(task_id)
        if task:
            dialog = TaskDialog(self, "编辑任务", task["name"])
            if dialog.exec_() == QDialog.Accepted:
                name = dialog.get_result()
                self.data_manager.update_task(task_id, name, task.get("description", ""))
                self.refresh_list()
                # 通知主窗口刷新图表
                if self.parent():
                    self.parent().refresh_chart()
    
    def show_allocation_dialog(self, task_id, pre_select_gpu_id=None, pre_fill_memory=None):
        """显示显存分配对话框"""
        gpus = self.data_manager.get_all_gpus()
        if not gpus:
            msg = QMessageBox(self)
            msg.setWindowTitle("提示")
            msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            msg.setIcon(QMessageBox.Information)
            msg.setText("请先添加GPU")
            msg.addButton("确定", QMessageBox.AcceptRole)
            msg.exec_()
            return
        
        # 获取已分配的GPU ID和显存使用量
        existing_allocations = {}
        allocations = self.data_manager.get_allocations_by_task(task_id)
        for alloc in allocations:
            existing_allocations[alloc["gpu_id"]] = alloc["memory_usage"]
        
        # 显示所有GPU（包括已分配的）
        if not gpus:
            msg = QMessageBox(self)
            msg.setWindowTitle("提示")
            msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            msg.setIcon(QMessageBox.Information)
            msg.setText("请先添加GPU")
            msg.addButton("确定", QMessageBox.AcceptRole)
            msg.exec_()
            return
        
        # 创建选择对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("显存分配")
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setGeometry(400, 400, 400, 200)
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # GPU选择
        gpu_layout = QHBoxLayout()
        gpu_label = QLabel("选择GPU:")
        gpu_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        gpu_label.setStyleSheet("color: #263238;")
        gpu_label.setMinimumWidth(100)
        gpu_layout.addWidget(gpu_label)
        
        gpu_combo = QComboBox()
        gpu_combo.setFont(QFont("Segoe UI", 11))
        
        # 存储每个GPU的当前分配显存（如果有）
        gpu_current_memory = {}
        
        for gpu in gpus:
            # 计算该GPU的剩余显存
            usage = self.data_manager.get_gpu_usage(gpu["id"])
            if usage:
                remaining_memory = usage["free_memory"]
            else:
                remaining_memory = gpu["total_memory"]
            
            # 检查该GPU是否已分配给此任务
            is_allocated = gpu["id"] in existing_allocations
            current_memory = existing_allocations.get(gpu["id"], 0)
            gpu_current_memory[gpu["id"]] = current_memory
            
            # 显示：GPU名称 (总显存GB, 剩余显存GB) [已分配: XGB]
            if is_allocated:
                display_text = f"{gpu['name']} ({gpu['total_memory']:.1f}GB, 剩余{remaining_memory:.1f}GB) [已分配:{current_memory:.1f}GB]"
            else:
                display_text = f"{gpu['name']} ({gpu['total_memory']:.1f}GB, 剩余{remaining_memory:.1f}GB)"
            
            gpu_combo.addItem(display_text, gpu["id"])
        gpu_combo.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                border: 2px solid #E8ECF0;
                border-radius: 8px;
                padding: 10px 15px;
                min-height: 20px;
                color: #263238;
            }
            QComboBox:focus {
                border-color: #5B8DEF;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #263238;
                border: 2px solid #E8ECF0;
                border-radius: 8px;
                selection-background-color: #E8ECF0;
                selection-color: #263238;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #F8F9FA;
                color: #263238;
            }
        """)
        gpu_layout.addWidget(gpu_combo, stretch=1)
        layout.addLayout(gpu_layout)
        
        # 显存输入
        memory_layout = QHBoxLayout()
        memory_label = QLabel("显存使用(GB):")
        memory_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        memory_label.setStyleSheet("color: #263238;")
        memory_label.setMinimumWidth(100)
        memory_layout.addWidget(memory_label)
        
        memory_edit = QLineEdit("0")
        memory_edit.setFont(QFont("Segoe UI", 11))
        memory_edit.setStyleSheet("""
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
        memory_layout.addWidget(memory_edit, stretch=1)
        layout.addLayout(memory_layout)
        
        # 当选择GPU时，更新显存输入框
        def on_gpu_selected(index):
            gpu_id = gpu_combo.itemData(index)
            if gpu_id in gpu_current_memory:
                memory_edit.setText(str(gpu_current_memory[gpu_id]))
            else:
                memory_edit.setText("0")
        
        gpu_combo.currentIndexChanged.connect(on_gpu_selected)
        
        # 初始化显存输入框
        if gpu_combo.count() > 0:
            # 如果指定了预选GPU，选择它
            if pre_select_gpu_id:
                for i in range(gpu_combo.count()):
                    if gpu_combo.itemData(i) == pre_select_gpu_id:
                        gpu_combo.setCurrentIndex(i)
                        break
            # 如果指定了预填显存，使用它
            if pre_fill_memory is not None:
                memory_edit.setText(str(pre_fill_memory))
            else:
                on_gpu_selected(gpu_combo.currentIndex())
        
        layout.addStretch()
        
        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        ok_btn = QPushButton("确定")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #5B8DEF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4A7DD6;
            }
            QPushButton:pressed {
                background-color: #357ABD;
            }
        """)
        ok_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #90A4AE;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #78909C;
            }
            QPushButton:pressed {
                background-color: #6B7D87;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            gpu_id = gpu_combo.currentData()
            try:
                memory = float(memory_edit.text())
                if memory < 0:
                    msg = QMessageBox(self)
                    msg.setWindowTitle("错误")
                    msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                    msg.setIcon(QMessageBox.Warning)
                    msg.setText("显存使用量不能为负数")
                    msg.addButton("确定", QMessageBox.AcceptRole)
                    msg.exec_()
                    return
                
                # 如果显存为0，删除分配；否则添加或更新分配
                if memory == 0:
                    # 检查是否已存在分配
                    if gpu_id in existing_allocations:
                        self.data_manager.delete_allocation(task_id, gpu_id)
                else:
                    # 验证分配的显存是否超过GPU的剩余显存
                    # 获取该GPU的使用情况
                    usage = self.data_manager.get_gpu_usage(gpu_id)
                    if usage:
                        # 如果该GPU已经分配给当前任务，需要减去当前任务已分配的显存
                        current_task_memory = existing_allocations.get(gpu_id, 0)
                        # 实际可用的剩余显存 = 当前剩余显存 + 当前任务已分配的显存
                        available_memory = usage["free_memory"] + current_task_memory
                    else:
                        # 如果获取不到使用情况，使用GPU的总显存
                        gpu = self.data_manager.get_gpu(gpu_id)
                        if gpu:
                            available_memory = gpu["total_memory"]
                        else:
                            available_memory = 0
                    
                    # 检查分配的显存是否超过可用显存
                    if memory > available_memory:
                        msg = QMessageBox(self)
                        msg.setWindowTitle("错误")
                        msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                        msg.setIcon(QMessageBox.Warning)
                        gpu = self.data_manager.get_gpu(gpu_id)
                        gpu_name = gpu["name"] if gpu else "GPU"
                        msg.setText(f"分配的显存 ({memory:.1f}GB) 超过了 {gpu_name} 的可用显存 ({available_memory:.1f}GB)")
                        msg.addButton("确定", QMessageBox.AcceptRole)
                        msg.exec_()
                        return
                    
                    self.data_manager.add_allocation(task_id, gpu_id, memory)
                
                self.refresh_allocation_list()
            except ValueError:
                msg = QMessageBox(self)
                msg.setWindowTitle("错误")
                msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                msg.setIcon(QMessageBox.Warning)
                msg.setText("请输入有效的显存数值")
                msg.addButton("确定", QMessageBox.AcceptRole)
                msg.exec_()
    
    def add_allocation(self):
        """添加显存分配"""
        if not self.current_task_id:
            msg = QMessageBox(self)
            msg.setWindowTitle("提示")
            msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            msg.setIcon(QMessageBox.Information)
            msg.setText("请先选择任务")
            msg.addButton("确定", QMessageBox.AcceptRole)
            msg.exec_()
            return
        self.show_allocation_dialog(self.current_task_id)
    
    def edit_allocation(self, gpu_id):
        """编辑显存分配"""
        if not self.current_task_id:
            return
        # 获取当前分配的显存
        allocations = self.data_manager.get_allocations_by_task(self.current_task_id)
        current_memory = 0
        for alloc in allocations:
            if alloc["gpu_id"] == gpu_id:
                current_memory = alloc["memory_usage"]
                break
        
        # 显示分配对话框，并预选该GPU
        self.show_allocation_dialog(self.current_task_id, gpu_id, current_memory)
    
    def delete_allocation(self):
        """删除显存分配"""
        if not self.current_task_id:
            msg = QMessageBox(self)
            msg.setWindowTitle("提示")
            msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            msg.setIcon(QMessageBox.Information)
            msg.setText("请先选择任务")
            msg.addButton("确定", QMessageBox.AcceptRole)
            msg.exec_()
            return
        
        item = self.alloc_tree.currentItem()
        if not item:
            msg = QMessageBox(self)
            msg.setWindowTitle("提示")
            msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            msg.setIcon(QMessageBox.Information)
            msg.setText("请先选择要删除的分配")
            msg.addButton("确定", QMessageBox.AcceptRole)
            msg.exec_()
            return
        
        gpu_id = item.data(0, Qt.UserRole)
        gpu = self.data_manager.get_gpu(gpu_id)
        if gpu:
            msg = QMessageBox(self)
            msg.setWindowTitle("确认")
            msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            msg.setIcon(QMessageBox.Question)
            msg.setText(f"确定要删除GPU '{gpu['name']}' 的分配吗？")
            yes_btn = msg.addButton("确定", QMessageBox.YesRole)
            no_btn = msg.addButton("取消", QMessageBox.NoRole)
            msg.exec_()
            if msg.clickedButton() == yes_btn:
                self.data_manager.delete_allocation(self.current_task_id, gpu_id)
                self.refresh_allocation_list()
    
    def delete_task(self):
        """删除任务"""
        item = self.tree.currentItem()
        if not item:
            # 如果没有选中项，尝试选中第一个
            if self.tree.topLevelItemCount() > 0:
                item = self.tree.topLevelItem(0)
                self.tree.setCurrentItem(item)
            else:
                return
        
        task_id = int(item.text(0))
        task = self.data_manager.get_task(task_id)
        if task:
            msg = QMessageBox(self)
            msg.setWindowTitle("确认")
            msg.setWindowFlags(msg.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            msg.setIcon(QMessageBox.Question)
            msg.setText(f"确定要删除任务 '{task['name']}' 吗？")
            yes_btn = msg.addButton("确定", QMessageBox.YesRole)
            no_btn = msg.addButton("取消", QMessageBox.NoRole)
            msg.exec_()
            if msg.clickedButton() == yes_btn:
                self.data_manager.delete_task(task_id)
                self.refresh_list()
                # 清空分配列表
                self.current_task_id = None
                self.alloc_tree.clear()
                # 通知主窗口刷新图表
                if self.parent():
                    self.parent().refresh_chart()