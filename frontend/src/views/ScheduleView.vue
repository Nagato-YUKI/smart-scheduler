<template>
  <div class="schedule-view management-page">
    <div class="schedule-view-header">
      <div class="header-title">
        <el-icon :size="24" color="var(--color-primary-6)"><Calendar /></el-icon>
        <span>课表查看</span>
      </div>
      <p class="header-desc">按班级、教师或教室维度查看课程表</p>
    </div>

    <el-tabs v-model="activeTab" type="card" @tab-click="handleTabClick" class="schedule-tabs">
      <el-tab-pane label="班级课表" name="class">
        <template #label>
          <span class="tab-label">
            <el-icon><Reading /></el-icon>
            <span>班级课表</span>
          </span>
        </template>
        <ClassSchedule />
      </el-tab-pane>
      <el-tab-pane label="教师课表" name="teacher">
        <template #label>
          <span class="tab-label">
            <el-icon><UserFilled /></el-icon>
            <span>教师课表</span>
          </span>
        </template>
        <TeacherSchedule />
      </el-tab-pane>
      <el-tab-pane label="教室课表" name="room">
        <template #label>
          <span class="tab-label">
            <el-icon><OfficeBuilding /></el-icon>
            <span>教室课表</span>
          </span>
        </template>
        <RoomSchedule />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Calendar, Reading, UserFilled, OfficeBuilding } from '@element-plus/icons-vue'
import ClassSchedule from './ClassSchedule.vue'
import TeacherSchedule from './TeacherSchedule.vue'
import RoomSchedule from './RoomSchedule.vue'
import '../assets/design-tokens.css'

const activeTab = ref('class')

function handleTabClick(tab) {
  activeTab.value = tab.props.name
}
</script>

<style scoped>
.schedule-view {
  padding: 24px;
  background: var(--bg-page);
  min-height: 100%;
}

.schedule-view-header {
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.header-title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.header-desc {
  margin-top: var(--space-2);
  font-size: var(--font-size-base);
  color: var(--text-secondary);
}

.schedule-tabs {
  background: transparent;
}

.tab-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

:deep(.el-tabs__header) {
  margin-bottom: var(--space-5);
}

:deep(.el-tabs--card .el-tabs__item) {
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  font-weight: var(--font-weight-medium);
  transition: all var(--duration-base) var(--ease-out);
  border: 1px solid var(--border-base) !important;
}

:deep(.el-tabs--card .el-tabs__item.is-active) {
  font-weight: var(--font-weight-semibold);
  color: var(--color-primary-6);
  border-color: var(--color-primary-6) !important;
  border-bottom-color: #fff !important;
}

:deep(.el-tabs__content) {
  padding: 0;
}
</style>
