# 飞书妙搭导入指南

## 文件说明

已生成以下文件：

1. **smart-scheduler-feishu.zip** - 项目压缩包（0.12 MB）
2. **feishu-config.json** - 飞书妙搭配置文件
3. **FEISHU_IMPORT_GUIDE.md** - 本导入指南

## 导入步骤

### 第1步：打开飞书妙搭

访问飞书妙搭平台，进入导入页面。

### 第2步：选择上传方式

点击 **"上传 .zip 文件"** 选项。

### 第3步：上传压缩包

选择 `smart-scheduler-feishu.zip` 文件上传。

### 第4步：配置项目

导入时可能需要填写以下信息：

- **项目名称**: 智能排课系统
- **项目描述**: 基于Python/Flask + Vue3的全栈排课解决方案
- **运行环境**: 
  - 后端: Python 3.10+
  - 前端: Node.js 18+

### 第5步：确认导入

确认配置无误后，点击导入按钮完成导入。

## 项目结构

```
smart-scheduler/
├── README.md                 # 项目文档
├── .gitignore                # Git忽略配置
├── feishu-config.json        # 妙搭配置文件
├── backend/                  # 后端代码
│   ├── app.py                # Flask入口
│   ├── config.py             # 配置
│   ├── peewee_manager.py     # 数据库模型
│   ├── requirements.txt      # Python依赖
│   ├── routes/               # API路由
│   ├── scheduler/            # 排课算法
│   └── utils/                # 工具函数
└── frontend/                 # 前端代码
    ├── package.json          # 前端依赖
    ├── vite.config.js        # Vite配置
    └── src/                  # Vue源码
```

## 依赖安装

### 后端

```bash
cd backend
pip install -r requirements.txt
```

依赖列表：
- Flask 3.1.0
- flask-cors 5.0.1
- openpyxl 3.1.5
- peewee 3.17.8
- python-dotenv 1.0.1

### 前端

```bash
cd frontend
npm install
```

依赖列表：
- Vue 3.5.13
- Element Plus 2.9.1
- Vite 6.0.5
- Vue Router 4.5.0
- Pinia 2.3.0
- Axios 1.7.9

## 启动服务

### 后端

```bash
cd backend
python app.py
```

服务地址: http://localhost:5000

### 前端

```bash
cd frontend
npm run dev
```

服务地址: http://localhost:5173

## 功能说明

1. **数据管理**: 教室/教师/班级/课程CRUD
2. **Excel导入**: 批量导入教学数据
3. **智能排课**: 自动分配时间、教室、教师
4. **课表展示**: 多维度查看课表
5. **统计分析**: 排课完成率统计

## 注意事项

1. 导入后首次运行需要初始化数据库
2. 确保Python版本 >= 3.10
3. 确保Node.js版本 >= 18.0
4. 后端服务需要先启动，前端才能正常调用API

## 常见问题

### Q: 导入后无法启动？
A: 检查依赖是否安装完整，特别是后端需要 `pip install -r requirements.txt`

### Q: 前端页面空白？
A: 确保后端服务已启动，检查浏览器控制台是否有跨域错误

### Q: 排课功能不工作？
A: 检查是否已导入基础数据（教室、教师、班级、课程）

## 联系支持

如有问题，请联系：
- GitHub: https://github.com/Nagato-YUKI/smart-scheduler
