<template>
  <el-container class="app-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside" :class="{ 'is-collapsed': isCollapse }">
      <!-- Logo 区域 -->
      <div class="aside-logo">
        <div class="logo-icon">
          <el-icon :size="28"><Calendar /></el-icon>
        </div>
        <transition name="logo-fade">
          <span v-show="!isCollapse" class="logo-text">智能排课系统</span>
        </transition>
      </div>

      <el-menu
        :default-active="$route.path"
        router
        :collapse="isCollapse"
        :collapse-transition="true"
        class="aside-menu"
        background-color="transparent"
        text-color="#c2cad8"
        active-text-color="#ffffff"
      >
        <!-- 概览分组 -->
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页</template>
        </el-menu-item>

        <el-divider class="menu-divider" />

        <!-- 基础数据分组 -->
        <el-sub-menu index="data-group">
          <template #title>
            <el-icon><Files /></el-icon>
            <span>基础数据</span>
          </template>
          <el-menu-item index="/rooms">
            <el-icon><OfficeBuilding /></el-icon>
            <template #title>教室管理</template>
          </el-menu-item>
          <el-menu-item index="/teachers">
            <el-icon><UserFilled /></el-icon>
            <template #title>教师管理</template>
          </el-menu-item>
          <el-menu-item index="/classes">
            <el-icon><Reading /></el-icon>
            <template #title>班级管理</template>
          </el-menu-item>
          <el-menu-item index="/courses">
            <el-icon><Notebook /></el-icon>
            <template #title>课程管理</template>
          </el-menu-item>
          <el-menu-item index="/holidays">
            <el-icon><Sunny /></el-icon>
            <template #title>节假日管理</template>
          </el-menu-item>
        </el-sub-menu>

        <!-- 排课操作分组 -->
        <el-sub-menu index="schedule-group">
          <template #title>
            <el-icon><SetUp /></el-icon>
            <span>排课操作</span>
          </template>
          <el-menu-item index="/import">
            <el-icon><UploadFilled /></el-icon>
            <template #title>数据导入</template>
          </el-menu-item>
          <el-menu-item index="/adjust-schedule">
            <el-icon><EditPen /></el-icon>
            <template #title>调整课表</template>
          </el-menu-item>
        </el-sub-menu>

        <el-divider class="menu-divider" />

        <!-- 查看统计分组 -->
        <el-menu-item index="/schedules">
          <el-icon><Calendar /></el-icon>
          <template #title>课表查看</template>
        </el-menu-item>
        <el-menu-item index="/statistics">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>课时统计</template>
        </el-menu-item>
      </el-menu>

      <!-- 折叠切换按钮 -->
      <div class="aside-collapse-btn" @click="toggleCollapse">
        <el-icon :size="16">
          <Fold v-if="!isCollapse" />
          <Expand v-else />
        </el-icon>
      </div>
    </el-aside>

    <el-container>
      <!-- 顶部栏 -->
      <el-header class="app-header">
        <div class="header-left">
          <el-breadcrumb separator="/" v-if="$route.path !== '/'">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentRouteName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-tooltip content="刷新数据" placement="bottom">
            <el-button circle @click="refreshPage">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Calendar, HomeFilled, Files, OfficeBuilding, UserFilled,
  Reading, Notebook, Sunny, SetUp, UploadFilled, EditPen,
  DataAnalysis, Fold, Expand, Refresh
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const isCollapse = ref(false)

// 路由名称映射
const routeNameMap = {
  '/': '首页',
  '/rooms': '教室管理',
  '/teachers': '教师管理',
  '/classes': '班级管理',
  '/courses': '课程管理',
  '/holidays': '节假日管理',
  '/import': '数据导入',
  '/schedules': '课表查看',
  '/statistics': '课时统计',
  '/adjust-schedule': '调整课表',
}

const currentRouteName = computed(() => routeNameMap[route.path] || '')

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value
}

