import json
import urllib.request

BACKEND_URL = "https://smart-scheduler-0q2w.onrender.com"

print("=" * 60)
print("测试所有API路由")
print("=" * 60)

urls = [
    ("GET", f"{BACKEND_URL}/api/health"),
    ("GET", f"{BACKEND_URL}/rooms"),
    ("GET", f"{BACKEND_URL}/teachers"),
    ("POST", f"{BACKEND_URL}/api/schedule/run"),
]

for method, url in urls:
    print(f"\n尝试: {method} {url}")
    try:
        req = urllib.request.Request(url, method=method)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            print(f"  状态码: {resp.status}")
            print(f"  响应: {json.dumps(data, ensure_ascii=False)[:300]}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP错误 {e.code}: {e.read().decode()[:200]}")
    except Exception as e:
        print(f"  错误: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
