# run_all_tests.sh
#!/bin/bash

echo "运行所有单元测试并生成覆盖率报告..."

# 运行测试
pytest app/test/ \
    --cov=app \
    --cov-report=html \
    --cov-report=term \
    --cov-report=xml \
    -v

echo "测试完成！"
echo "HTML报告: htmlcov/index.html"
echo "XML报告: coverage.xml"