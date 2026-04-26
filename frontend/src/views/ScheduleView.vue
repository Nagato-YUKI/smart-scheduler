<template>
  <div class="schedule-view">
    <el-tabs v-model="activeTab" type="border-card" @tab-click="handleTabClick">
      <el-tab-pane label="班级课表" name="class"><ClassSchedule /></el-tab-pane>
      <el-tab-pane label="教师课表" name="teacher"><TeacherSchedule /></el-tab-pane>
      <el-tab-pane label="教室课表" name="room"><RoomSchedule /></el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ClassSchedule from './ClassSchedule.vue'
import TeacherSchedule from './TeacherSchedule.vue'
import RoomSchedule from './RoomSchedule.vue'

const activeTab = ref('class')

function handleTabClick(tab) { activeTab.value = tab.props.name }
</script>

<style scoped>
.schedule-view { padding: 24px; background: var(--bg-page); min-height: 100%; }
:deep(.el-tabs__content) { padding: 0; }
:deep(.el-tabs--border-card) { box-shadow: none; border: none; background: transparent; }
:deep(.el-tabs__header) { margin-bottom: 20px; }
:deep(.el-tabs__item) { font-weight: var(--font-weight-medium); transition: all var(--duration-base) var(--ease-out); }
:deep(.el-tabs__item.is-active) { font-weight: var(--font-weight-semibold); color: var(--color-primary-6); }
</style>
