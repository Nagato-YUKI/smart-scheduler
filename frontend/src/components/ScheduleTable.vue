<template>
  <div class="schedule-table">
    <div class="table-wrapper">
      <table class="schedule-grid">
        <thead>
          <tr>
            <th class="week-header">周次</th>
            <th v-for="day in weekdays" :key="day.value" class="day-header">{{ day.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="week in visibleWeeks" :key="week" class="week-row">
            <td class="week-cell"><span class="week-number">第{{ week }}周</span></td>
            <td v-for="day in weekdays" :key="day.value" class="schedule-cell">
              <div v-for="course in getCourses(week, day.value)" :key="course.id" class="course-card" :class="{ 'is-evening': course.period === '晚上', 'is-afternoon': course.period === '下午', 'is-morning': course.period === '上午' }">
                <div class="course-name">{{ course.courseName }}</div>
                <div class="course-teacher" v-if="showTeacher">{{ course.teacher }}</div>
                <div class="course-room" v-if="showRoom">{{ course.room }}</div>
                <div class="course-period"><span class="period-badge">{{ course.period }}</span></div>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="pagination-controls" v-if="totalWeeks > 5">
      <el-button-group>
        <el-button @click="changeRange(-1)" :disabled="startWeek <= 1">上一组</el-button>
        <el-button>第 {{ startWeek }}-{{ endWeek }} 周</el-button>
        <el-button @click="changeRange(1)" :disabled="endWeek >= totalWeeks">下一组</el-button>
      </el-button-group>
      <div class="quick-jump">
        <span>快速跳转：</span>
        <el-select v-model="currentStartWeek" @change="onWeekChange" size="small">
          <el-option v-for="start in weekRanges" :key="start" :label="`第 ${start}-${Math.min(start + weeksPerView - 1, totalWeeks)} 周`" :value="start" />
        </el-select>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  scheduleData: { type: Array, default: () => [] },
  totalWeeks: { type: Number, default: 16 },
  weeksPerView: { type: Number, default: 5 },
  showTeacher: { type: Boolean, default: true },
  showRoom: { type: Boolean, default: true }
})

const weekdays = [
  { value: 1, label: '星期一' },
  { value: 2, label: '星期二' },
  { value: 3, label: '星期三' },
  { value: 4, label: '星期四' },
  { value: 5, label: '星期五' }
]

const startWeek = ref(1)
const endWeek = computed(() => Math.min(startWeek.value + props.weeksPerView - 1, props.totalWeeks))
const visibleWeeks = computed(() => { const weeks = []; for (let w = startWeek.value; w <= endWeek.value; w++) weeks.push(w); return weeks })
const weekRanges = computed(() => { const ranges = []; for (let i = 1; i <= props.totalWeeks; i += props.weeksPerView) ranges.push(i); return ranges })
const currentStartWeek = ref(1)

function getCourses(week, dayOfWeek) {
  return props.scheduleData.filter(course => {
    const weekMatch = course.week === week || (course.startWeek && course.endWeek && week >= course.startWeek && week <= course.endWeek)
    return weekMatch && course.dayOfWeek === dayOfWeek
  })
}

function changeRange(direction) {
  const newStart = startWeek.value + direction * props.weeksPerView
  if (newStart >= 1 && newStart <= props.totalWeeks) { startWeek.value = newStart; currentStartWeek.value = newStart }
}

function onWeekChange(value) { startWeek.value = value }
</script>

<style scoped>
.schedule-table { background: #fff; border-radius: 8px; padding: 20px; box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1); }
.table-wrapper { overflow-x: auto; }
.schedule-grid { width: 100%; border-collapse: collapse; table-layout: fixed; }
.week-header { width: 80px; background-color: #409EFF; color: #fff; padding: 12px 8px; font-weight: bold; border: 1px solid #dcdfe6; }
.day-header { background-color: #409EFF; color: #fff; padding: 12px 8px; font-weight: bold; border: 1px solid #dcdfe6; }
.week-row { min-height: 100px; }
.week-cell { background-color: #f5f7fa; border: 1px solid #dcdfe6; padding: 8px; text-align: center; vertical-align: middle; font-weight: bold; color: #606266; }
.week-number { writing-mode: vertical-lr; letter-spacing: 2px; }
.schedule-cell { border: 1px solid #dcdfe6; padding: 8px; vertical-align: top; min-height: 100px; background-color: #fafafa; }
.course-card { background: #fff; border-radius: 4px; padding: 8px; margin-bottom: 8px; border-left: 3px solid #409EFF; box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); font-size: 12px; }
.course-card.is-evening { border-left-color: #e6a23c; background-color: #fdf6ec; }
.course-card.is-afternoon { border-left-color: #67c23a; background-color: #f0f9ff; }
.course-card.is-morning { border-left-color: #409EFF; background-color: #ecf5ff; }
.course-name { font-weight: bold; color: #303133; margin-bottom: 4px; font-size: 13px; }
.course-teacher { color: #606266; font-size: 12px; margin-bottom: 2px; }
.course-room { color: #909399; font-size: 12px; margin-bottom: 4px; }
.course-period { margin-top: 4px; }
.period-badge { display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 11px; color: #fff; background-color: #409EFF; }
.is-evening .period-badge { background-color: #e6a23c; }
.is-afternoon .period-badge { background-color: #67c23a; }
.is-morning .period-badge { background-color: #409EFF; }
.pagination-controls { margin-top: 20px; display: flex; justify-content: space-between; align-items: center; padding-top: 16px; border-top: 1px solid #ebeef5; }
.quick-jump { display: flex; align-items: center; gap: 8px; color: #606266; font-size: 14px; }
</style>
