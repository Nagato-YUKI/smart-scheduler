import sys
import os

# 读取原始文件
with open('backend/scheduler/constraints.py', 'rb') as f:
    raw = f.read()

# 检查BOM
if raw[:3] == b'\xef\xbb\xbf':
    print("发现BOM!")
    raw = raw[3:]

# 检查是否有混合换行符
content = raw.decode('utf-8', errors='replace')
if '\r\n' in content:
    print("发现Windows换行符，转换为Unix...")
    content = content.replace('\r\n', '\n')
    raw = content.encode('utf-8')

# 重新写入（确保UTF-8无BOM，Unix换行符）
with open('backend/scheduler/constraints.py', 'wb') as f:
    f.write(raw)

print("文件已规范化")
print(f"文件大小: {len(raw)} bytes")

# 验证
with open('backend/scheduler/constraints.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print(f"总行数: {len(lines)}")
    for i, line in enumerate(lines[148:155], start=149):
        print(f"  Line {i}: {repr(line)}")
