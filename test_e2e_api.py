# -*- coding: utf-8 -*-
"""智能排课系统端到端测试脚本 - 纯标准库版本"""
import urllib.request
import urllib.error
import json
import time
from datetime import datetime

# ========== 配置 ==========
BACKEND_URL = "https://smart-scheduler-0q2w.onrender.com"
FRONTEND_URL = "https://nagato-yuki.github.io/smart-scheduler/"
TIMEOUT = 30

# ========== 测试结果记录 ==========
results = []

def print_result(test_id, name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    icon = "[OK]" if passed else "[FAIL]"
    print(f"{icon} TC-{test_id}: {name} - {status}")
    if detail:
        print(f"     详情: {detail}")
    results.append({
        "test_id": str(test_id),
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "detail": detail
    })

def http_get(url, headers=None, timeout=TIMEOUT):
    req = urllib.request.Request(url)
    if headers:
        for k, v in headers.items():
            req.add_header(k, v)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    resp = urllib.request.urlopen(req, timeout=timeout)
    body = resp.read().decode("utf-8", errors="replace")
    status = resp.status
    resp_headers = dict(resp.headers)
    return status, body, resp_headers

# ========== 测试开始 ==========
print("=" * 60)
print("智能排课系统 - 端到端测试")
print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"后端地址: {BACKEND_URL}")
print(f"前端地址: {FRONTEND_URL}")
print("=" * 60)

# ---- 测试 1: API 健康检查 ----
print("\n--- 测试 1: API 健康检查 ---")
try:
    start = time.time()
    status, body, headers = http_get(f"{BACKEND_URL}/api/health")
    elapsed = round(time.time() - start, 2)
    data = json.loads(body)
    passed = status == 200 and data.get("status") == "ok"
    print_result(1, "健康检查 /api/health", passed,
                 f"HTTP {status}, 响应时间: {elapsed}秒, 响应: {body.strip()}")
except Exception as e:
    print_result(1, "健康检查 /api/health", False, f"异常: {str(e)}")

# ---- 测试 2: 教室管理 API ----
print("\n--- 测试 2: 教室管理 API ---")
try:
    start = time.time()
    status, body, headers = http_get(f"{BACKEND_URL}/api/rooms")
    elapsed = round(time.time() - start, 2)
    data = json.loads(body)
    count = len(data) if isinstance(data, list) else 0
    passed = status == 200
    print_result(2, "获取教室列表 /api/rooms", passed,
                 f"HTTP {status}, 教室数量: {count}, 响应时间: {elapsed}秒")
except Exception as e:
    print_result(2, "获取教室列表 /api/rooms", False, f"异常: {str(e)}")

# ---- 测试 3: 教师管理 API ----
print("\n--- 测试 3: 教师管理 API ---")
try:
    start = time.time()
    status, body, headers = http_get(f"{BACKEND_URL}/api/teachers")
    elapsed = round(time.time() - start, 2)
    data = json.loads(body)
    count = len(data) if isinstance(data, list) else 0
    passed = status == 200
    print_result(3, "获取教师列表 /api/teachers", passed,
                 f"HTTP {status}, 教师数量: {count}, 响应时间: {elapsed}秒")
except Exception as e:
    print_result(3, "获取教师列表 /api/teachers", False, f"异常: {str(e)}")

# ---- 测试 4: 班级管理 API ----
print("\n--- 测试 4: 班级管理 API ---")
try:
    start = time.time()
    status, body, headers = http_get(f"{BACKEND_URL}/api/classes")
    elapsed = round(time.time() - start, 2)
    data = json.loads(body)
    count = len(data) if isinstance(data, list) else 0
    passed = status == 200
    print_result(4, "获取班级列表 /api/classes", passed,
                 f"HTTP {status}, 班级数量: {count}, 响应时间: {elapsed}秒")
except Exception as e:
    print_result(4, "获取班级列表 /api/classes", False, f"异常: {str(e)}")

# ---- 测试 5: 课程管理 API ----
print("\n--- 测试 5: 课程管理 API ---")
try:
    start = time.time()
    status, body, headers = http_get(f"{BACKEND_URL}/api/courses")
    elapsed = round(time.time() - start, 2)
    data = json.loads(body)
    count = len(data) if isinstance(data, list) else 0
    passed = status == 200
    print_result(5, "获取课程列表 /api/courses", passed,
                 f"HTTP {status}, 课程数量: {count}, 响应时间: {elapsed}秒")
