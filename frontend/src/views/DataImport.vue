<template>
  <div class="data-import management-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-title">
        <el-icon :size="24" color="var(--color-primary-6)"><UploadFilled /></el-icon>
        <span>数据导入</span>
      </div>
      <p class="header-desc">导入教室、教师、班级和课程数据，支持单个或综合导入</p>
    </div>

    <el-row :gutter="16">
      <!-- 左侧：导入操作区 -->
      <el-col :xs="24" :md="16">
        <!-- 步骤指引 -->
        <el-card class="import-steps-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="card-header__title">
                <el-icon><Guide /></el-icon>
                <span>导入步骤</span>
              </div>
            </div>
          </template>
          <el-steps :active="currentStep" finish-status="success" align-center class="import-steps">
            <el-step title="选择方式" description="选择导入模式" />
            <el-step title="下载模板" description="下载Excel模板" />
            <el-step title="上传文件" description="拖拽或选择文件" />
            <el-step title="查看结果" description="确认导入数据" />
          </el-steps>
        </el-card>

        <!-- 导入表单 -->
        <el-card class="import-form-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="card-header__title">
                <el-icon><Upload /></el-icon>
                <span>数据导入</span>
              </div>
              <div class="card-header__actions">
                <el-button type="danger" plain @click="handleClearAll">
                  <el-icon><Delete /></el-icon>
                  <span>清空所有数据</span>
                </el-button>
              </div>
            </div>
          </template>

          <!-- 导入说明 -->
          <el-alert
            title="导入说明"
            type="info"
            :closable="false"
            class="import-alert"
          >
            <template #default>
              <p>1. 请先下载对应的导入模板，按照模板格式填写数据</p>
              <p>2. 支持 Excel (.xlsx) 格式文件</p>
              <p>3. 导入后将覆盖已有数据，请谨慎操作</p>
            </template>
          </el-alert>

          <el-form :model="importForm" label-position="top" class="import-form">
            <!-- 导入方式选择 -->
            <el-form-item label="导入方式">
              <el-radio-group v-model="importForm.mode" size="large">
                <el-radio-button value="single">
                  <el-icon><Files /></el-icon>
                  <span>单个导入</span>
                </el-radio-button>
                <el-radio-button value="comprehensive">
                  <el-icon><Box /></el-icon>
                  <span>综合导入（推荐）</span>
                </el-radio-button>
              </el-radio-group>
            </el-form-item>

            <!-- 数据类型选择 -->
            <el-form-item label="数据类型" v-if="importForm.mode === 'single'">
              <el-select v-model="importForm.type" placeholder="请选择数据类型" style="width: 100%" size="large">
                <el-option label="教室数据" value="room">
                  <span class="option-with-icon">
                    <el-icon><OfficeBuilding /></el-icon>
                    <span>教室数据</span>
                  </span>
                </el-option>
                <el-option label="教师数据" value="teacher">
                  <span class="option-with-icon">
                    <el-icon><UserFilled /></el-icon>
                    <span>教师数据</span>
                  </span>
                </el-option>
                <el-option label="班级数据" value="class">
                  <span class="option-with-icon">
                    <el-icon><Reading /></el-icon>
                    <span>班级数据</span>
                  </span>
                </el-option>
                <el-option label="课程数据" value="course">
                  <span class="option-with-icon">
                    <el-icon><Notebook /></el-icon>
                    <span>课程数据</span>
                  </span>
                </el-option>
              </el-select>
            </el-form-item>

            <!-- 综合导入说明 -->
            <el-alert
              v-if="importForm.mode === 'comprehensive'"
              title="综合导入说明"
              type="success"
              :closable="false"
              class="comprehensive-alert"
            >
              <template #default>
                <p><el-icon><Box /></el-icon> 一键导入所有数据（教室、教师、班级、课程、节假日）</p>
                <p><el-icon><Document /></el-icon> 请使用包含多个工作表的综合Excel文件</p>
                <p><el-icon><Warning /></el-icon> 导入顺序：教室 → 教师 → 班级 → 课程</p>
              </template>
            </el-alert>

            <!-- 下载模板 -->
            <el-form-item label="下载模板" class="download-section">
              <el-button @click="handleDownloadTemplate" :disabled="!importForm.type" v-if="importForm.mode === 'single'">
                <el-icon><Download /></el-icon>
                下载 {{ typeLabel }} 模板
              </el-button>
              <el-button @click="handleDownloadComprehensiveTemplate" v-else>
                <el-icon><Download /></el-icon>
                下载综合模板（含所有数据）
              </el-button>
            </el-form-item>

            <!-- 上传文件 -->
            <el-form-item label="上传文件" class="upload-section">
              <el-upload
                ref="uploadRef"
                :auto-upload="false"
                :limit="1"
                :on-change="handleFileChange"
                :on-remove="handleFileRemove"
                accept=".xlsx,.xls"
                drag
                class="upload-area"
              >
                <el-icon class="upload-icon"><UploadFilled /></el-icon>
                <div class="el-upload__text">
                  将文件拖到此处，或<em>点击上传</em>
                </div>
                <template #tip>
                  <div class="el-upload__tip">仅支持 .xlsx/.xls 格式文件</div>
                </template>
              </el-upload>
            </el-form-item>

            <!-- 提交按钮 -->
            <div class="form-actions">
              <el-button
                type="primary"
                size="large"
                @click="handleUpload"
                :loading="uploadLoading"
                :disabled="!selectedFile"
              >
                <el-icon><Upload /></el-icon>
                {{ importForm.mode === 'comprehensive' ? '一键导入所有数据' : '开始导入' }}
              </el-button>
              <el-button size="large" @click="handleReset">
                <el-icon><RefreshLeft /></el-icon>
                重置
              </el-button>
            </div>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：导入结果区 -->
      <el-col :xs="24" :md="8">
        <el-card v-if="importResult" class="result-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="card-header__title">
                <el-icon v-if="importResult.success"><CircleCheckFilled color="var(--color-success-6)" /></el-icon>
                <el-icon v-else><CircleCloseFilled color="var(--color-error-6)" /></el-icon>
                <span>导入结果</span>
              </div>
            </div>
          </template>

          <!-- 综合导入结果 -->
          <div v-if="importForm.mode === 'comprehensive' && importResult.success">
            <el-descriptions :column="1" border>
              <el-descriptions-item label="教室数据">
                <span class="result-badge">新增 {{ importResult.details.room.imported }}</span>
                <span class="result-badge result-badge--update">更新 {{ importResult.details.room.updated }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="教师数据">
                <span class="result-badge">新增 {{ importResult.details.teacher.imported }}</span>
                <span class="result-badge result-badge--update">更新 {{ importResult.details.teacher.updated }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="班级数据">
                <span class="result-badge">新增 {{ importResult.details.class.imported }}</span>
                <span class="result-badge result-badge--update">更新 {{ importResult.details.class.updated }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="节假日数据">
                <span class="result-badge">导入 {{ importResult.details.holiday.imported }} 天</span>
              </el-descriptions-item>
              <el-descriptions-item label="课程数据">
                <span class="result-badge">新增 {{ importResult.details.course.imported }}</span>
                <span class="result-badge result-badge--update">更新 {{ importResult.details.course.updated }}</span>
              </el-descriptions-item>
            </el-descriptions>
            <div class="total-count">
              <el-icon><SuccessFilled /></el-icon>
              <span>总计导入 <strong>{{ importResult.count }}</strong> 条数据</span>
            </div>
          </div>

          <!-- 单个导入结果 -->
          <div v-else-if="importResult.success" class="single-result">
            <el-result icon="success" :title="'成功导入 ' + importResult.count + ' 条数据'" />
          </div>

          <!-- 错误信息 -->
          <el-alert
            v-if="importResult.errors"
            type="error"
            :closable="false"
            style="margin-top: 16px"
          >
            <template #default>
              部分数据导入失败：{{ importResult.errors }}
            </template>
          </el-alert>
        </el-card>

        <!-- 快速操作 -->
        <el-card class="quick-actions-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <div class="card-header__title">
                <el-icon><Operation /></el-icon>
                <span>快速操作</span>
              </div>
            </div>
          </template>
          <div class="quick-actions">
            <div class="quick-action-item" @click="$router.push('/rooms')">
              <el-icon><OfficeBuilding /></el-icon>
              <span>查看教室</span>
            </div>
            <div class="quick-action-item" @click="$router.push('/teachers')">
              <el-icon><UserFilled /></el-icon>
              <span>查看教师</span>
            </div>
            <div class="quick-action-item" @click="$router.push('/classes')">
              <el-icon><Reading /></el-icon>
              <span>查看班级</span>
            </div>
            <div class="quick-action-item" @click="$router.push('/courses')">
              <el-icon><Notebook /></el-icon>
              <span>查看课程</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 重新排课确认对话框 -->
    <el-dialog
      v-model="rescheduleDialogVisible"
      title="是否立即执行排课？"
      width="420px"
      align-center
    >
      <div class="schedule-confirm">
        <el-icon :size="48" color="var(--color-warning-5)"><Clock /></el-icon>
        <p class="confirm-text">数据导入成功，是否立即执行排课？</p>
      </div>
      <template #footer>
        <el-button @click="rescheduleDialogVisible = false">稍后排课</el-button>
        <el-button type="primary" @click="handleRunSchedule" :loading="scheduleLoading">
          <el-icon><VideoPlay /></el-icon>
          立即排课
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  UploadFilled, Upload, Delete, Guide, Files, Box, Download,
  RefreshLeft, CircleCheckFilled, CircleCloseFilled, SuccessFilled,
  Operation, OfficeBuilding, UserFilled, Reading, Notebook,
  Document, Warning, Clock, VideoPlay
} from '@element-plus/icons-vue'
import { importApi, scheduleApi } from '../api/index.js'
import '../assets/management-common.css'
import '../assets/design-tokens.css'

const uploadRef = ref(null)
const uploadLoading = ref(false)
const selectedFile = ref(null)
const importResult = ref(null)
const rescheduleDialogVisible = ref(false)
const scheduleLoading = ref(false)
const currentStep = ref(0)

const importForm = reactive({
  mode: 'comprehensive',
  type: ''
})

const typeMap = {
  room: '教室',
  teacher: '教师',
  class: '班级',
  course: '课程'
}

const typeLabel = computed(() => typeMap[importForm.type] || '')

const handleModeChange = () => {
  importForm.type = ''
  currentStep.value = 1
}

const handleDownloadTemplate = async () => {
  try {
    const response = await importApi.getTemplate(importForm.type)
    const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${typeLabel.value}_导入模板.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
    currentStep.value = 2
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  }
}

const handleDownloadComprehensiveTemplate = async () => {
  try {
    const response = await importApi.getTemplate('comprehensive')
    const blob = new Blob([response], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = '综合导入模板.xlsx'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('综合模板下载成功')
    currentStep.value = 2
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
  currentStep.value = 3
}

const handleFileRemove = () => {
  selectedFile.value = null
  importResult.value = null
  currentStep.value = 2
}

const handleUpload = async () => {
  if (importForm.mode === 'single' && !importForm.type) {
    ElMessage.warning('请选择数据类型')
    return
  }
  if (!selectedFile.value) {
    ElMessage.warning('请选择上传文件')
    return
  }

  uploadLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('type', importForm.mode === 'comprehensive' ? 'comprehensive' : importForm.type)

    const res = await importApi.upload(formData)
    importResult.value = {
      success: true,
      count: res.count || 0,
      details: res.details,
      errors: res.errors
    }

    if (importForm.mode === 'comprehensive') {
      ElMessage.success(`综合导入成功！共导入 ${res.count || 0} 条数据`)
    } else {
      ElMessage.success(`导入成功，共导入 ${res.count || 0} 条数据`)
    }

    currentStep.value = 4

    if (importForm.type === 'course' || importForm.type === 'class' || importForm.type === 'teacher' || importForm.mode === 'comprehensive') {
      rescheduleDialogVisible.value = true
    }
  } catch (error) {
    console.error('导入失败:', error)
    importResult.value = {
      success: false,
      errors: error.message || '导入失败'
    }
    ElMessage.error('导入失败')
  } finally {
    uploadLoading.value = false
  }
}

const handleRunSchedule = async () => {
  scheduleLoading.value = true
  try {
    const res = await scheduleApi.run({ start_date: '2026-09-07' })
    ElMessage.success(`排课完成！成功 ${res.success_count || 0} 条`)
    rescheduleDialogVisible.value = false
  } catch (error) {
    console.error('排课失败:', error)
    ElMessage.error('排课失败：' + (error.message || '未知错误'))
  } finally {
    scheduleLoading.value = false
  }
}

const handleClearAll = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有数据吗？此操作不可恢复！包括教室、教师、班级、课程、课表记录、节假日等所有数据。',
      '清空数据确认',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    const res = await scheduleApi.clearAll()
    ElMessage.success('所有数据已清空')
    importResult.value = null
    currentStep.value = 0
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清空数据失败:', error)
      ElMessage.error('清空数据失败')
    }
  }
}

