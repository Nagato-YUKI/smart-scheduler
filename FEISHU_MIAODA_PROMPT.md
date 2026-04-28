# 智能排课系统 - 飞书妙搭AI开发提示词

## 一、项目概述

### 1.1 项目定位
开发一个**纯前端智能排课系统**，使用飞书妙搭平台实现。数据通过 localStorage 本地存储，排课算法完全由前端 JavaScript 实现，无需后端服务器。

### 1.2 核心功能模块
1. **数据管理**: 教室、教师、班级、课程、节假日的增删改查
2. **智能排课**: 基于约束条件的自动排课算法
3. **课表查看**: 按班级/教师/教室维度查看周课表
4. **课表调整**: 手动调整已排课程时段
5. **数据统计**: 课时统计、排课完成率、时段分布
6. **Excel导入**: 支持导入模板批量录入数据

### 1.3 技术约束
- **平台**: 飞书妙搭（纯前端低代码平台）
- **数据存储**: localStorage / IndexedDB（替代后端数据库）
- **算法实现**: JavaScript 原生实现（替代 Python 排课引擎）
- **UI组件**: 飞书内置组件或自定义 HTML/CSS

---

## 二、数据模型设计

### 2.1 教室 (Room)
```javascript
{
  id: "唯一标识",
  room_number: "R001",          // 教室编号，唯一
  name: "教学楼A-101",           // 教室名称
  capacity: 60,                 // 容量（人数）
  room_type: "normal",          // 类型：normal(普通)/computer(机房)/lab(实验室)
  is_available: true            // 是否可用
}
```

### 2.2 教师 (Teacher)
```javascript
{
  id: "唯一标识",
  teacher_number: "T001",       // 教师编号，唯一
  name: "张老师",                // 姓名
  teachable_courses: ["高等数学", "线性代数"], // 可授课程列表
  max_weekly_sessions: 5        // 每周最多课次
}
```

### 2.3 班级 (SchoolClass)
```javascript
{
  id: "唯一标识",
  class_number: "C001",         // 班级编号，唯一
  name: "2024级计算机科学1班",    // 班级名称
  student_count: 40,            // 学生人数
  department: "计算机科学"        // 所属专业/年级
}
```

### 2.4 课程 (Course)
```javascript
{
  id: "唯一标识",
  course_number: "CS001",       // 课程编号，唯一
  name: "高等数学",               // 课程名称
  course_type: "lecture",       // 类型：lecture(授课)/lab(实验)/computer(上机)
  total_hours: 64,              // 总课时数
  teacher_id: "教师ID",          // 关联教师
  class_id: "班级ID"             // 关联班级
}
```

### 2.5 节假日 (Holiday)
```javascript
{
  id: "唯一标识",
  date: "2026-10-01",           // 日期 YYYY-MM-DD
  name: "国庆节"                 // 节假日名称
}
```

### 2.6 课表条目 (ScheduleEntry)
```javascript
{
  id: "唯一标识",
  course_id: "课程ID",
  teacher_id: "教师ID",
  class_id: "班级ID",
  room_id: "教室ID",
  week: 1,                      // 第几周 (1-20)
  day: 1,                       // 星期几 (1=周一, 5=周五)
  period: "morning",            // 时段：morning/afternoon/evening
  is_holiday: false             // 是否节假日
}
```

### 2.7 本地存储结构
```javascript
// localStorage keys
const STORAGE_KEYS = {
  rooms: "scheduler_rooms",
  teachers: "scheduler_teachers",
  classes: "scheduler_classes",
  courses: "scheduler_courses",
  holidays: "scheduler_holidays",
  schedule: "scheduler_schedule",
  settings: "scheduler_settings"
};
```

---

## 三、页面功能设计

### 3.1 首页 (Dashboard)
**功能**: 系统概览，快速导航

**页面元素**:
- 统计卡片: 教室总数、教师总数、班级总数、课程总数
- 快捷操作按钮: 一键排课、导入数据、查看课表
- 数据列表预览: 最近添加的教室、教师、班级、课程（各显示前5条）

### 3.2 教室管理
**功能**: 教室信息的增删改查

**页面元素**:
- 数据表格: 显示教室编号、名称、类型、容量、状态
- 操作按钮: 新增、编辑、删除
- 分页控件: 每页显示20条
- 表单弹窗: 录入/修改教室信息

