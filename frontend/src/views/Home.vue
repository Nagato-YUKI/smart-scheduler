<template>
  <div class="home-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card--blue">
          <el-statistic :value="stats.rooms"><template #title><el-icon><OfficeBuilding /></el-icon> 教室总数</template></el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card--green">
          <el-statistic :value="stats.teachers"><template #title><el-icon><User /></el-icon> 教师总数</template></el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card--orange">
          <el-statistic :value="stats.classes"><template #title><el-icon><Reading /></el-icon> 班级总数</template></el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card--purple">
          <el-statistic :value="stats.courses"><template #title><el-icon><Collection /></el-icon> 课程总数</template></el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- 列表区域 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="list-card">
          <template #header><span><el-icon><OfficeBuilding /></el-icon> 教室列表</span></template>
          <el-table :data="rooms.slice(0, 5)" border stripe>
            <el-table-column prop="room_number" label="编号" width="90" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="room_type" label="类型" width="120" />
            <el-table-column prop="capacity" label="容量" width="70" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="list-card">
          <template #header><span><el-icon><User /></el-icon> 教师列表</span></template>
          <el-table :data="teachers.slice(0, 5)" border stripe>
            <el-table-column prop="teacher_number" label="编号" width="90" />
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="teachable_courses" label="可授课程" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="list-card">
          <template #header><span><el-icon><Reading /></el-icon> 班级列表</span></template>
          <el-table :data="classes.slice(0, 5)" border stripe>
            <el-table-column prop="class_number" label="编号" width="90" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="student_count" label="人数" width="70" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="list-card">
          <template #header><span><el-icon><Collection /></el-icon> 课程列表</span></template>
          <el-table :data="courses.slice(0, 5)" border stripe>
            <el-table-column prop="course_number" label="编号" width="90" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="course_type" label="类型" width="100" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { OfficeBuilding, User, Reading, Collection } from '@element-plus/icons-vue'
import { roomApi, teacherApi, classApi, courseApi } from '../api/index.js'
import '../assets/design-tokens.css'

const stats = reactive({ rooms: 0, teachers: 0, classes: 0, courses: 0 })
const rooms = ref([])
const teachers = ref([])
const classes = ref([])
const courses = ref([])

const fetchData = async () => {
  try {
    const [rRes, tRes, cRes, coRes] = await Promise.all([
      roomApi.getList({ page: 1, per_page: 100 }),
      teacherApi.getList({ page: 1, per_page: 100 }),
      classApi.getList({ page: 1, per_page: 100 }),
      courseApi.getList({ page: 1, per_page: 100 }),
    ])
    rooms.value = rRes.rooms || []; stats.rooms = rRes.total || 0
    teachers.value = (tRes.teachers || []).map(t => ({ ...t, teachable_courses: Array.isArray(t.teachable_courses) ? t.teachable_courses.join(', ') : '' }))
    stats.teachers = tRes.total || 0
    classes.value = cRes.classes || []; stats.classes = cRes.total || 0
    courses.value = coRes.courses || []; stats.courses = coRes.total || 0
  } catch (e) { console.error('获取首页数据失败', e) }
}

onMounted(() => fetchData())
</script>

<style scoped>
.home-container { padding: 24px; background: var(--bg-page); min-height: 100%; }
.stat-card { text-align: center; border-radius: var(--radius-xl); border: 1px solid var(--border-light); box-shadow: var(--shadow-sm); transition: all var(--duration-base) var(--ease-out); overflow: hidden; }
.stat-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg) !important; }
.stat-card::before { content: ''; display: block; height: 4px; }
.stat-card--blue::before { background: linear-gradient(90deg, var(--color-primary-5), var(--color-primary-7)); }
.stat-card--green::before { background: linear-gradient(90deg, var(--color-success-4), var(--color-success-7)); }
.stat-card--orange::before { background: linear-gradient(90deg, var(--color-warning-4), var(--color-warning-7)); }
.stat-card--purple::before { background: linear-gradient(90deg, #722ed1, #9954ff); }
.stat-card :deep(.el-statistic__title) { font-size: var(--font-size-base); color: var(--text-secondary); display: flex; align-items: center; justify-content: center; gap: 6px; }
.stat-card :deep(.el-statistic__number) { font-size: var(--font-size-3xl); font-weight: var(--font-weight-bold); color: var(--text-primary); }
.list-card { border-radius: var(--radius-xl); border: 1px solid var(--border-light); box-shadow: var(--shadow-sm); }
.list-card :deep(.el-card__header) { font-weight: var(--font-weight-semibold); display: flex; align-items: center; gap: 8px; }
.list-card :deep(.el-table) { border-radius: var(--radius-md); overflow: hidden; }
.list-card :deep(.el-table__row:hover) { background-color: var(--color-primary-1) !important; }
</style>