const handleReset = () => {
  importForm.type = ''
  importForm.mode = 'comprehensive'
  selectedFile.value = null
  importResult.value = null
  currentStep.value = 0
  uploadRef.value?.clearFiles()
}
</script>

<style scoped>
.data-import {
  padding: var(--space-6);
  background: var(--bg-page);
  min-height: 100%;
}

/* 页面头部 */
.page-header {
  margin-bottom: var(--space-6);
  padding-bottom: var(--space-4);
  border-bottom: 1px solid var(--border-light);
}

.header-title {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
}

.header-desc {
  margin-top: var(--space-2);
  font-size: var(--font-size-base);
  color: var(--text-secondary);
}

/* 步骤卡片 */
.import-steps-card {
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-light);
  margin-bottom: var(--space-4);
}

.import-steps {
  padding: var(--space-4) 0;
}

/* 导入表单卡片 */
.import-form-card {
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-light);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-3);
}

.card-header__title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.import-alert {
  margin-bottom: var(--space-5);
  border-radius: var(--radius-lg);
}

.comprehensive-alert {
  margin-bottom: var(--space-5);
  border-radius: var(--radius-lg);
}

.comprehensive-alert :deep(.el-alert__content p) {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin: var(--space-1) 0;
}

/* 单选按钮组增强 */
:deep(.el-radio-button__inner) {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-5);
  border-radius: var(--radius-md);
}

