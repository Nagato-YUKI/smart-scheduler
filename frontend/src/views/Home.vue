<template>
  <div class="home-container">
    <!-- 欢迎区域 -->
    <div class="welcome-banner">
      <div class="welcome-content">
        <h1 class="welcome-title">欢迎使用智能排课系统</h1>
        <p class="welcome-desc">高效管理教室、教师、班级与课程资源，一键生成最优课表</p>
      </div>
      <div class="welcome-actions">
        <el-button type="primary" size="large" @click="$router.push('/import')">
          <el-icon><UploadFilled /></el-icon>
          <span>数据导入</span>
        </el-button>
        <el-button size="large" @click="$router.push('/schedules')">
          <el-icon><Calendar /></el-icon>
          <span>查看课表</span>
        </el-button>
      </div>
    </div>

    <!-- 统计卡片行 -->
    <el-row :gutter="16" class="stats-row">
      <el-col :xs="12" :sm="12" :md="6">
        <div class="stat-card stat-card--blue">
          <div class="stat-card__icon">
            <el-icon :size="28"><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__label">教室总数</div>
            <div class="stat-card__value">{{ stats.rooms }}</div>
          </div>
          <div class="stat-card__action" @click="$router.push('/rooms')">
            <span>查看详情</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <div class="stat-card stat-card--green">
          <div class="stat-card__icon">
            <el-icon :size="28"><UserFilled /></el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__label">教师总数</div>
            <div class="stat-card__value">{{ stats.teachers }}</div>
          </div>
          <div class="stat-card__action" @click="$router.push('/teachers')">
            <span>查看详情</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <div class="stat-card stat-card--orange">
          <div class="stat-card__icon">
            <el-icon :size="28"><Reading /></el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__label">班级总数</div>
            <div class="stat-card__value">{{ stats.classes }}</div>
          </div>
          <div class="stat-card__action" @click="$router.push('/classes')">
            <span>查看详情</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="12" :md="6">
        <div class="stat-card stat-card--purple">
          <div class="stat-card__icon">
            <el-icon :size="28"><Notebook /></el-icon>
          </div>
          <div class="stat-card__content">
            <div class="stat-card__label">课程总数</div>
            <div class="stat-card__value">{{ stats.courses }}</div>
          </div>
          <div class="stat-card__action" @click="$router.push('/courses')">
            <span>查看详情</span>
            <el-icon><ArrowRight /></el-icon>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 快捷入口 -->
    <el-card class="quick-access-card" shadow="hover">
      <template #header>
        <div class="card-header">
          <div class="card-header__title">
            <el-icon><Grid /></el-icon>
            <span>快捷入口</span>
          </div>
        </div>
      </template>
      <el-row :gutter="16">
        <el-col :xs="8" :sm="6" :md="4" v-for="item in quickAccessItems" :key="item.path">
          <div class="quick-item" @click="$router.push(item.path)">
            <div class="quick-item__icon" :style="{ background: item.color }">
              <el-icon :size="24"><component :is="item.icon" /></el-icon>
            </div>
            <div class="quick-item__text">{{ item.label }}</div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 数据概览 -->
    <el-row :gutter="16" class="overview-row">
      <el-col :xs="24" :md="12">
        <el-card class="overview-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="card-header__title">
                <el-icon><OfficeBuilding /></el-icon>
                <span>教室概览</span>
              </div>
              <el-button text type="primary" @click="$router.push('/rooms')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="rooms.slice(0, 5)" class="home-table">
            <el-table-column prop="room_number" label="编号" width="80" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="room_type" label="类型" width="100" />
            <el-table-column prop="capacity" label="容量" width="70" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card class="overview-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="card-header__title">
                <el-icon><UserFilled /></el-icon>
                <span>教师概览</span>
              </div>
              <el-button text type="primary" @click="$router.push('/teachers')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="teachers.slice(0, 5)" class="home-table">
            <el-table-column prop="teacher_number" label="编号" width="80" />
            <el-table-column prop="name" label="姓名" />
            <el-table-column prop="teachable_courses" label="可授课程" show-overflow-tooltip />
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="overview-row">
      <el-col :xs="24" :md="12">
        <el-card class="overview-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="card-header__title">
                <el-icon><Reading /></el-icon>
                <span>班级概览</span>
              </div>
              <el-button text type="primary" @click="$router.push('/classes')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="classes.slice(0, 5)" class="home-table">
            <el-table-column prop="class_number" label="编号" width="80" />
            <el-table-column prop="name" label="名称" />
            <el-table-column prop="student_count" label="人数" width="70" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :xs="24" :md="12">
        <el-card class="overview-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="card-header__title">
                <el-icon><Notebook /></el-icon>
                <span>课程概览</span>
              </div>
              <el-button text type="primary" @click="$router.push('/courses')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="courses.slice(0, 5)" class="home-table">
            <el-table-column prop="course_number" label="编号" width="80" />
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
import { useRouter } from 'vue-router'
import {
  OfficeBuilding, UserFilled, Reading, Notebook,
  ArrowRight, Grid, Calendar, UploadFilled,
  Files, EditPen, DataAnalysis, Sunny
} from '@element-plus/icons-vue'
import { roomApi, teacherApi, classApi, courseApi } from '../api/index.js'

const stats = reactive({ rooms: 0, teachers: 0, classes: 0, courses: 0 })
const rooms = ref([])
const teachers = ref([])
const classes = ref([])
const courses = ref([])

