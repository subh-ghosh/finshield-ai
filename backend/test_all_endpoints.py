import urllib.request, json

base = 'http://localhost:8000/api/v1'
tests = [
    ('GET', '/health', None),
    ('GET', '/version', None),
    ('POST', '/planner/investigate', {'customer_id': 'C_1'}),
    ('POST', '/planner/investigate', {'customer_id': 'CUST-8392'}),
    ('POST', '/planner/investigate', {'customer_id': 'CUST-3371'}),
]

for method, path, body in tests:
    try:
        data = json.dumps(body).encode() if body else None
        headers = {'Content-Type': 'application/json'} if data else {}
        req = urllib.request.Request(base + path, data=data, headers=headers, method=method)
        r = urllib.request.urlopen(req, timeout=30)
        result = json.loads(r.read())
        if method == 'GET':
            print(f'[OK] {method} {path}: {list(result.keys())[:3]}')
        else:
            cid = body["customer_id"] if body else ""
            print(f'[OK] {method} {path} ({cid}): status={result.get("planner_status")} rec={result.get("recommendation")} conf={result.get("confidence")}')
    except Exception as e:
        print(f'[FAIL] {method} {path}: {str(e)[:100]}')
