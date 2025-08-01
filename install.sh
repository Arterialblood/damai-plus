#!/bin/bash

echo "🚀 开始安装大麦网自动抢票工具..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [[ $(echo "$python_version >= 3.7" | bc -l) -eq 1 ]]; then
    echo "✅ Python版本检查通过: $python_version"
else
    echo "❌ 需要Python 3.7或更高版本"
    exit 1
fi

# 安装依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 检查ChromeDriver
if command -v chromedriver &> /dev/null; then
    echo "✅ ChromeDriver已安装"
else
    echo "📥 安装ChromeDriver..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew install chromedriver
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        echo "请在Linux上手动安装ChromeDriver"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        # Windows
        echo "请在Windows上手动安装ChromeDriver"
    fi
fi

echo "🎉 安装完成！"
echo ""
echo "📖 使用说明："
echo "1. 编辑 Automatic_ticket_purchase.py 中的配置"
echo "2. 运行: python3 Automatic_ticket_purchase.py --enhanced"
echo "3. 详细说明请查看 README.md" 