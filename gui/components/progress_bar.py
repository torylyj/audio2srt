"""
进度显示组件
"""

import customtkinter as ctk
from typing import Optional


# 颜色定义
COLORS = {
    "primary": "#6366f1",
    "success": "#10b981",
    "error": "#ef4444",
    "text": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "bg_progress": "#1a1a2e",
}


class ProgressPanel(ctk.CTkFrame):
    """进度显示面板"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="📊 处理进度",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"]
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 8))
        
        # 进度条容器
        progress_container = ctk.CTkFrame(self, fg_color="transparent")
        progress_container.pack(fill="x", padx=10, pady=5)
        
        # 进度条
        self._progress_bar = ctk.CTkProgressBar(
            progress_container, 
            width=400, 
            height=20,
            corner_radius=10,
            fg_color=COLORS["bg_progress"],
            progress_color=COLORS["primary"]
        )
        self._progress_bar.pack(fill="x")
        self._progress_bar.set(0)
        
        # 进度百分比
        self._percent_label = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["primary"]
        )
        self._percent_label.pack(pady=(8, 5))
        
        # 状态文字
        self._status_label = ctk.CTkLabel(
            self,
            text="⏳ 等待开始...",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        self._status_label.pack(pady=(0, 10))
    
    def update_progress(self, progress: float, status: str = ""):
        """
        更新进度
        
        Args:
            progress: 进度值 (0-100)
            status: 状态文字
        """
        # 将0-100转换为0-1
        self._progress_bar.set(progress / 100.0)
        
        # 更新百分比显示
        self._percent_label.configure(text=f"{int(progress)}%")
        
        # 根据进度调整颜色
        if progress >= 100:
            self._progress_bar.configure(progress_color=COLORS["success"])
            self._percent_label.configure(text_color=COLORS["success"])
        else:
            self._progress_bar.configure(progress_color=COLORS["primary"])
            self._percent_label.configure(text_color=COLORS["primary"])
        
        if status:
            self._status_label.configure(text=status)
    
    def reset(self):
        """重置进度"""
        self._progress_bar.set(0)
        self._progress_bar.configure(progress_color=COLORS["primary"])
        self._percent_label.configure(text="0%", text_color=COLORS["primary"])
        self._status_label.configure(text="⏳ 等待开始...")
    
    def set_status(self, status: str):
        """仅设置状态文字"""
        self._status_label.configure(text=status)
    
    def set_complete(self):
        """设置为完成状态"""
        self._progress_bar.set(1)
        self._progress_bar.configure(progress_color=COLORS["success"])
        self._percent_label.configure(text="100%", text_color=COLORS["success"])
        self._status_label.configure(text="✅ 转录完成!")
    
    def set_error(self, error_msg: str):
        """设置错误状态"""
        self._progress_bar.configure(progress_color=COLORS["error"])
        self._percent_label.configure(text_color=COLORS["error"])
        self._status_label.configure(text=f"❌ 错误: {error_msg[:50]}...")
