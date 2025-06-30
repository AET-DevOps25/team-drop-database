#!/bin/bash

# Travel Buddy AI 向量搜索系统快速启动脚本

echo "🚀 Travel Buddy AI - 向量搜索系统初始化"
echo "=========================================="

# 检查 Python 版本
echo "📋 检查 Python 环境..."
python_version=$(python3 --version 2>&1)
if [[ $? -eq 0 ]]; then
    echo "✅ Python 环境: $python_version"
else
    echo "❌ 未找到 Python3，请先安装 Python 3.10+"
    exit 1
fi

# 检查是否在正确的目录
if [ ! -f "pyproject.toml" ]; then
    echo "❌ 请在 genai 目录下运行此脚本"
    exit 1
fi

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境已创建"
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"

# 安装依赖
echo "📥 安装项目依赖..."
pip install --upgrade pip
pip install -e .
if [[ $? -eq 0 ]]; then
    echo "✅ 依赖安装完成"
else
    echo "❌ 依赖安装失败"
    exit 1
fi

# 检查环境配置文件
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚙️  创建环境配置文件..."
        cp .env.example .env
        echo "✅ 已创建 .env 文件，请编辑其中的配置"
        echo "⚠️  重要: 请配置以下必需的环境变量:"
        echo "   - OPENAI_API_KEY: OpenAI API 密钥"
        echo "   - ATTRACTION_DB_*: 景点数据库连接信息"
        echo "   - QDRANT_*: Qdrant 向量数据库连接信息"
    else
        echo "❌ 未找到 .env.example 文件"
        exit 1
    fi
else
    echo "✅ 环境配置文件已存在"
fi

# 检查必要的服务
echo "🔍 检查必要的服务..."

# 检查 Qdrant
echo "   检查 Qdrant 服务..."
if command -v curl &> /dev/null; then
    if curl -s http://localhost:6333/collections > /dev/null 2>&1; then
        echo "   ✅ Qdrant 服务运行正常"
    else
        echo "   ⚠️  Qdrant 服务未启动或不可访问"
        echo "   提示: 请确保 Qdrant 在 localhost:6333 运行"
        echo "   Docker 启动命令: docker run -p 6333:6333 qdrant/qdrant"
    fi
else
    echo "   ⚠️  无法检查 Qdrant 服务状态 (缺少 curl)"
fi

# 提供启动选项
echo ""
echo "🎯 接下来您可以选择:"
echo "1. 编辑 .env 文件配置环境变量"
echo "2. 启动开发服务器"
echo "3. 运行系统测试"
echo ""

while true; do
    read -p "请选择操作 (1/2/3) 或输入 'q' 退出: " choice
    case $choice in
        1)
            echo "📝 打开 .env 文件进行编辑..."
            if command -v nano &> /dev/null; then
                nano .env
            elif command -v vim &> /dev/null; then
                vim .env
            elif command -v code &> /dev/null; then
                code .env
            else
                echo "请手动编辑 .env 文件"
            fi
            ;;
        2)
            echo "🚀 启动开发服务器..."
            python -m travel_buddy_ai.main
            ;;
        3)
            echo "🧪 运行系统测试..."
            python test_vector_system.py
            ;;
        q|Q)
            echo "👋 再见！"
            break
            ;;
        *)
            echo "❌ 无效选择，请输入 1、2、3 或 q"
            ;;
    esac
done

echo ""
echo "📚 更多信息请查看 README_VECTOR_SEARCH.md"
echo "🌐 API 文档: http://localhost:8000/docs (服务启动后)"
