import json
import urllib.request
import urllib.error
import time

API_TOKEN = "rnd_F6lGbN8a68KuoR4sDX6myD1p0zoW"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def api_call(method, endpoint, data=None):
    url = f"https://api.render.com/v1{endpoint}"
    if data is not None:
        data = json.dumps(data).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None

SERVICE_ID = "srv-d7o8t2rbc2fs73993hj0"
BACKEND_URL = "https://smart-scheduler-oht3.onrender.com"

print("=" * 60)
print("触发 Render 部署")
print("=" * 60)

# 触发部署 - 使用空对象而不是clearCache
print("\n触发部署...")
result = api_call("POST", f"/services/{SERVICE_ID}/deploys", {})
if result:
    print(f"部署已触发!")
    print(f"响应: {json.dumps(result, indent=2)}")
else:
    print("部署触发失败，尝试其他方式...")
    # 尝试不带body的POST
    req = urllib.request.Request(
        f"https://api.render.com/v1/services/{SERVICE_ID}/deploys",
        data=b'{}',
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            print(f"部署已触发! 响应: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"也失败了: {e}")

# 获取最新部署状态
print("\n获取最新部署状态...")
deploys = api_call("GET", f"/services/{SERVICE_ID}/deploys")
if deploys:
    print(f"找到 {len(deploys)} 个部署记录")
    for d in deploys[:3]:
        deploy = d.get('deploy', d)
        print(f"  - ID: {deploy.get('id')}, 状态: {deploy.get('status')}, 时间: {deploy.get('createdAt')}")

print("\n" + "=" * 60)
print(f"后端URL: {BACKEND_URL}")
print("=" * 60)
