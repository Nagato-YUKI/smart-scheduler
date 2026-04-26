import os
import zipfile
import time

# 项目根目录
project_dir = r"e:\trae project\paike"
output_zip = os.path.join(project_dir, "smart-scheduler-feishu.zip")

# 需要排除的文件和目录
exclude_dirs = [
    '__pycache__',
    'node_modules',
    '.pytest_cache',
    '.git',
    '.venv',
    'venv',
    'env',
    'dist',
    '.vite',
]

exclude_files = [
    'paike.db',
    '.DS_Store',
    'Thumbs.db',
    'push_to_github.py',
    'test_template.csv',
    'test_upload.csv',
    'package-lock.json',
]

def should_exclude(filepath):
    """检查文件是否应该排除"""
    # 检查排除目录
    for exclude_dir in exclude_dirs:
        if f'\\{exclude_dir}\\' in filepath or filepath.endswith(f'\\{exclude_dir}'):
            return True
    
    # 检查排除文件
    filename = os.path.basename(filepath)
    if filename in exclude_files:
        return True
    
    # 排除所有 .db 文件
    if filename.endswith('.db'):
        return True
    
    # 排除 .pyc 文件
    if filename.endswith('.pyc'):
        return True
    
    return False

# 创建zip文件
print("正在打包项目...")
print(f"输出文件: {output_zip}")

with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    file_count = 0
    total_size = 0
    
    for root, dirs, files in os.walk(project_dir):
        # 过滤排除的目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            filepath = os.path.join(root, file)
            
            if should_exclude(filepath):
                continue
            
            # 计算相对路径
            rel_path = os.path.relpath(filepath, project_dir)
            
            # 跳过zip文件自己
            if rel_path == 'smart-scheduler-feishu.zip':
                continue
            
            try:
                zipf.write(filepath, rel_path)
                file_size = os.path.getsize(filepath)
                file_count += 1
                total_size += file_size
                print(f"  添加: {rel_path} ({file_size:,} bytes)")
            except Exception as e:
                print(f"  跳过: {rel_path} (错误: {e})")

# 输出统计信息
print("\n" + "="*60)
print("打包完成!")
print("="*60)
print(f"输出文件: {output_zip}")
print(f"文件数量: {file_count}")
print(f"总大小: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")
print(f"压缩后大小: {os.path.getsize(output_zip):,} bytes ({os.path.getsize(output_zip)/1024/1024:.2f} MB)")
print("="*60)