**表单字段**:
- 教室编号（必填，唯一，不可修改）
- 教室名称（必填）
- 教室类型（下拉：普通教室/机房/实验室）
- 容量（数字输入，1-500）
- 可用状态（开关：可用/不可用）

### 3.3 教师管理
**功能**: 教师信息的增删改查

**表单字段**:
- 教师编号（必填，唯一，不可修改）
- 姓名（必填）
- 可授课程（多选下拉，最多选2门）
- 每周课次上限（数字输入，1-5）

**可选课程列表**: 高等数学、线性代数、大学英语、计算机基础、数据库原理、有机化学、普通物理

### 3.4 班级管理
**功能**: 班级信息的增删改查

**表单字段**:
- 班级编号（必填，唯一，不可修改）
- 班级名称（必填）
- 学生人数（数字输入，1-200）
- 专业/年级（文本输入）

### 3.5 课程管理
**功能**: 课程信息的增删改查

**表单字段**:
- 课程编号（必填，唯一，不可修改）
- 课程名称（必填）
- 课程类型（下拉：普通授课/实验/上机）
- 总课时（数字输入，1-128，默认64）
- 授课教师（下拉选择）
- 授课班级（下拉选择）

### 3.6 节假日管理
**功能**: 设置不用排课的日期

**表单字段**:
- 日期（日期选择器，格式 YYYY-MM-DD）
- 节假日名称（文本输入）

**默认节假日**: 元旦、春节、清明、劳动节、端午、中秋、国庆

### 3.7 数据导入
**功能**: Excel文件批量导入

**页面元素**:
- 数据类型选择: 教室/教师/班级/课程
- 模板下载按钮: 下载对应类型的Excel模板
- 文件上传区域: 拖拽上传，仅支持 .xlsx
- 导入结果展示: 成功/失败状态，导入条数

**Excel模板格式**（每种类型不同列）:
- 教室: 教室编号 | 教室名称 | 教室类型 | 容量
- 教师: 教师编号 | 姓名 | 可授课程（逗号分隔）| 每周课次上限
- 班级: 班级编号 | 班级名称 | 学生人数 | 专业/年级
- 课程: 课程编号 | 课程名称 | 课程类型 | 总课时 | 教师编号 | 班级编号

### 3.8 智能排课
**功能**: 一键自动生成课表

**页面元素**:
- 排课配置区:
  - 学期总周数（默认20周）
  - 学期开始日期（默认2026-09-07）
  - 上课时间段设置（上午/下午/晚上课时数）
- 排课按钮: "开始排课"
- 进度显示: 排课中动画/进度条
- 结果展示:
  - 排课成功率（百分比）
  - 成功课程数/总课程数
  - 失败课程列表及原因

### 3.9 课表查看
**功能**: 多视角查看周课表

**三种视图切换**:
1. **班级课表**: 选择班级，显示该班级一周课表
2. **教师课表**: 选择教师，显示该教师一周课表
3. **教室课表**: 选择教室，显示该教室一周课表

**页面元素**:
- 视图切换标签页
- 周次选择器: 上一周/下一周/快速跳转（1-20周）
- 下拉选择: 选择班级/教师/教室
- 课表表格:
  - 横向: 星期一~星期五（显示日期）
  - 纵向: 上午(08:00-11:40)/下午(14:00-17:40)/晚上(19:00-22:00)
  - 单元格: 课程卡片（课程名、教师/班级、教室、周次范围）
- 操作按钮: 刷新、打印

**课程卡片样式**:
- 授课类: 蓝色系渐变背景
- 实验类: 橙色系渐变背景
- 上机类: 绿色系渐变背景

### 3.10 课表调整
**功能**: 手动调整已排课程的时段

**页面元素**:
- 筛选条件: 按周次、星期、关键词搜索
- 课表列表表格: 课程、教师、班级、教室、周次、星期、时段
- 调整按钮: 打开调整弹窗
- 调整弹窗:
  - 显示原课程信息
  - 选择目标周次（1-20）
  - 选择目标星期（单选按钮组）
  - 选择目标时段（上午/下午/晚上单选按钮组）
  - 冲突检测提示（如有冲突则显示红色警告）

