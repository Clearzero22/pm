#!/bin/bash
# Amazon 分析仪表盘启动脚本

echo "========================================"
echo "  📊 Amazon 分析仪表盘"
echo "========================================"
echo ""
echo "正在启动仪表盘..."
echo ""

# 检查虚拟环境
if [ ! -d ".venv-dashboard" ]; then
    echo "创建仪表盘虚拟环境..."
    python -m venv .venv-dashboard
    source .venv-dashboard/bin/activate
    pip install streamlit plotly pandas -q
    echo "✅ 环境准备完成"
fi

# 激活环境并启动
source .venv-dashboard/bin/activate

echo "访问地址: http://localhost:8501"
echo "按 Ctrl+C 停止"
echo ""

streamlit run dashboard/app.py --server.port=8501
