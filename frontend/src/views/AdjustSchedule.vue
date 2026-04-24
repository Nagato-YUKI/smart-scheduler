<template>
  <div class="adjust-page">
    <div class="schedule-toolbar">
      <h2 class="page-title">
        <span class="title-icon">🔄</span>
        调整课表
      </h2>
      <div class="toolbar-controls">
        <el-select v-model="filterWeek" placeholder="按周次筛选" @change="loadData" style="width: 120px" clearable>
          <el-option v-for="w in 20" :key="w" :label="`第${w}周`" :value="w" />
        </el-select>
        <el-select v-model="filterDay" placeholder="按星期筛选" @change="loadData" style="width: 120px" clearable>
          <el-option v-for="d in 5" :key="d" :label="`星期${['一','二','三','四','五'][d-1]}`" :value="d" />
        </el-select>
        <el-input v-model="filterKeyword" placeholder="搜索课程/教师/班级" @input="handleFilter" style="width: 200px" clearable>
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="loadData" :icon="Refresh" :loading="loading">刷新</el-button>
      </div>
    </div>

    <el-card shadow="hover" v-loading="loading" style="margin-top: 20px; border-radius: 12px;">
      <template #header>
        <div class="card-header">
          <el-icon><Calendar /></el-icon>
          <span>已排课程列表</span>
          <span class="header-badge">共 {{ pagination.total }} 条</span>
        </div>
      </template>
      
      <el-table :data="filteredTableData" border stripe max-height="500"
        :header-cell-style="{ background: '#f7f8fa', color: '#1d2129', fontWeight: '600' }"
      >
        <el-table-column prop="id" label="记录ID" width="90" />
        <el-table-column prop="course_name" label="课程" min-width="150">
          <template #default="{ row }">
            <span class="course-tag" :style="{ background: getCourseTagColor(row.course_name) }">
              {{ row.course_name }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="teacher_name" label="教师" width="110" />
        <el-table-column prop="class_name" label="班级" min-width="140" />
        <el-table-column prop="room_name" label="教室" width="130">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.room_name }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="week" label="周次" width="80">
          <template #default="{ row }">
            <el-tag size="small" type="info">第{{ row.week }}周</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="day" label="星期" width="80">
          <template #default="{ row }">
            <span class="day-badge">{{ ['一','二','三','四','五'][row.day-1] }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="period" label="时段" width="90">
          <template #default="{ row }">
            <el-tag size="small" :type="getPeriodType(row.period)">
              {{ { morning:'上午', afternoon:'下午', evening:'晚上' }[row.period] || row.period }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="openAdjust(row)" :icon="EditPen">调整</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="loadData"
        @current-change="loadData"
        style="margin-top: 16px; justify-content: flex-end"
        background
      />
    </el-card>

    <!-- 调整弹窗 -->
    <el-dialog v-model="adjustDialogVisible" title="调整课表" width="480px" :close-on-click-modal="false">
      <div class="adjust-dialog-content">
        <div class="adjust-info">
          <div class="info-row">
            <span class="info-label">当前课程：</span>
            <span class="info-value">{{ currentEntry?.course_name }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">原时段：</span>
            <span class="info-value original-time">
              第{{ currentEntry?.week }}周 / 星期{{ currentEntry ? ['一','二','三','四','五'][currentEntry.day-1] : '' }} / {{ currentEntry ? { morning:'上午', afternoon:'下午', evening:'晚上' }[currentEntry.period] : '' }}
            </span>
          </div>
        </div>

        <el-divider content-position="left">目标时段</el-divider>

        <el-form label-width="80px" label-position="right">
          <el-form-item label="目标周次">
            <el-select v-model="adjustForm.week" style="width: 100%">
              <el-option v-for="w in 20" :key="w" :label="`第${w}周`" :value="w" />
            </el-select>
          </el-form-item>
          <el-form-item label="目标星期">
            <el-radio-group v-model="adjustForm.day">
              <el-radio-button v-for="d in 5" :key="d" :value="d">
                周{{ ['一','二','三','四','五'][d-1] }}
              </el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="目标时段">
            <el-radio-group v-model="adjustForm.period">
              <el-radio-button value="morning">上午</el-radio-button>
              <el-radio-button value="afternoon">下午</el-radio-button>
              <el-radio-button value="evening">晚上</el-radio-button>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="adjustDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAdjust" :loading="submitLoading">
          <el-icon><Check /></el-icon>
          确认调整
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Refresh, Search, EditPen, Calendar, Check } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { scheduleApi } from '../api/index.js'
import '../assets/schedule-common.css'
import '../assets/design-tokens.css'

const loading = ref(false)
const submitLoading = ref(false)
const tableData = ref([])
const adjustDialogVisible = ref(false)
const currentEntry = ref(null)
const adjustForm = reactive({ week: 1, day: 1, period: 'morning' })
const pagination = reactive({ currentPage: 1, pageSize: 20, total: 0 })

const filterWeek = ref(null)
const filterDay = ref(null)
const filterKeyword = ref('')

const filteredTableData = computed(() => {
  let data = tableData.value
  if (filterWeek.value) {
    data = data.filter(row => row.week === filterWeek.value)
  }
  if (filterDay.value) {
    data = data.filter(row => row.day === filterDay.value)
  }
  if (filterKeyword.value) {
    const kw = filterKeyword.value.toLowerCase()
    data = data.filter(row => 
      (row.course_name || '').toLowerCase().includes(kw) ||
      (row.teacher_name || '').toLowerCase().includes(kw) ||
      (row.class_name || '').toLowerCase().includes(kw)
    )
  }
  return data
})

onMounted(() => loadData())

async function loadData() {
  loading.value = true
  try {
    const res = await scheduleApi.getResults({ page: pagination.currentPage, per_page: pagination.pageSize })
    tableData.value = res.results || []
    pagination.total = res.total || 0
  } catch (e) {
    console.error(e)
    ElMessage.error('加载课表数据失败')
  } finally {
    loading.value = false
  }
}

function handleFilter() {
  // computed 自动响应
}

function getPeriodType(period) {
  const map = { morning: 'warning', afternoon: 'success', evening: 'info' }
  return map[period] || ''
}

function getCourseTagColor(courseName) {
  const colors = [
    '#ecf5ff', '#f0f9eb', '#fdf6ec', '#fef0f0', '#f4f4f5', '#f9f0ff',
    '#e1f5fe', '#fff8e1', '#e8eaf6', '#f1f8e9'
  ]
  let hash = 0
  for (let i = 0; i < (courseName || '').length; i++) {
    hash = courseName.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

function openAdjust(row) {
  currentEntry.value = row
  adjustForm.week = row.week
  adjustForm.day = row.day
  adjustForm.period = row.period
  adjustDialogVisible.value = true
}

async function submitAdjust() {
  submitLoading.value = true
  try {
    await scheduleApi.adjust(currentEntry.value.id, {
      week: adjustForm.week,
      day: adjustForm.day,
      period: adjustForm.period,
    })
    ElMessage.success('调整成功')
    adjustDialogVisible.value = false
    loadData()
  } catch (e) {
    console.error(e)
    ElMessage.error('调整失败: ' + (e.response?.data?.error || e.message || '未知错误'))
  } finally {
    submitLoading.value = false
  }
}
</script>

<style scoped>
.adjust-page {
  padding: 24px;
  background: var(--bg-page);
  min-height: 100%;
}

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

.course-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.day-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: var(--color-primary-1);
  color: var(--color-primary-6);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
}

/* 调整弹窗 */
.adjust-dialog-content {
  padding: 4px 0;
}

.adjust-info {
  background: var(--color-neutral-1);
  padding: 16px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: var(--font-size-base);
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-label {
  color: var(--text-secondary);
  min-width: 80px;
}

.info-value {
  color: var(--text-primary);
  font-weight: var(--font-weight-medium);
}

.original-time {
  color: var(--color-error-6);
  font-weight: var(--font-weight-semibold);
}

/* 表格增强 */
:deep(.el-table) {
  border-radius: var(--radius-md);
  overflow: hidden;
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
