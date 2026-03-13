# Windows 环境集群部署指南

> **在 Windows 局域网环境下部署爬虫集群的完整方案**
>
> 适用于：Windows 10/11、Windows Server 2016+

---

## 目录

1. [Windows 环境特殊考虑](#1-windows-环境特殊考虑)
2. [方案一：Python 脚本 + 任务计划程序](#2-方案一 python-脚本 - 任务计划程序)
3. [方案二：NSSM Windows 服务](#3-方案二 nssm-windows-服务)
4. [方案三：Docker Desktop](#4-方案三 docker-desktop)
5. [批量部署工具](#5-批量部署工具)
6. [文件分发与下载](#6-文件分发与下载)
7. [常见问题排查](#7-常见问题排查)

---

## 1. Windows 环境特殊考虑

### 1.1 Windows vs Linux 差异

| 特性 | Windows | 解决方案 |
|------|---------|----------|
| **服务管理** | 无 systemd | 任务计划程序/NSSM |
| **路径分隔符** | `\` 而非 `/` | 使用 `pathlib` |
| **权限管理** | UAC/管理员权限 | 以管理员运行 |
| **Python 环境** | 需手动安装 | 嵌入式 Python/venv |
| **防火墙** | Windows Defender | 添加入站规则 |
| **远程执行** | 无 SSH（默认） | 启用 SSH/PsExec |

### 1.2 网络配置

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Windows 局域网环境                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  控制节点 (Windows Server/Win10)                                            │
│  IP: 192.168.1.100                                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Master 服务 (端口 8000)                                             │   │
│  │  Dashboard (端口 8501)                                               │   │
│  │  Redis (端口 6379)                                                   │   │
│  │  PostgreSQL (端口 5432)                                              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│              ┌─────────────────────┼─────────────────────┐                │
│              │                     │                     │                 │
│              ▼                     ▼                     ▼                 │
│     ┌───────────────┐     ┌───────────────┐     ┌───────────────┐        │
│     │  Win10-01     │     │  Win10-02     │     │  Win10-N      │        │
│     │ 192.168.1.101 │     │ 192.168.1.102 │     │ 192.168.1.10N │        │
│     │ Worker 服务   │     │ Worker 服务   │     │ Worker 服务   │        │
│     └───────────────┘     └───────────────┘     └───────────────┘        │
│                                                                             │
│  防火墙配置:                                                                │
│  - 控制节点：开放 8000, 8501, 6379, 5432 端口                               │
│  - 工作节点：允许出站连接到控制节点                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 方案一：Python 脚本 + 任务计划程序

### 2.1 创建 Windows 服务脚本

```python
# worker_service.py
"""
Windows Worker 服务脚本
可注册为 Windows 服务或任务计划程序
"""

import asyncio
import os
import sys
import logging
import socket
from pathlib import Path
from datetime import datetime

# 添加项目路径
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

from worker.worker import WorkerNode

# 配置日志
LOG_DIR = PROJECT_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / f"worker_{datetime.now().strftime('%Y%m%d')}.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_hostname():
    """获取主机名"""
    return socket.gethostname()


def get_local_ip():
    """获取本地 IP"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"


async def main():
    """主函数"""
    # 从环境变量或配置文件读取
    master_url = os.getenv("MASTER_URL", "http://192.168.1.100:8000")
    
    # 使用主机名 + MAC 地址作为唯一 ID
    hostname = get_hostname()
    local_ip = get_local_ip()
    worker_id = f"win_{hostname}_{local_ip.replace('.', '_')}"
    
    logger.info(f"Worker 启动信息:")
    logger.info(f"  主机名：{hostname}")
    logger.info(f"  IP 地址：{local_ip}")
    logger.info(f"  Worker ID: {worker_id}")
    logger.info(f"  Master URL: {master_url}")
    
    worker = WorkerNode(
        master_url=master_url,
        worker_id=worker_id,
        max_concurrent_tasks=3,
    )
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("收到停止信号")
        await worker.stop()
    except Exception as e:
        logger.error(f"Worker 异常：{e}", exc_info=True)
        raise


if __name__ == "__main__":
    # Windows 下需要设置事件循环策略
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
```

### 2.2 创建批处理启动脚本

```batch
@echo off
REM start_worker.bat
REM Windows Worker 启动脚本

echo ========================================
echo Crawler Worker Service
echo ========================================
echo.

REM 设置工作目录
cd /d "%~dp0"

REM 激活虚拟环境（如果有）
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 设置环境变量
set MASTER_URL=http://192.168.1.100:8000

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到 Python，请安装 Python 3.8+
    pause
    exit /b 1
)

echo 启动 Worker 服务...
echo 日志文件：logs\worker.log
echo.

REM 启动（后台运行可用 pythonw.exe）
python worker_service.py

REM 如果程序退出，暂停查看错误
if errorlevel 1 (
    echo.
    echo Worker 异常退出，按任意键查看错误...
    pause
)
```

### 2.3 注册为任务计划程序

```powershell
# register_task.ps1
# PowerShell 脚本：注册为 Windows 任务

$taskName = "CrawlerWorker"
$taskPath = "\"
$scriptPath = "C:\crawler\worker_service.py"
$pythonPath = "C:\Python311\python.exe"
$workingDir = "C:\crawler"
$accountName = "SYSTEM"  # 或使用具体用户名

# 创建任务操作
$action = New-ScheduledTaskAction -Execute $pythonPath `
    -Argument $scriptPath `
    -WorkingDirectory $workingDir

# 创建触发器（开机启动）
$trigger = New-ScheduledTaskTrigger -AtStartup

# 创建设置
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1)

# 创建主体（使用 SYSTEM 账户）
$principal = New-ScheduledTaskPrincipal -UserId $accountName -LogonType ServiceAccount -RunLevel Highest

# 注册任务
Register-ScheduledTask `
    -TaskName $taskName `
    -TaskPath $taskPath `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Crawler Worker Service" `
    -Force

Write-Host "任务已注册：$taskName"
Write-Host "启动任务..."
Start-ScheduledTask -TaskName $taskName -TaskPath $taskPath
```

### 2.4 手动安装指南

```
步骤 1: 准备 Python 环境
┌─────────────────────────────────────────────────────────┐
│ 1. 下载 Python 3.11                                      │
│    https://www.python.org/downloads/                    │
│                                                         │
│ 2. 安装时勾选 "Add Python to PATH"                      │
│                                                         │
│ 3. 验证安装                                              │
│    python --version                                     │
└─────────────────────────────────────────────────────────┘

步骤 2: 安装依赖
┌─────────────────────────────────────────────────────────┐
│ pip install -r requirements.txt                         │
│                                                         │
│ playwright install chromium                             │
└─────────────────────────────────────────────────────────┘

步骤 3: 配置文件
┌─────────────────────────────────────────────────────────┐
│ 创建 .env 文件：                                         │
│ MASTER_URL=http://192.168.1.100:8000                   │
│                                                         │
│ 创建 logs 目录：                                         │
│ mkdir logs                                              │
└─────────────────────────────────────────────────────────┘

步骤 4: 注册任务
┌─────────────────────────────────────────────────────────┐
│ 以管理员身份运行 PowerShell:                             │
│                                                         │
│ Set-ExecutionPolicy -ExecutionPolicy RemoteSigned       │
│ .\register_task.ps1                                     │
└─────────────────────────────────────────────────────────┘

步骤 5: 验证
┌─────────────────────────────────────────────────────────┐
│ 打开"任务计划程序库"                                     │
│ 找到"CrawlerWorker"任务                                  │
│ 右键 → 运行                                              │
│                                                         │
│ 查看日志：logs\worker.log                               │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 方案二：NSSM Windows 服务

### 3.1 NSSM 安装

```
NSSM (Non-Sucking Service Manager) 可将任何程序注册为 Windows 服务

下载：https://nssm.cc/download
```

### 3.2 使用 NSSM 注册服务

```batch
@echo off
REM install_service.bat
REM 使用 NSSM 安装 Worker 服务

echo ========================================
echo 安装 Crawler Worker Windows 服务
echo ========================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if errorlevel 1 (
    echo 错误：请以管理员身份运行此脚本
    pause
    exit /b 1
)

REM 设置路径
set SERVICE_NAME=CrawlerWorker
set SERVICE_DISPLAY_NAME=Crawler Worker Service
set SERVICE_DESCRIPTION=分布式爬虫工作节点服务
set PYTHON_PATH=C:\Python311\python.exe
set SCRIPT_PATH=%~dp0worker_service.py
set WORKING_DIR=%~dp0

REM 下载 NSSM（如果不存在）
if not exist "nssm.exe" (
    echo 下载 NSSM...
    powershell -Command "Invoke-WebRequest -Uri 'https://nssm.cc/release/nssm/2.24/nssm-2.24.zip' -OutFile 'nssm.zip'"
    powershell -Command "Expand-Archive -Path 'nssm.zip' -DestinationPath '.'"
    copy nssm-2.24\win64\nssm.exe .
    del nssm.zip
    rmdir nssm-2.24 /s /q
)

REM 安装服务
echo 安装服务 %SERVICE_NAME%...
nssm install %SERVICE_NAME% "%PYTHON_PATH%" "%SCRIPT_PATH%"

REM 配置服务
nssm set %SERVICE_NAME% DisplayName "%SERVICE_DISPLAY_NAME%"
nssm set %SERVICE_NAME% Description "%SERVICE_DESCRIPTION%"
nssm set %SERVICE_NAME% Start SERVICE_AUTO_START
nssm set %SERVICE_NAME% ServiceType SERVICE_WIN32_OWN_PROCESS
nssm set %SERVICE_NAME% ApplicationPriority NORMAL
nssm set %SERVICE_NAME% AppDirectory "%WORKING_DIR%"
nssm set %SERVICE_NAME% AppStdout "%WORKING_DIR%logs\service.log"
nssm set %SERVICE_NAME% AppStderr "%WORKING_DIR%logs\service_error.log"
nssm set %SERVICE_NAME% AppRotateFiles 1
nssm set %SERVICE_NAME% AppRotateOnline 1
nssm set %SERVICE_NAME% AppRotateBytes 10485760

REM 设置环境变量
nssm set %SERVICE_NAME% AppEnvironmentExtra "MASTER_URL=http://192.168.1.100:8000"

REM 启动服务
echo 启动服务...
nssm start %SERVICE_NAME%

echo.
echo ========================================
echo 服务安装完成！
echo ========================================
echo 服务名称：%SERVICE_NAME%
echo 使用以下命令管理服务:
echo   nssm start %SERVICE_NAME%    - 启动
echo   nssm stop %SERVICE_NAME%     - 停止
echo   nssm restart %SERVICE_NAME%  - 重启
echo   nssm edit %SERVICE_NAME%     - 编辑配置
echo   nssm remove %SERVICE_NAME%   - 删除服务
echo ========================================

pause
```

### 3.3 服务管理 GUI

```
使用 NSSM 的 GUI 界面管理服务:

1. 运行：nssm edit CrawlerWorker
2. 在 GUI 中配置:
   - Application: python.exe 路径
   - Arguments: worker_service.py
   - Startup directory: 工作目录
   - I/O: 日志文件路径
   - Log on: 登录账户
3. 点击"Edit service"保存
```

---

## 4. 方案三：Docker Desktop

### 4.1 Windows Docker 安装

```
步骤 1: 启用 WSL2
┌─────────────────────────────────────────────────────────┐
│ # 以管理员身份运行 PowerShell                            │
│                                                         │
│ wsl --install                                          │
│ wsl --set-default-version 2                            │
│                                                         │
│ # 重启电脑                                              │
└─────────────────────────────────────────────────────────┘

步骤 2: 安装 Docker Desktop
┌─────────────────────────────────────────────────────────┐
│ 1. 下载 Docker Desktop                                   │
│    https://desktop.docker.com/win/main/amd64/           │
│    Docker Desktop Installer.exe                         │
│                                                         │
│ 2. 运行安装程序                                          │
│                                                         │
│ 3. 启动 Docker Desktop                                   │
│                                                         │
│ 4. 验证安装                                              │
│    docker --version                                     │
└─────────────────────────────────────────────────────────┘
```

### 4.2 Docker Compose 部署

```yaml
# docker-compose.windows.yml
version: '3.8'

services:
  worker:
    image: crawler-worker:latest
    build:
      context: .
      dockerfile: Dockerfile.worker.windows
    environment:
      - MASTER_URL=http://host.docker.internal:8000
      - MAX_CONCURRENT_TASKS=3
    volumes:
      - ./worker:C:\app\worker
      - ./logs:C:\app\logs
      - playwright-browsers:C:\Users\Container\AppData\Local\ms-playwright
    restart: unless-stopped
    network_mode: "host"  # 使用主机网络

volumes:
  playwright-browsers:
```

```dockerfile
# Dockerfile.worker.windows
# Windows 容器镜像

FROM mcr.microsoft.com/windows/nanoserver:1809

# 或使用 Windows Server Core
# FROM mcr.microsoft.com/windows/servercore:ltsc2019

# 设置工作目录
WORKDIR C:\\app

# 复制文件
COPY requirements.txt .
COPY worker/ ./worker/

# 安装 Python（Windows 容器需要）
# 这里使用预装 Python 的基础镜像或使用 winget

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 浏览器
RUN playwright install chromium

# 设置环境变量
ENV MASTER_URL=http://host.docker.internal:8000

# 启动命令
CMD ["python", "worker/worker.py"]
```

### 4.3 启动脚本

```powershell
# start_docker_worker.ps1
# PowerShell: 启动 Docker Worker

Write-Host "========================================"
Write-Host "启动 Docker Worker"
Write-Host "========================================"

# 检查 Docker
$dockerVersion = docker --version
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker 未安装"
    exit 1
}
Write-Host "Docker 版本：$dockerVersion"

# 构建镜像
Write-Host "`n构建镜像..."
docker build -t crawler-worker:latest -f Dockerfile.worker.windows .

# 启动容器
Write-Host "`n启动容器..."
docker-compose -f docker-compose.windows.yml up -d

# 查看日志
Write-Host "`n查看日志 (Ctrl+C 退出)..."
docker-compose -f docker-compose.windows.yml logs -f worker
```

---

## 5. 批量部署工具

### 5.1 PowerShell 远程部署

```powershell
# deploy_to_windows_hosts.ps1
# PowerShell: 批量部署到 Windows 主机

param(
    [string]$ConfigFile = "hosts.yaml",
    [string]$Username = "Administrator",
    [string]$Password = ""
)

# 需要安装：Install-Module -Name powershell-yaml
$yaml = Get-Content $ConfigFile -Raw | ConvertFrom-Yaml
$masterUrl = $yaml.master_url
$hosts = $yaml.hosts

# 安装包列表
$packages = @(
    "Python311",
    "Git",
    "7zip"
)

# 部署脚本
$deployScript = @'
param($masterUrl)

# 创建目录
New-Item -ItemType Directory -Force -Path "C:\crawler"
Set-Location "C:\crawler"

# 下载 Python（如果未安装）
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "安装 Python..."
    winget install Python.Python.3.11
}

# 克隆或下载代码
if (!(Test-Path "worker")) {
    Write-Host "下载代码..."
    # 方式 1: Git
    # git clone <repository> .
    
    # 方式 2: 直接下载
    Invoke-WebRequest -Uri "<repo>/archive/main.zip" -OutFile "code.zip"
    Expand-Archive code.zip -DestinationPath .
    Move-Item *-main\* . -Force
    Remove-Item code.zip
}

# 安装依赖
pip install -r requirements.txt
playwright install chromium

# 创建.env 文件
@"
MASTER_URL=$masterUrl
"@ | Out-File -FilePath ".env" -Encoding utf8

# 安装服务
.\install_service.bat

Write-Host "部署完成"
'@

# 遍历主机
foreach ($hostConfig in $hosts) {
    $host = $hostConfig.host
    $label = $hostConfig.label
    
    Write-Host "`n========================================"
    Write-Host "部署到：$host ($label)"
    Write-Host "========================================"
    
    try {
        # 创建会话
        $session = New-PSSession -ComputerName $host -Credential (Get-Credential)
        
        # 执行部署
        Invoke-Command -Session $session -ScriptBlock {
            param($script, $masterUrl)
            Invoke-Expression $script
        } -ArgumentList $deployScript, $masterUrl
        
        # 关闭会话
        Remove-PSSession $session
        
        Write-Host "✓ 部署成功：$host"
    }
    catch {
        Write-Error "✗ 部署失败：$host - $_"
    }
}

Write-Host "`n========================================"
Write-Host "批量部署完成"
Write-Host "========================================"
```

### 5.2 共享文件夹部署

```batch
@echo off
REM deploy_via_share.bat
REM 通过共享文件夹部署

echo ========================================
echo 通过共享文件夹部署
echo ========================================

REM 设置
set MASTER_IP=192.168.1.100
set SHARE_PATH=\\%MASTER_IP%\crawler_deploy
set DEPLOY_LIST=hosts.txt

REM 检查共享
if not exist "%SHARE_PATH%" (
    echo 错误：无法访问共享文件夹 %SHARE_PATH%
    echo 请确保共享已创建并设置权限
    pause
    exit /b 1
)

REM 遍历主机列表
for /f %%h in (%DEPLOY_LIST%) do (
    echo.
    echo 部署到：%%h
    echo ========================================
    
    REM 使用 PsExec 远程执行
    psexec \\%%h -s -d cmd /c "
        mkdir C:\crawler 2>nul
        xcopy %SHARE_PATH%\* C:\crawler\ /E /Y /Q
        cd C:\crawler
        call install_service.bat
    "
    
    if errorlevel 1 (
        echo 部署失败：%%h
    ) else (
        echo 部署成功：%%h
    )
)

echo.
echo ========================================
echo 部署完成
echo ========================================

pause
```

### 5.3 主机列表

```txt
# hosts.txt
192.168.1.101
192.168.1.102
192.168.1.103
192.168.1.104
192.168.1.105
```

---

## 6. 文件分发与下载

### 6.1 集中文件服务器

```python
# master/file_server.py
"""
文件服务器
提供文件下载和分发功能
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import shutil

app = FastAPI()

# 文件存储目录
FILES_DIR = Path("files")
FILES_DIR.mkdir(exist_ok=True)

# 挂载静态文件
app.mount("/files", StaticFiles(directory=str(FILES_DIR)), name="files")


@app.post("/api/v1/files/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    file_path = FILES_DIR / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {
        "filename": file.filename,
        "url": f"/files/{file.filename}",
        "size": file_path.stat().st_size
    }


@app.get("/api/v1/files")
async def list_files():
    """获取文件列表"""
    files = []
    for file_path in FILES_DIR.iterdir():
        files.append({
            "name": file_path.name,
            "size": file_path.stat().st_size,
            "url": f"/files/{file_path.name}"
        })
    return files


@app.get("/api/v1/files/{filename}")
async def download_file(filename: str):
    """下载文件"""
    file_path = FILES_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)


@app.post("/api/v1/files/distribute")
async def distribute_file(filename: str, worker_ids: list = None):
    """分发文件到工作节点"""
    # 实现文件分发逻辑
    # 可以通过 HTTP 推送或通知 Worker 拉取
    pass
```

### 6.2 Worker 文件下载器

```python
# worker/file_downloader.py
"""
文件下载器
从 Master 下载所需文件
"""

import aiohttp
import asyncio
from pathlib import Path
from typing import List


class FileDownloader:
    """文件下载器"""
    
    def __init__(self, master_url: str, download_dir: str = "downloads"):
        self.master_url = master_url.rstrip("/")
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
    
    async def list_files(self) -> List[dict]:
        """获取文件列表"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.master_url}/api/v1/files") as resp:
                if resp.status == 200:
                    return await resp.json()
                return []
    
    async def download_file(self, filename: str, progress_callback=None) -> Path:
        """下载单个文件"""
        file_url = f"{self.master_url}/files/{filename}"
        file_path = self.download_dir / filename
        
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status != 200:
                    raise Exception(f"下载失败：{resp.status}")
                
                total_size = int(resp.headers.get('content-length', 0))
                downloaded = 0
                
                with open(file_path, 'wb') as f:
                    async for chunk in resp.content.iter_chunked(8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            await progress_callback(progress)
        
        return file_path
    
    async def download_files(self, filenames: List[str], max_concurrent=3):
        """批量下载文件"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def download_with_semaphore(filename):
            async with semaphore:
                return await self.download_file(filename)
        
        tasks = [download_with_semaphore(f) for f in filenames]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    async def sync_files(self, required_files: List[str]):
        """同步文件（只下载缺失的）"""
        # 检查本地文件
        local_files = set(f.name for f in self.download_dir.iterdir())
        
        # 需要下载的文件
        to_download = [f for f in required_files if f not in local_files]
        
        if to_download:
            print(f"需要下载 {len(to_download)} 个文件")
            await self.download_files(to_download)
        else:
            print("所有文件已存在")


# 使用示例
async def main():
    downloader = FileDownloader("http://192.168.1.100:8000")
    
    # 获取文件列表
    files = await downloader.list_files()
    print(f"可用文件：{[f['name'] for f in files]}")
    
    # 下载指定文件
    await downloader.download_file("browser_config.json")
    
    # 批量下载
    await downloader.download_files(["file1.zip", "file2.zip", "file3.zip"])
```

### 6.3 一键下载脚本

```batch
@echo off
REM download_and_install.bat
REM 一键下载并安装 Worker

echo ========================================
echo Crawler Worker 一键安装
echo ========================================
echo.

REM 设置 Master 地址
set MASTER_URL=http://192.168.1.100:8000

REM 创建目录
mkdir downloads 2>nul
mkdir C:\crawler 2>nul
cd downloads

echo 正在下载安装文件...
echo.

REM 下载 Python（如果没有）
python --version >nul 2>&1
if errorlevel 1 (
    echo 下载 Python...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe' -OutFile 'python-installer.exe'"
    echo 安装 Python...
    python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
)

REM 下载 Worker 代码
echo 下载 Worker 代码...
powershell -Command "Invoke-WebRequest -Uri '%MASTER_URL%/files/worker.zip' -OutFile 'worker.zip'"
powershell -Command "Expand-Archive worker.zip -DestinationPath '..\'"

REM 安装依赖
cd ..\crawler
echo 安装依赖...
pip install -r requirements.txt

REM 安装 Playwright
echo 安装 Playwright 浏览器...
playwright install chromium

REM 创建配置
echo 创建配置...
echo MASTER_URL=%MASTER_URL% > .env

REM 安装服务
echo 安装服务...
call install_service.bat

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo Worker 已安装到：C:\crawler
echo 服务名称：CrawlerWorker
echo 日志目录：C:\crawler\logs
echo ========================================

pause
```

---

## 7. 常见问题排查

### 7.1 Windows 防火墙配置

```powershell
# 添加入站规则（控制节点）
New-NetFirewallRule -DisplayName "Crawler Master" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Crawler Dashboard" -Direction Inbound -LocalPort 8501 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Redis" -Direction Inbound -LocalPort 6379 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "PostgreSQL" -Direction Inbound -LocalPort 5432 -Protocol TCP -Action Allow

# 查看规则
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*Crawler*"}
```

### 7.2 启用 PowerShell 远程

```powershell
# 在工作节点启用远程
Enable-PSRemoting -Force

# 信任所有主机（测试环境）
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*"

# 或信任特定主机
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "192.168.1.*"
```

### 7.3 服务无法启动

```
问题：服务安装后无法启动

排查步骤:
1. 检查日志：logs\service_error.log
2. 检查 Python 路径是否正确
3. 检查权限：服务是否以管理员运行
4. 手动测试：python worker_service.py
5. 使用 NSSM GUI 编辑配置
```

### 7.4 网络不通

```
问题：Worker 无法连接 Master

排查步骤:
1. ping 192.168.1.100
2. telnet 192.168.1.100 8000
3. 检查 Master 防火墙
4. 检查 Master 服务是否运行
5. 检查 MASTER_URL 环境变量
```

---

## 附录：完整部署检查清单

```markdown
# Windows 部署检查清单

## 控制节点
- [ ] 安装 Python 3.11+
- [ ] 安装 Redis
- [ ] 安装 PostgreSQL
- [ ] 部署 Master 服务
- [ ] 部署 Dashboard
- [ ] 配置防火墙规则
- [ ] 创建共享文件夹（可选）

## 工作节点（每台）
- [ ] 安装 Python 3.11+
- [ ] 安装 Git（可选）
- [ ] 下载 Worker 代码
- [ ] 安装依赖：pip install -r requirements.txt
- [ ] 安装 Playwright 浏览器
- [ ] 配置.env 文件
- [ ] 安装 Windows 服务
- [ ] 验证服务运行
- [ ] 检查日志输出

## 验证
- [ ] Master 可访问
- [ ] Worker 成功注册
- [ ] 任务正常分配
- [ ] 心跳正常上报
- [ ] Dashboard 显示节点
```

---

*文档版本：0.1.0 | 最后更新：2026-03-12*
