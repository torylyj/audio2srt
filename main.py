#!/usr/bin/env python3
"""
Audio2SRT - 音频字幕生成器
基于 Whisper 的高精度语音识别，生成 SRT 字幕文件

使用方法:
    python main.py

依赖安装:
    pip install -r requirements.txt
"""

import sys
import os
import traceback

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def setup_logging():
    """设置日志"""
    # 获取项目根目录
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    log_dir = os.path.join(base_path, 'data')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'audio2srt.log')
    
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def check_dependencies():
    """检查依赖是否已安装"""
    missing = []
    
    try:
        import customtkinter
    except ImportError as e:
        missing.append(f"customtkinter ({e})")
    
    try:
        import faster_whisper
    except ImportError as e:
        missing.append(f"faster-whisper ({e})")
    
    try:
        import av
    except ImportError as e:
        missing.append(f"av (PyAV) ({e})")
    
    if missing:
        print("缺少以下依赖:")
        for m in missing:
            print(f"  - {m}")
        print("\n请运行: pip install -r requirements.txt")
        return False
    
    return True


def main():
    """主函数"""
    logger = setup_logging()
    logger.info("Audio2SRT 启动中...")
    
    # 检查是否在打包环境中
    if hasattr(sys, 'frozen'):
        logger.info("运行在打包环境中")
    else:
        logger.info("运行在开发环境中")
    
    # 检查依赖
    if not check_dependencies():
        logger.error("依赖检查失败")
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 尝试启动GUI
    try:
        logger.info("正在导入GUI模块...")
        from gui.main_window import MainWindow
        
        logger.info("正在初始化主窗口...")
        app = MainWindow()
        
        logger.info("正在启动主循环...")
        app.mainloop()
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        print(f"\n错误: {e}")
        print("\n详细信息:")
        traceback.print_exc()
        
        # 写入日志文件
        with open(os.path.join(os.path.dirname(__file__), 'data', 'error.log'), 'w', encoding='utf-8') as f:
            traceback.print_exc(file=f)
        
        print(f"\n错误日志已保存到: data/error.log")
        input("\n按回车键退出...")
        sys.exit(1)
    
    logger.info("Audio2SRT 已退出")


if __name__ == "__main__":
    main()
