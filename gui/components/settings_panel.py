"""
参数设置面板
"""

import customtkinter as ctk
from typing import Optional

from core.transcriber import ModelSize, Language, TranscribeService


# 颜色定义
COLORS = {
    "primary": "#6366f1",
    "text": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "success": "#10b981",
    "warning": "#f59e0b",
}


class SettingsPanel(ctk.CTkFrame):
    """参数设置面板"""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self._language_var = ctk.StringVar(value="auto")
        self._model_var = ctk.StringVar(value="medium")
        self._gpu_var = ctk.BooleanVar(value=False)
        
        self._setup_ui()
        self._check_gpu()
    
    def _setup_ui(self):
        """设置UI"""
        # 标题
        title_label = ctk.CTkLabel(
            self,
            text="⚙️ 转录设置",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text"]
        )
        title_label.pack(anchor="w", padx=10, pady=(10, 12))
        
        # 语言选择
        lang_frame = ctk.CTkFrame(self, fg_color="transparent")
        lang_frame.pack(fill="x", padx=10, pady=5)
        
        lang_label = ctk.CTkLabel(
            lang_frame, 
            text="🌐 识别语言:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"]
        )
        lang_label.pack(side="left", padx=(0, 15))
        
        languages = [
            ("自动检测", "auto"),
            ("中文", "zh"),
            ("英文", "en")
        ]
        
        for text, value in languages:
            rb = ctk.CTkRadioButton(
                lang_frame,
                text=text,
                variable=self._language_var,
                value=value,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text"],
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary"]
            )
            rb.pack(side="left", padx=8)
        
        # 模型大小选择
        model_frame = ctk.CTkFrame(self, fg_color="transparent")
        model_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        model_label = ctk.CTkLabel(
            model_frame, 
            text="🧠 模型大小:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"]
        )
        model_label.pack(side="left", padx=(0, 15))
        
        models = [
            ("tiny", "tiny"),
            ("base", "base"),
            ("small", "small"),
            ("medium", "medium"),
            ("large", "large-v3")
        ]
        
        for text, value in models:
            rb = ctk.CTkRadioButton(
                model_frame,
                text=text,
                variable=self._model_var,
                value=value,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text"],
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary"]
            )
            rb.pack(side="left", padx=6)
        
        # 模型说明
        model_hint = ctk.CTkLabel(
            self,
            text="💡 提示：模型越大精度越高但速度越慢，推荐使用 medium 或 large",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        model_hint.pack(anchor="w", padx=10, pady=(5, 8))
        
        # GPU加速选项
        gpu_frame = ctk.CTkFrame(self, fg_color="transparent")
        gpu_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self._gpu_checkbox = ctk.CTkCheckBox(
            gpu_frame,
            text="⚡ 启用GPU加速",
            variable=self._gpu_var,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text"],
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary"]
        )
        self._gpu_checkbox.pack(side="left")
        
        self._gpu_status = ctk.CTkLabel(
            gpu_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        self._gpu_status.pack(side="left", padx=10)
    
    def _check_gpu(self):
        """检查GPU可用性"""
        cuda_available = TranscribeService.check_cuda_available()
        
        if cuda_available:
            self._gpu_status.configure(text="✅ CUDA 可用", text_color=COLORS["success"])
            self._gpu_var.set(True)  # 默认启用
        else:
            self._gpu_status.configure(text="⚠️ CUDA 不可用，将使用CPU", text_color=COLORS["warning"])
            self._gpu_checkbox.configure(state="disabled")
            self._gpu_var.set(False)
    
    def get_language(self) -> Language:
        """获取选择的语言"""
        lang_map = {
            "auto": Language.AUTO,
            "zh": Language.CHINESE,
            "en": Language.ENGLISH
        }
        return lang_map.get(self._language_var.get(), Language.AUTO)
    
    def get_model_size(self) -> ModelSize:
        """获取选择的模型大小"""
        model_map = {
            "tiny": ModelSize.TINY,
            "base": ModelSize.BASE,
            "small": ModelSize.SMALL,
            "medium": ModelSize.MEDIUM,
            "large-v3": ModelSize.LARGE
        }
        return model_map.get(self._model_var.get(), ModelSize.MEDIUM)
    
    def get_device(self) -> str:
        """获取运行设备"""
        return "cuda" if self._gpu_var.get() else "cpu"
    
    def set_enabled(self, enabled: bool):
        """设置面板启用状态"""
        state = "normal" if enabled else "disabled"
        for child in self.winfo_children():
            self._set_widget_state(child, state)
    
    def _set_widget_state(self, widget, state):
        """递归设置组件状态"""
        try:
            # 保持GPU复选框的特殊状态
            if widget == self._gpu_checkbox and not TranscribeService.check_cuda_available():
                return
            widget.configure(state=state)
        except:
            pass
        
        for child in widget.winfo_children():
            self._set_widget_state(child, state)
