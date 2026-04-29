/**
 * 课表通用工具函数
 */

/**
 * 课程卡片配色方案 - 按课程类型区分色系
 * 普通授课: 蓝/青/紫系列
 * 实验课: 橙/红系列
 * 上机课: 绿/靛系列
 * 基于 Material Design 配色，兼顾美观与可读性
 */

// 普通授课配色（10种）
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

// 实验课配色（6种）
export const labColors = [
  { bg: 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)', border: '#f57c00', text: '#e65100', accent: '#ef6c00' },
  { bg: 'linear-gradient(135deg, #fbe9e7 0%, #ffccbc 100%)', border: '#d84315', text: '#bf360c', accent: '#e64a19' },
  { bg: 'linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%)', border: '#f9a825', text: '#f57f17', accent: '#fbc02d' },
  { bg: 'linear-gradient(135deg, #fce4ec 0%, #f8bbd0 100%)', border: '#c2185b', text: '#880e4f', accent: '#ad1457' },
  { bg: 'linear-gradient(135deg, #fffde7 0%, #fff9c4 100%)', border: '#f9a825', text: '#f57f17', accent: '#fdd835' },
  { bg: 'linear-gradient(135deg, #fff3e0 0%, #ffd8b5 100%)', border: '#ef6c00', text: '#e65100', accent: '#fb8c00' },
]

// 上机课配色（6种）
export const computerColors = [
  { bg: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)', border: '#388e3c', text: '#1b5e20', accent: '#2e7d32' },
  { bg: 'linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%)', border: '#00796b', text: '#004d40', accent: '#00695c' },
  { bg: 'linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%)', border: '#558b2f', text: '#33691e', accent: '#689f38' },
  { bg: 'linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%)', border: '#0097a7', text: '#006064', accent: '#00acc1' },
  { bg: 'linear-gradient(135deg, #e8f5e9 0%, #bce6c1 100%)', border: '#43a047', text: '#1b5e20', accent: '#2e7d32' },
  { bg: 'linear-gradient(135deg, #e0f2f1 0%, #a6d8d4 100%)', border: '#00897b', text: '#004d40', accent: '#00796b' },
]

/**
 * 根据课程类型和ID获取配色
 * 支持按课程类型自动区分色系
 */
export function getCourseColor(courseId, courseType = '普通授课') {
  let colorPool
  if (courseType === '实验' || courseType === '实验课') {
    colorPool = labColors
  } else if (courseType === '上机' || courseType === '上机课') {
    colorPool = computerColors
  } else {
    colorPool = lectureColors
  }
  const idx = (courseId || 0) % colorPool.length
  return colorPool[idx]
}

/**
 * 课程类型映射表
 */
export const courseTypeMap = {
  '普通授课': { label: '授课', icon: '📖', color: '#1976d2' },
  '实验': { label: '实验', icon: '🧪', color: '#f57c00' },
  '上机': { label: '上机', icon: '💻', color: '#388e3c' },
}

/**
 * 获取当前日期所在周的周一日期
 * @param {Date} date 
 * @returns {Date}
 */
export function getMonday(date) {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day + (day === 0 ? -6 : 1)
  d.setDate(diff)
  d.setHours(0, 0, 0, 0)
  return d
}

/**
 * 获取指定周的周一日期
 * @param {number} weekNumber - 周次，从学期第一周开始计算
 * @param {Date} semesterStart - 学期开始日期（周一）
 * @returns {Date}
 */
export function getWeekMonday(weekNumber, semesterStart) {
  const d = new Date(semesterStart)
  d.setDate(d.getDate() + (weekNumber - 1) * 7)
  return d
}

/**
 * 格式化日期为 MM-DD 格式
 */
export function formatDateShort(date) {
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${month}-${day}`
}

/**
 * 获取当前周的日期信息
 * @param {number} weekNumber - 当前查看的周次
 * @param {Date} semesterStart - 学期开始日期
 * @returns {Array<{ index: number, name: string, date: string, fullDate: Date }>}
 */
export function getWeekDays(weekNumber = null, semesterStart = null) {
  const dayNames = ['星期一', '星期二', '星期三', '星期四', '星期五']
  const now = new Date()
  
  // 默认使用当前周
  const startMonday = semesterStart 
    ? getWeekMonday(weekNumber || getCurrentWeek(semesterStart), semesterStart)
    : getMonday(now)
  
  return dayNames.map((name, idx) => {
    const date = new Date(startMonday)
    date.setDate(date.getDate() + idx)
    return {
      index: idx + 1,
      name: `${name}`,
      date: formatDateShort(date),
      fullDate: date,
    }
  })
}

/**
 * 获取当前是第几周（相对于学期开始）
 */
export function getCurrentWeek(semesterStart) {
  const now = new Date()
  const start = new Date(semesterStart)
  const diffTime = now.getTime() - start.getTime()
  const diffWeeks = Math.floor(diffTime / (7 * 24 * 60 * 60 * 1000)) + 1
  return Math.max(1, diffWeeks)
}

/**
 * 打印课表
 * @param {string} title - 打印标题
 */
export function printSchedule(title = '课表') {
  // 等待页面渲染完成后再打印
  setTimeout(() => {
    window.print()
  }, 300)
}

/**
 * 学期配置
 */
export const semesterConfig = {
  name: '2026-2027 第一学期',
  startDate: '2026-09-07', // 默认学期开始日期
  totalWeeks: 20,
}
