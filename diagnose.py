#!/usr/bin/env python3
"""
Audio2SRT 诊断脚本
用于诊断界面无法打开的问题
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("Audio2SRT 诊断工具")
print("=" * 60)
print()

# 测试1: 检查依赖
print("[1/5] 检查依赖...")
try:
    import customtkinter
    print(f"  ✓ customtkinter: {customtkinter.__version__}")
except ImportError as e:
    print(f"  ✗ customtkinter: {e}")

try:
    import faster_whisper
    print(f"  ✓ faster_whisper: 已安装")
except ImportError as e:
    print(f"  ✗ faster_whisper: {e}")

try:
    import av
    print(f"  ✓ av (PyAV): 已安装")
except ImportError as e:
    print(f"  ✗ av (PyAV): {e}")

print()

# 测试2: 检查项目模块
print("[2/5] 检查项目模块...")
try:
    from core.transcriber import TranscribeService
    print("  ✓ core.transcriber")
except Exception as e:
    print(f"  ✗ core.transcriber: {e}")

try:
    from core.audio_processor import AudioProcessor
    print("  ✓ core.audio_processor")
except Exception as e:
    print(f"  ✗ core.audio_processor: {e}")

try:
    from core.srt_generator import SRTGenerator
    print("  ✓ core.srt_generator")
except Exception as e:
    print(f"  ✗ core.srt_generator: {e}")

print()

# 测试3: 检查GUI模块
print("[3/5] 检查GUI模块...")
try:
    from gui.components.file_selector import FileSelector
    print("  ✓ gui.components.file_selector")
except Exception as e:
    print(f"  ✗ gui.components.file_selector: {e}")

try:
    from gui.components.settings_panel import SettingsPanel
    print("  ✓ gui.components.settings_panel")
except Exception as e:
    print(f"  ✗ gui.components.settings_panel: {e}")

try:
    from gui.components.progress_bar import ProgressPanel
    print("  ✓ gui.components.progress_bar")
except Exception as e:
    print(f"  ✗ gui.components.progress_bar: {e}")

print()

# 测试4: 检查工具模块
print("[4/5] 检查工具模块...")
try:
    from utils.time_utils import format_duration
    print("  ✓ utils.time_utils")
except Exception as e:
    print(f"  ✗ utils.time_utils: {e}")

try:
    from utils.resource_path import get_app_data_dir
    print("  ✓ utils.resource_path")
except Exception as e:
    print(f"  ✗ utils.resource_path: {e}")

print()

# 测试5: 检查GUI主窗口
print("[5/5] 检查GUI主窗口...")
try:
    from gui.main_window import MainWindow
    print("  ✓ gui.main_window.MainWindow")
except Exception as e:
    print(f"  ✗ gui.main_window.MainWindow: {e}")
    import traceback
    traceback.print_exc()

print()

# 测试6: 检查models目录
print("[6/6] 检查models目录...")
models_dir = os.path.join(os.path.dirname(__file__), "models")
if os.path.isdir(models_dir):
    print(f"  ✓ models目录存在: {models_dir}")
    for item in os.listdir(models_dir):
        item_path = os.path.join(models_dir, item)
        if os.path.isdir(item_path):
            size = sum(os.path.getsize(os.path.join(dirpath, filename))
                      for dirpath, _, filenames in os.walk(item_path)
                      for filename in filenames)
            size_mb = size / (1024 * 1024)
            print(f"    - {item}: {size_mb:.1f} MB")
else:
    print(f"  ✗ models目录不存在: {models_dir}")

print()
print("=" * 60)
print("诊断完成")
print("=" * 60)
