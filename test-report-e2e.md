# 智能排课系统 - 端到端测试报告

## 基本信息

| 项目 | 详情 |
|------|------|
| 测试人员 | 自动化测试 Agent |
| 测试时间 | 2026-04-28 |
| 前端地址 | https://nagato-yuki.github.io/smart-scheduler/ |
| 后端地址 | https://smart-scheduler-0q2w.onrender.com |
| 测试环境 | Windows 10, Chrome (Playwright Headless) |
| 测试类型 | 端到端测试 (E2E) |

---

## 一、测试用例执行情况

### 1. 前端页面加载测试

| 编号 | 测试项 | 状态 | 详情 |
|------|--------|------|------|
| TC-01 | 首页加载 | **PASS** | HTTP 200, 页面标题"智能排课系统", 侧边栏可见, Element Plus组件加载成功 |
| TC-02 | 导航菜单渲染 | **PASS** | 10个导航菜单项正常渲染: 首页、教室管理、教师管理、班级管理、课程管理、节假日管理、数据导入、课表查看、课时统计、调整课表 |
| TC-03 | 页面样式加载 | **PASS** | 3个样式表加载成功, Element Plus组件正常渲染 |

### 2. API连接测试

| 编号 | 测试项 | 状态 | 详情 |
|------|--------|------|------|
| TC-04 | 后端连通性 | **PASS** | 后端服务在线, 响应正常 |
| TC-05 | CORS 跨域配置 | **PASS** | Access-Control-Allow-Origin: * |
| TC-06 | 健康检查 | **PASS** | GET /api/health → HTTP 200, 响应: `{"status":"ok"}`, 响应时间: 0.79秒 |

### 3. 业务API测试

| 编号 | 测试项 | 状态 | 详情 |
|------|--------|------|------|
| TC-07 | 教室管理 API | **FAIL** | GET /api/rooms → **HTTP 404** |
| TC-08 | 教师管理 API | **FAIL** | GET /api/teachers → **HTTP 404** |
| TC-09 | 班级管理 API | **FAIL** | GET /api/classes → **HTTP 404** |
| TC-10 | 课程管理 API | **FAIL** | GET /api/courses → **HTTP 404** |
| TC-11 | 节假日管理 API | **FAIL** | GET /api/holidays → **HTTP 404** |
| TC-12 | 排课结果 API | **FAIL** | GET /api/schedule/results → **HTTP 404** |
| TC-13 | 排课执行 API | **FAIL** | POST /api/schedule/run → **HTTP 404** |

### 4. 前端路由测试

| 编号 | 路由 | 状态 | 详情 |
|------|------|------|------|
| TC-14 | / (首页) | **PASS** | 直接访问正常 |
| TC-15 | /rooms (教室管理) | **FAIL** | 点击菜单后URL未跳转, 组件动态加载404 |
| TC-16 | /teachers (教师管理) | **FAIL** | 点击菜单后URL未跳转, 组件动态加载404 |
| TC-17 | /classes (班级管理) | **FAIL** | 点击菜单后URL未跳转, 组件动态加载404 |
| TC-18 | /courses (课程管理) | **FAIL** | 点击菜单后URL未跳转, 组件动态加载404 |
| TC-19 | /holidays (节假日管理) | **FAIL** | 点击菜单后URL未跳转, 组件动态加载404 |
| TC-20 | /import (数据导入) | **FAIL** | 点击菜单后URL未跳转, 组件动态加载404 |
| TC-21 | /schedules (课表查看) | **FAIL** | 点击菜单后URL未跳转, 组件动态加载404 |
| TC-22 | /statistics (课时统计) | **FAIL** | 点击菜单后URL未跳转, 组件动态加载404 |
| TC-23 | /adjust-schedule (调整课表) | **FAIL** | 点击菜单后URL未跳转, 组件动态加载404 |

### 5. JavaScript错误检查

