import urllib.request
import urllib.error
import json
import time

BASE_URL = "https://finshield-backend-131d.onrender.com/api"

ENDPOINTS = [
    ("GET", "/v1/metrics", None),
    ("GET", "/v1/monitoring/watchlist", None),
    ("POST", "/v1/simulation/what-if", {"customer_id": "C_4726", "transaction_amount": 50000}),
    ("GET", "/v1/eda/summary", None),
    ("GET", "/v1/features/C_4726", None),
    ("GET", "/v1/anomaly/C_4726", None),
    ("GET", "/v1/risk-classify/C_4726", None),
    ("GET", "/v1/risk-classify/summary/distribution", None),
    ("GET", "/v1/anomaly/summary/top?top_n=1", None),
    ("GET", "/v1/similar-cases/C_4726", None),
    ("GET", "/v1/similar-cases/C_4726/comparison?historical_case_id=C_2633", None),
    ("GET", "/v1/queue", None),
    ("POST", "/v1/planner/investigate", {"customer_id": "C_4726", "request": "Investigate customer C_4726"}),
    ("GET", "/v1/memory/search?query=fraud", None),
    ("GET", "/v1/memory/statistics", None),
    ("GET", "/v1/memory/customer/C_4726", None),
    ("GET", "/v1/customer/C_4726", None),
    ("GET", "/v1/graph/ego/C_4726", None),
    ("GET", "/v1/graph/summary/C_4726", None),
    ("GET", "/v1/rules/suggestions", None),
]

def verify_endpoints():
    print("Starting API Verification...")
    results = []
    
    for method, path, payload in ENDPOINTS:
        url = BASE_URL + path
        try:
            req = urllib.request.Request(url, method=method)
            req.add_header('Content-Type', 'application/json')
            if payload:
                req.data = json.dumps(payload).encode('utf-8')
            
            start_time = time.time()
            with urllib.request.urlopen(req, timeout=30) as response:
                status = response.getcode()
                response.read()
                latency = time.time() - start_time
                res = f"[OK] {method} {path} -> {status} ({latency:.2f}s)"
                print(res)
                results.append((path, "OK", status, latency))
        except urllib.error.HTTPError as e:
            res = f"[FAIL] {method} {path} -> HTTP {e.code}"
            print(res)
            results.append((path, "FAIL", e.code, 0))
        except Exception as e:
            res = f"[FAIL] {method} {path} -> {type(e).__name__}: {e}"
            print(res)
            results.append((path, "FAIL", 0, 0))
    
    with open("api_verification_results.txt", "w", encoding="utf-8") as f:
        f.write("\n".join([str(r) for r in results]))
    print("Verification complete.")

if __name__ == "__main__":
    verify_endpoints()