### 3.11 课时统计
**功能**: 排课数据统计分析

**页面元素**:
- 统计卡片: 教学班总数、已排课班级、总课时数、排课完成率
- 进度条: 排课进度可视化（渐变色）
- 时段分布: 上午/下午/晚上课时数统计
- 明细表格:
  - 教学班ID、课程名称、班级、教师
  - 排课次数、实际课时、缺课提示
  - 缺课提示标签（绿色"已排满"/橙色"缺课X课时"）

---

## 四、核心算法实现

### 4.1 排课算法（JavaScript实现）

```javascript
class SmartScheduler {
  constructor() {
    this.schedule = [];           // 已排课程
    this.holidays = [];           // 节假日
    this.rooms = [];              // 教室列表
    this.teachers = [];           // 教师列表
    this.classes = [];            // 班级列表
    this.courses = [];            // 课程列表
    this.totalWeeks = 20;         // 总周数
    this.periodHours = {          // 各时段课时数
      morning: 4,
      afternoon: 4,
      evening: 3
    };
  }

  // 主排课函数
  run() {
    this.schedule = [];
    const results = { success: 0, failed: 0, details: [] };
    
    // 按优先级排序课程
    const sortedCourses = this._sortCourses();
    
    for (const course of sortedCourses) {
      const success = this._scheduleCourse(course);
      if (success) {
        results.success++;
      } else {
        results.failed++;
        results.details.push({
          course: course.name,
          reason: this._getFailReason(course)
        });
      }
    }
    
    results.total = sortedCourses.length;
    results.rate = Math.round((results.success / results.total) * 100);
    return results;
  }

  // 课程优先级排序
  _sortCourses() {
    return [...this.courses].sort((a, b) => {
      // 课时多的优先，机房/实验室优先
      if (a.course_type !== 'lecture' && b.course_type === 'lecture') return -1;
      if (a.course_type === 'lecture' && b.course_type !== 'lecture') return 1;
      return b.total_hours - a.total_hours;
    });
  }

  // 为单个课程排课
  _scheduleCourse(course) {
    let scheduledHours = 0;
    const teacher = this.teachers.find(t => t.id === course.teacher_id);
    const schoolClass = this.classes.find(c => c.id === course.class_id);
    
    // 尝试不同时段
    const periods = ['morning', 'afternoon', 'evening'];
    
    for (const period of periods) {
      if (scheduledHours >= course.total_hours) break;
      
      const periodHours = this.periodHours[period];
      const slots = this._findAvailableSlots(course, teacher, schoolClass, period);
      
      for (const slot of slots) {
        if (scheduledHours >= course.total_hours) break;
        
        // 检查冲突
        if (!this._hasConflict(course, teacher, schoolClass, slot)) {
          // 找到合适教室
          const room = this._findSuitableRoom(course, slot);
          if (room) {
            this._addScheduleEntry(course, teacher, schoolClass, room, slot);
            scheduledHours += periodHours;
          }
        }
      }
    }
    
    return scheduledHours >= course.total_hours;
  }

  // 查找可用时段槽
  _findAvailableSlots(course, teacher, schoolClass, period) {
    const slots = [];
    const teacherSchedule = this.schedule.filter(e => e.teacher_id === teacher.id);
    const classSchedule = this.schedule.filter(e => e.class_id === schoolClass.id);
    
    for (let week = 1; week <= this.totalWeeks; week++) {
      for (let day = 1; day <= 5; day++) {
        // 检查是否节假日
        const date = this._getWeekDayDate(week, day);
        if (this._isHoliday(date)) continue;
        
        // 检查该时段是否已被占用
        const teacherBusy = teacherSchedule.some(e => 
          e.week === week && e.day === day && e.period === period
        );
        const classBusy = classSchedule.some(e => 
          e.week === week && e.day === day && e.period === period
        );
        
        if (!teacherBusy && !classBusy) {
          slots.push({ week, day, period, date });
        }
      }
    }
    return slots;
  }

  // 检查冲突
  _hasConflict(course, teacher, schoolClass, slot) {
    return this.schedule.some(entry => {
      // 教师冲突
      if (entry.teacher_id === teacher.id && 
          entry.week === slot.week && 
          entry.day === slot.day && 
          entry.period === slot.period) return true;
      
      // 班级冲突
      if (entry.class_id === schoolClass.id && 
          entry.week === slot.week && 
          entry.day === slot.day && 
          entry.period === slot.period) return true;
      
      return false;
    });
  }

  // 查找合适教室
  _findSuitableRoom(course, slot) {
    const schoolClass = this.classes.find(c => c.id === course.class_id);
    
    // 根据课程类型确定需要的教室类型
    const requiredRoomType = this._getRequiredRoomType(course.course_type);
    
    // 过滤可用教室
    const availableRooms = this.rooms.filter(r => 
      r.is_available &&
      r.room_type === requiredRoomType &&
      r.capacity >= schoolClass.student_count &&
      !this._isRoomOccupied(r.id, slot)
    );
    
    // 按容量升序，优先使用小教室
    availableRooms.sort((a, b) => a.capacity - b.capacity);
    
    return availableRooms.length > 0 ? availableRooms[0] : null;
  }

  // 课程类型到教室类型映射
  _getRequiredRoomType(courseType) {
    const map = {
      'lecture': 'normal',
      'lab': 'lab',
      'computer': 'computer'
    };
    return map[courseType] || 'normal';
  }

  // 检查教室是否被占用
  _isRoomOccupied(roomId, slot) {
    return this.schedule.some(e => 
      e.room_id === roomId && 
      e.week === slot.week && 
      e.day === slot.day && 
      e.period === slot.period
    );
  }

  // 添加课表条目
  _addScheduleEntry(course, teacher, schoolClass, room, slot) {
    this.schedule.push({
      id: this._generateId(),
      course_id: course.id,
      teacher_id: teacher.id,
      class_id: schoolClass.id,
      room_id: room.id,
      week: slot.week,
      day: slot.day,
      period: slot.period,
      is_holiday: false
    });
  }

  // 生成唯一ID
  _generateId() {
    return 'S' + Date.now() + Math.random().toString(36).substr(2, 9);
  }

  // 获取指定周/日的日期
  _getWeekDayDate(week, dayOfWeek) {
    // 学期开始日期作为第1周周一
    const startDate = new Date('2026-09-07');
    const targetDate = new Date(startDate);
    targetDate.setDate(startDate.getDate() + (week - 1) * 7 + (dayOfWeek - 1));
    return targetDate.toISOString().split('T')[0];
  }

  // 检查是否节假日
  _isHoliday(dateStr) {
    return this.holidays.some(h => h.date === dateStr);
  }
}
```

