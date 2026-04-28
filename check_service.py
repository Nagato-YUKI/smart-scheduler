import json
import urllib.request

API_TOKEN = "rnd_F6lGbN8a68KuoR4sDX6myD1p0zoW"
SERVICE_ID = "srv-d7o9ropj2pic739noq8g"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

print("=" * 60)
print("检查服务配置")
print("=" * 60)

# 获取服务详情
try:
    url = f"https://api.render.com/v1/services/{SERVICE_ID}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as resp:
        raw = json.loads(resp.read())
        service = raw.get('service', raw)
        print(f"\n服务名称: {service.get('name')}")
        print(f"服务状态: {service.get('status')}")
        print(f"部署状态: {service.get('latestDeploy', {}).get('status')}")
        
        # 获取环境变量
        env_vars = service.get('envVars', [])
        print(f"\n环境变量 ({len(env_vars)}个):")
        for var in env_vars:
            key = var.get('key', 'N/A')
            value = var.get('value', 'N/A')
            # 隐藏敏感信息
            if 'URL' in key or 'SECRET' in key:
                value = '***' + str(value)[-10:] if value else '(空)'
            print(f"  {key}={value}")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 60)
