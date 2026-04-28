import json
import urllib.request
import urllib.error

API_TOKEN = "rnd_F6lGbN8a68KuoR4sDX6myD1p0zoW"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

print("=" * 60)
print("Render API 详细诊断")
print("=" * 60)

# 检查原始API返回
endpoints = [
    ("服务列表", "GET", "/services"),
    ("数据库列表", "GET", "/postgres"),
    ("项目列表", "GET", "/projects"),
]

for name, method, endpoint in endpoints:
    print(f"\n尝试获取 {name}:")
    url = f"https://api.render.com/v1{endpoint}"
    req = urllib.request.Request(url, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            raw = resp.read()
            print(f"  状态码: {resp.status}")
            print(f"  原始返回: {raw[:500]}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:300]}")
    except Exception as e:
        print(f"  错误: {type(e).__name__}: {e}")

# 测试后端URL
print("\n" + "=" * 60)
print("测试后端URL...")
print("=" * 60)

urls = [
    "https://smart-scheduler-oht3.onrender.com",
    "https://smart-scheduler-oht3.onrender.com/api/health",
]

for url in urls:
    print(f"\n尝试: {url}")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read()
            print(f"  状态码: {resp.status}")
            print(f"  返回: {raw[:200]}")
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()[:100]}")
    except Exception as e:
        print(f"  错误: {type(e).__name__}: {e}")