### 4.2 约束条件
1. **教师冲突**: 同一教师同一时段只能上一门课
2. **班级冲突**: 同一班级同一时段只能上一门课
3. **教室冲突**: 同一教室同一时段只能有一个班级使用
4. **容量匹配**: 教室容量 >= 班级人数
5. **类型匹配**: 实验课需实验室，上机课需机房
6. **节假日避让**: 节假日不排课
7. **课时限制**: 每周总课时不超过设定值

---

## 五、样式设计规范

### 5.1 色彩系统
```css
:root {
  /* 主色调 */
  --primary: #165dff;
  --primary-light: #597ef7;
  --primary-bg: #f0f5ff;
  
  /* 功能色 */
  --success: #00b42a;
  --warning: #f77234;
  --error: #f53f3f;
  --info: #0073d6;
  
  /* 中性色 */
  --bg-page: #f5f7fa;
  --bg-card: #ffffff;
  --text-primary: #1d2129;
  --text-secondary: #86909c;
  --border: #e5e6eb;
  
  /* 圆角 */
  --radius: 8px;
  --radius-lg: 12px;
  
  /* 阴影 */
  --shadow: 0 2px 8px rgba(0,0,0,0.08);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
}
```

### 5.2 课程卡片配色
| 课程类型 | 背景 | 边框色 | 文字色 |
|---------|------|-------|-------|
| 普通授课 | 渐变蓝 #e3f2fd→#bbdefb | #1976d2 | #0d47a1 |
| 实验课 | 渐变橙 #fff3e0→#ffe0b2 | #f57c00 | #e65100 |
| 上机课 | 渐变绿 #e8f5e9→#c8e6c9 | #388e3c | #1b5e20 |

### 5.3 响应式布局
- 表格: 移动端可横向滚动
- 表单: 移动端字段全宽堆叠
- 课表: 最小宽度900px，超出可滑动