/* 下拉选项图标 */
.option-with-icon {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

/* 下载区域 */
.download-section {
  margin-bottom: var(--space-5);
}

/* 上传区域 */
.upload-section {
  margin-bottom: var(--space-5);
}

.upload-area {
  width: 100%;
}

.upload-icon {
  font-size: 48px;
  color: var(--color-neutral-4);
  margin-bottom: var(--space-3);
}

:deep(.el-upload-dragger) {
  border-radius: var(--radius-lg);
  border: 2px dashed var(--border-base);
  transition: all var(--duration-base) var(--ease-out);
  padding: var(--space-10);
}

:deep(.el-upload-dragger:hover) {
  border-color: var(--color-primary-4);
  background: var(--color-primary-1);
}

:deep(.el-upload__tip) {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  margin-top: var(--space-2);
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-top: var(--space-4);
  border-top: 1px solid var(--border-light);
}

/* 结果卡片 */
.result-card {
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-light);
  margin-bottom: var(--space-4);
}

.result-badge {
  display: inline-block;
  background: var(--color-success-1);
  color: var(--color-success-7);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  margin-right: var(--space-2);
}

.result-badge--update {
  background: var(--color-info-1);
  color: var(--color-info-7);
}

.total-count {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-4);
  padding: var(--space-3);
  background: var(--color-success-1);
  border-radius: var(--radius-md);
  color: var(--color-success-7);
  font-weight: var(--font-weight-semibold);
}

.single-result {
  text-align: center;
  padding: var(--space-4) 0;
}

/* 快速操作卡片 */
.quick-actions-card {
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-light);
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

.quick-action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-base) var(--ease-out);
  background: var(--color-neutral-1);
}

.quick-action-item:hover {
  background: var(--color-primary-1);
  transform: translateY(-2px);
}

.quick-action-item .el-icon {
  font-size: 24px;
  color: var(--color-primary-6);
}

.quick-action-item span {
  font-size: var(--font-size-sm);
  color: var(--text-regular);
}

/* 排课确认对话框 */
.schedule-confirm {
  text-align: center;
  padding: var(--space-4) 0;
}

.confirm-text {
  margin-top: var(--space-3);
  font-size: var(--font-size-lg);
  color: var(--text-primary);
}

/* 响应式 */
@media (max-width: 768px) {
  .data-import {
    padding: var(--space-4);
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions :deep(.el-button) {
    width: 100%;
  }

  .quick-actions {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
