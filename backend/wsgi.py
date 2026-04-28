import os
import sys

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 设置默认环境变量（如果未设置）
if not os.environ.get("DB_TYPE"):
    os.environ["DB_TYPE"] = "sqlite"
    
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = os.path.join(current_dir, "paike.db")

# 自动初始化数据库
def init_database():
    try:
        from peewee_manager import (
            Room, Teacher, SchoolClass, Course, Holiday, TeachingClass, ScheduleEntry, _database
        )
        
        _database.connect()
        tables = [Room, Teacher, SchoolClass, Course, Holiday, TeachingClass, ScheduleEntry]
        _database.create_tables(tables, safe=True)
        print("数据库表初始化成功")
        _database.close()
    except Exception as e:
        print(f"数据库初始化失败（可能已经存在）: {e}")

# 在启动前初始化数据库
init_database()

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run()
