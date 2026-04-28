import json
import urllib.request
import urllib.error

API_TOKEN = "rnd_cyYYfUSrtwFuLcqvjjMrRlzgUsQS"

# 尝试v2 API
def api_call_v2(method, endpoint, data=None):
    url = f"https://api.render.com/v2{endpoint}"
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

# 尝试Blueprint API
def api_call_blueprint(method, endpoint, data=None):
    url = f"https://api.render.com/v1{endpoint}"
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

# 测试Blueprint API
print("测试 Blueprint API...")
blueprint = api_call_blueprint("POST", "/blueprints", {
    "repository": {
        "url": "https://github.com/Nagato-YUKI/smart-scheduler.git",
        "branch": "main"
    }
})

if blueprint:
    print("Blueprint创建成功!")
    print(json.dumps(blueprint, indent=2))
else:
    print("Blueprint创建失败，尝试其他API...")
