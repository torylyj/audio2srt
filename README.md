# Audio2SRT - 智能语音转字幕工具

基于 AI 的高精度语音识别工具，可以将音频/视频文件转换为 SRT 字幕文件。

## 功能特点

- 🎙️ **语音识别**: 采用 OpenAI 的 Whisper 模型，高精度识别
- 📝 **字幕生成**: 自动生成标准 SRT 格式字幕
- 🌐 **多语言支持**: 支持中文、英文等多种语言
- 💻 **现代化界面**: 简洁美观的图形界面，易于使用
- 🍎 **Mac 原生**: 专为 macOS 优化打包
- 📦 **本地模型支持**: 支持集成本地模型，无需下载

## 系统要求

- macOS 10.15 (Catalina) 或更高版本
- 推荐 8GB 以上内存（用于运行 AI 模型）
- 至少 2GB 可用磁盘空间

## 安装方法

### 方法一：直接下载应用（推荐）

1. 下载 `Audio2SRT.app`
2. 将应用复制到 `/Applications` 目录
3. 双击运行

### 方法二：手动构建

如果你想从源代码构建：

```bash
# 1. 克隆或下载源码
cd audio2srt

# 2. 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行应用
python main.py
```

### 方法三：打包成 macOS 应用

```bash
# 安装构建工具
pip install pyinstaller

# 运行构建脚本
python build_mac.py
```

构建完成后，应用将生成在 `dist/Audio2SRT.app`

## 本地模型集成

如果你有本地的 Whisper 模型，可以将其集成到应用中，这样应用就不需要每次都从网络下载模型。

### 方式一：下载模型到本地

```bash
# 运行模型下载工具
python download_model.py

# 或者指定模型大小
python download_model.py medium   # 下载 medium 模型 (~1.5GB)
python download_model.py small    # 下载 small 模型 (~465MB)
python download_model.py tiny     # 下载 tiny 模型 (~75MB)
```

模型会下载到 `models/` 目录下。

### 方式二：手动复制模型

1. 创建 `models/` 目录
2. 在 `models/` 目录下创建模型子目录（如 `medium/`）
3. 将 faster-whisper 格式的模型文件复制到该目录

模型目录结构示例：
```
models/
└── medium/
    ├── config.json
    ├── model.bin
    ├── tokenizer.json
    └── ...
```

### 方式三：构建时自动集成

运行 `build_mac.py` 时，构建脚本会自动检查 `models/` 目录，并将本地模型复制到应用中。

## 首次使用

1. **启动应用**: 双击 Audio2SRT.app
2. **使用模型**: 
   - 如果已集成本地模型，将直接使用
   - 否则会自动下载 Whisper 模型
3. **开始使用**: 选择音频文件，设置语言，点击"开始转换"

## 使用说明

### 选择文件
- 点击"选择文件"按钮，选择音频或视频文件
- 支持的格式：MP3, WAV, MP4, M4A, MKV, AVI, FLAC, OGG, AAC, WebM, MOV

### 设置选项
- **模型大小**: 选择语音识别模型（推荐 Medium）
- **语言**: 选择音频语言，或选择"自动检测"
- **输出位置**: 选择生成的 SRT 文件保存位置

### 开始转换
- 点击"开始转换"按钮
- 等待转换完成
- SRT 文件将保存到指定位置

## 常见问题

### Q: 转换速度慢怎么办？
A: 可以选择更小的模型（如 Small），或在设置中启用 GPU 加速（如果有 NVIDIA 显卡）。

### Q: 识别不准确怎么办？
A: 尝试使用更大的模型（Medium 或 Large），或确保音频质量良好。

### Q: 应用打不开怎么办？
A: 
1. 右键点击应用，选择"打开"
2. 在弹出的对话框中点击"打开"
3. 如果仍然无法打开，可能需要授予完全磁盘访问权限

### Q: 模型下载失败怎么办？
A: 检查网络连接，确保可以访问 HuggingFace。可以尝试使用代理或手动下载模型。

### Q: 如何使用本地模型？
A: 
1. 将模型文件放到 `models/` 目录下
2. 确保模型是 faster-whisper 格式
3. 运行 `python download_model.py` 下载模型
4. 重新构建应用

## 技术细节

### 依赖
- **faster-whisper**: 高效的 Whisper 模型实现
- **CustomTkinter**: 现代化的 Python GUI 框架
- **PyAV**: 音视频处理

### 模型缓存
模型会缓存到以下位置：
```
~/Library/Application Support/Audio2SRT/models/
```

### 日志位置
应用日志会保存到：
```
~/Library/Application Support/Audio2SRT/logs/
```

## 卸载

1. 将 Audio2SRT.app 移到废纸篓
2. （可选）删除模型缓存：
   ```bash
   rm -rf ~/Library/Application\ Support/Audio2SRT/
   ```

## 许可证

本软件仅供个人学习交流使用。

## 更新日志

### v1.0.0
- 初始版本
- 支持 Whisper 语音识别
- 生成 SRT 字幕文件
- 现代化 GUI 界面
- 支持本地模型集成

---

如有问题或建议，请提交 Issue。
