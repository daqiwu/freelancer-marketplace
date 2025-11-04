@echo off
REM Integration Test Runner for Windows Command Prompt
REM Runs integration tests against local backend server at http://localhost:8000

echo ============================================================
echo   FREELANCER MARKETPLACE - INTEGRATION TEST RUNNER
echo ============================================================

REM Check if backend is running
echo.
echo Checking if backend is running at http://localhost:8000...
curl -f -s http://localhost:8000/docs >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Cannot connect to backend server at http://localhost:8000
    echo.
    echo Please start your backend server first:
    echo    cd backend
    echo    poetry run uvicorn app.main:app --reload
    echo.
    pause
    exit /b 1
)

echo [OK] Backend server is running!

REM Run integration tests
echo.
echo Running integration tests...
echo ------------------------------------------------------------

poetry run pytest app/test/admin_test/ ^
                  app/test/auth_test/service_test.py ^
                  app/test/customer_test/ ^
                  app/test/profile_test.py ^
                  -v ^
                  --tb=short ^
                  --color=yes

set TEST_EXIT_CODE=%ERRORLEVEL%

echo.
echo ------------------------------------------------------------
if %TEST_EXIT_CODE% EQU 0 (
    echo [PASS] All integration tests PASSED!
) else (
    echo [FAIL] Some integration tests FAILED
    echo Exit code: %TEST_EXIT_CODE%
)
echo ------------------------------------------------------------

pause
exit /b %TEST_EXIT_CODE%
