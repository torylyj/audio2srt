"""
资源路径工具
用于处理开发环境和打包后环境的资源路径问题
"""

import os
import sys
import functools


def get_resource_path(relative_path: str) -> str:
    """
    获取资源的绝对路径
    
    在开发环境下，返回项目根目录下的资源路径
    在打包环境下，返回 PyInstaller 提取的资源路径
    
    Args:
        relative_path: 相对于项目根目录的资源路径
        
    Returns:
        资源的绝对路径
    """
    # 检查是否在打包环境中运行
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # 打包环境：资源在 _MEIPASS 目录中
        base_path = sys._MEIPASS
    else:
        # 开发环境：资源在项目根目录
        # 获取项目根目录（main.py 所在目录）
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)


def get_app_data_dir() -> str:
    """
    获取应用数据目录
    
    用于存储用户数据、模型缓存等
    
    Returns:
        应用数据目录路径
    """
    if getattr(sys, 'frozen', False):
        # 打包环境：使用系统应用数据目录
        app_name = "Audio2SRT"
    else:
        # 开发环境：使用项目目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, 'data')
    
    # 根据操作系统选择合适的目录
    if sys.platform == 'darwin':
        # macOS
        data_dir = os.path.expanduser(f"~/Library/Application Support/{app_name}")
    elif sys.platform == 'win32':
        # Windows
        data_dir = os.path.join(os.environ.get('APPDATA', ''), app_name)
    else:
        # Linux
        data_dir = os.path.expanduser(f"~/.local/share/{app_name}")
    
    # 确保目录存在
    os.makedirs(data_dir, exist_ok=True)
    
    return data_dir


def get_models_dir() -> str:
    """
    获取模型存储目录
    
    Returns:
        模型目录路径
    """
    models_dir = os.path.join(get_app_data_dir(), 'models')
    os.makedirs(models_dir, exist_ok=True)
    return models_dir


def get_temp_dir() -> str:
    """
    获取临时文件目录
    
    Returns:
        临时目录路径
    """
    import tempfile
    
    if getattr(sys, 'frozen', False):
        # 打包环境：使用系统临时目录
        temp_dir = os.path.join(tempfile.gettempdir(), 'Audio2SRT')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir
    else:
        # 开发环境：使用项目临时目录
        temp_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir


def is_frozen() -> bool:
    """
    检查是否在打包环境中运行
    
    Returns:
        True 表示在打包环境中，False 表示在开发环境中
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
