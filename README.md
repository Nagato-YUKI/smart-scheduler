# 智能排课系统

> 基于Python/Flask后端 + Vue3前端的全栈排课解决方案，支持Excel数据导入和智能排课算法

## 项目简介

智能排课系统是一款面向学校教务部门的排课管理工具，能够自动为课程分配教师、教室、时间和班级，解决传统手动排课效率低、容易出错的问题。

### 核心功能

- **数据管理**：教室、教师、班级、课程的增删改查
- **Excel导入**：批量导入教学数据，支持模板下载
- **智能排课**：基于贪心算法自动分配时间、教室、教师
- **课表展示**：标准周课表视图，支持多维度筛选
- **统计面板**：排课完成率、课时分布、教师工作量统计

### 排课规则

- **大课时制**：上午4节、下午4节、晚上3节
- **学期范围**：默认16周（9月-次年2月）
- **节假日排除**：自动跳过法定节假日
- **教师容量**：每周最多5-6节课
- **教室匹配**：根据学生人数和课程类型自动选择合适教室

## 环境要求

### 后端环境

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.10+ | 运行环境 |
| Flask | 3.1.0 | Web框架 |
| Peewee | 3.17.8 | ORM框架 |
| SQLite | 内置 | 数据库 |
| openpyxl | 3.1.5 | Excel处理 |
| flask-cors | 5.0.1 | 跨域支持 |

### 前端环境

| 组件 | 版本要求 | 说明 |
|------|---------|------|
| Node.js | 18.0+ | 运行环境 |
| Vue | 3.5.13+ | 前端框架 |
| Vite | 6.0.5+ | 构建工具 |
| Element Plus | 2.9.1+ | UI组件库 |
| Vue Router | 4.5.0+ | 路由管理 |
| Pinia | 2.3.0+ | 状态管理 |

### 硬件要求

| 项目 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 双核 | 四核以上 |
| 内存 | 2GB | 4GB以上 |
| 磁盘 | 500MB | 1GB以上 |
| 操作系统 | Windows 10 / macOS 10.15+ / Linux | Windows 11 / macOS 12+ |

## 安装与部署

### 方法一：手动安装（开发环境）

#### 1. 克隆项目

```bash
git clone https://github.com/Nagato-YUKI/smart-scheduler.git
cd smart-scheduler
```

#### 2. 配置后端

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

pip install -r requirements.txt
```

#### 3. 配置前端

```bash
cd ../frontend
npm install
```

#### 4. 启动服务

**启动后端（终端1）：**
```bash
cd backend
venv\Scripts\activate
python app.py
```
后端默认运行在 http://localhost:5000

**启动前端（终端2）：**
```bash
cd frontend
npm run dev
```
前端默认运行在 http://localhost:5173

### 方法二：一键启动脚本

创建启动脚本 `start.bat`：

```batch
@echo off
echo 正在启动智能排课系统...

start cmd /k "cd backend && venv\Scripts\activate && python app.py"
timeout /t 3 /nobreak >nul
start cmd /k "cd frontend && npm run dev"