| 编号 | 错误类型 | 状态 | 详情 |
|------|----------|------|------|
| TC-24 | 控制台错误数量 | **FAIL** | 发现 **31 个控制台错误** |
| TC-25 | 页面运行时错误 | **FAIL** | 发现 **10 个页面错误 (pageerror)** |
| TC-26 | 动态导入模块失败 | **FAIL** | 所有10个Vue组件模块动态导入返回404 |
| TC-27 | CSS预加载失败 | **FAIL** | _plugin-vue_export-helper CSS预加载失败 |

---

## 二、缺陷汇总报告

### 缺陷 #1 - [致命/Blocker] 前端Vue组件动态导入全部404

**严重程度**: 致命 (Blocker) - 核心功能完全不可用  
**优先级**: P0

**问题描述**:  
GitHub Pages 部署的前端页面加载后，所有Vue组件的动态导入（Code Splitting）均返回 HTTP 404。导致点击任何导航菜单项时，页面内容无法加载。

**影响范围**:
- Home.vue → `assets/Home-DPJ9xm_t.js` 404
- RoomManagement.vue → `assets/RoomManagement-DB94mTyV.js` 404
- TeacherManagement.vue → `assets/TeacherManagement-BqO6VpV5.js` 404
- ClassManagement.vue → `assets/ClassManagement-B1OolYFF.js` 404
- CourseManagement.vue → `assets/CourseManagement-_V4Ncb_i.js` 404
- HolidayManagement.vue → `assets/HolidayManagement-CDViTXzp.js` 404
- DataImport.vue → `assets/DataImport-CXFRMNz6.js` 404
- ScheduleView.vue → `assets/ScheduleView-CYYvnOei.js` 404
- StatisticsView.vue → `assets/StatisticsView-CPOQX4sU.js` 404
- AdjustSchedule.vue → `assets/AdjustSchedule-CD0idX7l.js` 404
- `_plugin-vue_export-helper-C-bjXCXd.css` 预加载 404

**根因分析**:
- `gh-pages-temp/index.html` 引用的JS文件为 `index-DBPK4P4m.js`
- 浏览器实际请求 `index-DSeQm1hZ.js`（文件名不匹配）
- 本地 `gh-pages-temp/assets/` 目录中的文件哈希与部署到 GitHub Pages 的文件哈希**不一致**
- 说明 **GitHub Pages 部署的构建产物与本地不同步**，需要重新构建并部署

**复现步骤**:
1. 访问 https://nagato-yuki.github.io/smart-scheduler/
2. 等待页面加载完成
3. 打开浏览器开发者工具 → Console
4. 观察到大量 "Failed to fetch dynamically imported module" 错误
5. 点击任意导航菜单项，页面无响应

---

### 缺陷 #2 - [致命/Blocker] 后端业务API全部返回404

**严重程度**: 致命 (Blocker) - 后端业务逻辑完全不可用  
**优先级**: P0

**问题描述**:  
除 `/api/health` 端点外，所有业务API端点（教室、教师、班级、课程、节假日、排课）均返回 HTTP 404。

**影响范围**:
- `GET /api/rooms` → 404
- `GET /api/teachers` → 404
- `GET /api/classes` → 404
- `GET /api/courses` → 404
- `GET /api/holidays` → 404
- `GET /api/schedule/results` → 404
- `POST /api/schedule/run` → 404

**根因分析**:
1. 本地 `backend/config.py` 只有模块级变量（`DB_TYPE`, `DATABASE`, `CORS_ORIGINS`, `SECRET_KEY`, `ITEMS_PER_PAGE`），**没有定义 `Config` 类**
2. `app.py`、`peewee_manager.py` 等文件尝试 `from config import Config` 将抛出 `ImportError`
3. Render 上 `/api/health` 正常但业务路由404，说明 Render 上部署的代码与当前本地代码**不一致**
4. 可能的情况：Render 上的代码是旧版本，仅包含 health 端点；或者蓝图导入时发生静默失败

