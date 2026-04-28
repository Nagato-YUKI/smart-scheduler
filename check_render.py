import json
import urllib.request
import urllib.error

API_TOKEN = "rnd_F6lGbN8a68KuoR4sDX6myD1p0zoW"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

def api_call(endpoint):
    url = f"https://api.render.com/v1{endpoint}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None

print("=" * 60)
print("检查Render当前状态")
print("=" * 60)

# 检查数据库
print("\n[1/2] 检查数据库...")
databases_raw = api_call("/postgres")
if databases_raw:
    databases = [item.get('postgres', item) for item in databases_raw]
    for db in databases:
        name = db.get('name', 'N/A')
        status = db.get('status', 'N/A')
        dbid = db.get('id', 'N/A')
        print(f"数据库: {name} (ID: {dbid}, 状态: {status})")
else:
    print("未找到数据库")

# 检查服务
print("\n[2/2] 检查服务...")
services_raw = api_call("/services")
if services_raw:
    services = [item.get('service', item) for item in services_raw]
    for s in services:
        name = s.get('name', 'N/A')
        status = s.get('status', 'N/A')
        sid = s.get('id', 'N/A')
        url = s.get('serviceDetails', {}).get('url', 'N/A')
        print(f"服务: {name} (ID: {sid}, 状态: {status})")
        print(f"  URL: https://{url}")
else:
    print("未找到服务")

print("\n" + "=" * 60)
