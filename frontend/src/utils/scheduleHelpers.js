/**
 * 课表通用工具函数
 */

export const lectureColors = [
  { bg: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)', border: '#1976d2', text: '#0d47a1', accent: '#1565c0' },
  { bg: 'linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%)', border: '#0097a7', text: '#006064', accent: '#00acc1' },
  { bg: 'linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)', border: '#7b1fa2', text: '#4a148c', accent: '#6a1b9a' },
  { bg: 'linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%)', border: '#3949ab', text: '#1a237e', accent: '#303f9f' },
  { bg: 'linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%)', border: '#0288d1', text: '#01579b', accent: '#039be5' },
  { bg: 'linear-gradient(135deg, #ede7f6 0%, #d1c4e9 100%)', border: '#512da8', text: '#311b92', accent: '#5e35b1' },
  { bg: 'linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%)', border: '#00796b', text: '#004d40', accent: '#00695c' },
  { bg: 'linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%)', border: '#558b2f', text: '#33691e', accent: '#689f38' },
  { bg: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)', border: '#388e3c', text: '#1b5e20', accent: '#2e7d32' },
  { bg: 'linear-gradient(135deg, #e3f2fd 0%, #d0e1fd 100%)', border: '#1e88e5', text: '#0d47a1', accent: '#1976d2' },
]

export const labColors = [
  { bg: 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)', border: '#f57c00', text: '#e65100', accent: '#ef6c00' },
  { bg: 'linear-gradient(135deg, #fbe9e7 0%, #ffccbc 100%)', border: '#d84315', text: '#bf360c', accent: '#e64a19' },
  { bg: 'linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%)', border: '#f9a825', text: '#f57f17', accent: '#fbc02d' },
  { bg: 'linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%)', border: '#c2185b', text: '#880e4f', accent: '#ad1457' },
  { bg: 'linear-gradient(135deg, #fffde7 0%, #fff9c4 100%)', border: '#f9a825', text: '#f57f17', accent: '#fdd835' },
  { bg: 'linear-gradient(135deg, #fff3e0 0%, #ffd8b5 100%)', border: '#ef6c00', text: '#e65100', accent: '#fb8c00' },
]

export const computerColors = [
  { bg: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)', border: '#388e3c', text: '#1b5e20', accent: '#2e7d32' },
  { bg: 'linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%)', border: '#00796b', text: '#004d40', accent: '#00695c' },
  { bg: 'linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%)', border: '#558b2f', text: '#33691e', accent: '#689f38' },
  { bg: 'linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%)', border: '#0097a7', text: '#006064', accent: '#00acc1' },
  { bg: 'linear-gradient(135deg, #e8f5e9 0%, #bce6c1 100%)', border: '#43a047', text: '#1b5e20', accent: '#2e7d32' },
  { bg: 'linear-gradient(135deg, #e0f2f1 0%, #a6d8d4 100%)', border: '#00897b', text: '#004d40', accent: '#00796b' },
]

export function getCourseColor(courseId, courseType = '普通授课') {
  let colorPool
  if (courseType === '实验' || courseType === '实验课') { colorPool = labColors }
  else if (courseType === '上机' || courseType === '上机课') { colorPool = computerColors }
  else { colorPool = lectureColors }
  const idx = (courseId || 0) % colorPool.length
  return colorPool[idx]
}

export const courseTypeMap = {
  '普通授课': { label: '授课', icon: '📖', color: '#1976d2' },
  '实验': { label: '实验', icon: '🧪', color: '#f57c00' },
  '上机': { label: '上机', icon: '💻', color: '#388e3c' },
}

export function getMonday(date) {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1)
  d.setDate(diff)
  d.setHours(0, 0, 0, 0)
  return d
}

export function getWeekMonday(weekNumber, semesterStart) {
  const d = new Date(semesterStart)
  d.setDate(d.getDate() + (weekNumber - 1) * 7)
  return d
}

export function formatDateShort(date) {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${month}-${day}`
}

export function getWeekDays(weekNumber = null, semesterStart = null) {
  const dayNames = ['星期一', '星期二', '星期三', '星期四', '星期五']
  const now = new Date()
  const startMonday = semesterStart ? getWeekMonday(weekNumber || getCurrentWeek(semesterStart), semesterStart) : getMonday(now)
  return dayNames.map((name, idx) => {
    const date = new Date(startMonday)
    date.setDate(date.getDate() + idx)
    return { index: idx + 1, name: `${name}`, date: formatDateShort(date), fullDate: date }
  })
}

export function getCurrentWeek(semesterStart) {
  const now = new Date()
  const start = new Date(semesterStart)
  const diffTime = now.getTime() - start.getTime()
  const diffWeeks = Math.floor(diffTime / (7 * 24 * 60 * 60 * 1000)) + 1
  return Math.max(1, diffWeeks)
}

export function printSchedule(title = '课表') {
  setTimeout(() => { window.print() }, 300)
}

export const semesterConfig = {
  name: '2026-2027 第一学期',
  startDate: '2026-09-07',
  totalWeeks: 20,
}
