<template>
  <div class="statistics-page">
    <div class="schedule-toolbar">
      <h2 class="page-title">
        <span class="title-icon">📊</span>
        课时统计
      </h2>
      <div class="toolbar-controls">
        <el-button type="primary" @click="loadData" :icon="Refresh" :loading="loading">刷新数据</el-button>
      </div>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <!-- 总体统计卡片 -->
      <el-col :xs="24" :sm="12" :md="6" class="stat-col">
        <el-card shadow="hover" class="stat-card stat-card--blue">
          <div class="stat-card-content">
            <div class="stat-icon">
              <el-icon :size="28"><OfficeBuilding /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_classes || 0 }}</div>
              <div class="stat-label">教学班总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" class="stat-col">
        <el-card shadow="hover" class="stat-card stat-card--green">
          <div class="stat-card-content">
            <div class="stat-icon">
              <el-icon :size="28"><Finished /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.scheduled_classes || 0 }}</div>
              <div class="stat-label">已排课班级</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" class="stat-col">
        <el-card shadow="hover" class="stat-card stat-card--orange">
          <div class="stat-card-content">
            <div class="stat-icon">
              <el-icon :size="28"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_hours || 0 }}</div>
              <div class="stat-label">总课时数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" class="stat-col">
        <el-card shadow="hover" class="stat-card stat-card--purple">
          <div class="stat-card-content">
            <div class="stat-icon">
              <el-icon :size="28"><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.completion_rate || 0 }}%</div>
              <div class="stat-label">排课完成率</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 完成率状态 -->
    <el-card shadow="hover" class="progress-card" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <el-icon><DataLine /></el-icon>
          <span>排课状态</span>
        </div>
      </template>
      <div class="status-wrapper">
        <div class="status-display" :class="isComplete ? 'status-complete' : 'status-incomplete'">
          <div class="status-icon">{{ isComplete ? '✅' : '⏳' }}</div>
          <div class="status-text">{{ isComplete ? '已完成' : '未完成' }}</div>
        </div>
        <div class="status-details">
          <div class="detail-row">
            <span class="detail-label">已排课班级：</span>
            <span class="detail-value">{{ stats.scheduled_classes || 0 }} / {{ stats.total_classes || 0 }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">排课完成率：</span>
            <span class="detail-value">{{ stats.completion_rate || 0 }}%</span>
          </div>
          <div v-if="!isComplete" class="status-hint">
            <el-icon><WarningFilled /></el-icon>
            <span>还有 {{ (stats.missing_classes || []).length }} 个教学班未排课</span>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 时段分布 -->
    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <el-icon><PieChart /></el-icon>
          <span>时段分布</span>
        </div>
      </template>
      <el-row :gutter="20">
        <el-col :xs="24" :sm="8">
          <div class="period-stat period-stat--morning">
            <div class="period-stat-icon">🌅</div>
            <div class="period-stat-content">
              <div class="period-stat-value">{{ stats.period_distribution?.morning || 0 }}</div>
              <div class="period-stat-label">上午课时</div>
              <div class="period-stat-sub">（4课时/次）</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="8">
          <div class="period-stat period-stat--afternoon">
            <div class="period-stat-icon">☀️</div>
            <div class="period-stat-content">
              <div class="period-stat-value">{{ stats.period_distribution?.afternoon || 0 }}</div>
              <div class="period-stat-label">下午课时</div>
              <div class="period-stat-sub">（4课时/次）</div>
            </div>
          </div>
        </el-col>
        <el-col :xs="24" :sm="8">
          <div class="period-stat period-stat--evening">
            <div class="period-stat-icon">🌙</div>
            <div class="period-stat-content">
              <div class="period-stat-value">{{ stats.period_distribution?.evening || 0 }}</div>
              <div class="period-stat-label">晚上课时</div>
              <div class="period-stat-sub">（3课时/次）</div>
            </div>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- 各教学班课时明细 -->
    <el-card shadow="hover" style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <el-icon><List /></el-icon>
          <span>各教学班课时明细</span>
          <span class="header-badge">共 {{ classDetails.length }} 个教学班</span>
        </div>
      </template>
      <el-table :data="classDetails" border stripe max-height="500" row-key="teaching_class_id"
        :header-cell-style="{ background: '#f7f8fa', color: '#1d2129', fontWeight: '600' }"
      >
        <el-table-column prop="teaching_class_id" label="教学班ID" width="110" sortable />
        <el-table-column prop="course_name" label="课程名称" min-width="160" />
        <el-table-column prop="class_name" label="班级" min-width="140" />
        <el-table-column prop="teacher_name" label="教师" width="110" />
        <el-table-column prop="session_count" label="排课次数" width="100" sortable />
        <el-table-column prop="actual_hours" label="实际课时" width="110" sortable>
          <template #default="{ row }">
            <span class="hours-badge">{{ row.actual_hours }}课时</span>
          </template>
        </el-table-column>
        <el-table-column label="缺课提示" width="180" fixed="right">
          <template #default="{ row }">
            <el-tag v-if="row.missing_hours > 0" type="warning" size="small" effect="dark">
              <el-icon><WarningFilled /></el-icon>
              <span style="margin-left: 4px">缺课{{ row.missing_hours }}课时</span>
            </el-tag>
            <el-tag v-else type="success" size="small" effect="dark">
              <el-icon><CircleCheckFilled /></el-icon>
              <span style="margin-left: 4px">已排满</span>
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Refresh, OfficeBuilding, Finished, Clock, TrendCharts, DataLine, PieChart, List, WarningFilled, CircleCheckFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { scheduleApi, classApi, teacherApi } from '../api/index.js'
import '../assets/schedule-common.css'
import '../assets/design-tokens.css'

const loading = ref(false)
const stats = ref({})
const classDetails = ref([])

const isComplete = computed(() => (stats.value.completion_rate || 0) >= 100)

onMounted(() => loadData())

async function loadData() {
  loading.value = true
  try {
    const res = await scheduleApi.getStatistics()
    stats.value = res || {}
    await buildClassDetails(res)
  } catch (e) {
    console.error(e)
    ElMessage.error('加载统计数据失败')
  } finally {
    loading.value = false
  }
}

async function buildClassDetails(res) {
  const details = []
  const periodHours = { morning: 4, afternoon: 4, evening: 3 }

  const [clsRes, tchRes] = await Promise.all([
    classApi.getList({ page: 1, per_page: 100 }),
    teacherApi.getList({ page: 1, per_page: 100 })
  ])
  const clsMap = {}
  for (const c of (clsRes.classes || [])) clsMap[c.id] = c
  const tchMap = {}
  for (const t of (tchRes.teachers || [])) tchMap[t.id] = t

  const entriesRes = await scheduleApi.getResults({ page: 1, per_page: 2000 })
  const entries = entriesRes.results || []

  const tcGroups = {}
  for (const e of entries) {
    const tid = e.teaching_class_id
    if (!tcGroups[tid]) tcGroups[tid] = { hours: 0, count: 0, course_name: e.course_name || '-', class_name: e.class_name || '-', teacher_name: e.teacher_name || '-' }
    tcGroups[tid].hours += periodHours[e.period] || 0
    tcGroups[tid].count += 1
  }

  for (const [tid, info] of Object.entries(tcGroups)) {
    details.push({
      teaching_class_id: Number(tid),
      course_name: info.course_name,
      class_name: info.class_name,
      teacher_name: info.teacher_name,
      session_count: info.count,
      actual_hours: info.hours,
      missing_hours: Math.max(0, 64 - info.hours)
    })
  }

  for (const mc of (res.missing_classes || [])) {
    const tid = mc.teaching_class_id
    if (!tcGroups[tid]) {
      details.push({
        teaching_class_id: tid,
        course_name: '-',
        class_name: '-',
        teacher_name: '-',
        session_count: 0,
        actual_hours: 0,
        missing_hours: 64
      })
    }
  }

  classDetails.value = details.sort((a, b) => a.teaching_class_id - b.teaching_class_id)
}
</script>

<style scoped>
.statistics-page {
  padding: 24px;
  background: var(--bg-page);
  min-height: 100%;
}

.stat-col {
  margin-bottom: 16px;
}

.stat-card {
  border-radius: var(--radius-xl);
  overflow: hidden;
  transition: transform var(--duration-base) var(--ease-out), box-shadow var(--duration-base) var(--ease-out);
  border: 1px solid var(--border-light);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg) !important;
}

