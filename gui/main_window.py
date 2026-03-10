"""
主窗口
整合所有GUI组件，实现完整的用户界面
"""

import os
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

import customtkinter as ctk

from gui.components.file_selector import FileSelector
from gui.components.settings_panel import SettingsPanel
from gui.components.progress_bar import ProgressPanel
from core.transcriber import TranscribeService, TranscribeResult
from utils.time_utils import format_duration


# 自定义颜色主题
COLORS = {
    "primary": "#6366f1",       # 主色调 - 靛蓝色
    "primary_hover": "#4f46e5",
    "secondary": "#8b5cf6",     # 次要色 - 紫色
    "success": "#10b981",       # 成功 - 绿色
    "warning": "#f59e0b",       # 警告 - 橙色
    "error": "#ef4444",         # 错误 - 红色
    "bg_dark": "#1e1e2e",       # 深色背景
    "bg_card": "#2d2d3d",       # 卡片背景
    "text": "#e2e8f0",          # 主文字
    "text_secondary": "#94a3b8", # 次要文字
}


class MainWindow(ctk.CTk):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 窗口配置
        self.title("Audio2SRT - 智能字幕生成器")
        self.geometry("750x820")
        self.minsize(650, 720)
        
        # 设置深色主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 设置窗口背景色
        self.configure(fg_color=COLORS["bg_dark"])
        
        # 初始化服务
        self._transcribe_service = TranscribeService()
        self._is_processing = False
        self._current_result: Optional[TranscribeResult] = None
        
        # 设置UI
        self._setup_ui()
        
        # 窗口关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_card(self, parent, **kwargs) -> ctk.CTkFrame:
        """创建卡片容器"""
        return ctk.CTkFrame(
            parent,
            fg_color=COLORS["bg_card"],
            corner_radius=12,
            **kwargs
        )
    
    def _setup_ui(self):
        """设置UI布局"""
        # 主容器 - 使用滚动容器
        main_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=COLORS["primary"],
            scrollbar_button_hover_color=COLORS["primary_hover"]
        )
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ===== 标题区域 =====
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        # 图标和标题
        title_label = ctk.CTkLabel(
            header_frame,
            text="🎬 Audio2SRT",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS["text"]
        )
        title_label.pack()
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="基于 AI 的智能语音转字幕工具",
            font=ctk.CTkFont(size=13),
            text_color=COLORS["text_secondary"]
        )
        subtitle_label.pack(pady=(5, 0))
        
        # ===== 文件选择卡片 =====
        file_card = self._create_card(main_frame)
        file_card.pack(fill="x", pady=(0, 15))
        
        self._file_selector = FileSelector(
            file_card,
            on_file_selected=self._on_file_selected
        )
        self._file_selector.pack(fill="x", padx=5, pady=5)
        
        # ===== 设置卡片 =====
        settings_card = self._create_card(main_frame)
        settings_card.pack(fill="x", pady=(0, 15))
        
        self._settings_panel = SettingsPanel(settings_card)
        self._settings_panel.pack(fill="x", padx=5, pady=5)
        
        # ===== 操作按钮区域 =====
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15))
        
        # 转录按钮
        self._transcribe_btn = ctk.CTkButton(
            btn_frame,
            text="🚀 开始转录",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            corner_radius=10,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self._start_transcribe
        )
        self._transcribe_btn.pack(fill="x")
        
        # 取消按钮（初始隐藏）
        self._cancel_btn = ctk.CTkButton(
            btn_frame,
            text="⏹ 取消",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            corner_radius=10,
            fg_color=COLORS["error"],
            hover_color="#dc2626",
            command=self._cancel_transcribe
        )
        
        # ===== 进度卡片 =====
        progress_card = self._create_card(main_frame)
        progress_card.pack(fill="x", pady=(0, 15))
        
        self._progress_panel = ProgressPanel(progress_card)
        self._progress_panel.pack(fill="x", padx=5, pady=5)
        
        # ===== 预览卡片 =====
        preview_card = self._create_card(main_frame)
        preview_card.pack(fill="both", expand=True, pady=(0, 15))
        
        preview_header = ctk.CTkFrame(preview_card, fg_color="transparent")
        preview_header.pack(fill="x", padx=15, pady=(15, 10))
        
        preview_title = ctk.CTkLabel(
            preview_header,
            text="📝 字幕预览",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"]
        )
        preview_title.pack(side="left")
        
        # 保存按钮
        self._save_btn = ctk.CTkButton(
            preview_header,
            text="💾 保存SRT",
            width=100,
            height=32,
            corner_radius=8,
            fg_color=COLORS["success"],
            hover_color="#059669",
            state="disabled",
            command=self._save_srt
        )
        self._save_btn.pack(side="right")
        
        # 预览文本框
        self._preview_text = ctk.CTkTextbox(
            preview_card,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
            height=200,
            corner_radius=8,
            fg_color="#1a1a2e",
            text_color=COLORS["text"],
            border_width=1,
            border_color=COLORS["bg_card"]
        )
        self._preview_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # ===== 状态栏 =====
        status_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        status_frame.pack(fill="x")
        
        self._status_bar = ctk.CTkLabel(
            status_frame,
            text="✨ 准备就绪 | 首次使用将自动下载AI模型",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        self._status_bar.pack(anchor="w")
    
    def _on_file_selected(self, file_path: str):
        """文件选择回调"""
        # 清空预览
        self._preview_text.delete("0.0", "end")
        self._save_btn.configure(state="disabled")
        self._current_result = None
        
        # 更新状态栏
        file_name = Path(file_path).name
        self._status_bar.configure(text=f"📁 已选择: {file_name}")
    
    def _start_transcribe(self):
        """开始转录"""
        # 检查文件是否已选择
        file_path = self._file_selector.get_selected_file()
        if not file_path:
            messagebox.showwarning("提示", "请先选择音频/视频文件")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在，请重新选择")
            return
        
        # 切换到处理状态
        self._set_processing_state(True)
        
        # 在后台线程执行转录
        thread = threading.Thread(target=self._do_transcribe, args=(file_path,))
        thread.daemon = True
        thread.start()
    
    def _do_transcribe(self, file_path: str):
        """执行转录（后台线程）"""
        try:
            # 获取设置
            model_size = self._settings_panel.get_model_size()
            language = self._settings_panel.get_language()
            device = self._settings_panel.get_device()
            
            # 加载模型（带进度显示）
            self._transcribe_service.load_model(
                model_size=model_size,
                device=device,
                progress_callback=lambda p, msg: self._update_ui(
                    lambda: self._progress_panel.update_progress(p, msg)
                )
            )
            
            # 重置进度条准备转录
            self._update_ui(lambda: self._progress_panel.update_progress(0, "模型已就绪，开始转录..."))
            
            # 执行转录
            result = self._transcribe_service.transcribe(
                file_path,
                language=language,
                progress_callback=lambda p, s: self._update_ui(
                    lambda: self._progress_panel.update_progress(p, s)
                )
            )
            
            # 更新结果
            self._update_ui(lambda: self._show_result(result))
            
        except Exception as e:
            error_msg = str(e)
            self._update_ui(lambda: self._show_error(error_msg))
        
        finally:
            self._update_ui(lambda: self._set_processing_state(False))
    
    def _update_ui(self, func):
        """在主线程更新UI"""
        self.after(0, func)
    
    def _show_result(self, result: TranscribeResult):
        """显示转录结果"""
        self._current_result = result
        
        # 更新预览
        self._preview_text.delete("0.0", "end")
        self._preview_text.insert("0.0", result.srt_content)
        
        # 启用保存按钮
        self._save_btn.configure(state="normal")
        
        # 更新状态
        duration_str = format_duration(result.duration)
        segment_count = len(result.segments)
        lang_name = {"zh": "中文", "en": "英文"}.get(result.detected_language, result.detected_language)
        
        self._status_bar.configure(
            text=f"✅ 转录完成 | 时长: {duration_str} | 字幕段数: {segment_count} | 语言: {lang_name}"
        )
        
        self._progress_panel.set_complete()
    
    def _show_error(self, error_msg: str):
        """显示错误"""
        self._progress_panel.set_error(error_msg)
        self._status_bar.configure(text=f"❌ 转录失败: {error_msg[:50]}...")
        messagebox.showerror("转录失败", error_msg)
    
    def _cancel_transcribe(self):
        """取消转录"""
        self._transcribe_service.cancel()
        self._progress_panel.set_status("正在取消...")
        self._status_bar.configure(text="⏹ 正在取消...")
    
    def _save_srt(self):
        """保存SRT文件"""
        if not self._current_result:
            return
        
        # 获取原文件名作为默认名称
        source_file = self._file_selector.get_selected_file()
        if source_file:
            default_name = Path(source_file).stem + ".srt"
        else:
            default_name = "subtitle.srt"
        
        # 选择保存路径
        file_path = filedialog.asksaveasfilename(
            title="保存字幕文件",
            defaultextension=".srt",
            initialfile=default_name,
            filetypes=[("SRT字幕文件", "*.srt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                from core.srt_generator import SRTGenerator
                SRTGenerator.save(self._current_result.srt_content, file_path)
                self._status_bar.configure(text=f"💾 已保存到: {Path(file_path).name}")
                messagebox.showinfo("成功", f"字幕文件已保存到:\n{file_path}")
            except Exception as e:
                messagebox.showerror("保存失败", str(e))
    
    def _set_processing_state(self, is_processing: bool):
        """设置处理状态"""
        self._is_processing = is_processing
        
        if is_processing:
            self._transcribe_btn.pack_forget()
            self._cancel_btn.pack(fill="x")
            self._settings_panel.set_enabled(False)
            self._progress_panel.reset()
            self._status_bar.configure(text="⏳ 正在处理中...")
        else:
            self._cancel_btn.pack_forget()
            self._transcribe_btn.pack(fill="x")
            self._settings_panel.set_enabled(True)
    
    def _on_closing(self):
        """窗口关闭事件"""
        if self._is_processing:
            if messagebox.askyesno("确认", "正在处理中，确定要退出吗？"):
                self._transcribe_service.cancel()
                self.destroy()
        else:
            self.destroy()
