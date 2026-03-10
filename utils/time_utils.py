"""
时间格式转换工具
"""


def seconds_to_srt_time(seconds: float) -> str:
    """
    将秒数转换为SRT时间格式
    
    Args:
        seconds: 秒数（浮点数）
    
    Returns:
        SRT时间格式字符串 (HH:MM:SS,mmm)
    
    Example:
        >>> seconds_to_srt_time(3661.5)
        '01:01:01,500'
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"


def format_duration(seconds: float) -> str:
    """
    将秒数格式化为可读的时长字符串
    
    Args:
        seconds: 秒数
    
    Returns:
        格式化的时长字符串
    
    Example:
        >>> format_duration(125)
        '2分5秒'
    """
    if seconds < 60:
        return f"{int(seconds)}秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        if secs > 0:
            return f"{minutes}分{secs}秒"
        return f"{minutes}分钟"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        if minutes > 0:
            return f"{hours}小时{minutes}分"
        return f"{hours}小时"
