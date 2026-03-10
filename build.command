#!/bin/bash
#
# Audio2SRT 快速构建脚本
# 用于在 macOS 上快速打包应用
#

set -e

echo "========================================"
echo "Audio2SRT macOS 快速构建"
echo "========================================"
echo ""

# 检查 Python 版本
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "Python 版本: $python_version"

# 检查是否在 macOS 上
if [ "$(uname)" != "Darwin" ]; then
    echo "警告: 此脚本应该在 macOS 上运行"
fi

# 创建虚拟环境
echo ""
echo "[1/5] 创建虚拟环境..."
if [ -d "venv" ]; then
    echo "虚拟环境已存在，跳过"
else
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo ""
echo "[2/5] 安装依赖..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# 清理旧构建
echo ""
echo "[3/5] 清理旧构建..."
rm -rf build dist
rm -f *.spec

# 构建应用
echo ""
echo "[4/5] 构建应用..."
pyinstaller main.py \
    --name=Audio2SRT \
    --windowed \
    --onedir \
    --clean \
    --noconfirm \
    --add-data="$(python3 -c 'import customtkinter; print(customtkinter.__path__[0])'):customtkinter" \
    --hidden-import=faster_whisper \
    --hidden-import=ctranslate2 \
    --hidden-import=huggingface_hub \
    --hidden-import=huggingface_hub.utils \
    --hidden-import=huggingface_hub.file_download \
    --hidden-import=av \
    --hidden-import=sklearn.utils._cython_blas \
    --hidden-import=sklearn.neighbors.typedefs \
    --collect-all=customtkinter \
    --collect-all=faster_whisper

# 验证构建结果
echo ""
echo "[5/5] 验证构建..."
if [ -d "dist/Audio2SRT.app" ]; then
    echo "构建成功!"
    echo ""
    echo "应用位置: $(pwd)/dist/Audio2SRT.app"
    echo ""
    echo "使用方法:"
    echo "  1. cp -r dist/Audio2SRT.app /Applications/"
    echo "  2. 双击运行 Audio2SRT.app"
else
    echo "构建失败，请检查错误信息"
    exit 1
fi

echo ""
echo "========================================"
echo "构建完成!"
echo "========================================"
