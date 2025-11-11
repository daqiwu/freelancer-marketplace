#!/bin/bash
# 查看测试覆盖率 HTML 报告

echo "🔍 打开测试覆盖率 HTML 报告..."
echo ""
echo "📊 当前覆盖率统计："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 从 coverage.xml 或重新运行获取统计
if [ -f "htmlcov/index.html" ]; then
    echo "✅ HTML 报告已生成"
    echo "📂 位置: $(pwd)/htmlcov/index.html"
    echo ""
    echo "正在打开浏览器..."
    open htmlcov/index.html
else
    echo "❌ 未找到 HTML 报告，请先运行测试："
    echo "   ./run_tests.sh"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💡 提示："
echo "  - 🟢 绿色: 已覆盖的代码"
echo "  - 🔴 红色: 未覆盖的代码" 
echo "  - 🟡 黄色: 部分覆盖的代码"
echo ""