**复现步骤**:
1. 访问 https://smart-scheduler-0q2w.onrender.com/api/rooms
2. 观察返回 HTTP 404 Not Found

---

### 缺陷 #3 - [严重/Critical] 前端子路由直接访问需要404重定向

**严重程度**: 严重 (Critical) - 影响用户体验  
**优先级**: P1

**问题描述**:  
直接访问子路由（如 `/rooms`）时，GitHub Pages 返回 HTTP 404，依赖 `404.html` 的 JavaScript 重定向到首页。虽然最终能加载应用，但：
- HTTP 响应码为 404（影响 SEO 和浏览器行为）
- 用户体验有轻微延迟
- URL 在重定向过程中可能短暂变化

**复现步骤**:
1. 直接在浏览器地址栏输入 https://nagato-yuki.github.io/smart-scheduler/rooms
2. 观察到短暂加载后重定向到首页

---

## 三、测试结果汇总

| 指标 | 数值 |
|------|------|
| 总测试用例数 | **27** |
| 通过 | **6** (22.2%) |
| 失败 | **21** (77.8%) |
| 致命缺陷 (Blocker) | **2** |
| 严重缺陷 (Critical) | **1** |

---

## 四、验收结论

### **验收结果: 不通过 (NOT PASSED)**

### 不予发布的理由:

1. **前端功能完全不可用**: 所有Vue组件动态导入返回404，用户只能看到首页的导航菜单外壳，点击任何菜单项均无法加载对应页面内容。
   
2. **后端业务功能完全不可用**: 除健康检查端点外，所有CRUD API（教室、教师、班级、课程、节假日、排课）均返回404，前后端数据交互完全中断。

3. **大量JavaScript运行时错误**: 31个控制台错误 + 10个页面运行时错误，浏览器控制台满是红色报错，用户体验极差。

### 修复建议（按优先级排序）:

**P0 - 必须立即修复**:

1. **重新构建并部署前端到 GitHub Pages**
   - 在项目根目录运行: `npm run build`
   - 将 `frontend/dist/` 目录内容（或 `gh-pages-temp/` 内容）推送到 `gh-pages` 分支
   - 确保 `index.html` 中引用的JS/CSS文件名与 `assets/` 目录中的实际文件一致
   - 验证: 访问首页后打开开发者工具，应无 404 错误

2. **修复 Render 后端部署**
   - 检查 `backend/config.py`，添加 `Config` 类:
     ```python
     class Config:
         DB_TYPE = os.environ.get("DB_TYPE", "sqlite")
         DATABASE = os.environ.get("DATABASE_URL", ...)
         ...
     ```
   - 或者确保 `app.py` 和 `peewee_manager.py` 使用模块级变量而非 `Config` 类
   - 推送到 GitHub 触发 Render 自动部署，或手动重新部署
   - 验证: 访问 `/api/rooms` 应返回 200 及教室列表JSON

**P1 - 建议修复**:

3. **优化 GitHub Pages SPA 路由处理**
   - 当前的 `404.html` 重定向方案可接受但不够优雅
   - 考虑使用 Vite 的 `base` 配置确保 GitHub Pages 兼容

---

## 五、测试环境说明

| 项目 | 配置 |
|------|------|
| 操作系统 | Windows 10 |
| 浏览器 | Chromium (Playwright Headless) |
| 屏幕分辨率 | 1440x900 |
| 网络 | 正常网络环境 |
| API测试工具 | Python urllib (标准库) |
| 前端测试工具 | Playwright 1.59.1 |

---

## 六、自动化测试命令

如需重新执行测试，运行以下命令:

```powershell
# API 测试
python "e:\trae project\paike\test_e2e_api.py"

# 前端浏览器测试 (需已安装 Playwright)
cd "e:\trae project\paike"
node playwright-smart-scheduler.spec.js
```

测试结果文件:
- API测试结果: `test-results-api.json`
- 浏览器测试结果: `test-results.json`
- 截图: `test-homepage.png`
