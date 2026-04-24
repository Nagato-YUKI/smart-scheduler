<template>
  <div class="export-panel">
    <h3 class="panel-title">导出与打印</h3>
    
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="export-card">
          <template #header>
            <div class="card-header">
              <span>导出Excel</span>
            </div>
          </template>
          
          <div class="export-options">
            <el-form label-width="100px">
              <el-form-item label="导出类型">
                <el-select v-model="exportType" style="width: 100%">
                  <el-option label="完整课表" value="full" />
                  <el-option label="班级课表" value="class" />
                  <el-option label="教师课表" value="teacher" />
                  <el-option label="教室课表" value="room" />
                  <el-option label="课时统计" value="statistics" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="教学班" v-if="exportType === 'class'">
                <el-select
                  v-model="selectedClassId"
                  placeholder="请选择教学班"
                  style="width: 100%"
                  clearable
                >
                  <el-option
                    v-for="cls in classList"
                    :key="cls.id"
                    :label="cls.name"
                    :value="cls.id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="教师" v-if="exportType === 'teacher'">
                <el-select
                  v-model="selectedTeacherId"
                  placeholder="请选择教师"
                  style="width: 100%"
                  clearable
                >
                  <el-option
                    v-for="teacher in teacherList"
                    :key="teacher.id"
                    :label="teacher.name"
                    :value="teacher.id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="教室" v-if="exportType === 'room'">
                <el-select
                  v-model="selectedRoomId"
                  placeholder="请选择教室"
                  style="width: 100%"
                  clearable
                >
                  <el-option
                    v-for="room in roomList"
                    :key="room.id"
                    :label="room.name"
                    :value="room.id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="周次范围">
                <el-row :gutter="10">
                  <el-col :span="11">
                    <el-input-number
                      v-model="startWeek"
                      :min="1"
                      :max="totalWeeks"
                      placeholder="起始周"
                      style="width: 100%"
                    />
                  </el-col>
                  <el-col :span="2" class="text-center">-</el-col>
                  <el-col :span="11">
                    <el-input-number
                      v-model="endWeek"
                      :min="1"
                      :max="totalWeeks"
                      placeholder="结束周"
                      style="width: 100%"
                    />
                  </el-col>
                </el-row>
              </el-form-item>
            </el-form>
            
            <div class="export-actions">
              <el-button
                type="primary"
                @click="handleExport"
                :loading="exporting"
                size="large"
              >
                <el-icon v-if="!exporting"><Download /></el-icon>
                导出Excel
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card class="print-card">
          <template #header>
            <div class="card-header">
              <span>打印课表</span>
            </div>
          </template>
          
          <div class="print-options">
            <el-form label-width="100px">
              <el-form-item label="打印类型">
                <el-select v-model="printType" style="width: 100%">
                  <el-option label="完整课表" value="full" />
                  <el-option label="班级课表" value="class" />
                  <el-option label="教师课表" value="teacher" />
                  <el-option label="教室课表" value="room" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="教学班" v-if="printType === 'class'">
                <el-select
                  v-model="selectedClassId"
                  placeholder="请选择教学班"
                  style="width: 100%"
                  clearable
                >
                  <el-option
                    v-for="cls in classList"
                    :key="cls.id"
                    :label="cls.name"
                    :value="cls.id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="教师" v-if="printType === 'teacher'">
                <el-select
                  v-model="selectedTeacherId"
                  placeholder="请选择教师"
                  style="width: 100%"
                  clearable
                >
                  <el-option
                    v-for="teacher in teacherList"
                    :key="teacher.id"
                    :label="teacher.name"
                    :value="teacher.id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="教室" v-if="printType === 'room'">
                <el-select
                  v-model="selectedRoomId"
                  placeholder="请选择教室"
                  style="width: 100%"
                  clearable
                >
                  <el-option
                    v-for="room in roomList"
                    :key="room.id"
                    :label="room.name"
                    :value="room.id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="周次范围">
                <el-row :gutter="10">
                  <el-col :span="11">
                    <el-input-number
                      v-model="printStartWeek"
                      :min="1"
                      :max="totalWeeks"
                      placeholder="起始周"
                      style="width: 100%"
                    />
                  </el-col>
                  <el-col :span="2" class="text-center">-</el-col>
                  <el-col :span="11">
                    <el-input-number
                      v-model="printEndWeek"
                      :min="1"
                      :max="totalWeeks"
                      placeholder="结束周"
                      style="width: 100%"
                    />
                  </el-col>
                </el-row>
              </el-form-item>
              
              <el-form-item label="打印方向">
                <el-radio-group v-model="printOrientation">
                  <el-radio-button label="landscape">横向</el-radio-button>
                  <el-radio-button label="portrait">纵向</el-radio-button>
                </el-radio-group>
              </el-form-item>
            </el-form>
            
            <div class="print-actions">
              <el-button
                type="success"
                @click="handlePrint"
                :loading="printing"
                size="large"
              >
                <el-icon v-if="!printing"><Printer /></el-icon>
                打印课表
              </el-button>
            </div>
          </div>
        </el-card>
        
        <el-card class="preview-card" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <span>打印预览</span>
            </div>
          </template>
          
          <div class="preview-container" v-if="scheduleData.length > 0">
            <table class="preview-table">
              <thead>
                <tr>
                  <th>周次</th>
                  <th>星期一</th>
                  <th>星期二</th>
                  <th>星期三</th>
                  <th>星期四</th>
                  <th>星期五</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="week in previewWeeks" :key="week">
                  <td class="week-cell">第{{ week }}周</td>
                  <td v-for="day in [1, 2, 3, 4, 5]" :key="day" class="day-cell">
                    <div
                      v-for="course in getCourses(week, day)"
                      :key="course.id"
                      class="preview-course"
                      :class="`period-${course.period}`"
                    >
                      <div class="course-name">{{ course.courseName }}</div>
                      <div class="course-info">{{ course.teacherName }}</div>
                      <div class="course-info">{{ course.className }}</div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <el-empty v-else description="暂无课表数据" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Download, Printer } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  scheduleData: {
    type: Array,
    default: () => []
  },
  classList: {
    type: Array,
    default: () => []
  },
  teacherList: {
    type: Array,
    default: () => []
  },
  roomList: {
    type: Array,
    default: () => []
  },
  totalWeeks: {
    type: Number,
    default: 16
  }
})