---

## 六、数据流设计

### 6.1 数据读写流程
```
用户操作 → 页面组件 → 数据服务层 → localStorage
                                  ↓
                             JSON序列化/反序列化
```

### 6.2 数据服务层
```javascript
class DataService {
  // 通用CRUD操作
  getAll(key) {
    const data = localStorage.getItem(key);
    return data ? JSON.parse(data) : [];
  }
  
  save(key, data) {
    localStorage.setItem(key, JSON.stringify(data));
  }
  
  add(key, item) {
    const items = this.getAll(key);
    item.id = Date.now().toString();
    items.push(item);
    this.save(key, items);
    return item;
  }
  
  update(key, id, updates) {
    const items = this.getAll(key);
    const idx = items.findIndex(i => i.id === id);
    if (idx !== -1) {
      items[idx] = { ...items[idx], ...updates };
      this.save(key, items);
    }
  }
  
  delete(key, id) {
    const items = this.getAll(key).filter(i => i.id !== id);
    this.save(key, items);
  }
  
  // 清空所有数据
  clearAll() {
    Object.values(STORAGE_KEYS).forEach(key => localStorage.removeItem(key));
  }
}
```

### 6.3 Excel导入处理
使用浏览器原生API或飞书提供的文件处理能力：
```javascript
async function importExcel(file, type) {
  // 1. 读取文件
  const arrayBuffer = await file.arrayBuffer();
  
  // 2. 解析Excel（使用SheetJS或飞书内置解析器）
  const workbook = XLSX.read(arrayBuffer, { type: 'array' });
  const sheet = workbook.Sheets[workbook.SheetNames[0]];
  const rows = XLSX.utils.sheet_to_json(sheet);
  
  // 3. 转换为数据模型
  const data = rows.map(row => mapRowToModel(row, type));
  
  // 4. 保存到localStorage
  const service = new DataService();
  const existing = service.getAll(STORAGE_KEYS[type + 's']);
  const merged = mergeData(existing, data);
  service.save(STORAGE_KEYS[type + 's'], merged);
  
  return { success: true, count: data.length };
}
```

---

## 七、排课流程说明

### 7.1 前置条件
用户必须先完成以下数据录入，才能执行排课：
1. 添加至少1间可用教室
2. 添加至少1名教师
3. 添加至少1个班级
4. 添加至少1门课程（含教师和班级关联）
5. 可选：设置节假日

### 7.2 排课步骤
```
1. 用户点击"开始排课"
2. 从localStorage读取所有基础数据
3. 初始化SmartScheduler实例
4. 加载节假日到调度器
5. 按优先级排序课程
6. 遍历每个课程，尝试分配时段和教室
7. 输出排课结果（成功数、失败数、详情）
8. 将课表保存到localStorage
9. 显示结果页面
```

### 7.3 排课策略
1. **优先级**: 实验/上机课 > 普通授课，课时多的 > 课时少的
2. **时段偏好**: 上午 > 下午 > 晚上
3. **教室分配**: 容量最接近班级人数的教室优先（节约资源）
4. **均衡分布**: 同一课程的不同课时尽量分散在不同天

---

## 八、关键交互细节

### 8.1 表单验证规则
| 字段 | 规则 | 错误提示 |
|-----|------|---------|
| 编号 | 必填，唯一 | "该编号已存在" |
| 名称 | 必填 | "请输入名称" |
| 容量/人数 | 必填，1-500 | "请输入有效数值" |
| 类型 | 必选 | "请选择类型" |

### 8.2 删除确认
删除任何数据前弹出确认框：
```
确定删除 "{名称}" 吗？此操作不可撤销。
[取消] [确定删除]
```

### 8.3 空状态提示
- 无数据时显示引导页："暂无数据，点击新增按钮添加"
- 排课前无基础数据时提示："请先完成教室、教师、班级、课程的录入"
- 课表为空时："该{班级/教师/教室}本周暂无课表"

### 8.4 加载状态
- 表格加载: 显示骨架屏或旋转加载图标
- 排课中: 显示进度条和"正在排课..."文字，禁用操作按钮
- 导入中: 显示"正在导入..."和文件处理动画

---

## 九、飞书妙搭适配建议