const quickAccessItems = [
  { label: '教室管理', path: '/rooms', icon: 'OfficeBuilding', color: 'linear-gradient(135deg, #667eea, #764ba2)' },
  { label: '教师管理', path: '/teachers', icon: 'UserFilled', color: 'linear-gradient(135deg, #f093fb, #f5576c)' },
  { label: '班级管理', path: '/classes', icon: 'Reading', color: 'linear-gradient(135deg, #4facfe, #00f2fe)' },
  { label: '课程管理', path: '/courses', icon: 'Notebook', color: 'linear-gradient(135deg, #43e97b, #38f9d7)' },
  { label: '数据导入', path: '/import', icon: 'UploadFilled', color: 'linear-gradient(135deg, #fa709a, #fee140)' },
  { label: '课表查看', path: '/schedules', icon: 'Calendar', color: 'linear-gradient(135deg, #a18cd1, #fbc2eb)' },
]

const fetchData = async () => {
  try {
    const [rRes, tRes, cRes, coRes] = await Promise.all([
      roomApi.getList({ page: 1, per_page: 100 }),
      teacherApi.getList({ page: 1, per_page: 100 }),
      classApi.getList({ page: 1, per_page: 100 }),
      courseApi.getList({ page: 1, per_page: 100 }),
    ])
    rooms.value = rRes.rooms || []
    stats.rooms = rRes.total || 0
    teachers.value = (tRes.teachers || []).map(t => ({
      ...t,
      teachable_courses: Array.isArray(t.teachable_courses) ? t.teachable_courses.join(', ') : ''
    }))
    stats.teachers = tRes.total || 0
    classes.value = cRes.classes || []
    stats.classes = cRes.total || 0
    courses.value = coRes.courses || []
    stats.courses = coRes.total || 0
  } catch (e) {
    console.error('获取首页数据失败', e)
  }
}

onMounted(() => fetchData())
</script>

<style scoped>
.home-container {
  padding: var(--space-6);
  background: var(--bg-page);
  min-height: 100%;
}

/* ===== 欢迎横幅 ===== */
.welcome-banner {
  background: linear-gradient(135deg, var(--color-primary-6) 0%, var(--color-primary-8) 100%);
  border-radius: var(--radius-xl);
  padding: var(--space-8) var(--space-8);
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-6);
  color: #ffffff;
  box-shadow: 0 4px 16px rgba(22, 93, 255, 0.3);
}

.welcome-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--space-2);
  letter-spacing: 0.5px;
}

.welcome-desc {
  font-size: var(--font-size-base);
  opacity: 0.85;
  line-height: var(--line-height-base);
}

.welcome-actions {
  display: flex;
  gap: var(--space-3);
  flex-shrink: 0;
}

.welcome-actions :deep(.el-button) {
  border-radius: var(--radius-md);
  font-weight: var(--font-weight-medium);
}

.welcome-actions :deep(.el-button--primary) {
  background: #ffffff;
  color: var(--color-primary-6);
  border: none;
}

.welcome-actions :deep(.el-button--primary:hover) {
  background: var(--color-primary-1);
}

/* ===== 统计卡片 ===== */
.stats-row {
  margin-bottom: var(--space-6);
}

.stat-card {
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  transition: all var(--duration-base) var(--ease-out);
  cursor: pointer;
  position: relative;
  overflow: hidden;
  height: 100%;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.stat-card__icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
}

.stat-card--blue .stat-card__icon {
  background: linear-gradient(135deg, var(--color-primary-4), var(--color-primary-7));
}

.stat-card--green .stat-card__icon {
  background: linear-gradient(135deg, var(--color-success-3), var(--color-success-7));
}

.stat-card--orange .stat-card__icon {
  background: linear-gradient(135deg, var(--color-warning-3), var(--color-warning-7));
}

.stat-card--purple .stat-card__icon {
  background: linear-gradient(135deg, #a78bfa, #7c3aed);
}

.stat-card__label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-bottom: var(--space-1);
}

.stat-card__value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  line-height: var(--line-height-tight);
}

.stat-card__action {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--font-size-sm);
  color: var(--color-primary-6);
  margin-top: auto;
  padding-top: var(--space-3);
  border-top: 1px solid var(--border-light);
  transition: all var(--duration-fast) var(--ease-out);
}

.stat-card__action:hover {
  color: var(--color-primary-7);
}

/* ===== 快捷入口 ===== */
.quick-access-card {
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-6);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header__title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-2);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-base) var(--ease-out);
}

.quick-item:hover {
  background: var(--color-neutral-1);
  transform: translateY(-2px);
}

.quick-item__icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
}

.quick-item__text {
  font-size: var(--font-size-sm);
  color: var(--text-regular);
  text-align: center;
  white-space: nowrap;
}

/* ===== 数据概览 ===== */
.overview-row {
  margin-bottom: var(--space-6);
}

.overview-card {
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
  margin-bottom: var(--space-4);
}

.home-table {
  border-radius: var(--radius-md);
}

.home-table :deep(.el-table__header th) {
  background: var(--color-neutral-1);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.home-table :deep(.el-table__row:hover) {
  background-color: var(--color-primary-1) !important;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .home-container {
    padding: var(--space-4);
  }

  .welcome-banner {
    flex-direction: column;
    text-align: center;
    gap: var(--space-4);
    padding: var(--space-5) var(--space-4);
  }

  .welcome-title {
    font-size: var(--font-size-xl);
  }

  .welcome-actions {
    flex-direction: column;
    width: 100%;
  }

  .welcome-actions :deep(.el-button) {
    width: 100%;
  }

  .stat-card {
    margin-bottom: var(--space-3);
  }

  .stat-card__value {
    font-size: var(--font-size-2xl);
  }
}

@media (max-width: 480px) {
  .home-container {
    padding: var(--space-3);
  }

  .welcome-banner {
    padding: var(--space-4) var(--space-3);
  }

  .welcome-title {
    font-size: var(--font-size-lg);
  }

  .welcome-desc {
    font-size: var(--font-size-sm);
  }
}
</style>
