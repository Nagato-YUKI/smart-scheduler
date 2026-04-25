import subprocess
import os
import sys

print("尝试创建GitHub仓库并推送代码...")
print("="*60)

# 步骤1: 检查gh是否安装
try:
    result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("✅ GitHub CLI 已安装")
    else:
        print("⚠️ GitHub CLI 未正确安装")
except FileNotFoundError:
    print("⚠️ GitHub CLI 未安装，尝试手动方式...")

# 步骤2: 检查git配置
result = subprocess.run(['git', 'config', '--global', 'user.name'], capture_output=True, text=True)
print(f"Git用户名: {result.stdout.strip()}")
result = subprocess.run(['git', 'config', '--global', 'user.email'], capture_output=True, text=True)
print(f"Git邮箱: {result.stdout.strip()}")

# 步骤3: 提供手动命令
print("\n" + "="*60)
print("请手动执行以下步骤:")
print("="*60)
print()
print("1. 创建GitHub仓库（在GitHub网站上）:")
print("   - 访问: https://github.com/new")
print("   - 仓库名: smart-scheduler")
print("   - 描述: 智能排课系统")
print("   - 不要初始化README/.gitignore")
print()
print("2. 添加远程仓库并推送（在终端中执行）:")
print("   cd e:\\trae project\\paike")
print("   git remote add origin https://github.com/Nagato-YUKI/smart-scheduler.git")
print("   git branch -M main")
print("   git push -u origin main")
print()
print("3. 如果已登录GitHub账号，可直接推送")
print("   否则会提示登录")