/* 顶部装饰条 */
.stat-card::before {
  content: '';
  display: block;
  height: 4px;
}

.stat-card--blue::before { background: linear-gradient(90deg, var(--color-primary-5), var(--color-primary-7)); }
.stat-card--green::before { background: linear-gradient(90deg, var(--color-success-4), var(--color-success-7)); }
.stat-card--orange::before { background: linear-gradient(90deg, var(--color-warning-4), var(--color-warning-7)); }
.stat-card--purple::before { background: linear-gradient(90deg, #722ed1, #9954ff); }

.stat-card-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 0;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--duration-base) var(--ease-bounce);
}

.stat-card:hover .stat-icon {
  transform: scale(1.1) rotate(5deg);
}

.stat-card--blue .stat-icon { background: linear-gradient(135deg, var(--color-primary-1), var(--color-primary-2)); color: var(--color-primary-6); }
.stat-card--green .stat-icon { background: linear-gradient(135deg, var(--color-success-1), var(--color-success-2)); color: var(--color-success-6); }
.stat-card--orange .stat-icon { background: linear-gradient(135deg, var(--color-warning-1), var(--color-warning-2)); color: var(--color-warning-6); }
.stat-card--purple .stat-icon { background: linear-gradient(135deg, #f3e8ff, #e9d5ff); color: #722ed1; }

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  line-height: var(--line-height-tight);
  font-variant-numeric: tabular-nums;
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin-top: 4px;
  font-weight: var(--font-weight-medium);
}

/* 状态显示 */
.progress-card {
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-light);
}

