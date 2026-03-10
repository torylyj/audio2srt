"""
音频预处理模块
使用 PyAV (av) 处理音频，无需额外安装 FFmpeg
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

import av
import numpy as np


class AudioProcessor:
    """音频预处理器"""
    
    # 支持的输入格式
    SUPPORTED_FORMATS = {
        ".mp3", ".wav", ".mp4", ".m4a", ".mkv", ".avi",
        ".flac", ".ogg", ".wma", ".aac", ".webm", ".mov"
    }
    
    def __init__(self):
        self._temp_file: Optional[str] = None
    
    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """检查文件格式是否支持"""
        ext = Path(file_path).suffix.lower()
        return ext in cls.SUPPORTED_FORMATS
    
    @classmethod
    def get_supported_formats_string(cls) -> str:
        """获取支持格式的字符串描述"""
        formats = sorted([f.upper().replace(".", "") for f in cls.SUPPORTED_FORMATS])
        return ", ".join(formats)
    
    def get_audio_duration(self, file_path: str) -> float:
        """
        获取音频时长（秒）
        
        Args:
            file_path: 音频文件路径
        
        Returns:
            音频时长（秒）
        """
        try:
            with av.open(file_path) as container:
                if container.streams.audio:
                    stream = container.streams.audio[0]
                    if stream.duration and stream.time_base:
                        return float(stream.duration * stream.time_base)
                    # 备用方法：通过容器获取时长
                    if container.duration:
                        return container.duration / av.time_base
        except Exception:
            pass
        
        # 如果无法获取时长，返回估计值
        return 0.0
    
    def prepare_audio(self, file_path: str) -> str:
        """
        预处理音频文件
        faster-whisper 可以直接处理大多数格式，所以这里直接返回原文件路径
        
        Args:
            file_path: 输入音频/视频文件路径
        
        Returns:
            音频文件路径
        """
        # faster-whisper 使用 PyAV 可以直接处理多种格式
        # 不需要转换，直接返回原路径
        return file_path
    
    def cleanup(self) -> None:
        """清理临时文件"""
        if self._temp_file and os.path.exists(self._temp_file):
            try:
                os.remove(self._temp_file)
            except OSError:
                pass
            self._temp_file = None
    
    def __del__(self):
        self.cleanup()
