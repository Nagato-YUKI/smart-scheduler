import json
import urllib.request

API_TOKEN = "rnd_F6lGbN8a68KuoR4sDX6myD1p0zoW"
SERVICE_ID = "srv-d7o8t2rbc2fs73993hj0"

DATABASE_URL = "postgresql://paike_db_user:w8q6uJaA16ibBbrtZMz9nGEphEW3jecC@dpg-d7o8upsvikkc73bo7j6g-a/paike_db"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 60)
print("通过API设置环境变量并触发部署")
print("=" * 60)

# 方式1: 逐个添加环境变量
print("\n[1/6] 添加 PYTHON_VERSION...")
data = {"key": "PYTHON_VERSION", "value": "3.11"}
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars",
    data=json.dumps(data).encode(),
    headers=headers,
    method="POST"
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"  成功: {resp.status}")
except Exception as e:
    print(f"  失败: {e}")

print("\n[2/6] 添加 FLASK_ENV...")
data = {"key": "FLASK_ENV", "value": "production"}
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars",
    data=json.dumps(data).encode(),
    headers=headers,
    method="POST"
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"  成功: {resp.status}")
except Exception as e:
    print(f"  失败: {e}")

print("\n[3/6] 添加 DB_TYPE...")
data = {"key": "DB_TYPE", "value": "postgresql"}
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars",
    data=json.dumps(data).encode(),
    headers=headers,
    method="POST"
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"  成功: {resp.status}")
except Exception as e:
    print(f"  失败: {e}")

print("\n[4/6] 添加 DATABASE_URL...")
data = {"key": "DATABASE_URL", "value": DATABASE_URL}
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars",
    data=json.dumps(data).encode(),
    headers=headers,
    method="POST"
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"  成功: {resp.status}")
except Exception as e:
    print(f"  失败: {e}")

print("\n[5/6] 添加 CORS_ORIGINS...")
data = {"key": "CORS_ORIGINS", "value": "https://nagato-yuki.github.io"}
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars",
    data=json.dumps(data).encode(),
    headers=headers,
    method="POST"
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        print(f"  成功: {resp.status}")
except Exception as e:
    print(f"  失败: {e}")

# 触发部署
print("\n[6/6] 触发部署...")
req = urllib.request.Request(
    f"https://api.render.com/v1/services/{SERVICE_ID}/deploys",
    data=b"{}",
    headers=headers,
    method="POST"
)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read())
        print(f"  部署已触发!")
        deploy = result.get("deploy", result)
        print(f"  部署ID: {deploy.get('id')}")
        print(f"  状态: {deploy.get('status')}")
except Exception as e:
    print(f"  失败: {e}")

print("\n" + "=" * 60)
print("环境变量设置完成，等待部署...")
print("=" * 60)
