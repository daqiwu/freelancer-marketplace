import http from "k6/http";
import { check, sleep } from "k6";

export const options = {
  vus: 50, // 50 concurrent virtual users
  duration: "2m", // for 2 minutes max
};

export default function () {
  const url = "https://sy9wjpmxya.ap-southeast-1.awsapprunner.com/auth/login";
  const payload = JSON.stringify({
    email: "Dave@123163.com",
    password: "88888888",
  });

  const params = {
    headers: { "Content-Type": "application/json" },
  };

  const res = http.post(url, payload, params);

  check(res, {
    "status is 200": (r) => r.status === 200,
    "response time < 3s": (r) => r.timings.duration < 3000,
  });

  sleep(1); // simulate user wait time
}
