# -*- mode: python ; coding: utf-8 -*-
"""
Audio2SRT PyInstaller 配置文件
支持跨平台构建
"""

import os
import sys
import platform
from PyInstaller.utils.hooks import collect_all, collect_data_files

# 获取项目根目录
project_root = os.path.dirname(os.path.abspath(FILE))

# ============ 动态收集依赖 ============

# 收集 customtkinter 的所有数据
try:
    ctk_data = collect_all('customtkinter')
    ctk_datas = ctk_data[0]
    ctk_binaries = ctk_data[1]
    ctk_hiddenimports = ctk_data[2]
except Exception:
    ctk_datas = []
    ctk_binaries = []
    ctk_hiddenimports = []

# 收集 faster-whisper 的所有数据
try:
    fw_data = collect_all('faster_whisper')
    fw_datas = fw_data[0]
    fw_binaries = fw_data[1]
    fw_hiddenimports = fw_data[2]
except Exception:
    fw_datas = []
    fw_binaries = []
    fw_hiddenimports = []

# 收集 huggingface_hub 的数据
try:
    hf_datas = collect_data_files('huggingface_hub')
except Exception:
    hf_datas = []

# 收集 av (PyAV) 的数据
try:
    av_data = collect_all('av')
    av_datas = av_data[0]
    av_binaries = av_data[1]
    av_hiddenimports = av_data[2]
except Exception:
    av_datas = []
    av_binaries = []
    av_hiddenimports = []

# 合并所有数据
all_datas = ctk_datas + fw_datas + hf_datas + av_datas
all_binaries = ctk_binaries + fw_binaries + av_binaries
all_hiddenimports = (
    ctk_hiddenimports + 
    fw_hiddenimports + 
    av_hiddenimports + 
    [
        'faster_whisper',
        'ctranslate2',
        'huggingface_hub',
        'huggingface_hub.utils',
        'huggingface_hub.file_download',
        'huggingface_hub.snapshot_download',
        'av',
        'av.audio',
        'av.container',
        'numpy.core._methods',
        'numpy.lib.format',
    ]
)

# 排除不需要的模块（减小体积）
excludes = [
    'torch', 'torchvision', 'torchaudio',
    'tensorflow', 'tensorboard',
    'test', 'tests', 'pytest',
    'IPython', 'jupyter', 'notebook',
]

# ============ 确定目标架构 ============
# 获取当前系统架构
current_system = platform.system()
print(f"当前系统: {current_system}")

# Windows: 不需要特殊架构处理
# macOS: 根据错误信息，需要使用 --target-arch 或不指定（让PyInstaller自动选择）
# Linux: 不需要特殊处理

target_arch = None  # 让 PyInstaller 自动选择

# ============ 构建 Analysis ============
a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# ============ 创建 PYZ ============
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# ============ 创建 EXE ============
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Audio2SRT',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=target_arch,
    codesign_identity=None,
    entitlements_file=None,
)

# ============ 创建 COLLECT (生成文件夹模式) ============
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Audio2SRT',
)

# ============ 创建 BUNDLE (macOS app 模式，可选) ============
if current_system == 'Darwin':
    app = BUNDLE(
        coll,
        name='Audio2SRT.app',
        info_plist={
            'CFBundleName': 'Audio2SRT',
            'CFBundleDisplayName': 'Audio2SRT',
            'CFBundleIdentifier': 'com.audio2srt.app',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundlePackageType': 'APPL',
            'CFBundleExecutable': 'Audio2SRT',
            'LSMinimumSystemVersion': '10.15',
            'NSHumanReadableCopyright': 'Copyright © 2024. All rights reserved.',
            'NSPrincipalClass': 'NSApplication',
            'LSApplicationCategoryType': 'public.app-category.utilities',
            'NSHighResolutionCapable': True,
            'NSAppTransportSecurity': {
                'NSAllowsArbitraryLoads': True
            },
        },
        icon=None,
        bundle_identifier=None,
    )
