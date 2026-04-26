/**
 * 周次选择 Composable
 */
import { ref, computed } from 'vue'
import { getWeekDays, getCurrentWeek, semesterConfig, formatDateShort, getWeekMonday } from '../utils/scheduleHelpers.js'

export function useWeekSelector(defaultSemesterStart = null) {
  const semesterStart = ref(new Date(defaultSemesterStart || semesterConfig.startDate))
  const currentWeek = ref(getCurrentWeek(semesterStart.value))
  
  const weekOptions = computed(() => {
    return Array.from({ length: semesterConfig.totalWeeks }, (_, i) => i + 1)
  })
  
  const weekDays = computed(() => getWeekDays(currentWeek.value, semesterStart.value))
  
  const weekTitle = computed(() => {
    if (weekDays.value.length === 0) return ''
    const first = weekDays.value[0]
    const last = weekDays.value[weekDays.value.length - 1]
    return `第${currentWeek.value}周 (${first.date} ~ ${last.date})`
  })
  
  function prevWeek() {
    if (currentWeek.value > 1) {
      currentWeek.value--
    }
  }
  
  function nextWeek() {
    if (currentWeek.value < semesterConfig.totalWeeks) {
      currentWeek.value++
    }
  }
  
  function goCurrentWeek() {
    currentWeek.value = getCurrentWeek(semesterStart.value)
  }
  
  return {
    currentWeek,
    semesterStart,
    weekOptions,
    weekDays,
    weekTitle,
    prevWeek,
    nextWeek,
    goCurrentWeek,
  }
}
