import http from "k6/http";
import { check, sleep } from "k6";

// Spike test configuration - Sudden traffic spikes
export const options = {
  stages: [
    { duration: "20s", target: 10 }, // Start with 10 users
    { duration: "20s", target: 10 }, // Stay at 10
    { duration: "20s", target: 100 }, // Spike to 100 users
    { duration: "20s", target: 100 }, // Stay at peak
    { duration: "20s", target: 10 }, // Drop back to 10
    { duration: "20s", target: 0 }, // Ramp down
  ],
  thresholds: {
    http_req_duration: ["p(95)<3000"], // 95% under 3s
    http_req_failed: ["rate<0.2"], // Allow higher error rate for spikes
  },
};

export default function () {
  const baseUrl = "https://sy9wjpmxya.ap-southeast-1.awsapprunner.com";

  // Test only endpoints that exist
  const endpoints = ["/docs", "/openapi.json"];

  const randomEndpoint =
    endpoints[Math.floor(Math.random() * endpoints.length)];
  const res = http.get(`${baseUrl}${randomEndpoint}`);

  check(res, {
    "status is 200": (r) => r.status === 200,
    "response time < 3s": (r) => r.timings.duration < 3000,
  });

  sleep(Math.random() * 2); // Random sleep 0-2 seconds
}
