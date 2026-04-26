# 飞书妙搭导入指南

## 文件说明

已生成以下文件：

1. **smart-scheduler-frontend-feishu.zip** - 前端项目压缩包（51.86 KB）
2. **pack_frontend_only.py** - 前端打包脚本
3. **FEISHU_IMPORT_GUIDE.md** - 本导入指南

## 导入步骤

### 第1步：打开飞书妙搭

访问飞书妙搭平台，进入导入页面。

### 第2步：选择上传方式

点击 **"上传 .zip 文件"** 选项。

### 第3步：上传压缩包

选择 `smart-scheduler-frontend-feishu.zip` 文件上传。

### 第4步：配置项目

导入时可能需要填写以下信息：

- **项目名称**: 智能排课系统
- **项目描述**: 基于Vue3的排课管理前端
- **运行环境**: Node.js 18+

### 第5步：确认导入

确认配置无误后，点击导入按钮完成导入。

## 项目结构

```
frontend/
├── package.json          # 前端依赖
├── vite.config.js        # Vite配置
├── index.html            # 入口HTML
└── src/
    ├── main.js           # Vue入口
    ├── App.vue           # 根组件
    ├── router/           # 路由配置
    ├── views/            # 页面组件
    ├── components/       # 公共组件
    ├── assets/           # 静态资源
    ├── api/              # API接口
    ├── composables/      # 组合式函数
    └── utils/            # 工具函数
```

## 依赖安装

```bash
cd frontend
npm install
```

## 注意事项

1. 飞书妙搭仅支持前端项目
2. 后端代码（Python/Flask）不在导入范围内
3. 导入后需要手动安装依赖

## 联系支持

如有问题，请联系：
- GitHub: https://github.com/Nagato-YUKI/smart-scheduler
