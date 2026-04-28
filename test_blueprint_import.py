# -*- coding: utf-8 -*-
"""测试蓝图导入是否正常"""
import sys
import os

# 添加 backend 目录到路径
backend_dir = r"e:\trae project\paike\backend"
sys.path.insert(0, backend_dir)
os.chdir(backend_dir)

# 设置环境变量
os.environ.setdefault("DB_TYPE", "sqlite")
os.environ.setdefault("DATABASE_URL", "test_diag.db")
os.environ.setdefault("SECRET_KEY", "test")

try:
    print("尝试导入蓝图...")
    from routes import rooms_bp, teachers_bp, classes_bp, courses_bp, holidays_bp, schedule_bp, import_bp
    print(f"rooms_bp: {rooms_bp}")
    print(f"teachers_bp: {teachers_bp}")
    print(f"classes_bp: {classes_bp}")
    print(f"courses_bp: {courses_bp}")
    print(f"holidays_bp: {holidays_bp}")
    print(f"schedule_bp: {schedule_bp}")
    print(f"import_bp: {import_bp}")
    print("所有蓝图导入成功!")
except Exception as e:
    print(f"蓝图导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n尝试创建 app...")
try:
    from app import create_app
    app = create_app()
    print("App 创建成功!")
    print("\n已注册路由:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")
except Exception as e:
    print(f"App 创建失败: {e}")
    import traceback
    traceback.print_exc()
