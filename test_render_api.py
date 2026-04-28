import json
import urllib.request

API_TOKEN = "rnd_cyYYfUSrtwFuLcqvjjMrRlzgUsQS"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

# 测试各种API端点
print("=" * 60)
print("测试Render API端点...")
print("=" * 60)

endpoints = [
    "https://api.render.com/v1/user",
    "https://api.render.com/v1/me",
    "https://api.render.com/v1/services",
    "https://api.render.com/v1/postgres",
    "https://api.render.com/v1/projects",
]

for endpoint in endpoints:
    print(f"\n尝试: {endpoint}")
    try:
        req = urllib.request.Request(endpoint, headers=headers)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            print(f"  状态码: {resp.status}")
            print(f"  返回数据: {json.dumps(data, indent=2)[:200]}...")
    except urllib.error.HTTPError as e:
        print(f"  HTTP错误 {e.code}: {e.read().decode()}")
    except Exception as e:
        print(f"  错误: {e}")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)
