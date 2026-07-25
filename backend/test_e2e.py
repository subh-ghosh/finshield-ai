import urllib.request, json

# Use a real customer ID from the dataset (C_1, C_10, etc.)
customer_id = "C_1"

data = json.dumps({"customer_id": customer_id}).encode()
req = urllib.request.Request(
    "http://localhost:8000/api/v1/planner/investigate",
    data=data,
    headers={"Content-Type": "application/json"}
)
try:
    resp = urllib.request.urlopen(req, timeout=120)
    result = json.loads(resp.read().decode())
    print("=== SUCCESS ===")
    print("Status:", result.get("planner_status"))
    print("Customer:", result.get("customer_id"))
    print("Recommendation:", result.get("recommendation"))
    print("Confidence:", result.get("confidence"))
    print("Complete:", result.get("investigation_complete"))
    print("Tool Calls:", result.get("tool_calls"))
    print("Execution Time:", result.get("execution_time_ms"), "ms")
    print("Reasoning Steps:", len(result.get("reasoning_steps", [])))
    for s in result.get("reasoning_steps", []):
        print("  -", s)
    print("Errors:", result.get("errors"))
    report = result.get("final_report", "")
    print("Report length:", len(report), "chars")
    print("\n=== FIRST 800 CHARS OF REPORT ===")
    print(report[:800])
except urllib.error.HTTPError as e:
    print(f"HTTP Error {e.code}")
    print("Body:", e.read().decode()[:2000])
except Exception as e:
    print(f"Error: {e}")
