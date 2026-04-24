<template>
  <div class="schedule-drag-drop">
    <h3 class="panel-title">拖拽调整课表</h3>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="source-card">
          <template #header>
            <div class="card-header">
              <span>待调整课程</span>
              <el-input
                v-model="searchQuery"
                placeholder="搜索课程..."
                prefix-icon="Search"
                size="small"
                style="width: 200px"
              />
            </div>
          </template>
          
          <div class="course-list">
            <div
              v-for="course in filteredCourses"
              :key="course.id"
              class="draggable-course"
              draggable="true"
              @dragstart="onDragStart($event, course)"
              @dragend="onDragEnd"
            >
              <div class="course-info">
                <div class="course-name">{{ course.courseName }}</div>
                <div class="course-details">
                  <span>教师：{{ course.teacherName }}</span>
                  <span>班级：{{ course.className }}</span>
                </div>
                <div class="course-time">
                  <el-tag size="small" :type="getPeriodType(course.period)">
                    {{ course.period }}
                  </el-tag>
                  <span>第{{ course.week }}周</span>
                  <span>星期{{ course.dayOfWeek }}</span>
                </div>
              </div>
              <div class="drag-handle">
                <el-icon><Rank /></el-icon>
              </div>
            </div>
            
            <el-empty
              v-if="filteredCourses.length === 0"
              description="没有可调整的课程"
            />
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="target-card">
          <template #header>
            <div class="card-header">
              <span>目标时段</span>
              <div class="target-controls">
                <el-select v-model="targetWeek" placeholder="选择周次" size="small">
                  <el-option
                    v-for="w in weekOptions"
                    :key="w"
                    :label="`第${w}周`"
                    :value="w"
                  />
                </el-select>
                <el-select v-model="targetDay" placeholder="选择星期" size="small">
                  <el-option
                    v-for="d in dayOptions"
                    :key="d.value"
                    :label="d.label"
                    :value="d.value"
                  />
                </el-select>
                <el-select v-model="targetPeriod" placeholder="选择时段" size="small">
                  <el-option label="上午" value="上午" />
                  <el-option label="下午" value="下午" />
                  <el-option label="晚上" value="晚上" />
                </el-select>
              </div>
            </div>
          </template>
          
          <div
            class="drop-zone"
            :class="{ 'is-drag-over': isDragOver }"
            @dragover.prevent="onDragOver"
            @dragleave="onDragLeave"
            @drop="onDrop"
          >
            <div class="drop-content" v-if="targetWeek && targetDay && targetPeriod">
              <div class="drop-header">
                <span class="target-info">
                  第{{ targetWeek }}周 / 星期{{ targetDay }} / {{ targetPeriod }}
                </span>
                <span class="conflict-info" v-if="conflictCount > 0">
                  <el-icon color="#f56c6c"><WarningFilled /></el-icon>
                  {{ conflictCount }}个冲突
                </span>
              </div>
              
              <div class="existing-courses">
                <div
                  v-for="course in existingCourses"
                  :key="course.id"
                  class="existing-course"
                >
                  <div class="course-name">{{ course.courseName }}</div>
                  <div class="course-details">
                    <span>教师：{{ course.teacherName }}</span>
                    <span>班级：{{ course.className }}</span>
                  </div>
                  <el-tag
                    v-if="isConflicting(draggedCourse, course)"
                    type="danger"
                    size="small"
                  >
                    冲突
                  </el-tag>
                </div>
              </div>
            </div>
            
            <el-empty
              v-else
              description="请选择目标时段"
            />
          </div>
          
          <div class="adjust-actions">
            <el-button
              type="primary"
              @click="confirmAdjustment"
              :disabled="!draggedCourse || !targetWeek || !targetDay || !targetPeriod || conflictCount > 0"
            >
              确认调整
            </el-button>
            <el-button @click="resetSelection">
              重置选择
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-dialog
      v-model="showConfirmDialog"
      title="确认调整"
      width="500px"
    >
      <p>确认将以下课程调整到指定时段吗？</p>
      <div class="confirm-info">
        <div class="info-row">
          <span class="label">课程：</span>
          <span>{{ confirmData?.courseName }}</span>
        </div>
        <div class="info-row">
          <span class="label">教师：</span>
          <span>{{ confirmData?.teacherName }}</span>
        </div>
        <div class="info-row">
          <span class="label">班级：</span>
          <span>{{ confirmData?.className }}</span>
        </div>
        <div class="info-row">
          <span class="label">调整到：</span>
          <span>第{{ targetWeek }}周 / 星期{{ targetDay }} / {{ targetPeriod }}</span>
        </div>
      </div>
      <template #footer>
        <el-button @click="showConfirmDialog = false">取消</el-button>
        <el-button type="primary" @click="executeAdjustment">确认</el-button>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="showConflictDialog"
      title="冲突提示"
      width="500px"
    >
      <el-alert
        title="存在冲突，无法调整"
        type="error"
        :closable="false"
        show-icon
      />
      <div class="conflict-details" v-if="conflicts.length > 0">
        <p>以下课程与当前调整冲突：</p>
        <ul>
          <li v-for="(conflict, index) in conflicts" :key="index">
            {{ conflict.courseName }} - {{ conflict.teacherName }} ({{ conflict.className }})
          </li>
        </ul>
      </div>
      <template #footer>
        <el-button type="primary" @click="showConflictDialog = false">我知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Rank, WarningFilled, Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  scheduleData: {
    type: Array,
    default: () => []
  },
  weekOptions: {
    type: Array,
    default: () => [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
  },
  dayOptions: {
    type: Array,
    default: () => [
      { value: 1, label: '星期一' },
      { value: 2, label: '星期二' },
      { value: 3, label: '星期三' },
      { value: 4, label: '星期四' },
      { value: 5, label: '星期五' }
    ]
  }
})

