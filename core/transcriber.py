"""
语音转录服务
基于 faster-whisper 实现高精度语音识别
支持本地模型路径
"""

import os
import threading
from typing import Callable, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from faster_whisper import WhisperModel

from core.audio_processor import AudioProcessor
from core.srt_generator import SRTGenerator


class ModelSize(Enum):
    """Whisper模型大小"""
    TINY = "tiny"
    BASE = "base"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large-v3"
    
    @property
    def repo_id(self) -> str:
        """获取HuggingFace仓库ID"""
        repo_map = {
            "tiny": "Systran/faster-whisper-tiny",
            "base": "Systran/faster-whisper-base",
            "small": "Systran/faster-whisper-small",
            "medium": "Systran/faster-whisper-medium",
            "large-v3": "Systran/faster-whisper-large-v3",
        }
        return repo_map.get(self.value, f"Systran/faster-whisper-{self.value}")
    
    @property
    def size_mb(self) -> int:
        """模型大小（MB）"""
        size_map = {
            "tiny": 75,
            "base": 145,
            "small": 465,
            "medium": 1500,
            "large-v3": 3000,
        }
        return size_map.get(self.value, 1000)


class Language(Enum):
    """支持的语言"""
    AUTO = None           # 自动检测
    CHINESE = "zh"        # 中文
    ENGLISH = "en"        # 英文


@dataclass
class TranscribeResult:
    """转录结果"""
    segments: List[Tuple[float, float, str]]  # (start, end, text)
    srt_content: str
    detected_language: str
    duration: float


