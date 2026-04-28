# 智能排课系统（大课制版）任务清单

## Tasks

- [x] Task 1: 初始化项目结构与基础配置
  - [x] SubTask 1.1: 创建项目目录结构（前端、后端、数据库）
  - [x] SubTask 1.2: 配置后端框架（Python Flask）
  - [x] SubTask 1.3: 配置前端框架（Vue.js）
  - [x] SubTask 1.4: 配置数据库（SQLite）

- [ ] Task 2: 数据库模型与数据实体实现
  - [ ] SubTask 2.1: 创建教室模型（Room）
  - [ ] SubTask 2.2: 创建教师模型（Teacher）
  - [ ] SubTask 2.3: 创建班级模型（Class）
  - [ ] SubTask 2.4: 创建课程模型（Course）
  - [ ] SubTask 2.5: 创建节假日模型（Holiday）
  - [ ] SubTask 2.6: 创建教学班模型（TeachingClass）
  - [ ] SubTask 2.7: 创建课表记录模型（ScheduleEntry）
  - [ ] SubTask 2.8: 编写数据库迁移脚本

- [x] Task 3: 后端API接口实现 - 数据管理
  - [x] SubTask 3.1: 实现教室CRUD API
  - [x] SubTask 3.2: 实现教师CRUD API
  - [x] SubTask 3.3: 实现班级CRUD API
  - [x] SubTask 3.4: 实现课程CRUD API
  - [x] SubTask 3.5: 实现节假日管理API
  - [x] SubTask 3.6: 实现数据导入导出API（Excel）
  - [x] SubTask 3.7: 编写数据校验逻辑（教师课次上限、可授课程等）

- [x] Task 4: 排课算法核心实现
  - [x] SubTask 4.1: 实现时间资源池生成器（16周×5天×3大时段）
  - [x] SubTask 4.2: 实现节假日标记逻辑
  - [x] SubTask 4.3: 实现教室预分配算法（容量、类型匹配）
  - [x] SubTask 4.4: 实现排课主循环（贪心算法）
  - [x] SubTask 4.5: 实现硬约束检查函数
  - [x] SubTask 4.6: 实现软约束优化（教师课程集中、班级课表均衡）
  - [x] SubTask 4.7: 实现排课结果验证逻辑
  - [x] SubTask 4.8: 实现课时计算与缺课统计

- [x] Task 5: 后端API接口实现 - 排课功能
  - [x] SubTask 5.1: 实现触发排课API
  - [x] SubTask 5.2: 实现获取排课结果API
  - [x] SubTask 5.3: 实现手动调整课表API
  - [x] SubTask 5.4: 实现冲突检测API
  - [x] SubTask 5.5: 实现统计面板数据API

- [x] Task 6: 前端基础架构与数据管理页面
  - [x] SubTask 6.1: 创建前端项目框架
  - [x] SubTask 6.2: 实现教室管理页面（列表、新增、编辑、删除）
  - [x] SubTask 6.3: 实现教师管理页面
  - [x] SubTask 6.4: 实现班级管理页面
  - [x] SubTask 6.5: 实现课程管理页面
  - [x] SubTask 6.6: 实现节假日管理页面
  - [x] SubTask 6.7: 实现数据导入页面（Excel上传）

- [x] Task 7: 课表可视化展示
  - [x] SubTask 7.1: 实现班级课表视图（周次×星期表格）
  - [x] SubTask 7.2: 实现教师课表视图
  - [x] SubTask 7.3: 实现教室课表视图
  - [x] SubTask 7.4: 实现晚上排课标蓝提示
  - [x] SubTask 7.5: 实现课表视图切换组件

- [ ] Task 8: 统计面板与交互功能
  - [ ] SubTask 8.1: 实现统计面板（课时明细、缺课提示）
  - [ ] SubTask 8.2: 实现拖拽调整课表功能
  - [ ] SubTask 8.3: 实现调整时实时冲突校验
  - [ ] SubTask 8.4: 实现导出Excel功能
  - [ ] SubTask 8.5: 实现打印课表功能

- [x] Task 9: 系统集成测试与优化
  - [x] SubTask 9.1: 编写排课算法单元测试
  - [x] SubTask 9.2: 编写API接口集成测试
  - [x] SubTask 9.3: 测试硬约束场景（节假日、冲突等）
  - [x] SubTask 9.4: 测试软约束优化效果
  - [x] SubTask 9.5: 性能优化（大数据量排课）
  - [x] SubTask 9.6: 前端UI/UX优化

## Task Dependencies

- Task 1 是所有其他任务的前置条件
- Task 2 必须在 Task 3 和 Task 4 之前完成
- Task 3 必须在 Task 5 之前完成
- Task 4 必须在 Task 5 之前完成
- Task 3 和 Task 4 可并行进行
- Task 6 可在 Task 2 完成后开始
- Task 7 必须在 Task 5 之后完成（需要API支持）
- Task 8 必须在 Task 7 之后完成
- Task 9 必须在所有其他任务完成后进行
