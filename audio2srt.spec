# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = [
    # CUDA DLLs for ctranslate2 GPU support
    (r'C:\Users\admin\AppData\Local\Programs\Python\Python313\Lib\site-packages\ctranslate2\cudnn64_9.dll', 'ctranslate2'),
    (r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cublas64_12.dll', '.'),
    (r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cublasLt64_12.dll', '.'),
    (r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cudart64_12.dll', '.'),
    (r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cufft64_11.dll', '.'),
    (r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\curand64_10.dll', '.'),
    (r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cusolver64_11.dll', '.'),
    (r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.8\bin\cusparse64_12.dll', '.'),
]
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
    excludes=['torch', 'torchvision', 'torchaudio', 'tensorflow', 'tensorboard', 'torch.distributed', 'torch.utils.tensorboard'],
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
    target_arch=None,
    codesign_identity=None,
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