class TranscribeService:
    """语音转录服务"""
    
    # 默认模型路径（相对于应用目录）
    DEFAULT_MODEL_DIR = "models"
    
    def __init__(self):
        self._model: Optional[WhisperModel] = None
        self._model_size: Optional[ModelSize] = None
        self._model_path: Optional[str] = None  # 本地模型路径
        self._audio_processor = AudioProcessor()
        self._cancel_flag = False
        self._lock = threading.Lock()
    
    def _get_default_model_path(self, model_size: ModelSize) -> str:
        """
        获取默认的本地模型路径
        
        查找顺序：
        1. ./models/{model_size}/ (项目目录)
        2. ./models/ (项目目录)
        3. None (使用默认的 HuggingFace 下载)
        """
        # 获取项目根目录
        import sys
        if getattr(sys, 'frozen', False):
            # 打包环境
            base_path = os.path.dirname(sys.executable)
        else:
            # 开发环境
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 检查 ./models/{model_size}/
        model_dir = os.path.join(base_path, "models", model_size.value)
        if os.path.isdir(model_dir):
            return model_dir
        
        # 检查 ./models/
        model_dir = os.path.join(base_path, "models")
        if os.path.isdir(model_dir):
            return model_dir
        
        return None
    
    def _check_model_cached(self, model_size: ModelSize) -> bool:
        """检查模型是否已缓存"""
        try:
            from huggingface_hub import try_to_load_from_cache
            result = try_to_load_from_cache(
                repo_id=model_size.repo_id,
                filename="model.bin"
            )
            return result is not None
        except Exception:
            return False
    
    def _download_model(
        self,
        model_size: ModelSize,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> str:
        """
        下载模型并显示进度
        """
        from tqdm import tqdm
        from huggingface_hub import snapshot_download
        
        repo_id = model_size.repo_id
        
        if progress_callback:
            progress_callback(0, f"检查模型 {model_size.value}...")
        
        # 自定义进度条
        class ProgressCallback(tqdm):
            def __init__(self, *args, **kwargs):
                self._callback = kwargs.pop('progress_callback', None)
                super().__init__(*args, **kwargs)
            
            def update(self, n=1):
                super().update(n)
                if self._callback and self.total:
                    percent = (self.n / self.total) * 100
                    downloaded_mb = self.n / 1024 / 1024
                    total_mb = self.total / 1024 / 1024
                    self._callback(
                        percent,
                        f"下载模型中... {downloaded_mb:.1f}MB / {total_mb:.1f}MB ({percent:.0f}%)"
                    )
        
        original_tqdm = None
        if progress_callback:
            import huggingface_hub.file_download as fd
            original_tqdm = getattr(fd, 'tqdm', None)
            
            def custom_tqdm(*args, **kwargs):
                kwargs['progress_callback'] = progress_callback
                return ProgressCallback(*args, **kwargs)
            
            fd.tqdm = custom_tqdm
        
        try:
            if progress_callback:
                progress_callback(5, f"正在下载 {model_size.value} 模型 (~{model_size.size_mb}MB)...")
            
            model_path = snapshot_download(
                repo_id=repo_id,
                allow_patterns=["*.bin", "*.json", "*.txt", "config.json", "model.bin", 
                              "vocabulary.*", "tokenizer.*"],
            )
            
            if progress_callback:
                progress_callback(100, "模型下载完成")
            
            return model_path
            
        finally:
            if original_tqdm is not None:
                import huggingface_hub.file_download as fd
                fd.tqdm = original_tqdm
    
    def load_model(
        self,
        model_size: ModelSize = ModelSize.MEDIUM,
        device: str = "auto",
        compute_type: str = "auto",
        progress_callback: Optional[Callable[[float, str], None]] = None,
        local_model_path: Optional[str] = None
    ) -> None:
        """
        加载Whisper模型
        
        Args:
            model_size: 模型大小
            device: 运行设备 ("auto", "cuda", "cpu")
            compute_type: 计算精度 ("auto", "float16", "int8")
            progress_callback: 进度回调函数 (percent, message)
            local_model_path: 本地模型路径（可选）
                              - 如果指定，将直接从该路径加载模型
                              - 如果为 None，将使用默认路径或从 HuggingFace 下载
        """
        # 如果已加载相同模型，直接返回
        if self._model is not None and self._model_size == model_size and self._model_path == local_model_path:
            if progress_callback:
                progress_callback(100, "模型已就绪")
            return
        
        # 优先使用用户指定的本地模型路径
        model_path_to_use = local_model_path
        
        if model_path_to_use is None:
            # 尝试使用默认的本地模型路径
            model_path_to_use = self._get_default_model_path(model_size)
        
        # 检查本地模型是否存在
        local_model_exists = False
        if model_path_to_use and os.path.isdir(model_path_to_use):
            # 检查目录中是否有模型文件
            model_files = os.listdir(model_path_to_use)
            # faster-whisper 模型通常包含 .bin 文件
            if any(f.endswith('.bin') for f in model_files):
                local_model_exists = True
                if progress_callback:
                    progress_callback(20, f"找到本地模型: {model_path_to_use}")
        
        if local_model_exists:
            # 使用本地模型
            if progress_callback:
                progress_callback(50, f"正在加载本地模型...")
            
            # 根据设备自动选择计算类型
            if compute_type == "auto":
                if device == "cuda":
                    compute_type = "float16"
                else:
                    compute_type = "int8"
            
            if progress_callback:
                progress_callback(85, "正在初始化模型...")
            
            self._model = WhisperModel(
                model_path_to_use,  # 传入本地路径
                device=device,
                compute_type=compute_type
            )
            self._model_size = model_size
            self._model_path = model_path_to_use
            
            if progress_callback:
                progress_callback(100, "本地模型加载完成")
        else:
            # 使用 HuggingFace 下载模型
            # 检查是否已缓存
            is_cached = self._check_model_cached(model_size)
            
            if is_cached:
                if progress_callback:
                    progress_callback(50, f"正在加载 {model_size.value} 模型...")
            else:
                if progress_callback:
                    progress_callback(0, f"首次使用，正在下载 {model_size.value} 模型...")
                # 下载模型
                self._download_model(model_size, progress_callback)
                if progress_callback:
                    progress_callback(80, "下载完成，正在加载模型...")
            
            # 根据设备自动选择计算类型
            if compute_type == "auto":
                if device == "cuda":
                    compute_type = "float16"
                else:
                    compute_type = "int8"
            
            if progress_callback:
                progress_callback(85, "正在初始化模型...")
            
            self._model = WhisperModel(
                model_size.value,
                device=device,
                compute_type=compute_type
            )
            self._model_size = model_size
            self._model_path = None
            
            if progress_callback:
                progress_callback(100, "模型加载完成，准备就绪")

    def transcribe(
        self,
        file_path: str,
        language: Language = Language.AUTO,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> TranscribeResult:
        """
        转录音频文件
        """
        if self._model is None:
            raise RuntimeError("模型未加载，请先调用 load_model()")
        
        if not AudioProcessor.is_supported(file_path):
            raise ValueError(
                f"不支持的文件格式。支持的格式: {AudioProcessor.get_supported_formats_string()}"
            )
        
        self._cancel_flag = False
        
        # 步骤1: 预处理音频
        if progress_callback:
            progress_callback(0, "正在处理音频...")
        
        audio_path = self._audio_processor.prepare_audio(file_path)
        duration = self._audio_processor.get_audio_duration(file_path)
        
        if self._cancel_flag:
            self._audio_processor.cleanup()
            raise Exception("转录已取消")
        
        # 步骤2: 执行转录
        if progress_callback:
            progress_callback(5, "正在识别语音...")
        
        segments_generator, info = self._model.transcribe(
            audio_path,
            language=language.value,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
            )
        )
        
        # 收集结果并更新进度
        segments = []
        detected_language = info.language
        
        for segment in segments_generator:
            if self._cancel_flag:
                self._audio_processor.cleanup()
                raise Exception("转录已取消")
            
            segments.append((segment.start, segment.end, segment.text))
            
            # 计算进度 (5% 到 95%)
            if duration > 0 and progress_callback:
                progress = 5 + (segment.end / duration) * 90
                progress = min(progress, 95)
                progress_callback(progress, f"正在识别... {int(progress)}%")
        
        # 步骤3: 生成SRT
        if progress_callback:
            progress_callback(95, "正在生成字幕...")
        
        srt_content = SRTGenerator.generate(segments)
        
        # 清理临时文件
        self._audio_processor.cleanup()
        
        if progress_callback:
            progress_callback(100, "完成")
        
        return TranscribeResult(
            segments=segments,
            srt_content=srt_content,
            detected_language=detected_language,
            duration=duration
        )
    
    def cancel(self) -> None:
        """取消当前转录任务"""
        with self._lock:
            self._cancel_flag = True
    
    def is_model_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self._model is not None
    
    def get_loaded_model_size(self) -> Optional[ModelSize]:
        """获取当前加载的模型大小"""
        return self._model_size
    
    @staticmethod
    def check_cuda_available() -> bool:
        """检查CUDA是否可用（通过 ctranslate2）"""
        try:
            import ctranslate2
            return ctranslate2.get_cuda_device_count() > 0
        except Exception:
            return False