const emit = defineEmits(['adjust'])

const searchQuery = ref('')
const targetWeek = ref(null)
const targetDay = ref(null)
const targetPeriod = ref(null)
const draggedCourse = ref(null)
const isDragOver = ref(false)
const showConfirmDialog = ref(false)
const showConflictDialog = ref(false)
const conflicts = ref([])
const confirmData = ref(null)

const filteredCourses = computed(() => {
  if (!searchQuery.value) {
    return props.scheduleData
  }
  const query = searchQuery.value.toLowerCase()
  return props.scheduleData.filter(course =>
    course.courseName?.toLowerCase().includes(query) ||
    course.teacherName?.toLowerCase().includes(query) ||
    course.className?.toLowerCase().includes(query)
  )
})

const existingCourses = computed(() => {
  if (!targetWeek.value || !targetDay.value || !targetPeriod.value) {
    return []
  }
  return props.scheduleData.filter(course =>
    course.week === targetWeek.value &&
    course.dayOfWeek === targetDay.value &&
    course.period === targetPeriod.value
  )
})

const conflictCount = computed(() => {
  if (!draggedCourse.value || !existingCourses.value.length) {
    return 0
  }
  return existingCourses.value.filter(course =>
    isConflicting(draggedCourse.value, course)
  ).length
})

function onDragStart(event, course) {
  draggedCourse.value = course
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', course.id)
}

function onDragEnd() {
  draggedCourse.value = null
  isDragOver.value = false
}

function onDragOver(event) {
  isDragOver.value = true
  event.dataTransfer.dropEffect = 'move'
}

function onDragLeave() {
  isDragOver.value = false
}

function onDrop(event) {
  isDragOver.value = false
  if (!draggedCourse.value || !targetWeek.value || !targetDay.value || !targetPeriod.value) {
    ElMessage.warning('请完整选择目标时段')
    return
  }
  
  if (conflictCount.value > 0) {
    conflicts.value = existingCourses.value.filter(course =>
      isConflicting(draggedCourse.value, course)
    )
    showConflictDialog.value = true
    return
  }
  
  confirmData.value = draggedCourse.value
  showConfirmDialog.value = true
}

function isConflicting(course1, course2) {
  if (!course1 || !course2) return false
  
  return (
    course1.teacherId === course2.teacherId ||
    course1.classId === course2.classId ||
    course1.roomId === course2.roomId
  )
}

function confirmAdjustment() {
  showConfirmDialog.value = false
  executeAdjustment()
}

function executeAdjustment() {
  const adjustment = {
    courseId: draggedCourse.value.id,
    oldWeek: draggedCourse.value.week,
    oldDay: draggedCourse.value.dayOfWeek,
    oldPeriod: draggedCourse.value.period,
    newWeek: targetWeek.value,
    newDay: targetDay.value,
    newPeriod: targetPeriod.value
  }
  
  emit('adjust', adjustment)
  
  ElMessage.success('课表调整成功')
  resetSelection()
  showConfirmDialog.value = false
}

function resetSelection() {
  draggedCourse.value = null
  targetWeek.value = null
  targetDay.value = null
  targetPeriod.value = null
  conflicts.value = []
  confirmData.value = null
  isDragOver.value = false
}

function getPeriodType(period) {
  switch (period) {
    case '上午':
      return 'primary'
    case '下午':
      return 'success'
    case '晚上':
      return 'warning'
    default:
      return 'info'
  }
}
</script>

<style scoped>
.schedule-drag-drop {
  padding: 20px;
}

.panel-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #303133;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.course-list {
  max-height: 500px;
  overflow-y: auto;
}

.draggable-course {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  cursor: move;
  transition: all 0.2s;
}

.draggable-course:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.draggable-course.dragging {
  opacity: 0.5;
}

.course-info {
  flex: 1;
}

.course-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 4px;
}

.course-details {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
  display: flex;
  gap: 15px;
}

.course-time {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.drag-handle {
  color: #c0c4cc;
  font-size: 18px;
  cursor: move;
  padding: 8px;
}

.target-controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.drop-zone {
  min-height: 200px;
  border: 2px dashed #dcdfe6;
  border-radius: 4px;
  padding: 20px;
  transition: all 0.2s;
}

.drop-zone.is-drag-over {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.drop-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.target-info {
  font-weight: bold;
  color: #409eff;
}

.conflict-info {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #f56c6c;
  font-weight: bold;
}

.existing-courses {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.existing-course {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.existing-course .course-name {
  font-size: 14px;
}

.existing-course .course-details {
  font-size: 12px;
}

.adjust-actions {
  margin-top: 20px;
  display: flex;
  gap: 10px;
  justify-content: center;
}

.confirm-info {
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.info-row {
  display: flex;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  font-weight: bold;
  width: 80px;
  color: #606266;
}

.conflict-details {
  margin-top: 15px;
}

.conflict-details ul {
  padding-left: 20px;
}

.conflict-details li {
  color: #f56c6c;
  padding: 5px 0;
}
</style>
