<template>
  <div class="schedule-page">
    <div class="schedule-toolbar">
      <h2 class="page-title"><span class="title-icon">📅</span>班级课表</h2>
      <div class="toolbar-controls">
        <div class="week-selector">
          <el-button class="week-nav-btn" :icon="ArrowLeft" @click="prevWeek" :disabled="currentWeek <= 1" circle />
          <span class="week-text">{{ weekTitle }}</span>
          <el-button class="week-nav-btn" :icon="ArrowRight" @click="nextWeek" :disabled="currentWeek >= 20" circle />
          <el-select v-model="currentWeek" @change="loadSchedule" style="width: 100px" size="small">
            <el-option v-for="w in weekOptions" :key="w" :label="`第${w}周`" :value="w" />
          </el-select>
          <el-button size="small" @click="goCurrentWeek">本周</el-button>
        </div>
        <el-select v-model="selectedClassId" placeholder="请选择班级" @change="loadSchedule" style="width: 200px" clearable>
          <el-option v-for="c in classList" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-button type="primary" @click="loadSchedule" :icon="Refresh" :loading="loading">刷新</el-button>
        <el-button @click="handlePrint" :icon="Printer">打印</el-button>
      </div>
    </div>

    <div v-if="!selectedClassId" class="empty-tip"><el-empty description="请选择班级查看课表" /></div>

    <div v-else-if="loading" class="loading-tip"><el-icon class="is-loading loading-icon" :size="40"><Loading /></el-icon><p>正在加载课表...</p></div>

    <div v-else>
      <div class="info-bar class-info" v-if="selectedClass">
        <span class="info-item"><span class="info-label">班级：</span><span class="info-value">{{ selectedClass.name }}</span></span>
        <span class="info-sep">|</span>
        <span class="info-item"><span class="info-label">人数：</span><span class="info-value">{{ selectedClass.student_count }}人</span></span>
        <span class="info-sep">|</span>
        <span class="info-item"><span class="info-label">学期：</span><span class="info-value">2026-2027 第一学期</span></span>
      </div>

      <div class="schedule-wrapper" ref="scheduleRef">
        <table class="weekly-schedule">
          <thead>
            <tr>
              <th class="period-col">节次</th>
              <th v-for="(day, idx) in weekDays" :key="idx" class="day-col"><div class="day-header"><span class="day-name">{{ day.name }}</span><span class="day-date">{{ day.date }}</span></div></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(section, sIdx) in periodSections" :key="sIdx">
              <tr v-for="(period, pIdx) in section.periods" :key="pIdx" :class="{ 'section-break': pIdx === section.periods.length - 1 }">
                <td class="period-label" :rowspan="section.periods.length" v-if="pIdx === 0"><div class="section-label" :style="{ color: section.color }">{{ section.label }}</div><div class="section-time">{{ section.time }}</div></td>
                <td class="schedule-cell" v-for="day in weekDays" :key="day.index">
                  <div v-if="getCellContent(day.index, period)" class="course-card" :style="getCardStyle(getCellContent(day.index, period))">
                    <div class="course-name">{{ getCellContent(day.index, period).course_name }}</div>
                    <div class="course-detail"><span class="icon">👤</span><span>{{ getCellContent(day.index, period).teacher_name }}</span></div>
                    <div class="course-weeks">{{ getCellContent(day.index, period).week_ranges }}周</div>
                    <div class="course-room"><span class="icon">🏫</span><span>{{ getCellContent(day.index, period).room_name }}</span></div>
                  </div>
                  <div v-else class="empty-slot"><span>-</span></div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading, Refresh, ArrowLeft, ArrowRight, Printer } from '@element-plus/icons-vue'
import { classApi, scheduleApi } from '../api/index.js'
import { useWeekSelector } from '../composables/useWeekSelector.js'
import { getCourseColor, printSchedule } from '../utils/scheduleHelpers.js'
import '../assets/schedule-common.css'
import '../assets/design-tokens.css'

const selectedClassId = ref(null)
const classList = ref([])
const courseData = ref([])
const loading = ref(false)
const scheduleRef = ref(null)

const { currentWeek, weekOptions, weekDays, weekTitle, prevWeek, nextWeek, goCurrentWeek } = useWeekSelector()

const periodSections = [
  { label: '上午', time: '08:00-11:40', periods: ['morning'], color: '#f7ba1e' },
  { label: '下午', time: '14:00-17:40', periods: ['afternoon'], color: '#0fc6c2' },
  { label: '晚上', time: '19:00-22:00', periods: ['evening'], color: '#3370ff' },
]

const selectedClass = computed(() => classList.value.find(c => c.id === selectedClassId.value) || null)

const cellMap = computed(() => {
  const map = {}
  courseData.value.forEach(c => { const key = `${c.day}-${c.period}`; if (!map[key]) map[key] = c })
  return map
})

function getCellContent(day, period) { return cellMap.value[`${day}-${period}`] || null }
function getCardStyle(cell) { const color = getCourseColor(cell.course_id, cell.course_type); return { '--course-border': color.border, '--course-bg': color.bg, '--course-text': color.text, background: color.bg, borderLeft: `3px solid ${color.border}`, color: color.text } }
function handlePrint() { printSchedule('班级课表') }

async function loadClassList() {
  try {
    const res = await classApi.getList({ page: 1, per_page: 100 })
    classList.value = res.classes || []
    if (classList.value.length > 0 && !selectedClassId.value) { selectedClassId.value = classList.value[0].id; loadSchedule() }
  } catch (e) { console.error(e) }
}

async function loadSchedule() {
  if (!selectedClassId.value) { courseData.value = []; return }
  loading.value = true
  try {
    const res = await scheduleApi.getWeekly({ class_id: selectedClassId.value, week: currentWeek.value })
    courseData.value = res.courses || []
    if (!courseData.value.length) ElMessage.warning('该班级本周暂无排课数据')
  } catch (e) { console.error(e); ElMessage.error('加载课表失败') } finally { loading.value = false }
}

onMounted(() => { loadClassList() })
</script>

<style scoped>.class-info { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }</style>
