import json
import urllib.request

API_TOKEN = "rnd_cyYYfUSrtwFuLcqvjjMrRlzgUsQS"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

print("=" * 60)
print("诊断 Render API 问题...")
print("=" * 60)

# 测试API连接
try:
    url = "https://api.render.com/v1/services"
    print(f"\n测试: GET {url}")
    req = urllib.request.Request(url, headers=headers)
    
    with urllib.request.urlopen(req, timeout=10) as resp:
        status = resp.status
        data = json.loads(resp.read())
        print(f"状态码: {status}")
        print(f"返回数据:")
        print(json.dumps(data, indent=2)[:1000])
        
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"HTTP错误 {e.code}: {error_body}")
    
except Exception as e:
    print(f"错误: {type(e).__name__}: {e}")
