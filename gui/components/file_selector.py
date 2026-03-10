"""
文件选择组件
"""

import customtkinter as ctk
from tkinter import filedialog
from typing import Callable, Optional

from core.audio_processor import AudioProcessor


# 颜色定义
COLORS = {
    "primary": "#6366f1",
    "primary_hover": "#4f46e5",
    "text": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "bg_input": "#1a1a2e",
}


class FileSelector(ctk.CTkFrame):
    """文件选择组件"""
    
    def __init__(
        self,
        master,
        on_file_selected: Optional[Callable[[str], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self._on_file_selected = on_file_selected
        self._selected_file: Optional[str] = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI"""
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="📁 选择文件",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"]
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 8))
        
        # 文件路径框架
        path_frame = ctk.CTkFrame(self, fg_color="transparent")
        path_frame.pack(fill="x", padx=10, pady=5)
        
        # 文件路径输入框
        self._path_entry = ctk.CTkEntry(
            path_frame,
            placeholder_text="点击浏览选择音频/视频文件...",
            state="readonly",
            height=40,
            corner_radius=8,
            fg_color=COLORS["bg_input"],
            border_color=COLORS["primary"],
            border_width=1,
            text_color=COLORS["text"]
        )
        self._path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # 浏览按钮
        browse_btn = ctk.CTkButton(
            path_frame,
            text="📂 浏览",
            width=90,
            height=40,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._browse_file
        )
        browse_btn.pack(side="right")
        
        # 支持格式提示
        formats = AudioProcessor.get_supported_formats_string()
        hint_label = ctk.CTkLabel(
            self,
            text=f"支持格式: {formats}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        hint_label.pack(anchor="w", padx=10, pady=(5, 10))
    
    def _browse_file(self):
        """打开文件选择对话框"""
        # 构建文件类型过滤器
        filetypes = [
            ("音视频文件", "*.mp3 *.wav *.mp4 *.m4a *.mkv *.avi *.flac *.ogg *.wma *.aac *.webm *.mov"),
            ("音频文件", "*.mp3 *.wav *.m4a *.flac *.ogg *.wma *.aac"),
            ("视频文件", "*.mp4 *.mkv *.avi *.webm *.mov"),
            ("所有文件", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(
            title="选择音频/视频文件",
            filetypes=filetypes
        )
        
        if file_path:
            self._selected_file = file_path
            
            # 更新显示
            self._path_entry.configure(state="normal")
            self._path_entry.delete(0, "end")
            self._path_entry.insert(0, file_path)
            self._path_entry.configure(state="readonly")
            
            # 触发回调
            if self._on_file_selected:
                self._on_file_selected(file_path)
    
    def get_selected_file(self) -> Optional[str]:
        """获取选中的文件路径"""
        return self._selected_file
    
    def clear(self):
        """清空选择"""
        self._selected_file = None
        self._path_entry.configure(state="normal")
        self._path_entry.delete(0, "end")
        self._path_entry.configure(state="readonly")
