import json
import urllib.request
import urllib.error

API_TOKEN = "rnd_cyYYfUSrtwFuLcqvjjMrRlzgUsQS"
BASE_URL = "https://api.render.com/v1"

def api_call(method, endpoint, data=None):
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    if data:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Step 1: 获取用户信息
print("=" * 50)
print("Step 1: 获取用户信息")
print("=" * 50)
user = api_call("GET", "/user")
if user:
    print(f"用户名: {user.get('name')}")
    print(f"邮箱: {user.get('email')}")
else:
    print("无法获取用户信息，请检查API Token")
    exit(1)

# Step 2: 获取或创建项目
print("\n" + "=" * 50)
print("Step 2: 获取项目")
print("=" * 50)

projects = api_call("GET", "/projects")
if projects:
    print(f"找到 {len(projects)} 个项目")
    for p in projects:
        print(f"  - {p.get('name')} (ID: {p.get('id')})")
    
    # 查找或创建 smart-scheduler 项目
    project = None
    for p in projects:
        if p.get('name') == 'smart-scheduler':
            project = p
            break
    
    if not project:
        print("\n创建新项目...")
        project_data = {
            "name": "smart-scheduler",
            "ownerId": None  # 使用当前用户作为owner
        }
        project = api_call("POST", "/projects", project_data)
        if project:
            print(f"项目创建成功: {project.get('name')} (ID: {project.get('id')})")
        else:
            print("项目创建失败")
            exit(1)
    
    project_id = project.get('id')
    print(f"\n使用项目: {project.get('name')} (ID: {project_id})")

# Step 3: 创建 PostgreSQL 数据库
print("\n" + "=" * 50)
print("Step 3: 创建 PostgreSQL 数据库")
print("=" * 50)

db_data = {
    "name": "paike-db",
    "ownerId": project_id,
    "plan": "free",
    "region": "oregon",
    "version": "15"
}

database = api_call("POST", "/postgres", db_data)
if database:
    print(f"数据库创建成功!")
    print(f"  名称: {database.get('name')}")
    print(f"  ID: {database.get('id')}")
    print(f"  状态: {database.get('status')}")
    print(f"  Dashboard URL: {database.get('dashboardUrl')}")
    db_id = database.get('id')
else:
    print("数据库创建失败")
    exit(1)

# Step 4: 创建 Web 服务
print("\n" + "=" * 50)
print("Step 4: 创建 Web 服务")
print("=" * 50)

web_service_data = {
    "type": "web_service",
    "name": "smart-scheduler-backend",
    "ownerId": project_id,
    "repo": "https://github.com/Nagato-YUKI/smart-scheduler.git",
    "branch": "main",
    "buildCommand": "cd backend && pip install -r requirements.txt",
    "startCommand": "cd backend && gunicorn --bind 0.0.0.0:$PORT wsgi:app",
    "plan": "free",
    "region": "oregon",
    "runtime": "python",
    "autoDeploy": True,
    "envVars": [
        {"key": "PYTHON_VERSION", "value": "3.11.0"},
        {"key": "FLASK_ENV", "value": "production"},
        {"key": "DB_TYPE", "value": "postgresql"},
        {"key": "DATABASE_URL", "fromDatabase": {"name": "paike-db", "property": "connectionString"}},
        {"key": "CORS_ORIGINS", "value": "https://nagato-yuki.github.io"}
    ]
}

web_service = api_call("POST", "/services", web_service_data)
if web_service:
    print(f"Web 服务创建成功!")
    print(f"  名称: {web_service.get('name')}")
    print(f"  ID: {web_service.get('id')}")
    print(f"  状态: {web_service.get('status')}")
    print(f"  URL: https://{web_service.get('id')}.onrender.com")
else:
    print("Web 服务创建失败")
    exit(1)

print("\n" + "=" * 50)
print("部署完成!")
print("=" * 50)
print(f"\n后端 API 地址: https://{web_service.get('id')}.onrender.com")
print(f"数据库 Dashboard: {database.get('dashboardUrl')}")
print("\n等待服务部署完成后，请告诉我后端URL，我会继续配置前端!")
