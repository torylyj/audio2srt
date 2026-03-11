#!/usr/bin/env python3
"""
Audio2SRT macOS 构建脚本
专门用于 macOS 平台打包
"""

import os
import sys
import subprocess
import platform


def print_info(msg):
    print(f"[INFO] {msg}")


def print_error(msg):
    print(f"[ERROR] {msg}")


def run_command(cmd, check=True):
    """运行命令"""
    print(f"执行: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=check)
    if result.returncode != 0:
        print_error(f"命令失败: {result.stderr}")
    return result


def check_macos():
    """检查是否为 macOS"""
    if platform.system() != 'Darwin':
        print_error("此脚本仅适用于 macOS 系统")
        return False
    print_info("检测到 macOS 系统")
    return True


def check_python():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.minor < 10):
        print_error(f"需要 Python 3.10+，当前版本: {version.major}.{version.minor}")
        return False
    print_info(f"Python 版本: {version.major}.{version.minor}")
    return True


def install_dependencies():
    """安装依赖"""
    print_info("安装构建依赖...")
    
    # 安装 PyInstaller
    try:
        import PyInstaller
        print_info("PyInstaller 已安装")
    except ImportError:
        print_info("安装 PyInstaller...")
        run_command([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
    
    return True


def clean_build():
    """清理构建文件"""
    print_info("清理旧构建...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            import shutil
            shutil.rmtree(dir_name)
    
    print_info("清理完成")
    return True


def check_models():
    """检查本地模型"""
    models_dir = "models"
    if not os.path.isdir(models_dir):
        print_info("未找到 models 目录，应用将自动下载模型")
        return False
    
    # 检查模型
    model_count = 0
    for item in os.listdir(models_dir):
        item_path = os.path.join(models_dir, item)
        if os.path.isdir(item_path):
            files = os.listdir(item_path)
            if any(f.endswith('.bin') for f in files):
                model_count += 1
                size = sum(os.path.getsize(os.path.join(dirpath, f))
                          for dirpath, _, filenames in os.walk(item_path)
                          for f in filenames)
                size_mb = size / (1024 * 1024)
                print_info(f"  - {item}: {size_mb:.1f} MB")
    
    if model_count > 0:
        print_info(f"找到 {model_count} 个本地模型")
        return True
    return False


def build_macos():
    """构建 macOS 应用"""
    print_info("开始构建 macOS 应用...")
    
    # 检查架构
    import subprocess
    arch_result = subprocess.run(['uname', '-m'], capture_output=True, text=True)
    arch = arch_result.stdout.strip()
    print_info(f"CPU 架构: {arch}")
    
    # 构建命令 - 使用 onedir 模式，避免 universal2 问题
    # 不指定 --target-arch，让 PyInstaller 自动选择当前架构
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        'main.py',
        '--name=Audio2SRT',
        '--windowed',          # GUI 应用，不显示控制台
        '--onedir',           # 目录模式（而不是单文件）
        '--clean',
        '--noconfirm',
        # 收集所有依赖
        '--collect-all=customtkinter',
        '--collect-all=faster-whisper',
        # 隐藏导入
        '--hidden-import=faster_whisper',
        '--hidden-import=ctranslate2',
        '--hidden-import=huggingface_hub',
        '--hidden-import=huggingface_hub.utils',
        '--hidden-import=huggingface_hub.file_download',
        '--hidden-import=huggingface_hub.snapshot_download',
        '--hidden-import=av',
        '--hidden-import=av.audio',
        '--hidden-import=av.container',
    ]
    
    print_info("运行 PyInstaller...")
    result = run_command(cmd, check=False)
    
    if result.returncode == 0:
        print_info("macOS 构建成功!")
        
        # 复制模型到应用（如果存在）
        if os.path.isdir("models"):
            import shutil
            target_dir = "dist/Audio2SRT.app/Contents/Resources/models"
            if os.path.exists("dist/Audio2SRT.app"):
                os.makedirs(target_dir, exist_ok=True)
                shutil.copytree("models", target_dir, dirs_exist_ok=True)
                print_info("模型已复制到应用中")
        
        return True
    else:
        print_error(f"macOS 构建失败")
        print_error(result.stderr)
        return False


def verify_build():
    """验证构建结果"""
    app_path = "dist/Audio2SRT.app"
    
    if not os.path.exists(app_path):
        print_error("应用未生成")
        return False
    
    # 检查必要文件
    required_files = [
        "Contents/MacOS/Audio2SRT",
        "Contents/Info.plist",
    ]
    
    for file_path in required_files:
        full_path = os.path.join(app_path, file_path)
        if not os.path.exists(full_path):
            print_error(f"缺少必要文件: {file_path}")
            return False
    
    # 计算大小
    size = sum(os.path.getsize(os.path.join(dirpath, f))
              for dirpath, _, filenames in os.walk(app_path)
              for f in filenames)
    size_mb = size / (1024 * 1024)
    
    print_info(f"应用构建成功!")
    print_info(f"  位置: {os.path.abspath(app_path)}")
    print_info(f"  大小: {size_mb:.1f} MB")
    
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("Audio2SRT macOS 构建工具")
    print("=" * 60)
    
    # 检查环境
    if not check_macos():
        sys.exit(1)
    
    if not check_python():
        sys.exit(1)
    
    # 检查模型
    has_models = check_models()
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 清理旧构建
    clean_build()
    
    # 构建
    if not build_macos():
        sys.exit(1)
    
    # 验证
    if not verify_build():
        sys.exit(1)
    
    print("=" * 60)
    print("构建完成!")
    print("=" * 60)
    print()
    print("使用方法:")
    print("  1. cp -r dist/Audio2SRT.app /Applications/")
    print("  2. 双击运行 Audio2SRT.app")
    print()
    if not has_models:
        print("注意: 首次运行将自动下载 Whisper 模型")
    print()


if __name__ == '__main__':
    main()
