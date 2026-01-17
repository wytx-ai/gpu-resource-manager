"""
GPU管理工具 - 打包成EXE文件的Python脚本
使用PyInstaller进行打包
"""
import os
import sys
import subprocess
import shutil

def check_pyinstaller():
    """检查PyInstaller是否已安装"""
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
        return True
    except ImportError:
        print("✗ PyInstaller 未安装")
        print("\n请先安装依赖:")
        print("  pip install -r requirements.txt")
        print("\n或者单独安装 PyInstaller:")
        print("  pip install pyinstaller")
        return False

def check_resources():
    """检查必要的资源文件是否存在"""
    resources = [
        "icons/gpu.png",
        "main.py",
        "data_manager.py",
        "ui/main_window.py",
    ]
    
    missing = []
    for resource in resources:
        if not os.path.exists(resource):
            missing.append(resource)
    
    if missing:
        print("✗ 缺少以下文件:")
        for f in missing:
            print(f"  - {f}")
        return False
    
    print("✓ 所有资源文件检查通过")
    return True

def build_exe():
    """执行打包"""
    print("\n开始打包...")
    print("=" * 50)
    
    # PyInstaller命令参数
    cmd = [
        "pyinstaller",
        "--name=GPU管理工具",
        "--onefile",  # 打包成单个exe文件
        "--windowed",  # 不显示控制台窗口
        "--icon=icons/gpu.png",  # 设置exe图标
        "--add-data=icons;icons",  # 包含图标文件夹（Windows格式：源路径;目标路径）
        "--hidden-import=PyQt5.QtCore",
        "--hidden-import=PyQt5.QtGui",
        "--hidden-import=PyQt5.QtWidgets",
        "--hidden-import=data_manager",
        "--hidden-import=ui.main_window",
        "--hidden-import=ui.chart_widget",
        "--hidden-import=ui.dialogs.scheme_manager_dialog",
        "--hidden-import=ui.dialogs.gpu_manager_dialog",
        "--hidden-import=ui.dialogs.task_manager_dialog",
        "--hidden-import=ui.dialogs.gpu_dialog",
        "--hidden-import=ui.dialogs.task_dialog",
        "--clean",  # 清理临时文件
        "main.py"
    ]
    
    try:
        # 执行打包命令
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ 打包成功！")
        print(f"\n生成的exe文件位置: dist/GPU管理工具.exe")
        return True
    except subprocess.CalledProcessError as e:
        print("✗ 打包失败！")
        print(f"错误信息: {e.stderr}")
        return False

def cleanup():
    """清理临时文件"""
    print("\n清理临时文件...")
    dirs_to_remove = ["build", "__pycache__"]
    files_to_remove = ["GPU管理工具.spec"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✓ 已删除: {dir_name}")
            except Exception as e:
                print(f"✗ 删除失败 {dir_name}: {e}")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
                print(f"✓ 已删除: {file_name}")
            except Exception as e:
                print(f"✗ 删除失败 {file_name}: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("GPU管理工具 - EXE打包工具")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("\n请安装依赖后再运行此脚本。")
        return
    
    # 检查资源文件
    if not check_resources():
        print("\n请确保所有必要的文件都存在后再试。")
        return
    
    # 执行打包
    if build_exe():
        print("\n" + "=" * 50)
        print("打包完成！")
        print("=" * 50)
        print("\n使用说明:")
        print("1. exe文件位于 dist 文件夹中")
        print("2. 首次运行时，程序会在exe同目录下创建 gpu_data.json")
        print("3. 可以将exe文件复制到任何位置运行")
        
        # 询问是否清理临时文件
        response = input("\n是否清理临时文件？(y/n): ").strip().lower()
        if response == 'y':
            cleanup()
    else:
        print("\n打包失败，请检查错误信息。")

if __name__ == "__main__":
    main()
