import http from "k6/http";
import { check, sleep } from "k6";

// Stress test configuration - High load
export const options = {
  stages: [
    { duration: "30s", target: 50 }, // Ramp up to 50 users
    { duration: "1m", target: 100 }, // Peak at 100 users for stress test
    { duration: "30s", target: 0 }, // Ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<3000"], // 95% of requests under 3s
    http_req_failed: ["rate<0.15"], // Error rate under 15%
  },
};

export default function () {
  const baseUrl = "https://sy9wjpmxya.ap-southeast-1.awsapprunner.com";

  // Login endpoint stress test
  const loginPayload = JSON.stringify({
    email: "Dave@123163.com",
    password: "88888888",
  });

  const params = {
    headers: { "Content-Type": "application/json" },
  };

  const res = http.post(`${baseUrl}/auth/login`, loginPayload, params);

  check(res, {
    "login status is 200 or 401": (r) => r.status === 200 || r.status === 401,
    "response time < 3s": (r) => r.timings.duration < 3000,
  });

  sleep(0.3); // Shorter sleep for stress test
}