.status-wrapper {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 16px 0;
}

.status-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 120px;
  padding: 20px;
  border-radius: var(--radius-xl);
}

.status-complete {
  background: linear-gradient(135deg, #e8ffea 0%, #b7f4c2 100%);
}

.status-incomplete {
  background: linear-gradient(135deg, #fff7e6 0%, #ffe7ba 100%);
}

.status-icon {
  font-size: 36px;
  margin-bottom: 8px;
}

.status-text {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.status-details {
  flex: 1;
}

.detail-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.detail-label {
  font-size: var(--font-size-base);
  color: var(--text-regular);
  min-width: 120px;
}

.detail-value {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.status-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 12px;
  padding: 8px 12px;
  background: #fff7e6;
  border-radius: var(--radius-md);
  color: #e6a23c;
  font-size: var(--font-size-sm);
}

/* 时段分布 */
.period-stat {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: var(--radius-lg);
  margin: 8px 0;
  transition: transform var(--duration-base) var(--ease-out), box-shadow var(--duration-base) var(--ease-out);
  border: 1px solid transparent;
}

.period-stat:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
  border-color: rgba(0,0,0,0.04);
}

.period-stat--morning {
  background: linear-gradient(135deg, #fff7e6 0%, #ffe7ba 100%);
}

.period-stat--afternoon {
  background: linear-gradient(135deg, #e8ffea 0%, #b7f4c2 100%);
}

.period-stat--evening {
  background: linear-gradient(135deg, #e8f3ff 0%, #b7dfff 100%);
}

.period-stat-icon {
  font-size: 32px;
  transition: transform var(--duration-base) var(--ease-bounce);
}

.period-stat:hover .period-stat-icon {
  transform: scale(1.15);
}

.period-stat-content {
  flex: 1;
}

.period-stat-value {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.period-stat-label {
  font-size: var(--font-size-base);
  color: var(--text-regular);
  font-weight: var(--font-weight-medium);
}

.period-stat-sub {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

/* 卡片头部 */
.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.header-badge {
  margin-left: auto;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  font-weight: var(--font-weight-regular);
  background: var(--color-neutral-2);
  padding: 2px 10px;
  border-radius: var(--radius-full);
}

.hours-badge {
  background: var(--color-primary-1);
  color: var(--color-primary-6);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

/* 表格增强 */
:deep(.el-table) {
  border-radius: var(--radius-md);
  overflow: hidden;
}

:deep(.el-table__header-wrapper) {
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}

:deep(.el-table__row) {
  transition: background-color var(--duration-base) var(--ease-out);
}

:deep(.el-table__row:hover) {
  background-color: var(--color-primary-1) !important;
}

:deep(.el-table__row:hover > td) {
  background-color: transparent !important;
}

:deep(.el-table--striped .el-table__body tr.el-table__row--striped td) {
  background-color: var(--color-neutral-1);
}
</style>
