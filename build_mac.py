#!/usr/bin/env python3
"""
Audio2SRT 构建脚本
用于将应用打包成 macOS 可执行程序 (.app)

功能:
- 自动安装构建依赖
- 打包 Python 应用为 macOS 应用
- 自动复制本地模型到应用中
- 创建 DMG 安装镜像

使用方法:
    python build_mac.py

前置要求:
    - macOS 10.15 或更高版本
    - Python 3.10+
    - 至少 8GB 可用磁盘空间
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_step(step: str, message: str):
    """打印步骤信息"""
    print(f"{Colors.BLUE}{Colors.BOLD}[{step}]{Colors.END} {message}")


def print_success(message: str):
    """打印成功信息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_warning(message: str):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def print_error(message: str):
    """打印错误信息"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def run_command(cmd: list, cwd: str = None, check: bool = True) -> subprocess.CompletedProcess:
    """运行命令"""
    print(f"  执行: {' '.join(cmd)}")
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check
    )
    return result


def check_python_version() -> bool:
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print_error(f"需要 Python 3.10+，当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    print_success(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    return True


def check_macos() -> bool:
    """检查是否为 macOS 系统"""
    if sys.platform != 'darwin':
        print_warning("当前不在 macOS 系统上，部分功能可能无法正常工作")
        print("  仍然可以进行打包，但建议在 macOS 上运行最终构建")
        return False
    print_success("检测到 macOS 系统")
    return True


def install_dependencies() -> bool:
    """安装构建依赖"""
    print_step("1", "安装构建依赖...")
    
    try:
        import PyInstaller
        print_success("PyInstaller 已安装")
    except ImportError:
        print("  正在安装 PyInstaller...")
        try:
            run_command([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
            print_success("PyInstaller 安装完成")
        except subprocess.CalledProcessError:
            print_error("PyInstaller 安装失败")
            return False
    
    return True


def check_models() -> bool:
    """检查本地模型"""
    print_step("2", "检查本地模型...")
    
    models_dir = Path("models")
    
    if not models_dir.exists():
        print_warning("未找到 models 目录")
        print("  应用将自动从网络下载模型")
        print("  如需使用本地模型，请先运行: python download_model.py")
        return False
    
    # 检查模型目录
    model_sizes = []
    for item in models_dir.iterdir():
        if item.is_dir():
            # 检查目录中是否有模型文件
            has_model = any(f.suffix == '.bin' for f in item.iterdir())
            if has_model:
                model_sizes.append(item.name)
                size_mb = sum(f.stat().st_size for f in item.rglob('*') if f.is_file()) / (1024 * 1024)
                print(f"  ✓ {item.name}: {size_mb:.1f} MB")
    
    if not model_sizes:
        print_warning("models 目录中没有找到模型文件")
        print("  应用将自动从网络下载模型")
        return False
    
    print_success(f"找到 {len(model_sizes)} 个本地模型")
    return True


def clean_build() -> bool:
    """清理旧的构建文件"""
    print_step("3", "清理旧构建...")
    
    build_dirs = ['build', 'dist']
    for dir_name in build_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  删除 {dir_name}/")
            shutil.rmtree(dir_path)
    
    print_success("清理完成")
    return True


def build_app() -> bool:
    """构建 macOS 应用"""
    print_step("4", "构建 macOS 应用...")
    
    spec_file = 'audio2srt.spec'
    
    if not Path(spec_file).exists():
        print_error(f"找不到 spec 文件: {spec_file}")
        return False
    
    print("  运行 PyInstaller...")
    try:
        run_command([
            sys.executable, '-m', 'PyInstaller',
            spec_file,
            '--clean',
            '--noconfirm'
        ])
        print_success("构建完成")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"构建失败: {e}")
        return False


def copy_models_to_app() -> bool:
    """复制本地模型到应用中"""
    print_step("5", "复制模型到应用...")
    
    models_dir = Path("models")
    app_path = Path("dist/Audio2SRT.app")
    
    if not app_path.exists():
        print_error("应用未生成")
        return False
    
    if not models_dir.exists():
        print("  无本地模型，跳过")
        return True
    
    # 目标目录
    target_dir = app_path / "Contents" / "Resources" / "models"
    
    # 复制模型目录
    if target_dir.exists():
        shutil.rmtree(target_dir)
    
    print(f"  复制 models 到应用...")
    shutil.copytree(models_dir, target_dir)
    
    # 计算大小
    size_mb = sum(f.stat().st_size for f in target_dir.rglob('*') if f.is_file()) / (1024 * 1024)
    print_success(f"模型已复制 ({size_mb:.1f} MB)")
    
    return True


def verify_app() -> bool:
    """验证构建结果"""
    print_step("6", "验证构建结果...")
    
    app_path = Path('dist/Audio2SRT.app')
    
    if not app_path.exists():
        print_error(f"应用未生成: {app_path}")
        return False
    
    # 检查应用结构
    expected_files = [
        'Contents/MacOS/Audio2SRT',
        'Contents/Info.plist',
    ]
    
    for file_path in expected_files:
        full_path = app_path / file_path
        if not full_path.exists():
            print_error(f"缺少必要文件: {file_path}")
            return False
    
    # 检查模型
    models_path = app_path / 'Contents' / 'Resources' / 'models'
    if models_path.exists():
        model_count = sum(1 for _ in models_path.rglob('*.bin'))
        print(f"  模型文件: {model_count} 个")
    
    # 获取应用大小
    size = sum(f.stat().st_size for f in app_path.rglob('*') if f.is_file())
    size_mb = size / (1024 * 1024)
    
    print_success(f"应用构建成功!")
    print(f"  位置: {app_path.absolute()}")
    print(f"  大小: {size_mb:.1f} MB")
    
    return True


def create_dmg() -> bool:
    """创建 DMG 安装镜像"""
    print_step("7", "创建 DMG 安装镜像...")
    
    if sys.platform != 'darwin':
        print_warning("非 macOS 系统，跳过 DMG 创建")
        return False
    
    dmg_path = Path('dist/Audio2SRT_Installer.dmg')
    app_path = Path('dist/Audio2SRT.app')
    
    if not app_path.exists():
        print_error("应用未生成，无法创建 DMG")
        return False
    
    try:
        run_command(['which', 'create-dmg'], check=False)
    except Exception:
        print_warning("create-dmg 未安装，跳过 DMG 创建")
        print("  安装: brew install create-dmg")
        return False
    
    try:
        run_command([
            'create-dmg',
            '--volname', 'Audio2SRT',
            '--window-pos', '200', '120',
            '--window-size', '600', '400',
            '--icon-size', '100',
            '--icon', 'Audio2SRT.app', '150', '185',
            '--app-drop-link', '425', '185',
            '--hide-extension', 'Audio2SRT.app',
            str(dmg_path),
            str(app_path)
        ], check=False)
        
        if dmg_path.exists():
            print_success(f"DMG 创建成功: {dmg_path}")
            return True
        else:
            print_warning("DMG 创建可能未成功")
            return False
            
    except Exception as e:
        print_warning(f"创建 DMG 时出错: {e}")
        return False


def print_usage():
    """打印使用说明"""
    print()
    print(f"{Colors.BOLD}{'='*60}")
    print("构建完成!")
    print(f"{'='*60}{Colors.END}")
    print()
    print("使用方法:")
    print(f"  1. 将 Audio2SRT.app 复制到 /Applications 目录")
    print(f"  2. 双击运行 Audio2SRT.app")
    print()
    print("首次运行:")
    print("  - 如果已集成模型，将直接使用本地模型")
    print("  - 否则会自动从网络下载 Whisper 模型")
    print()
    print("注意事项:")
    print("  - 如果遇到安全提示，右键点击应用选择'打开'")
    print()


def main():
    """主函数"""
    print()
    print(f"{Colors.BOLD}{'='*60}")
    print("Audio2SRT macOS 应用构建工具")
    print(f"{'='*60}{Colors.END}")
    print()
    
    # 检查环境
    if not check_python_version():
        sys.exit(1)
    
    check_macos()
    
    # 检查模型
    check_models()
    
    # 安装依赖
    if not install_dependencies():
        sys.exit(1)
    
    # 清理旧构建
    clean_build()
    
    # 构建应用
    if not build_app():
        sys.exit(1)
    
    # 复制模型到应用
    copy_models_to_app()
    
    # 验证结果
    if not verify_app():
        sys.exit(1)
    
    # 创建 DMG
    create_dmg()
    
    # 打印使用说明
    print_usage()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
