# Integration Testing Guide

**Status:** ✅ Backend server is running at http://localhost:8000  
**Date:** November 4, 2025

---

## Quick Start

### Option 1: Run Quick Integration Test (Recommended)

1. **Install httpx** (one-time setup):
   ```bash
   cd E:\SWE5006\freelancer-marketplace\backend
   pip install httpx
   ```

2. **Run the quick test**:
   ```bash
   python quick_integration_test.py
   ```

   This will test:
   - ✅ Server health check
   - ✅ User registration
   - ✅ User login
   - ✅ API endpoint accessibility

---

### Option 2: Run Full Integration Test Suite

**Prerequisites:**
1. Backend must be running at http://localhost:8000
2. Poetry dependencies installed

**Commands:**

**Using PowerShell:**
```powershell
cd E:\SWE5006\freelancer-marketplace\backend
.\run_integration_tests.ps1
```

**Using Command Prompt:**
```cmd
cd E:\SWE5006\freelancer-marketplace\backend
run_integration_tests.bat
```

**Using Python:**
```bash
cd E:\SWE5006\freelancer-marketplace\backend
python run_integration_tests.py
```

---

## Current Status

### ✅ What's Working

1. **Backend Server**
   - Running at: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Status: Accessible (200 OK)

2. **GitHub Actions CI/CD**
   - ✅ Linting (black, isort, flake8)
   - ✅ Unit tests (44 tests passing)
   - ✅ SAST (Bandit)
   - ✅ SCA (pip-audit)
   - ⚠️ Integration tests skipped (need local server)

3. **Test Scripts Created**
   - `quick_integration_test.py` - Fast smoke tests
   - `run_integration_tests.py` - Full test suite (Python)
   - `run_integration_tests.ps1` - Full test suite (PowerShell)
   - `run_integration_tests.bat` - Full test suite (Batch)

---

## Test Files Overview

### Unit Tests (Run in CI) ✅
- `tests/test_security_classifier.py` - 32 tests
- `app/test/auth_test/model_test.py` - 7 tests  
- `app/test/auth_test/route_test.py` - 8 tests

### Integration Tests (Require Running Server) ⚠️
- `app/test/admin_test/admin_test.py` - 4 tests
- `app/test/auth_test/service_test.py` - 2 tests
- `app/test/customer_test/orders_test.py` - 5 tests
- `app/test/profile_test.py` - 3 tests

---

## Known Issues

### 1. Integration Tests Use localhost:8000
**Problem:** Tests hardcode `http://localhost:8000` instead of using TestClient

**Files Affected:**
- admin_test.py
- service_test.py
- orders_test.py  
- profile_test.py

**Solution:** See `CI_TEST_FIXES.md` for refactoring guide

### 2. WSL-Windows Networking
**Problem:** WSL cannot easily connect to Windows localhost

**Workaround:** Run tests from Windows PowerShell instead of WSL

### 3. Poetry Not in PATH for Background Jobs
**Problem:** Poetry commands fail in PowerShell background jobs

**Workaround:** Use `python -m uvicorn` directly

---

## How to Run Tests Manually

### 1. Start Backend Server

**Option A: PowerShell (New Window)**
```powershell
Start-Process pwsh -ArgumentList "-NoExit", "-Command", "cd E:\SWE5006\freelancer-marketplace\backend; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
```

**Option B: Direct Command**
```bash
cd E:\SWE5006\freelancer-marketplace\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Verify Server is Running

**PowerShell:**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/docs" -TimeoutSec 2 -UseBasicParsing
```

**Browser:**
- Open http://localhost:8000/docs
- You should see the FastAPI Swagger UI

### 3. Run Integration Tests

**Quick Test (3 tests, ~5 seconds):**
```bash
python quick_integration_test.py
```

**Full Test Suite (~30 seconds):**
```powershell
.\run_integration_tests.ps1
```

---

## Troubleshooting

### Server Not Accessible
```powershell
# Check if process is running
Get-Process | Where-Object { $_.ProcessName -like "*python*" }

# Kill existing server if needed
Get-Process -Name "python" | Where-Object { $_.MainWindowTitle -like "*uvicorn*" } | Stop-Process

# Restart server
cd E:\SWE5006\freelancer-marketplace\backend
python -m uvicorn app.main:app --reload
```

### Module Not Found Errors
```bash
# Install missing dependencies
cd E:\SWE5006\freelancer-marketplace\backend
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx aiosqlite
```

### Port Already in Use
```bash
# Change port in server start command
python -m uvicorn app.main:app --port 8001 --reload

# Update test scripts to use new port
$env:TEST_SERVER_URL="http://localhost:8001"
```

---

## Next Steps

### Immediate (Can do now)
1. ✅ Install httpx: `pip install httpx`
2. ✅ Run quick test: `python quick_integration_test.py`
3. ⏳ Review test results

### Short Term (1-2 days)
1. ⏳ Refactor integration tests to use TestClient (see CI_TEST_FIXES.md)
2. ⏳ Fix 3 security classifier test assertions
3. ⏳ Add test fixtures (conftest.py)

### Long Term (1 week)
1. ⏳ Increase coverage to 70%+
2. ⏳ Add mock database for integration tests
3. ⏳ Run full test suite in GitHub Actions

---

## Documentation Files

1. **QA_REPORT.md** - Full quality assurance report with all scan results
2. **CI_TEST_FIXES.md** - Detailed guide for fixing integration tests
3. **INTEGRATION_TESTING.md** - This file

---

## Commands Cheat Sheet

```bash
# Start backend server
python -m uvicorn app.main:app --reload

# Run quick integration test
python quick_integration_test.py

# Run full integration tests  
.\run_integration_tests.ps1

# Run unit tests only (no server needed)
pytest tests/ app/test/auth_test/model_test.py app/test/auth_test/route_test.py -v

# Check server health
curl http://localhost:8000/docs

# View API documentation
# Browser: http://localhost:8000/docs
```

---

**Last Updated:** November 4, 2025  
**Backend Status:** ✅ Running at http://localhost:8000  
**Next Action:** Run `python quick_integration_test.py`