const refreshPage = () => {
  // 触发当前页面的重新加载数据（由各子组件自行处理）
  window.dispatchEvent(new CustomEvent('refresh-page'))
}
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

/* ===== 侧边栏 ===== */
.aside {
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 50%, #334155 100%);
  height: 100vh;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15);
  transition: width var(--duration-slow) var(--ease-in-out);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.aside.is-collapsed {
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.1);
}

/* Logo 区域 */
.aside-logo {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  flex-shrink: 0;
}

.logo-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary-5), var(--color-primary-7));
  border-radius: var(--radius-md);
  color: #ffffff;
  flex-shrink: 0;
}

.logo-text {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  color: #ffffff;
  white-space: nowrap;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #ffffff 0%, #c2cad8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-fade-enter-active,
.logo-fade-leave-active {
  transition: opacity var(--duration-base) var(--ease-out);
}

.logo-fade-enter-from,
.logo-fade-leave-to {
  opacity: 0;
}

/* 侧边栏菜单 */
.aside-menu {
  flex: 1;
  border-right: none !important;
  background: transparent !important;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 8px 0;
}

/* 隐藏菜单滚动条 */
.aside-menu::-webkit-scrollbar {
  width: 4px;
}

.aside-menu::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
}

/* 菜单分割线 */
.menu-divider {
  border-color: rgba(255, 255, 255, 0.06);
  margin: 4px 12px;
}

/* 菜单项样式 */
.aside-menu .el-menu-item,
.aside-menu .el-sub-menu__title {
  height: 44px;
  line-height: 44px;
  margin: 2px 8px;
  border-radius: var(--radius-md);
  transition: all var(--duration-base) var(--ease-out);
  font-size: var(--font-size-base);
}

.aside-menu .el-menu-item:hover,
.aside-menu .el-sub-menu__title:hover {
  background: rgba(255, 255, 255, 0.08) !important;
}

.aside-menu .el-menu-item.is-active {
  background: linear-gradient(135deg, rgba(22, 93, 255, 0.35), rgba(22, 93, 255, 0.15)) !important;
  color: #ffffff !important;
  font-weight: var(--font-weight-semibold);
  box-shadow: 0 2px 8px rgba(22, 93, 255, 0.2);
}

.aside-menu .el-menu-item.is-active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--color-primary-5);
  border-radius: 0 2px 2px 0;
}

.aside-menu .el-sub-menu .el-menu-item {
  height: 40px;
  line-height: 40px;
  margin: 2px 8px 2px 16px;
  font-size: var(--font-size-base);
}

.aside-menu .el-sub-menu .el-menu-item.is-active {
  margin-left: 16px;
}

/* 折叠按钮 */
.aside-collapse-btn {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: rgba(255, 255, 255, 0.4);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  transition: all var(--duration-base) var(--ease-out);
  flex-shrink: 0;
}

.aside-collapse-btn:hover {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.05);
}

/* 折叠状态下菜单项居中 */
.aside-menu.el-menu--collapse {
  width: 48px;
}

.aside-menu.el-menu--collapse .el-menu-item,
.aside-menu.el-menu--collapse .el-sub-menu__title {
  justify-content: center;
  padding: 0 !important;
}

.aside-menu.el-menu--collapse .el-menu-item.is-active::before {
  display: none;
}

/* ===== 顶部栏 ===== */
.app-header {
  height: 56px;
  background: var(--bg-card);
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: var(--shadow-xs);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 面包屑 */
:deep(.el-breadcrumb__inner) {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

:deep(.el-breadcrumb__inner a),
:deep(.el-breadcrumb__inner.is-link) {
  color: var(--text-regular);
  font-weight: var(--font-weight-regular);
}

:deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
  color: var(--text-primary);
  font-weight: var(--font-weight-medium);
}

/* ===== 主内容区 ===== */
.main {
  background-color: var(--bg-page);
  min-height: calc(100vh - 56px);
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
