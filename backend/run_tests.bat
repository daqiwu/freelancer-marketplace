@echo off
REM AI Security Classifier - Run Tests Script
REM This script runs all tests with coverage reporting

echo ========================================
echo  AI Security Classifier - Test Runner
echo ========================================
echo.

REM Check if pytest is installed
python -c "import pytest" 2>nul
if errorlevel 1 (
    echo ERROR: pytest is not installed
    echo Please run: pip install -r requirements.txt
    exit /b 1
)

echo [1/4] Running unit tests...
pytest tests/test_security_classifier.py -v

if errorlevel 1 (
    echo.
    echo ERROR: Unit tests failed!
    exit /b 1
)

echo.
echo [2/4] Generating coverage report...
pytest tests/test_security_classifier.py --cov=app.services.security_classifier_service --cov=app.routes.security --cov-report=html --cov-report=term-missing --cov-fail-under=80

if errorlevel 1 (
    echo.
    echo ERROR: Coverage threshold not met (minimum 80%%)
    exit /b 1
)

echo.
echo [3/4] Running code quality checks...
echo Checking code format...
black --check --line-length 120 app/services/security_classifier_service.py app/routes/security.py 2>nul
if errorlevel 1 (
    echo WARNING: Code formatting issues found. Run 'black app/' to fix.
)

echo.
echo [4/4] Running security scan...
bandit -r app/services/security_classifier_service.py app/routes/security.py -f screen 2>nul
if errorlevel 1 (
    echo WARNING: Security issues detected. Please review.
)

echo.
echo ========================================
echo  All Tests Completed Successfully!
echo ========================================
echo.
echo Coverage report: htmlcov\index.html
echo.
pause

