import json
import urllib.request

API_TOKEN = "rnd_F6lGbN8a68KuoR4sDX6myD1p0zoW"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

print("=" * 60)
print("获取API返回的原始数据结构...")
print("=" * 60)

# 获取服务列表
try:
    url = "https://api.render.com/v1/services"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        print(f"\n服务列表 - 原始返回:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"错误: {e}")

# 获取数据库列表
try:
    url = "https://api.render.com/v1/postgres"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        print(f"\n数据库列表 - 原始返回:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"错误: {e}")
