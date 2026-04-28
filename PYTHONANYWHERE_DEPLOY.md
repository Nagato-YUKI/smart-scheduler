# PythonAnywhere 部署指南

## 1. 注册账号

访问 [https://www.pythonanywhere.com](https://www.pythonanywhere.com) 注册免费账号

## 2. 创建Web应用

1. 登录后，点击 **"Web"** 标签
2. 点击 **"Add a new web app"**
3. 选择 **Manual configuration**
4. 选择 **Python 3.10**（或最新版本）
5. 输入域名：`你的用户名.pythonanywhere.com`
6. 点击 **Next**

## 3. 配置代码

### 3.1 打开 Bash 控制台

在 PythonAnywhere 控制台，点击 **"Consoles"** > **"Bash"**

### 3.2 克隆代码

```bash
git clone https://github.com/Nagato-YUKI/smart-scheduler.git
cd smart-scheduler/backend
```

### 3.3 安装依赖

```bash
pip3.10 install --user -r requirements.txt
```

## 4. 配置 WSGI 文件

### 4.1 进入 Web 配置页面

回到 **"Web"** 标签，找到 **WSGI configuration file**，点击链接

### 4.2 编辑 WSGI 文件

删除原有内容，替换为：

```python
import os
import sys

# 添加项目路径
path = '/home/你的用户名/smart-scheduler/backend'
if path not in sys.path:
    sys.path.append(path)

# 设置环境变量
os.environ['FLASK_ENV'] = 'production'
os.environ['DATABASE_PATH'] = '/home/你的用户名/smart-scheduler/backend/paike.db'
os.environ['CORS_ORIGINS'] = 'https://nagato-yuki.github.io'

# 导入 Flask 应用
from app import create_app
application = create_app()
```

**注意：将 `你的用户名` 替换为你的 PythonAnywhere 用户名**

## 5. 配置虚拟环境（可选）

在 **"Web"** 标签的 **Virtualenv** 部分，输入：

```
/home/你的用户名/.local
```

## 6. 初始化数据库

在 Bash 控制台执行：

```bash
cd /home/你的用户名/smart-scheduler/backend
python3.10 init_db.py
```

## 7. 重新加载应用

点击 **"Web"** 标签顶部的 **Reload** 按钮

## 8. 测试后端

访问：`https://你的用户名.pythonanywhere.com/api/health`

应该返回：
```json
{"status": "ok"}
```

## 9. 修改前端配置

### 9.1 修改前端 API 配置

编辑 `frontend/src/api/index.js`，将：

```javascript
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})
```

改为：

```javascript
const api = axios.create({
  baseURL: 'https://你的用户名.pythonanywhere.com/api',
  timeout: 10000
})
```

### 9.2 重新构建前端

```bash
cd frontend
npm install
npm run build
```

### 9.3 部署到 GitHub Pages

将 `frontend/dist` 目录的内容推送到 `gh-pages` 分支：

```bash
cd frontend/dist
git init
git add .
git commit -m "Deploy to GitHub Pages"
git branch -M gh-pages
git remote add origin https://github.com/Nagato-YUKI/smart-scheduler.git
git push -f origin gh-pages
```

## 10. 完成

现在访问：`https://nagato-yuki.github.io/smart-scheduler/`

前端将调用 PythonAnywhere 的后端 API，数据会持久保存在 PythonAnywhere 的文件系统中。

## 注意事项

1. **免费账号限制**：
   - 每天需要手动在控制台点击一次保持活跃
   - 每月有 CPU 和带宽限制
   - 只能使用 HTTP（不能自定义域名HTTPS）

2. **数据备份**：
   - 数据库文件位于：`/home/你的用户名/smart-scheduler/backend/paike.db`
   - 定期下载备份

3. **日志查看**：
   - 在 **"Web"** 标签可以查看错误日志
   - 调试时非常有用
