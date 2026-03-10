#!/usr/bin/env python3
"""
Audio2SRT 本地模型下载工具
用于下载 faster-whisper 模型到本地

使用方法:
    python download_model.py [model_size]

示例:
    python download_model.py medium  # 下载 medium 模型
    python download_model.py small   # 下载 small 模型
    python download_model.py tiny    # 下载 tiny 模型
"""

import os
import sys
from typing import Optional


# 模型信息
MODELS = {
    "tiny": {
        "name": "Tiny",
        "size": "~75 MB",
        "description": "最快，最不准确，适合测试",
        "repo_id": "Systran/faster-whisper-tiny"
    },
    "base": {
        "name": "Base",
        "size": "~145 MB",
        "description": "快速，较低准确度",
        "repo_id": "Systran/faster-whisper-base"
    },
    "small": {
        "name": "Small",
        "size": "~465 MB",
        "description": "平衡速度和准确度（推荐）",
        "repo_id": "Systran/faster-whisper-small"
    },
    "medium": {
        "name": "Medium",
        "size": "~1.5 GB",
        "description": "较慢，高准确度",
        "repo_id": "Systran/faster-whisper-medium"
    },
    "large-v3": {
        "name": "Large v3",
        "size": "~3 GB",
        "description": "最慢，最高准确度",
        "repo_id": "Systran/faster-whisper-large-v3"
    }
}


def get_models_dir() -> str:
    """获取模型存储目录"""
    # 获取项目根目录
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    models_dir = os.path.join(base_path, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    return models_dir


def download_model(model_size: str, show_progress: bool = True) -> bool:
    """
    下载模型
    
    Args:
        model_size: 模型大小 (tiny, base, small, medium, large-v3)
        show_progress: 是否显示进度
    
    Returns:
        是否成功
    """
    from huggingface_hub import snapshot_download
    from tqdm import tqdm
    
    if model_size not in MODELS:
        print(f"错误: 未知模型大小 '{model_size}'")
        print(f"可用模型: {', '.join(MODELS.keys())}")
        return False
    
    model_info = MODELS[model_size]
    repo_id = model_info["repo_id"]
    
    print(f"\n开始下载 {model_info['name']} 模型...")
    print(f"大小: {model_info['size']}")
    print(f"描述: {model_info['description']}")
    print(f"仓库: {repo_id}")
    print()
    
    # 模型保存目录
    models_dir = get_models_dir()
    target_dir = os.path.join(models_dir, model_size)
    
    # 检查是否已存在
    if os.path.exists(target_dir):
        # 检查是否有模型文件
        existing_files = os.listdir(target_dir)
        if any(f.endswith('.bin') for f in existing_files):
            print(f"模型已存在于: {target_dir}")
            response = input("是否重新下载? (y/n): ").strip().lower()
            if response != 'y':
                print("取消下载")
                return True
            # 删除旧目录
            import shutil
            shutil.rmtree(target_dir)
    
    # 创建进度条回调
    class ProgressCallback(tqdm):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
        
        def update(self, n=1):
            super().update(n)
    
    try:
        # 下载模型
        print("正在下载，请稍候...")
        
        if show_progress:
            model_path = snapshot_download(
                repo_id=repo_id,
                allow_patterns=["*.bin", "*.json", "*.txt", "config.json", "model.bin", 
                              "vocabulary.*", "tokenizer.*"],
                tqdm_class=ProgressCallback
            )
        else:
            model_path = snapshot_download(
                repo_id=repo_id,
                allow_patterns=["*.bin", "*.json", "*.txt", "config.json", "model.bin", 
                              "vocabulary.*", "tokenizer.*"]
            )
        
        # 移动到目标目录
        if model_path != target_dir:
            import shutil
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.move(model_path, target_dir)
        
        print(f"\n✓ 模型下载成功!")
        print(f"  保存位置: {target_dir}")
        print(f"\n模型将自动被 Audio2SRT 使用")
        
        return True
        
    except Exception as e:
        print(f"\n✗ 下载失败: {e}")
        return False


def list_models():
    """列出所有可用模型"""
    print("\n可用模型:")
    print("-" * 60)
    for size, info in MODELS.items():
        print(f"{size:12} | {info['size']:12} | {info['description']}")
    print("-" * 60)


def main():
    """主函数"""
    print("=" * 60)
    print("Audio2SRT 模型下载工具")
    print("=" * 60)
    
    # 获取模型目录
    models_dir = get_models_dir()
    print(f"\n模型将保存到: {models_dir}")
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        model_size = sys.argv[1].lower()
    else:
        # 显示模型列表，让用户选择
        print("\n请选择要下载的模型:")
        print()
        for i, (size, info) in enumerate(MODELS.items(), 1):
            print(f"  {i}. {info['name']:12} - {info['size']:12} - {info['description']}")
        print()
        
        try:
            choice = input("请输入编号 (1-5): ").strip()
            choice = int(choice)
            if choice < 1 or choice > 5:
                print("无效选择")
                sys.exit(1)
            model_size = list(MODELS.keys())[choice - 1]
        except ValueError:
            print("请输入有效的数字")
            sys.exit(1)
    
    # 下载模型
    success = download_model(model_size)
    
    if not success:
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("完成!")
print("=" * 60)


if __name__ == "__main__":
    main()
