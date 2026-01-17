"""
主窗口模块
"""
import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QFrame, QScrollArea,
                             QGroupBox, QDialog, QSystemTrayIcon, QMenu, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QIcon
from ui.chart_widget import ChartWidget
from ui.dialogs.scheme_manager_dialog import SchemeManagerDialog
from ui.dialogs.gpu_manager_dialog import GPUManagerDialog
from ui.dialogs.task_manager_dialog import TaskManagerDialog
from data_manager import DataManager


class GPUMainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPU管理工具")
        self.setGeometry(100, 100, 1200, 800)
        
        # 获取图标路径（相对于项目根目录）
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons", "gpu.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # 初始化数据管理器
        self.data_manager = DataManager()
        
        # 初始化系统托盘
        self.init_system_tray(icon_path)
        
        # 创建主界面
        self.init_ui()
        
        # 刷新显示
        self.refresh_scheme_combo()
        self.refresh_chart()
    
    def init_ui(self):
        """初始化界面"""
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 顶部工具栏 - 更优雅的设计
        top_frame = QFrame()
        top_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 22px;
                border: 1px solid #E8ECF0;
            }
        """)
        top_layout = QHBoxLayout(top_frame)
        top_layout.setSpacing(15)
        top_layout.setContentsMargins(22, 22, 22, 22)
        
        # 方案选择区域 - 确保标签可见
        scheme_label = QLabel("GPU组")
        scheme_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        scheme_label.setStyleSheet("""
            QLabel {
                color: #263238;
                background-color: transparent;
                padding: 0px;
            }
        """)
        scheme_label.setMinimumWidth(60)  # 确保有足够宽度显示
        top_layout.addWidget(scheme_label)
        
        self.scheme_combo = QComboBox()
        self.scheme_combo.setFont(QFont("Segoe UI", 11))
        self.scheme_combo.setMinimumWidth(320)
        self.scheme_combo.setStyleSheet("""
            QComboBox {
                background-color: #FFFFFF;
                border: 2px solid #E8ECF0;
                border-radius: 8px;
                padding: 10px 15px;
                min-height: 20px;
                color: #263238;
            }
            QComboBox:hover {
                border-color: #5B8DEF;
            }
            QComboBox:focus {
                border-color: #5B8DEF;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 6px solid #546E7A;
                width: 0;
                height: 0;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                border: 2px solid #E8ECF0;
                border-radius: 8px;
                selection-background-color: #E3F2FD;
                selection-color: #1976D2;
                padding: 4px;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 12px;
                border-radius: 4px;
                color: #263238;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #E8ECF0;
                color: #263238;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
            }
        """)
        self.scheme_combo.currentIndexChanged.connect(self.on_scheme_changed)
        top_layout.addWidget(self.scheme_combo)
        
        # GPU组管理按钮 - 更现代的设计
        scheme_btn = QPushButton("GPU组管理")
        scheme_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        scheme_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6B9EFF, stop:1 #4A7DD6);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 14px 28px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5B8DEF, stop:1 #357ABD);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4A7DD6, stop:1 #2E5A9E);
            }
        """)
        scheme_btn.clicked.connect(self.open_scheme_manager)
        top_layout.addWidget(scheme_btn)
        
        # 分隔线 - 更优雅
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("""
            QFrame {
                background-color: #E8ECF0;
                max-width: 1px;
                margin: 8px 20px;
            }
        """)
        top_layout.addWidget(separator)
        
        # GPU管理按钮
        gpu_btn = QPushButton("GPU管理")
        gpu_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        gpu_btn.setStyleSheet(scheme_btn.styleSheet())
        gpu_btn.clicked.connect(self.open_gpu_manager)
        top_layout.addWidget(gpu_btn)
        
        # 任务管理按钮
        task_btn = QPushButton("任务管理")
        task_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        task_btn.setStyleSheet(scheme_btn.styleSheet())
        task_btn.clicked.connect(self.open_task_manager)
        top_layout.addWidget(task_btn)
        
        # 分隔线
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setStyleSheet("""
            QFrame {
                background-color: #E8ECF0;
                max-width: 1px;
                margin: 8px 20px;
            }
        """)
        top_layout.addWidget(separator2)
        
        # 刷新按钮
        refresh_btn = QPushButton("刷新")
        refresh_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #52D273, stop:1 #45C165);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 14px 28px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #62E283, stop:1 #35A155);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45C165, stop:1 #2E8B47);
            }
        """)
        refresh_btn.clicked.connect(self.refresh_chart)
        top_layout.addWidget(refresh_btn)
        
        top_layout.addStretch()
        main_layout.addWidget(top_frame)
        
        # 图表区域 - 更优雅的设计
        chart_group = QGroupBox("GPU使用情况")
        chart_group.setFont(QFont("Segoe UI", 13, QFont.Bold))
        chart_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #E8ECF0;
                border-radius: 12px;
                background-color: #FFFFFF;
                padding: 20px;
                margin-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #263238;
                font-weight: bold;
            }
        """)
        chart_layout = QVBoxLayout(chart_group)
        
        # 创建图表组件
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none; background-color: #FFFFFF;")
        
        self.chart_widget = ChartWidget()
        scroll_area.setWidget(self.chart_widget)
        chart_layout.addWidget(scroll_area)
        
        main_layout.addWidget(chart_group, stretch=1)
        
        # 设置窗口样式 - 更优雅的背景
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F8F9FA, stop:1 #F0F2F5);
            }
        """)
    
    def init_system_tray(self, icon_path):
        """初始化系统托盘"""
        # 检查系统是否支持系统托盘
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        # 创建系统托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.setToolTip("GPU管理工具")
        
        # 创建托盘菜单
        tray_menu = QMenu(self)
        
        # 显示/隐藏窗口
        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self.show)
        show_action.triggered.connect(self.raise_)
        show_action.triggered.connect(self.activateWindow)
        tray_menu.addAction(show_action)
        
        # 退出
        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # 双击托盘图标显示窗口
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        # 显示托盘图标
        self.tray_icon.show()
    
    def tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()
    
    def closeEvent(self, event):
        """窗口关闭事件 - 直接关闭"""
        # 隐藏系统托盘图标
        if hasattr(self, 'tray_icon'):
            self.tray_icon.hide()
        event.accept()
    
    def refresh_scheme_combo(self):
        """刷新方案下拉框"""
        schemes = self.data_manager.get_all_schemes()
        scheme_names = [f"{s['id']}: {s['name']}" for s in schemes]
        self.scheme_combo.clear()
        self.scheme_combo.addItems(scheme_names)
        
        # 设置当前选中的方案
        current_scheme = self.data_manager.get_current_scheme()
        if current_scheme:
            current_text = f"{current_scheme['id']}: {current_scheme['name']}"
            index = self.scheme_combo.findText(current_text)
            if index >= 0:
                self.scheme_combo.setCurrentIndex(index)
        elif scheme_names:
            self.scheme_combo.setCurrentIndex(0)
            if schemes:
                self.data_manager.set_current_scheme(schemes[0]["id"])
    
    def on_scheme_changed(self, index):
        """方案切换事件"""
        if index >= 0:
            selected = self.scheme_combo.currentText()
            if selected:
                scheme_id = int(selected.split(":")[0])
                self.data_manager.set_current_scheme(scheme_id)
                self.refresh_chart()
    
    def refresh_chart(self):
        """刷新图表"""
        gpus = self.data_manager.get_all_gpus()
        if not gpus:
            self.chart_widget.set_data([], [], [], {})
            return
        
        # 准备数据
        gpu_names = []
        total_memories = []
        task_breakdown = []
        
        for gpu in gpus:
            gpu_names.append(gpu["name"])
            total_memories.append(gpu["total_memory"])
            
            usage = self.data_manager.get_gpu_usage(gpu["id"])
            if usage:
                task_info = {}
                for alloc in usage["allocations"]:
                    task_name = alloc["task_name"]
                    if task_name not in task_info:
                        task_info[task_name] = 0
                    task_info[task_name] += alloc["memory_usage"]
                task_breakdown.append(task_info)
            else:
                task_breakdown.append({})
        
        # 获取所有任务名称（用于颜色映射）
        all_tasks = self.data_manager.get_all_tasks()
        task_names = [task["name"] for task in all_tasks]
        
        # 定义任务颜色 - 明亮柔和配色（提高亮度，保持柔和）
        task_colors = [
            QColor("#8FA5D4"),  # 明亮蓝 - 优雅专业
            QColor("#E0A8C0"),  # 明亮粉 - 温暖舒适
            QColor("#8FC5A3"),  # 明亮绿 - 自然清新
            QColor("#E0B38A"),  # 明亮橙 - 温暖明亮
            QColor("#7BB8D4"),  # 明亮青 - 清新透明
            QColor("#D4A89A"),  # 明亮棕 - 复古优雅
            QColor("#9BB8D4"),  # 明亮蓝灰 - 清新淡雅
            QColor("#B89BC8"),  # 明亮紫灰 - 优雅神秘
            QColor("#8FC5B0"),  # 明亮绿蓝 - 自然宁静
            QColor("#D4B38A"),  # 明亮米橙 - 温暖柔和
            QColor("#8BB8D4"),  # 明亮蓝青 - 冷静专业
            QColor("#B8D4A8"),  # 明亮绿灰 - 清新自然
            QColor("#D4A8C0"),  # 明亮粉紫 - 温柔优雅
            QColor("#9BB8D4")   # 明亮蓝灰 - 清新淡雅
        ]
        task_color_map = {}
        for i, name in enumerate(task_names):
            task_color_map[name] = task_colors[i % len(task_colors)]
        
        # 设置图表数据
        self.chart_widget.set_data(gpu_names, total_memories, task_breakdown, task_color_map)
    
    def open_scheme_manager(self):
        """打开GPU组管理弹窗"""
        dialog = SchemeManagerDialog(self, self.data_manager)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_scheme_combo()
            self.refresh_chart()
    
    def open_gpu_manager(self):
        """打开GPU管理弹窗"""
        dialog = GPUManagerDialog(self, self.data_manager)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_chart()
    
    def open_task_manager(self):
        """打开任务管理弹窗"""
        dialog = TaskManagerDialog(self, self.data_manager)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_chart()
