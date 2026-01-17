"""
图表组件 - 使用QPainter绘制GPU显存使用情况
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (QPainter, QColor, QFont, QPen, QBrush, QFontMetrics, QLinearGradient)


class ChartWidget(QWidget):
    """自定义图表组件 - 使用QPainter绘制"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.setStyleSheet("background-color: #FFFFFF;")
        
        # 数据
        self.gpu_names = []
        self.total_memories = []
        self.task_breakdown = []  # 每个GPU的任务分解
        self.task_color_map = {}
        
        # 固定参数
        self.bar_height_px = 42  # 增加柱子高度
        self.spacing_px = 12
        self.left_margin = 100
        self.top_margin = 40
        self.right_margin = 120
        self.bottom_margin = 30
        
    def set_data(self, gpu_names, total_memories, task_breakdown, task_color_map):
        """设置图表数据"""
        self.gpu_names = gpu_names
        self.total_memories = total_memories
        self.task_breakdown = task_breakdown
        self.task_color_map = task_color_map
        self.update()
    
    def paintEvent(self, event):
        """绘制图表"""
        if not self.gpu_names:
            # 绘制空状态提示
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
            painter.setPen(QColor("#90A4AE"))
            painter.drawText(self.rect(), Qt.AlignCenter, "暂无GPU数据")
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        width = self.width()
        height = self.height()
        
        # 计算x轴比例
        max_memory = max(self.total_memories) if self.total_memories else 100
        x_scale = (width - self.left_margin - self.right_margin) / (max_memory * 1.1)
        
        # 计算总高度
        total_height = (self.top_margin + 
                       len(self.gpu_names) * (self.bar_height_px + self.spacing_px) - 
                       self.spacing_px + self.bottom_margin)
        
        # 设置最小高度
        if total_height < height:
            total_height = height
        
        # 绘制标题 - 更优雅的样式
        title_font = QFont("Segoe UI", 16, QFont.Bold)
        painter.setFont(title_font)
        painter.setPen(QColor("#263238"))
        title_text = "GPU显存使用情况"
        title_rect = painter.fontMetrics().boundingRect(title_text)
        painter.drawText(int(width // 2 - title_rect.width() // 2), 25, title_text)
        
        # 定义标签字体（用于GPU名称和总显存）
        label_font = QFont("Segoe UI", 10)
        
        # 绘制每个GPU的柱子
        for gpu_idx in range(len(self.gpu_names)):
            y_center = (self.top_margin + 
                       gpu_idx * (self.bar_height_px + self.spacing_px) + 
                       self.bar_height_px / 2)
            y_top = y_center - self.bar_height_px / 2
            y_bottom = y_center + self.bar_height_px / 2
            
            # 绘制GPU名称
            painter.setFont(label_font)
            painter.setPen(QColor("#2C3E50"))
            metrics = QFontMetrics(label_font)
            text_width = metrics.width(self.gpu_names[gpu_idx])
            painter.drawText(int(self.left_margin - 10 - text_width), int(y_center + 5), 
                           self.gpu_names[gpu_idx])
            
            # 绘制总显存背景柱 - 更优雅的样式
            total_width_px = self.total_memories[gpu_idx] * x_scale
            # 使用渐变背景
            bg_gradient = QLinearGradient(self.left_margin, int(y_top), 
                                        self.left_margin, int(y_bottom))
            bg_gradient.setColorAt(0, QColor("#F8F9FA"))
            bg_gradient.setColorAt(1, QColor("#F0F2F5"))
            painter.setBrush(QBrush(bg_gradient))
            painter.setPen(QPen(QColor("#DEE2E6"), 1.5))
            painter.drawRoundedRect(self.left_margin, int(y_top), 
                                  int(total_width_px), self.bar_height_px, 4, 4)
            
            # 绘制任务分段
            current_x = self.left_margin
            for task_name, value in self.task_breakdown[gpu_idx].items():
                if value > 0:
                    segment_width_px = value * x_scale
                    start_x_px = current_x
                    end_x_px = current_x + segment_width_px
                    
                    # 绘制任务段 - 使用圆角和渐变
                    color = self.task_color_map.get(task_name, QColor("#cccccc"))
                    # 创建渐变效果
                    segment_gradient = QLinearGradient(int(start_x_px), int(y_top), 
                                                     int(start_x_px), int(y_bottom))
                    segment_gradient.setColorAt(0, color.lighter(110))
                    segment_gradient.setColorAt(1, color.darker(110))
                    painter.setBrush(QBrush(segment_gradient))
                    painter.setPen(QPen(QColor("#FFFFFF"), 2))
                    painter.drawRoundedRect(int(start_x_px), int(y_top), 
                                          int(segment_width_px), self.bar_height_px, 4, 4)
                    
                    # 显示任务名称和显存 - 黑色文字，简洁清晰
                    if segment_width_px > 60:
                        mid_x_px = (start_x_px + end_x_px) / 2
                        display_text = f'{task_name}：{value:.1f}GB'
                        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
                        metrics = QFontMetrics(painter.font())
                        text_width = metrics.width(display_text)
                        text_x = int(mid_x_px - text_width / 2)
                        
                        # 绘制文字 - 黑色，简洁清晰
                        painter.setPen(QColor("#000000"))
                        painter.drawText(text_x, int(y_center + 3), display_text)
                    
                    current_x = end_x_px
            
            # 显示总显存
            total_x_px = self.left_margin + total_width_px
            painter.setFont(label_font)
            painter.setPen(QColor("#5A6C7D"))
            total_text = f'{self.total_memories[gpu_idx]:.1f}GB'
            painter.drawText(int(total_x_px + 10), int(y_center + 5), total_text)