echo 服务已启动：
echo - 后端: http://localhost:5000
echo - 前端: http://localhost:5173
```

### 方法三：生产环境部署

#### 1. 后端部署（Gunicorn + Nginx）

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 2. 前端构建

```bash
cd frontend
npm run build
```

构建产物在 `frontend/dist/` 目录，可部署到Nginx、Apache或CDN。

#### 3. Nginx配置示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 快速开始

### 1. 初始化数据库

访问 http://localhost:5000/api/health 确认后端正常。

### 2. 导入基础数据

进入系统后，依次导入以下数据：

1. **教室数据** - 下载模板，填写教室信息
2. **教师数据** - 下载模板，填写教师信息
3. **班级数据** - 下载模板，填写班级信息
4. **课程数据** - 下载模板，填写课程信息

> 注意：课程导入时需要教师和班级已存在

### 3. 执行排课

1. 进入"智能排课"页面
2. 设置学期开始日期
3. 点击"开始排课"
4. 等待算法完成（约10-30秒）

### 4. 查看课表

- **班级课表**：按班级查看周课表
- **教师课表**：按教师查看周课表
- **教室课表**：按教室查看周课表
- **统计面板**：查看排课统计信息

## Excel导入模板

### 教室模板

| 教室编号 | 教室名称 | 容量 | 教室类型 |
|---------|---------|------|---------|
| R001 | 博学楼101 | 60 | 普通教室 |
| R002 | 博学楼102 | 50 | 多媒体教室 |
| R003 | 博学楼201 | 40 | 机房 |
| R004 | 博学楼301 | 35 | 实验室 |

> 教室类型可选：普通教室、多媒体教室、机房、实验室

### 教师模板

| 教师工号 | 教师姓名 | 可授课程 | 每周最大课次 |
|---------|---------|---------|-------------|
| T001 | 张伟 | 高等数学,线性代数 | 5 |
| T002 | 李娜 | 大学英语,通信原理 | 5 |

> 可授课程用逗号分隔

### 班级模板

| 班级编号 | 班级名称 | 学生人数 | 所属院系 |
|---------|---------|---------|---------|
| C001 | 计算机科学与技术1班 | 45 | 计算机科学与技术 |
| C002 | 软件工程1班 | 42 | 软件工程 |

### 课程模板

| 课程编号 | 课程名称 | 课程类型 | 总课时 | 授课教师 | 授课班级 |
|---------|---------|---------|-------|---------|---------|
| CR001 | 高等数学 | 普通授课 | 64 | 张伟 | 计算机科学与技术1班 |
| CR002 | 数据结构 | 上机 | 64 | 陈明 | 软件工程1班 |

> 课程类型可选：普通授课、上机、实验

## 项目结构

```
smart-scheduler/
├── README.md                 # 项目说明文档
├── .gitignore                # Git忽略配置
├── backend/                  # 后端代码
│   ├── app.py                # Flask应用入口
│   ├── config.py             # 配置文件
│   ├── peewee_manager.py     # 数据库模型
│   ├── init_db.py            # 数据库初始化脚本
│   ├── requirements.txt      # Python依赖
│   ├── routes/               # API路由
│   │   ├── __init__.py       # 路由注册
│   │   ├── rooms.py          # 教室管理API
│   │   ├── teachers.py       # 教师管理API
│   │   ├── classes.py        # 班级管理API
│   │   ├── courses.py        # 课程管理API
│   │   ├── holidays.py       # 节假日API
│   │   ├── schedule.py       # 排课API
│   │   └── import_data.py    # 数据导入API
│   ├── scheduler/            # 排课算法
│   │   ├── __init__.py
│   │   ├── main_scheduler.py # 主调度器
│   │   ├── time_pool.py      # 时间池管理
│   │   ├── room_allocator.py # 教室分配
│   │   ├── holiday_manager.py# 节假日管理
│   │   ├── constraints.py    # 约束检查
│   │   ├── optimizer.py      # 优化器
│   │   ├── validator.py      # 验证器
│   │   └── statistics.py     # 统计模块
│   ├── utils/                # 工具函数
│   │   ├── __init__.py
│   │   └── validators.py     # 数据验证
│   └── tests/                # 测试用例
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_api.py
│       ├── test_constraints.py
│       ├── test_full_system.py
│       └── test_scheduler.py
├── frontend/                 # 前端代码
│   ├── package.json          # 前端依赖
│   ├── index.html            # 入口HTML
│   └── src/
│       ├── main.js           # Vue入口
│       ├── App.vue           # 根组件
│       ├── router/           # 路由配置
│       │   └── index.js
│       ├── views/            # 页面组件
│       │   ├── Home.vue
│       │   ├── Rooms.vue
│       │   ├── Teachers.vue
│       │   ├── Classes.vue
│       │   ├── Courses.vue
│       │   ├── Schedule.vue
│       │   ├── DataImport.vue
│       │   ├── ClassSchedule.vue
│       │   ├── TeacherSchedule.vue
│       │   ├── RoomSchedule.vue
│       │   └── Statistics.vue
│       ├── components/       # 公共组件
│       ├── assets/           # 静态资源
│       │   ├── design-tokens.css
│       │   └── global.css
│       └── stores/           # Pinia状态管理
└── start.bat                 # 一键启动脚本
```

## API接口

### 基础路径

所有API接口前缀为 `/api`

### 教室管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/rooms` | 获取教室列表 |
| GET | `/api/rooms/:id` | 获取教室详情 |
| POST | `/api/rooms` | 创建教室 |
| PUT | `/api/rooms/:id` | 更新教室 |
| DELETE | `/api/rooms/:id` | 删除教室 |

