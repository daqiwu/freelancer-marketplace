#!/bin/bash
# AI Security Classifier - Run Tests Script
# This script runs all tests with coverage reporting

echo "========================================"
echo " AI Security Classifier - Test Runner"
echo "========================================"
echo ""

# Check if pytest is installed
if ! python -c "import pytest" 2>/dev/null; then
    echo "ERROR: pytest is not installed"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

echo "[1/4] Running unit tests..."
pytest tests/test_security_classifier.py -v

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Unit tests failed!"
    exit 1
fi

echo ""
echo "[2/4] Generating coverage report..."
pytest tests/test_security_classifier.py \
    --cov=app.services.security_classifier_service \
    --cov=app.routes.security \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-fail-under=80

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Coverage threshold not met (minimum 80%)"
    exit 1
fi

echo ""
echo "[3/4] Running code quality checks..."
echo "Checking code format..."
black --check --line-length 120 app/services/security_classifier_service.py app/routes/security.py 2>/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: Code formatting issues found. Run 'black app/' to fix."
fi

echo ""
echo "[4/4] Running security scan..."
bandit -r app/services/security_classifier_service.py app/routes/security.py -f screen 2>/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: Security issues detected. Please review."
fi

echo ""
echo "========================================"
echo " All Tests Completed Successfully!"
echo "========================================"
echo ""
echo "Coverage report: htmlcov/index.html"
echo ""

