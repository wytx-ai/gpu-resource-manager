"""
GPU管理工具主程序 - PyQt5版本
程序入口文件
"""
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon
from PyQt5.QtGui import QIcon
from ui.main_window import GPUMainWindow


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 获取图标路径（相对于项目根目录）
    icon_path = os.path.join(os.path.dirname(__file__), "icons", "gpu.png")
    
    # 设置应用图标
    app.setWindowIcon(QIcon(icon_path))
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    # 检查系统托盘是否可用
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(None, "系统托盘", 
                            "系统托盘不可用，某些功能可能无法正常工作。")
    
    window = GPUMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
