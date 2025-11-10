# AWS App Runner 502 Error - Troubleshooting Guide

## 🔴 Current Issue
**Error:** HTTP 502 - Service unavailable on AWS App Runner
**URL:** qhtrs9pnqw.ap-southeast-1.awsapprunner.com

## 🔍 Common Causes of 502 Errors

### 1. **Health Check Path Issue** (Most Common)
AWS App Runner checks `/` by default, but your app might not have a root endpoint.

### 2. **Port Configuration Mismatch**
App Runner expects port 8000, but your app might be using a different port.

### 3. **Startup Timeout**
Database initialization taking too long during container startup.

### 4. **Environment Variables Missing**
Database credentials or other required env vars not set in App Runner.

## ✅ **Fixes Applied**

### Fix 1: Added Health Check Endpoint
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Fix 2: Graceful Database Initialization
- Database errors no longer crash the app
- App starts even if DB connection fails temporarily

## 🛠️ **AWS App Runner Configuration Required**

### Step 1: Update Health Check Path
In AWS Console:
```
App Runner → Your Service → Configuration → Health check
Path: /health  (change from / to /health)
Interval: 10 seconds
Timeout: 5 seconds
Healthy threshold: 1
Unhealthy threshold: 5
```

### Step 2: Verify Port Configuration
```
App Runner → Your Service → Configuration → Networking
Port: 8000
```

### Step 3: Check Environment Variables
Required variables:
```
DATABASE_URL=mysql+aiomysql://user:pass@host:3306/dbname
PORT=8000
WORKERS=4
```

### Step 4: Increase Startup Timeout
```
App Runner → Your Service → Configuration → Service settings
Health check grace period: 60 seconds (increase if needed)
```

## 📋 **AWS CLI Commands to Fix**

### Update Health Check:
```bash
aws apprunner update-service \
  --service-arn YOUR_SERVICE_ARN \
  --health-check-configuration Protocol=HTTP,Path=/health,Interval=10,Timeout=5,HealthyThreshold=1,UnhealthyThreshold=5
```

### Check Service Logs:
```bash
aws apprunner list-operations --service-arn YOUR_SERVICE_ARN
aws logs tail /aws/apprunner/YOUR_SERVICE_NAME/application --follow
```

## 🔧 **Quick Test After Deployment**

### Test 1: Health Check
```bash
curl https://qhtrs9pnqw.ap-southeast-1.awsapprunner.com/health
# Expected: {"status":"healthy"}
```

### Test 2: API Docs
```bash
curl https://qhtrs9pnqw.ap-southeast-1.awsapprunner.com/docs
# Expected: HTML page with Swagger UI
```

### Test 3: Check Logs
Go to AWS Console → App Runner → Your Service → Logs

Look for:
- ✅ "数据库表创建完成！"
- ✅ "Application startup complete"
- ❌ Any error messages

## 🎯 **Most Likely Solution**

**Change the health check path from `/` to `/health` in AWS App Runner console.**

### How to do it:
1. Open AWS Console
2. Go to App Runner
3. Select your service (qhtrs9pnqw)
4. Click "Configuration" tab
5. Edit "Health check"
6. Change **Path** from `/` to `/health`
7. Click "Save"
8. Wait for redeployment (~2-3 minutes)

## 🚨 **If Still Not Working**

### Check Container Logs:
```bash
# In AWS Console
App Runner → Your Service → Logs → View CloudWatch logs
```

Look for these errors:
- Database connection failures
- Port binding errors
- Import errors
- Module not found errors

### Common Issues:

**Issue 1: Database Not Accessible**
```
Solution: Check RDS security group allows App Runner VPC
```

**Issue 2: Wrong Port**
```
Solution: Ensure PORT=8000 in environment variables
```

**Issue 3: Missing Dependencies**
```
Solution: Verify Dockerfile installs all packages
```

## 📞 **Need More Help?**

Share the logs from:
```
AWS Console → App Runner → Your Service → Logs
```

And I can provide specific fixes based on the error messages.
