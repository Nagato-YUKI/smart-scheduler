import json
import urllib.request

API_TOKEN = "rnd_cyYYfUSrtwFuLcqvjjMrRlzgUsQS"
SERVICE_ID = "srv-d7o8i2bc2cfs73993q10"

DATABASE_URL = "postgresql://paike_db_user:w8q6uJaA16ibBbrtZMz9nGEphEW3jecC@dpg-d7o8upsvikkc73bo7j6g-a/paike_db"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# 尝试通过API更新环境变量
print("=" * 60)
print("通过API更新环境变量...")
print("=" * 60)

# 首先获取服务详情
try:
    url = f"https://api.render.com/v1/services/{SERVICE_ID}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        service = json.loads(resp.read())
        print(f"服务名称: {service.get('name')}")
        print(f"当前环境变量: {service.get('envVars', [])}")
except Exception as e:
    print(f"获取服务失败: {e}")

# 尝试更新环境变量
print(f"\n尝试添加 DATABASE_URL 环境变量...")

update_data = {
    "envVars": [
        {"key": "PYTHON_VERSION", "value": "3.11.0"},
        {"key": "FLASK_ENV", "value": "production"},
        {"key": "DB_TYPE", "value": "postgresql"},
        {"key": "DATABASE_URL", "value": DATABASE_URL},
        {"key": "CORS_ORIGINS", "value": "https://nagato-yuki.github.io"}
    ]
}

try:
    url = f"https://api.render.com/v1/services/{SERVICE_ID}"
    data = json.dumps(update_data).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
    with urllib.request.urlopen(req) as resp:
        result = json.loads(resp.read())
        print(f"更新成功!")
        print(f"服务URL: {result.get('serviceDetails', {}).get('url')}")
except urllib.error.HTTPError as e:
    error_body = e.read().decode()
    print(f"HTTP错误 {e.code}: {error_body}")
except Exception as e:
    print(f"错误: {e}")
