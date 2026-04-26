<template>
  <el-container class="app-container">
    <el-aside width="200px" class="aside">
      <el-menu
        :default-active="$route.path"
        router
        class="aside-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/">
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/rooms">
          <span>教室管理</span>
        </el-menu-item>
        <el-menu-item index="/teachers">
          <span>教师管理</span>
        </el-menu-item>
        <el-menu-item index="/classes">
          <span>班级管理</span>
        </el-menu-item>
        <el-menu-item index="/courses">
          <span>课程管理</span>
        </el-menu-item>
        <el-menu-item index="/holidays">
          <span>节假日管理</span>
        </el-menu-item>
        <el-menu-item index="/import">
          <span>数据导入</span>
        </el-menu-item>
        <el-menu-item index="/schedules">
          <span>课表查看</span>
        </el-menu-item>
        <el-menu-item index="/statistics">
          <span>课时统计</span>
        </el-menu-item>
        <el-menu-item index="/adjust-schedule">
          <span>调整课表</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style>
@import './assets/design-tokens.css';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
}

body {
  font-family: var(--font-family-sans);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--text-primary);
  background-color: var(--bg-page);
}

#app {
  width: 100%;
  min-height: 100vh;
}

.app-container {
  height: 100vh;
}

/* 侧边栏 */
.aside {
  background: linear-gradient(180deg, #1a1f36 0%, #2d3748 100%);
  height: 100vh;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  transition: all var(--duration-slow) var(--ease-out);
}

.aside-menu {
  height: 100%;
  border-right: none;
  background: transparent !important;
}

.aside-menu .el-menu-item {
  border-radius: var(--radius-md);
  margin: 4px 12px;
  transition: all var(--duration-base) var(--ease-out);
}

.aside-menu .el-menu-item:hover {
  background: rgba(255, 255, 255, 0.08) !important;
}

.aside-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, rgba(22, 93, 255, 0.2), rgba(22, 93, 255, 0.1)) !important;
  color: #597ef7 !important;
  font-weight: var(--font-weight-semibold);
}

/* 主内容区 */
.main {
  background-color: var(--bg-page);
  height: 100vh;
  overflow-y: auto;
  padding: 0;
}

/* 滚动条美化 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: var(--color-neutral-1);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb {
  background: var(--color-neutral-4);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-neutral-5);
}
</style>
