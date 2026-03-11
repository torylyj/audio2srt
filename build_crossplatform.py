#!/usr/bin/env python3
"""
Audio2SRT 跨平台构建脚本
支持 Windows、macOS、Linux
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
    return result


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
    
    # 删除 spec 文件缓存
    for spec_file in ['audio2srt.spec', 'build', 'dist']:
        spec_cache = f"{spec_file}.cache"
        if os.path.exists(spec_cache):
            import shutil
            shutil.rmtree(spec_cache)
    
    print_info("清理完成")
    return True


def build_windows():
    """构建 Windows 版本"""
    print_info("开始构建 Windows 版本...")
    
    # 使用 spec 文件构建
    result = run_command([
        sys.executable, '-m', 'PyInstaller',
        'audio2srt.spec',
        '--clean',
        '--noconfirm'
    ], check=False)
    
    if result.returncode == 0:
        print_info("Windows 构建成功!")
        return True
    else:
        print_error(f"Windows 构建失败: {result.stderr}")
        return False


def build_macos():
    """构建 macOS 版本"""
    print_info("开始构建 macOS 版本...")
    
    # macOS 构建选项
    # 不指定 --target-arch，让 PyInstaller 自动选择
    # 如果需要构建 universal2，需要分别构建然后合并
    
    # 先尝试使用 onedir 模式
    result = run_command([
        sys.executable, '-m', 'PyInstaller',
        'main.py',
        '--name=Audio2SRT',
        '--windowed',
        '--onedir',
        '--clean',
        '--noconfirm',
        '--collect-all=customtkinter',
        '--collect-all=faster_whisper',
    ], check=False)
    
    if result.returncode == 0:
        print_info("macOS 构建成功!")
        return True
    else:
        print_error(f"macOS 构建失败: {result.stderr}")
        return False


def build_linux():
    """构建 Linux 版本"""
    print_info("开始构建 Linux 版本...")
    
    result = run_command([
        sys.executable, '-m', 'PyInstaller',
        'main.py',
        '--name=Audio2SRT',
        '--console',
        '--onedir',
        '--clean',
        '--noconfirm',
        '--collect-all=customtkinter',
        '--collect-all=faster_whisper',
    ], check=False)
    
    if result.returncode == 0:
        print_info("Linux 构建成功!")
        return True
    else:
        print_error(f"Linux 构建失败: {result.stderr}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("Audio2SRT 跨平台构建工具")
    print("=" * 60)
    
    # 检查 Python 版本
    if not check_python():
        sys.exit(1)
    
    # 获取当前系统
    current_system = platform.system()
    print_info(f"当前系统: {current_system}")
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 清理旧构建
    clean_build()
    
    # 根据系统选择构建方式
    success = False
    
    if current_system == 'Windows':
        success = build_windows()
    elif current_system == 'Darwin':
        success = build_macos()
    elif current_system == 'Linux':
        success = build_linux()
    else:
        print_error(f"不支持的系统: {current_system}")
        sys.exit(1)
    
    if success:
        print("=" * 60)
        print("构建完成!")
        print("=" * 60)
        print(f"输出目录: dist/")
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
