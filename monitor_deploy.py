import json
import urllib.request
import time

API_TOKEN = "rnd_F6lGbN8a68KuoR4sDX6myD1p0zoW"
SERVICE_ID = "srv-d7o8t2rbc2fs73993hj0"
BACKEND_URL = "https://smart-scheduler-oht3.onrender.com"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

def api_call(endpoint):
    url = f"https://api.render.com/v1{endpoint}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"错误: {e}")
        return None

print("=" * 60)
print("等待Render自动部署...")
print("=" * 60)

# 等待并监控部署状态
for i in range(12):  # 最多等待3分钟
    time.sleep(15)
    
    deploys = api_call(f"/services/{SERVICE_ID}/deploys")
    if deploys:
        latest = deploys[0].get("deploy", deploys[0])
        status = latest.get("status", "unknown")
        trigger = latest.get("trigger", "unknown")
        print(f"[{(i+1)*15}s] 状态: {status}, 触发: {trigger}")
        
        if status in ["live", "completed", "ready"]:
            print("\n部署成功!")
            break
        elif status in ["failed", "error", "update_failed"]:
            print("\n部署失败!")
            break
    else:
        print(f"[{(i+1)*15}s] 无法获取状态")

# 测试后端API
print("\n" + "=" * 60)
print("测试后端API...")
print("=" * 60)

try:
    req = urllib.request.Request(f"{BACKEND_URL}/api/health")
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
        print(f"API健康检查: {data}")
except Exception as e:
    print(f"API测试失败: {e}")

# 获取最终服务状态
print("\n获取服务最终状态...")
service = api_call(f"/services/{SERVICE_ID}")
if service:
    svc = service.get("service", service)
    print(f"服务名称: {svc.get('name')}")
    print(f"服务状态: {svc.get('status')}")
    url_detail = svc.get("serviceDetails", {})
    print(f"服务URL: {url_detail.get('url', 'N/A')}")
