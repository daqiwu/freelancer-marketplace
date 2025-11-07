# Performance Testing with K6

This folder contains K6 performance test scripts for the Freelancer Marketplace API.

## 🚀 Prerequisites

Install K6:

### Linux (Debian/Ubuntu):
```bash
sudo apt install k6
```

### macOS:
```bash
brew install k6
```

### Windows:
```bash
winget install k6
```

## 📋 Available Tests

### 1. **login_test.js** - Basic Login Performance
```bash
k6 run login_test.js
```
- **Users**: 50 concurrent users
- **Duration**: 30 seconds
- **Target**: Login endpoint with credentials
- **Checks**: Status 200, response time < 1s

### 2. **load_test.js** - Ramp-up Load Test
```bash
k6 run load_test.js
```
- **Pattern**: Ramp up → Peak → Ramp down
- **Peak Users**: 50
- **Duration**: 2 minutes total
- **Targets**: Multiple endpoints (docs, root, openapi)
- **Thresholds**: 95% requests < 1s, error rate < 10%

### 3. **stress_test.js** - High Load Stress Test
```bash
k6 run stress_test.js
```
- **Peak Users**: 300
- **Duration**: 9 minutes total
- **Target**: Login endpoint under stress
- **Thresholds**: 95% requests < 2s, error rate < 15%

### 4. **spike_test.js** - Traffic Spike Test
```bash
k6 run spike_test.js
```
- **Spike Users**: 500 (sudden spike)
- **Pattern**: Normal → Spike → Recovery
- **Targets**: Random endpoint selection
- **Thresholds**: 95% requests < 3s, error rate < 20%

## 📊 Sample Output

```
running (0m30.0s), 50 VUs, 1000 complete and 0 interrupted iterations
default ✓ [======================================] 50 VUs  30s

checks.........................: 100.00% ✓ 1000 ✗ 0
http_req_duration..............: avg=243ms  p(95)=498ms  p(99)=710ms
http_reqs......................: 1000  (33.3/s)
```

## 🎯 Key Metrics to Monitor

| Metric | Good Range | What It Means |
|--------|------------|---------------|
| `http_req_duration` (avg) | < 500ms | Average response time |
| `p(95)` | < 1s | 95% of requests under 1s |
| `http_reqs` | Higher = better | Requests per second (throughput) |
| `http_req_failed` | 0-1% | Error rate percentage |
| `checks` | 100% | Validation success rate |

## 🔧 Customization

### Change User Load:
```javascript
export const options = {
  vus: 100,          // 100 concurrent users
  duration: '5m',    // 5 minutes
};
```

### Add Custom Thresholds:
```javascript
thresholds: {
  http_req_duration: ['p(95)<1000', 'p(99)<2000'],
  http_req_failed: ['rate<0.05'],
  checks: ['rate>0.95'],
},
```

### Export Results:
```bash
# Export to CSV
k6 run --out csv=results.csv login_test.js

# Export to JSON
k6 run --out json=results.json load_test.js

# Export to InfluxDB
k6 run --out influxdb=http://localhost:8086/k6 stress_test.js
```

## 🌐 API Endpoints Tested

- **Base URL**: `https://freelancer-marketplace-api.onrender.com`
- **Endpoints**:
  - `POST /auth/login` - User authentication
  - `GET /` - Root endpoint
  - `GET /docs` - API documentation
  - `GET /openapi.json` - OpenAPI specification

## 🚨 Test Credentials

The tests use these credentials (update as needed):
```javascript
{
  "email": "Dave@123163.com",
  "password": "88888888"
}
```

## 📈 Performance Benchmarks

### Expected Performance Targets:
- **Response Time**: < 500ms average
- **95th Percentile**: < 1 second
- **Error Rate**: < 1%
- **Throughput**: > 30 requests/second

### Load Capacity:
- **Normal Load**: 50 concurrent users
- **Peak Load**: 200 concurrent users
- **Stress Limit**: 300+ concurrent users

## 🔄 Running Tests in CI/CD

These tests can be integrated into GitHub Actions:

```yaml
- name: Run Performance Tests
  run: |
    sudo apt install k6
    k6 run performance-tests/load_test.js
```

## 📞 Usage Examples

```bash
# Quick smoke test
k6 run login_test.js

# Production load simulation
k6 run load_test.js

# Find breaking point
k6 run stress_test.js

# Test traffic spikes
k6 run spike_test.js

# Custom run with options
k6 run --vus 100 --duration 2m login_test.js
```

Happy testing! 🎯