import json
import urllib.request

API_TOKEN = "rnd_cyYYfUSrtwFuLcqvjjMrRlzgUsQS"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Accept": "application/json"
}

# 获取所有Postgres数据库
print("=" * 60)
print("获取PostgreSQL数据库...")
print("=" * 60)
try:
    url = "https://api.render.com/v1/postgres"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as resp:
        databases = json.loads(resp.read())
        print(f"找到 {len(databases)} 个数据库")
        for db in databases:
            print(f"\n数据库详情:")
            print(f"  ID: {db.get('id')}")
            print(f"  名称: {db.get('name')}")
            print(f"  状态: {db.get('status')}")
            print(f"  连接URL: {db.get('connectionDetails', {}).get('externalUrl', 'N/A')}")
            print(f"  内部URL: {db.get('connectionDetails', {}).get('internalUrl', 'N/A')}")
except urllib.error.HTTPError as e:
    print(f"HTTP错误 {e.code}: {e.read().decode()}")
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
