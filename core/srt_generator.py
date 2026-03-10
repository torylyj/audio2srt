"""
SRT字幕文件生成器
支持按字数智能分行
"""

import re
from typing import List, Tuple, Optional
from utils.time_utils import seconds_to_srt_time

# 中文标点断行优先级
_CN_BREAK_PUNCTUATION = "。！？；、，：）」》】"
# 英文标点断行
_EN_BREAK_PUNCTUATION = ".!?;,)"


class SRTGenerator:
    """SRT字幕生成器"""
    
    @staticmethod
    def _split_line(text: str, max_chars: int) -> str:
        """
        智能分行：将超长文本分为最多2行
        
        策略优先级：
        1. 在中文标点处断行
        2. 在英文空格/标点处断行
        3. 强制按字数断行
        
        Args:
            text: 原始字幕文本
            max_chars: 单行最大字符数
        
        Returns:
            分行后的文本（用\\n连接）
        """
        text = text.strip()
        
        # 不超过限制，直接返回
        if len(text) <= max_chars:
            return text
        
        best_break = -1
        mid = len(text) // 2
        
        # 策略1: 在中文标点处寻找最接近中间的断点
        for i, ch in enumerate(text):
            if ch in _CN_BREAK_PUNCTUATION and i > 0:
                if best_break == -1 or abs(i - mid) < abs(best_break - mid):
                    best_break = i
        
        if best_break > 0:
            line1 = text[:best_break + 1].strip()
            line2 = text[best_break + 1:].strip()
            if line1 and line2:
                return f"{line1}\n{line2}"
        
        # 策略2: 在英文空格处寻找最接近中间的断点
        best_break = -1
        for i, ch in enumerate(text):
            if ch == ' ' and i > 0:
                if best_break == -1 or abs(i - mid) < abs(best_break - mid):
                    best_break = i
        
        if best_break > 0:
            line1 = text[:best_break].strip()
            line2 = text[best_break + 1:].strip()
            if line1 and line2:
                return f"{line1}\n{line2}"
        
        # 策略3: 在英文标点处寻找
        best_break = -1
        for i, ch in enumerate(text):
            if ch in _EN_BREAK_PUNCTUATION and i > 0:
                if best_break == -1 or abs(i - mid) < abs(best_break - mid):
                    best_break = i
        
        if best_break > 0:
            line1 = text[:best_break + 1].strip()
            line2 = text[best_break + 1:].strip()
            if line1 and line2:
                return f"{line1}\n{line2}"
        
        # 策略4: 强制在max_chars处断行
        line1 = text[:max_chars].strip()
        line2 = text[max_chars:].strip()
        if line1 and line2:
            return f"{line1}\n{line2}"
        
        return text
    
    @staticmethod
    def generate(
        segments: List[Tuple[float, float, str]], 
        max_chars_per_line: Optional[int] = None
    ) -> str:
        """
        从识别结果生成SRT格式字幕
        
        Args:
            segments: 字幕片段列表，每个元素为 (start_time, end_time, text)
            max_chars_per_line: 单行最大字符数，None表示不限制
        
        Returns:
            SRT格式的字幕字符串
        """
        srt_content = []
        index = 0
        
        for start, end, text in segments:
            # 清理文本（去除首尾空白）
            text = text.strip()
            if not text:
                continue
            
            index += 1
            
            # 智能分行
            if max_chars_per_line and max_chars_per_line > 0:
                text = SRTGenerator._split_line(text, max_chars_per_line)
            
            # 构建SRT条目
            start_time = seconds_to_srt_time(start)
            end_time = seconds_to_srt_time(end)
            
            srt_entry = f"{index}\n{start_time} --> {end_time}\n{text}\n"
            srt_content.append(srt_entry)
        
        return "\n".join(srt_content)
    
    @staticmethod
    def save(content: str, file_path: str, encoding: str = "utf-8") -> None:
        """
        保存SRT内容到文件
        
        Args:
            content: SRT字幕内容
            file_path: 保存路径
            encoding: 文件编码，默认UTF-8
        """
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
