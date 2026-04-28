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

print("=" * 60)
print("自动化 Render 清理和重新部署")
print("=" * 60)

# 1. 获取并删除现有服务
print("\n[1/6] 获取现有服务...")
services_raw = api_call("GET", "/services")
if services_raw:
    services = [item.get('service', item) for item in services_raw]
    for s in services:
        sid = s.get('id')
        name = s.get('name', '')
        print(f"  找到服务: {name} (ID: {sid})")
        if 'smart' in name.lower() or 'paike' in name.lower():
            print(f"  删除服务: {name}...")
            result = api_call("DELETE", f"/services/{sid}")
            if result is None or result == {}:
                print(f"  删除成功!")
            time.sleep(2)

# 2. 获取并删除现有数据库
print("\n[2/6] 获取现有数据库...")
databases_raw = api_call("GET", "/postgres")
if databases_raw:
    databases = [item.get('postgres', item) for item in databases_raw]
    for db in databases:
        dbid = db.get('id')
        name = db.get('name', '')
        print(f"  找到数据库: {name} (ID: {dbid})")
        if 'paike' in name.lower() or 'smart' in name.lower():
            print(f"  删除数据库: {name}...")
            result = api_call("DELETE", f"/postgres/{dbid}")
            if result is None or result == {}:
                print(f"  删除成功!")
            time.sleep(2)

# 3. 获取并删除现有项目
print("\n[3/6] 获取现有项目...")
projects = api_call("GET", "/projects")
if projects:
    for p in projects:
        pid = p.get('id')
        name = p.get('name', '')
        print(f"  找到项目: {name} (ID: {pid})")
        if 'smart' in name.lower() or 'paike' in name.lower():
            print(f"  删除项目: {name}...")
            result = api_call("DELETE", f"/projects/{pid}")
            if result is None or result == {}:
                print(f"  删除成功!")
            time.sleep(2)

print("\n" + "=" * 60)
print("清理完成！")
print("=" * 60)
print("\n现在准备创建新的Blueprint...")

# 4. 创建新项目
print("\n[4/6] 创建新项目...")
project_data = {"name": "smart-scheduler"}
project = api_call("POST", "/projects", project_data)
if project:
    project_id = project.get('id')
    print(f"项目创建成功: {project.get('name')} (ID: {project_id})")
else:
    print("项目创建失败，使用默认项目")
    project_id = None

# 5. 创建PostgreSQL数据库
print("\n[5/6] 创建PostgreSQL数据库...")
db_data = {
    "name": "paike-db",
    "region": "oregon",
    "plan": "free",
    "version": "15"
}
if project_id:
    db_data["ownerId"] = project_id

database = api_call("POST", "/postgres", db_data)
if database:
    db_id = database.get('id')
    print(f"数据库创建成功: {database.get('name')} (ID: {db_id})")
    print(f"等待数据库就绪...")
    time.sleep(30)  # 等待数据库初始化
else:
    print("数据库创建失败")
    exit(1)

# 6. 创建Web服务
print("\n[6/6] 创建Web服务...")
web_data = {
    "type": "web_service",
    "name": "smart-scheduler",
    "repo": "https://github.com/Nagato-YUKI/smart-scheduler.git",
    "branch": "main",
    "rootDir": "backend",
    "buildCommand": "pip install -r requirements.txt",
    "startCommand": "gunicorn --bind 0.0.0.0:$PORT wsgi:app",
    "plan": "free",
    "region": "oregon",
    "autoDeploy": "yes",
    "envVars": [
        {"key": "PYTHON_VERSION", "value": "3.11"},
        {"key": "FLASK_ENV", "value": "production"},
        {"key": "DB_TYPE", "value": "postgresql"},
        {"key": "DATABASE_URL", "fromService": {"type": "postgres", "name": "paike-db", "property": "connectionString"}},
        {"key": "CORS_ORIGINS", "value": "https://nagato-yuki.github.io"}
    ]
}
if project_id:
    web_data["ownerId"] = project_id

web_service = api_call("POST", "/services", web_data)
if web_service:
    service = web_service.get('service', web_service)
    print(f"Web服务创建成功!")
    print(f"  名称: {service.get('name')}")
    print(f"  ID: {service.get('id')}")
    print(f"  URL: {service.get('dashboardUrl', 'N/A')}")
    
    # 尝试获取服务URL
    service_details = service.get('serviceDetails', {})
    print(f"  访问URL: https://{service_details.get('url', 'deploying...')}")
else:
    print("Web服务创建失败")
    exit(1)

print("\n" + "=" * 60)
print("部署完成!")
print("=" * 60)
print("\n请等待2-3分钟让部署完成，然后测试后端API")
