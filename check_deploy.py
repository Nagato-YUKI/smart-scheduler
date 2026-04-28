import json
import urllib.request

API_TOKEN = "rnd_F6lGbN8a68KuoR4sDX6myD1p0zoW"
SERVICE_ID = "srv-d7o8t2rbc2fs73993hj0"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

print("=" * 60)
print("获取服务详情和最新状态...")
print("=" * 60)

# 获取服务详情
try:
    url = f"https://api.render.com/v1/services/{SERVICE_ID}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = json.loads(resp.read())
        service = raw.get("service", raw)
        print(f"服务名称: {service.get('name')}")
        print(f"服务状态: {service.get('status')}")
        print(f"最后更新: {service.get('updatedAt')}")
        print(f"当前部署: {service.get('latestDeploy', {})}")
except Exception as e:
    print(f"错误: {e}")

# 获取环境变量
print("\n当前环境变量:")
try:
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        env_vars = json.loads(resp.read())
        for var in env_vars:
            key = var.get("key", "")
            value = var.get("value", "")
            # 隐藏敏感信息
            if "URL" in key or "SECRET" in key:
                value = "***" + value[-10:] if value else "(空)"
            print(f"  {key}={value}")
except Exception as e:
    print(f"错误: {e}")

# 尝试获取部署日志
print("\n尝试获取构建日志...")
try:
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/events?limit=20"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        events = json.loads(resp.read())
        print(f"找到 {len(events)} 个事件")
        for e in events[:10]:
            event = e.get("event", e)
            print(f"  [{event.get('createdAt')}] {event.get('type')}: {event.get('message', '')[:200]}")
except Exception as e:
    print(f"错误: {e}")