### 9.1 功能映射
| 原系统功能 | 飞书妙搭实现方式 |
|-----------|----------------|
| 后端API | 前端JavaScript服务层 |
| SQLite数据库 | localStorage / IndexedDB |
| Flask路由 | 页面路由/标签页切换 |
| Python排课算法 | JavaScript排课类 |
| Excel解析(openpyxl) | SheetJS库或飞书内置解析 |
| Vue组件 | 飞书表单/表格/自定义组件 |
| Element Plus | 飞书内置UI组件 |

### 9.2 数据容量限制
- localStorage通常限制5-10MB
- 建议单表数据不超过1000条
- 如数据量大，可改用飞书云文档API存储

### 9.3 注意事项
1. **跨页面数据共享**: 使用全局状态管理或localStorage
2. **Excel处理**: 飞书可能不支持第三方库，需使用内置文件处理功能
3. **打印功能**: 使用浏览器原生 window.print()
4. **移动端适配**: 飞书内置浏览器，需测试移动端表现

### 9.4 替代方案
如果localStorage容量不够，可选方案：
1. **飞书云文档**: 使用飞书API读写多维表格作为数据库
2. **IndexedDB**: 浏览器内置大容量存储（50MB+）
3. **飞书表单+表格**: 数据录入用表单，数据查看用多维表格

---

## 十、测试检查清单

### 10.1 功能测试
- [ ] 教室增删改查正常
- [ ] 教师增删改查正常
- [ ] 班级增删改查正常
- [ ] 课程增删改查正常
- [ ] 节假日增删改查正常
- [ ] Excel导入教室数据成功
- [ ] Excel导入教师数据成功
- [ ] Excel导入班级数据成功
- [ ] Excel导入课程数据成功
- [ ] 排课算法能正常运行
- [ ] 排课结果无冲突
- [ ] 班级课表显示正确
- [ ] 教师课表显示正确
- [ ] 教室课表显示正确
- [ ] 课表调整功能正常
- [ ] 课时统计显示正确

### 10.2 约束测试
- [ ] 教师不出现时间冲突
- [ ] 班级不出现时间冲突
- [ ] 教室不出现时间冲突
- [ ] 教室容量满足班级人数
- [ ] 实验课分配实验室
- [ ] 上机课分配机房
- [ ] 节假日不排课
- [ ] 教师周课时不超限

### 10.3 边界测试
- [ ] 无数据时点击排课有提示
- [ ] 删除已排课程的班级有警告
- [ ] 导入重复数据有处理
- [ ] 超大/超小容量输入有验证
- [ ] 多标签页切换数据不丢失

---

## 十一、部署与维护

### 11.1 数据备份
提供数据导出功能：
```javascript
function exportAllData() {
  const backup = {};
  Object.entries(STORAGE_KEYS).forEach(([name, key]) => {
    backup[name] = localStorage.getItem(key);
  });
  const blob = new Blob([JSON.stringify(backup, null, 2)], { type: 'application/json' });
  downloadFile(blob, `排课数据备份_${new Date().toISOString().slice(0,10)}.json`);
}
```

### 11.2 数据恢复
提供数据导入功能：
```javascript
function importBackup(jsonString) {
  const backup = JSON.parse(jsonString);
  Object.entries(backup).forEach(([name, data]) => {
    if (STORAGE_KEYS[name]) {
      localStorage.setItem(STORAGE_KEYS[name], data);
    }
  });
  location.reload(); // 刷新页面加载新数据
}
```

---

## 十二、开发优先级建议

| 优先级 | 模块 | 说明 |
|-------|------|------|
| P0 | 数据管理页面 | 基础CRUD，排课前提 |
| P0 | 数据存储层 | localStorage读写 |
| P1 | 排课算法 | 核心功能 |
| P1 | 课表查看 | 结果展示 |
| P2 | 数据导入 | 提升效率 |
| P2 | 课表调整 | 手动微调 |
| P3 | 课时统计 | 数据分析 |
| P3 | 数据备份/恢复 | 数据安全 |

---

**说明**: 本文档为飞书妙搭AI提供完整的开发指导，包含数据模型、页面设计、算法实现、样式规范等全部必要信息。由于飞书妙搭是纯前端平台，所有后端功能均使用JavaScript和浏览器存储替代。