### 教师管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/teachers` | 获取教师列表 |
| GET | `/api/teachers/:id` | 获取教师详情 |
| POST | `/api/teachers` | 创建教师 |
| PUT | `/api/teachers/:id` | 更新教师 |
| DELETE | `/api/teachers/:id` | 删除教师 |

### 班级管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/classes` | 获取班级列表 |
| GET | `/api/classes/:id` | 获取班级详情 |
| POST | `/api/classes` | 创建班级 |
| PUT | `/api/classes/:id` | 更新班级 |
| DELETE | `/api/classes/:id` | 删除班级 |

### 课程管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/courses` | 获取课程列表 |
| GET | `/api/courses/:id` | 获取课程详情 |
| POST | `/api/courses` | 创建课程 |
| PUT | `/api/courses/:id` | 更新课程 |
| DELETE | `/api/courses/:id` | 删除课程 |

### 排课功能

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/schedule/run` | 执行排课 |
| GET | `/api/schedule/results` | 获取排课结果 |
| GET | `/api/schedule/weekly` | 获取周课表 |
| GET | `/api/schedule/statistics` | 获取排课统计 |
| DELETE | `/api/schedule/clear` | 清空课表 |

### 数据导入

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/import/template/:type` | 下载导入模板 |
| POST | `/api/import/upload` | 上传导入数据 |

### 节假日

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/holidays` | 获取节假日列表 |
| POST | `/api/holidays` | 创建节假日 |
| DELETE | `/api/holidays/:id` | 删除节假日 |

## 常见问题

### 1. 前端页面空白

- 检查后端服务是否正常运行（http://localhost:5000/api/health）
- 检查浏览器控制台是否有跨域错误
- 确认前端代理配置正确

### 2. 排课成功率为0

- 检查是否有教学班记录（课程必须关联教师和班级）
- 检查教室数量是否足够
- 检查教师可授课程是否匹配

### 3. Excel导入失败

- 确认文件格式为 .xlsx 或 .xls
- 检查表头是否与模板一致
- 确认关联数据（教师、班级）已存在

### 4. 端口被占用

- 后端：修改 `backend/config.py` 中的端口
- 前端：修改 `frontend/vite.config.js` 中的端口

### 5. npm install 失败

```bash
# 清除缓存
npm cache clean --force

# 使用淘宝镜像
npm config set registry https://registry.npmmirror.com

# 重新安装
npm install
```

## 性能优化

### 大规模数据处理

- 建议单次排课不超过500门课程
- 超过2000条记录建议分批导入
- 数据库文件超过100MB建议定期清理

### 并发处理

- 生产环境建议使用Gunicorn（4+ worker）
- 前端静态资源建议CDN加速
- 数据库查询可添加索引优化

## 许可证

MIT License

## 作者

- GitHub: [Nagato-YUKI](https://github.com/Nagato-YUKI)
- 仓库: https://github.com/Nagato-YUKI/smart-scheduler

## 更新日志

### v1.0.0 (2026-04-25)

- 首次发布
- 支持Excel数据导入
- 支持智能排课算法
- 支持多维度课表查看
- 支持排课统计分析
- 支持飞书妙搭导入
