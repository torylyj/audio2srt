# -*- mode: python ; coding: utf-8 -*-
# macOS build spec - GPU support via Metal (no CUDA DLLs needed)
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['faster_whisper', 'ctranslate2', 'huggingface_hub', 'av']
tmp_ret = collect_all('customtkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('faster_whisper')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['torch', 'torchvision', 'torchaudio', 'tensorflow', 'tensorboard'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

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
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='universal2',
    codesign_identity='-',
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Audio2SRT',
)

# Create .app bundle
app = BUNDLE(
    coll,
    name='Audio2SRT.app',
    icon=None,
    bundle_identifier='com.audio2srt.app',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleName': 'Audio2SRT',
        'NSHighResolutionCapable': True,
    },
)
