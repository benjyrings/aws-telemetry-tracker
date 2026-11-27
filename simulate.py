import json
import random
import subprocess
import time
import urllib.request
import urllib.error

STACK_NAME = "telemetry-tracker-stack"
REGION = "ap-southeast-1"
SERVICES = ["auth-service", "payment-api", "catalog-service"]

def get_api_endpoint():
    cmd = [
        "aws", "cloudformation", "describe-stacks",
        "--stack-name", STACK_NAME,
        "--region", REGION,
        "--query", "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue",
        "--output", "text"
    ]
    result = subprocess.check_output(cmd, text=True).strip()
    if not result or result == "None":
        raise RuntimeError("ApiEndpoint tidak ditemukan. Pastikan stack sudah selesai di-deploy.")
    return result

def main():
    api_url = get_api_endpoint()
    print(f"Target Endpoint: {api_url}\n")

    for i in range(1, 16):
        payload = {
            "service_name": random.choice(SERVICES),
            "latency_ms": round(random.uniform(35.0, 480.0), 2),
            "status_code": random.choice([200, 200, 200, 503])
        }
        req = urllib.request.Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        try:
            with urllib.request.urlopen(req) as resp:
                body = resp.read().decode("utf-8")
                print(f"[{i:02d}/15] OK | {payload['service_name']} ({payload['latency_ms']} ms) -> {body}")
        except urllib.error.HTTPError as e:
            print(f"[{i:02d}/15] HTTP Error {e.code}: {e.read().decode('utf-8')}")
        time.sleep(0.5)

if __name__ == "__main__":
    main()