except Exception as e:
    print_result(5, "获取课程列表 /api/courses", False, f"异常: {str(e)}")

# ---- 测试 6: 节假日管理 API ----
print("\n--- 测试 6: 节假日管理 API ---")
try:
    start = time.time()
    status, body, headers = http_get(f"{BACKEND_URL}/api/holidays")
    elapsed = round(time.time() - start, 2)
    data = json.loads(body)
    count = len(data) if isinstance(data, list) else 0
    passed = status == 200
    print_result(6, "获取节假日列表 /api/holidays", passed,
                 f"HTTP {status}, 节假日数量: {count}, 响应时间: {elapsed}秒")
except Exception as e:
    print_result(6, "获取节假日列表 /api/holidays", False, f"异常: {str(e)}")

# ---- 测试 7: CORS 跨域配置 ----
print("\n--- 测试 7: CORS 跨域配置 ---")
try:
    status, body, headers = http_get(f"{BACKEND_URL}/api/health")
    cors = headers.get("Access-Control-Allow-Origin", headers.get("access-control-allow-origin", ""))
    passed = "*" in cors or "github" in cors.lower()
    print_result(7, "CORS 跨域配置", passed,
                 f"Access-Control-Allow-Origin: {cors}")
except Exception as e:
    print_result(7, "CORS 跨域配置", False, f"异常: {str(e)}")

# ---- 测试 8: 前端首页可达性 ----
print("\n--- 测试 8: 前端首页可达性 ---")
try:
    start = time.time()
    status, body, headers = http_get(FRONTEND_URL)
    elapsed = round(time.time() - start, 2)
    has_vue = "vue" in body.lower() or "id=\"app\"" in body.lower()
    passed = status == 200 and has_vue
    print_result(8, "前端首页可达性", passed,
                 f"HTTP {status}, 响应时间: {elapsed}秒, 包含Vue标记: {has_vue}")
except Exception as e:
    print_result(8, "前端首页可达性", False, f"异常: {str(e)}")

# ---- 测试 9: 前端路由可达性 ----
print("\n--- 测试 9: 前端路由可达性 ---")
routes = [
    ("/", "首页"),
    ("/rooms", "教室管理"),
    ("/teachers", "教师管理"),
    ("/classes", "班级管理"),
    ("/courses", "课程管理"),
    ("/import", "数据导入"),
    ("/schedules", "排课管理"),
    ("/statistics", "统计分析"),
    ("/adjust-schedule", "调整课表"),
    ("/holidays", "节假日管理"),
]

for route, name in routes:
    try:
        url = f"{FRONTEND_URL}{route}" if route != "/" else FRONTEND_URL
        status, body, headers = http_get(url)
        passed = status == 200
        print_result(f"9-{route}", f"前端路由: {name}", passed,
                     f"HTTP {status}")
    except Exception as e:
        print_result(f"9-{route}", f"前端路由: {name}", False,
                     f"异常: {str(e)}")

# ========== 汇总 ==========
print("\n" + "=" * 60)
print("测试汇总")
print("=" * 60)

pass_count = sum(1 for r in results if r["status"] == "PASS")
fail_count = sum(1 for r in results if r["status"] == "FAIL")
total_count = len(results)

print(f"总测试数: {total_count}")
print(f"通过: {pass_count}")
print(f"失败: {fail_count}")
print(f"通过率: {round(pass_count/total_count*100, 1)}%")

print("\n失败项目:")
for r in results:
    if r["status"] == "FAIL":
        print(f"  - TC-{r['test_id']}: {r['name']}")
        print(f"    详情: {r['detail']}")

# 保存结果
with open("e:\\trae project\\paike\\test-results-api.json", "w", encoding="utf-8") as f:
    json.dump({
        "test_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "backend_url": BACKEND_URL,
        "frontend_url": FRONTEND_URL,
        "total": total_count,
        "pass": pass_count,
        "fail": fail_count,
        "pass_rate": f"{round(pass_count/total_count*100, 1)}%",
        "results": results
    }, f, ensure_ascii=False, indent=2)

print(f"\n详细结果已保存到 test-results-api.json")
