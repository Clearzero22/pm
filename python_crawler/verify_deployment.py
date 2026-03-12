#!/usr/bin/env python3
"""
部署验证脚本
验证服务器环境是否准备好运行爬虫
"""
import os
import sys
import subprocess
import platform as plt
from pathlib import Path


def print_header(title):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(name, success, message=""):
    """打印结果"""
    status = "✅" if success else "❌"
    print(f"{status} {name}")
    if message:
        print(f"   {message}")


def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    major, minor = version.major, version.minor

    if major >= 3 and minor >= 14:
        return True, f"Python {major}.{minor}.{version.micro}"
    else:
        return False, f"Python {major}.{minor} (需要 >= 3.14)"


def check_uv():
    """检查 uv 包管理器"""
    try:
        result = subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, "uv 未安装"
    except FileNotFoundError:
        return False, "uv 命令未找到"


def check_project_files():
    """检查项目文件"""
    required_files = [
        "main.py",
        "pyproject.toml",
        "src/crawler.py",
        "src/search_crawler.py",
    ]

    missing = [f for f in required_files if not Path(f).exists()]

    if not missing:
        return True, "所有项目文件完整"
    else:
        return False, f"缺少文件: {', '.join(missing)}"


def check_playwright():
    """检查 Playwright"""
    try:
        import playwright
        # 尝试获取版本（如果没有 __version__ 就只用包名）
        try:
            version = playwright.__version__
        except AttributeError:
            version = "已安装"
        return True, f"Playwright {version}"
    except ImportError:
        return False, "Playwright 未安装"


def check_chromium():
    """检查 Chromium 浏览器"""
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()

        return True, "Chromium 已安装"

    except Exception as e:
        error_msg = str(e)
        if "Executable doesn't exist" in error_msg:
            return False, "Chromium 未安装 (运行: uv run playwright install chromium)"
        else:
            return False, f"Chromium 测试失败: {error_msg}"


def check_directories():
    """检查目录结构"""
    dirs = {
        "output": "数据输出目录",
        "logs": "日志目录",
        "src": "源代码目录",
    }

    issues = []
    for dir_name, desc in dirs.items():
        if not Path(dir_name).exists():
            issues.append(f"{dir_name}/ ({desc})")

    if not issues:
        return True, "所有目录存在"
    else:
        # 尝试创建
        for dir_name in issues:
            try:
                Path(dir_name).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                return False, f"目录创建失败: {dir_name} ({e})"
        return True, "目录已创建"


def check_disk_space():
    """检查磁盘空间"""
    try:
        stat = os.statvfs(".")
        free_gb = stat.f_bavail * stat.f_frsize / (1024**3)

        if free_gb > 10:
            return True, f"可用空间: {free_gb:.1f} GB"
        elif free_gb > 1:
            return True, f"可用空间: {free_gb:.1f} GB (充足)"
        else:
            return False, f"可用空间: {free_gb:.1f} GB (建议至少 10GB)"
    except Exception as e:
        return False, f"无法检查磁盘空间: {e}"


def check_memory():
    """检查内存"""
    try:
        # 读取 /proc/meminfo
        with open("/proc/meminfo", "r") as f:
            meminfo = f.read()

        # 解析总内存和可用内存
        total_mem = 0
        available_mem = 0

        for line in meminfo.split("\n"):
            if line.startswith("MemTotal:"):
                total_mem = int(line.split()[1]) // 1024  # KB to MB
            elif line.startswith("MemAvailable:"):
                available_mem = int(line.split()[1]) // 1024

        if available_mem > 2000:
            return True, f"可用内存: {available_mem} MB"
        elif available_mem > 500:
            return True, f"可用内存: {available_mem} MB (充足)"
        else:
            return False, f"可用内存: {available_mem} MB (建议至少 500MB)"

    except Exception as e:
        return False, f"无法检查内存: {e}"


def check_network():
    """检查网络连接"""
    try:
        import urllib.request
        urllib.request.urlopen("https://www.amazon.com", timeout=10)
        return True, "可以访问 Amazon"
    except Exception as e:
        return False, f"网络连接失败: {e}"


def detect_platform():
    """检测运行平台"""
    import platform as plt

    system = plt.system()
    machine = plt.machine()

    platform_info = f"{system} ({machine})"

    # 树莓派检测
    if system == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()
                if "Raspberry Pi" in cpuinfo:
                    return platform_info, "树莓派"
        except:
            pass

    # Mac 检测
    if system == "Darwin":
        return platform_info, "macOS"

    return platform_info, system


def main():
    """主函数"""
    print_header("Amazon Crawler 部署验证")

    # 检测平台
    platform_info, system_type = detect_platform()
    print(f"📱 平台: {platform_info} ({system_type})")
    print()

    # 运行所有检查
    results = {}
    checks = [
        ("Python 版本", check_python_version),
        ("uv 包管理器", check_uv),
        ("项目文件", check_project_files),
        ("Playwright", check_playwright),
        ("Chromium 浏览器", check_chromium),
        ("目录结构", check_directories),
        ("磁盘空间", check_disk_space),
    ]

    # 内存检查 (Linux only)
    if plt.system() == "Linux":
        checks.append(("内存", check_memory))

    # 网络检查 (可选，可能慢)
    # checks.append(("网络连接", check_network))

    for name, check_func in checks:
        success, message = check_func()
        results[name] = (success, message)
        print_result(name, success, message)

    # 总结
    print()
    print("=" * 60)
    print("验证总结")
    print("=" * 60)

    passed = sum(1 for s, _ in results.values() if s)
    total = len(results)

    print(f"通过: {passed}/{total}")
    print()

    # 推荐下一步
    if passed == total:
        print("🎉 所有检查通过！你可以运行爬虫了：")
        print()
        print("   uv run python main.py --headless --pages 1 --products 5")
        print()
        return 0
    else:
        print("⚠️  部分检查失败，需要修复：")
        print()

        for name, (success, message) in results.items():
            if not success:
                print(f"   • {name}: {message}")

        print()
        print("💡 提示:")
        print("   - 安装 uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("   - 安装依赖: uv sync")
        print("   - 安装浏览器: uv run playwright install chromium")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
