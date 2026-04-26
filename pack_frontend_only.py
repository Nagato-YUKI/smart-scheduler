import os
import zipfile

project_dir = r"e:\trae project\paike"
frontend_dir = os.path.join(project_dir, "frontend")
output_zip = os.path.join(project_dir, "smart-scheduler-frontend-feishu.zip")

exclude_dirs = ['__pycache__', 'node_modules', '.pytest_cache', '.git', '.venv', 'venv', 'env', 'dist', '.vite']
exclude_files = ['.DS_Store', 'Thumbs.db', 'package-lock.json']

def should_exclude(filepath):
    for exclude_dir in exclude_dirs:
        if f'\\{exclude_dir}\\' in filepath or filepath.endswith(f'\\{exclude_dir}'):
            return True
    filename = os.path.basename(filepath)
    if filename in exclude_files:
        return True
    if filename.endswith('.db') or filename.endswith('.pyc'):
        return True
    return False

print("正在打包前端项目（不含后端代码）...")
print(f"输出文件: {output_zip}")

with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    file_count = 0
    total_size = 0
    
    for root, dirs, files in os.walk(frontend_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            filepath = os.path.join(root, file)
            if should_exclude(filepath):
                continue
            rel_path = os.path.relpath(filepath, project_dir)
            if rel_path.endswith('.zip'):
                continue
            try:
                zipf.write(filepath, rel_path)
                file_size = os.path.getsize(filepath)
                file_count += 1
                total_size += file_size
                print(f"  添加: {rel_path} ({file_size:,} bytes)")
            except Exception as e:
                print(f"  跳过: {rel_path} (错误: {e})")

print(f"\n打包完成!")
print(f"输出文件: {output_zip}")
print(f"文件数量: {file_count}")
print(f"总大小: {total_size:,} bytes ({total_size/1024:.2f} KB)")
print(f"压缩后大小: {os.path.getsize(output_zip):,} bytes ({os.path.getsize(output_zip)/1024:.2f} KB)")
