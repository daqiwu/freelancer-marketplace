import http from "k6/http";
import { check, sleep } from "k6";

// Ramp-up test configuration
export const options = {
  stages: [
    { duration: "30s", target: 50 }, // Ramp up to 50 users
    { duration: "1m", target: 100 }, // Scale to 100 users for 1 minute
    { duration: "30s", target: 0 }, // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ["p(95)<3000"], // 95% of requests must be below 3s
    http_req_failed: ["rate<0.1"], // Error rate must be below 10%
  },
};

export default function () {
  // Test endpoints that actually exist
  const baseUrl = "https://sy9wjpmxya.ap-southeast-1.awsapprunner.com";

  // Test 1: Documentation endpoint
  let res = http.get(`${baseUrl}/docs`);
  check(res, {
    "docs status is 200": (r) => r.status === 200,
    "docs response time < 3s": (r) => r.timings.duration < 3000,
  });

  sleep(0.5);

  // Test 2: OpenAPI endpoint
  res = http.get(`${baseUrl}/openapi.json`);
  check(res, {
    "openapi status is 200": (r) => r.status === 200,
    "openapi response time < 3s": (r) => r.timings.duration < 3000,
  });

  sleep(1);
}
