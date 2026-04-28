import json
import urllib.request

API_TOKEN = "rnd_cyYYfUSrtwFuLcqvjjMrRlzgUsQS"

# 测试API Token
print("=" * 60)
print("测试 Render API...")
print("=" * 60)

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

# 尝试获取服务列表
try:
    url = "https://api.render.com/v1/services"
    req = urllib.request.Request(url, headers=headers)
    print(f"\n请求: GET {url}")
    print(f"Headers: Authorization: Bearer {API_TOKEN[:10]}...")
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        print(f"状态码: {resp.status}")
        print(f"返回数据: {json.dumps(data, indent=2)[:500]}")
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"HTTP错误 {e.code}: {error_body}")
except urllib.error.URLError as e:
    print(f"URL错误: {e.reason}")
except Exception as e:
    print(f"错误: {type(e).__name__}: {e}")