const emit = defineEmits(['export', 'print'])

const exportType = ref('full')
const printType = ref('full')
const selectedClassId = ref(null)
const selectedTeacherId = ref(null)
const selectedRoomId = ref(null)
const startWeek = ref(1)
const endWeek = ref(props.totalWeeks)
const printStartWeek = ref(1)
const printEndWeek = ref(props.totalWeeks)
const printOrientation = ref('landscape')
const exporting = ref(false)
const printing = ref(false)

const previewWeeks = computed(() => {
  const start = Math.min(printStartWeek.value, printEndWeek.value)
  const end = Math.max(printStartWeek.value, printEndWeek.value)
  const weeks = []
  for (let i = start; i <= end; i++) {
    weeks.push(i)
  }
  return weeks
})

function getCourses(week, day) {
  return props.scheduleData.filter(course =>
    course.week === week && course.dayOfWeek === day
  )
}

async function handleExport() {
  if (exportType.value !== 'full' && exportType.value !== 'statistics') {
    if (!getSelectedId()) {
      ElMessage.warning('请选择对应的选项')
      return
    }
  }
  
  exporting.value = true
  try {
    const params = {
      type: exportType.value,
      classId: selectedClassId.value,
      teacherId: selectedTeacherId.value,
      roomId: selectedRoomId.value,
      startWeek: startWeek.value,
      endWeek: endWeek.value
    }
    
    emit('export', params)
    ElMessage.success('导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
  } finally {
    exporting.value = false
  }
}

async function handlePrint() {
  if (printType.value !== 'full') {
    if (!getSelectedId()) {
      ElMessage.warning('请选择对应的选项')
      return
    }
  }
  
  printing.value = true
  try {
    const params = {
      type: printType.value,
      classId: selectedClassId.value,
      teacherId: selectedTeacherId.value,
      roomId: selectedRoomId.value,
      startWeek: printStartWeek.value,
      endWeek: printEndWeek.value,
      orientation: printOrientation.value
    }
    
    emit('print', params)
    window.print()
    ElMessage.success('打印成功')
  } catch (error) {
    ElMessage.error('打印失败')
  } finally {
    printing.value = false
  }
}

function getSelectedId() {
  switch (exportType.value) {
    case 'class':
      return selectedClassId.value
    case 'teacher':
      return selectedTeacherId.value
    case 'room':
      return selectedRoomId.value
    default:
      return null
  }
}

watch(exportType, () => {
  selectedClassId.value = null
  selectedTeacherId.value = null
  selectedRoomId.value = null
})

watch(printType, () => {
  selectedClassId.value = null
  selectedTeacherId.value = null
  selectedRoomId.value = null
})
</script>

<style scoped>
.export-panel {
  padding: 20px;
}

.panel-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #303133;
}

.card-header {
  font-weight: bold;
}

.export-options,
.print-options {
  padding: 10px 0;
}

.export-actions,
.print-actions {
  margin-top: 20px;
  text-align: center;
}

.text-center {
  text-align: center;
}

.preview-container {
  max-height: 400px;
  overflow: auto;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.preview-table th,
.preview-table td {
  border: 1px solid #dcdfe6;
  padding: 8px;
  text-align: center;
  vertical-align: top;
}

.preview-table th {
  background-color: #409eff;
  color: #fff;
  font-weight: bold;
}

.week-cell {
  background-color: #f5f7fa;
  font-weight: bold;
  writing-mode: vertical-lr;
  letter-spacing: 2px;
}

.period-上午 {
  background-color: #ecf5ff;
}

.period-下午 {
  background-color: #f0f9ff;
}

.period-晚上 {
  background-color: #fdf6ec;
}

.preview-course {
  padding: 5px;
  margin-bottom: 5px;
  border-radius: 3px;
  border-left: 3px solid #409eff;
}

.course-name {
  font-weight: bold;
  margin-bottom: 2px;
}

.course-info {
  font-size: 11px;
  color: #606266;
}
</style>
