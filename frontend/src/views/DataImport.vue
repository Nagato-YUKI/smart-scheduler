<template>
  <div class="data-import management-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>数据导入</span>
        </div>
      </template>

      <el-alert
        title="导入说明"
        type="info"
        :closable="false"
        style="margin-bottom: 20px"
      >
        <p>1. 请先下载对应的导入模板，按照模板格式填写数据</p>
        <p>2. 支持 Excel (.xlsx) 格式文件</p>
        <p>3. 导入后将覆盖已有数据，请谨慎操作</p>
      </el-alert>

      <el-form :model="importForm" label-width="100px">
        <el-form-item label="数据类型">
          <el-select v-model="importForm.type" placeholder="请选择数据类型" style="width: 100%">
            <el-option label="教室数据" value="room" />
            <el-option label="教师数据" value="teacher" />
            <el-option label="班级数据" value="class" />
            <el-option label="课程数据" value="course" />
          </el-select>
        </el-form-item>

        <el-form-item label="下载模板">
          <el-button @click="handleDownloadTemplate" :disabled="!importForm.type">
            下载 {{ typeLabel }} 模板
          </el-button>
        </el-form-item>

        <el-form-item label="上传文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            accept=".xlsx,.xls"
            drag
            style="width: 100%"
          >
            <div class="upload-area">
              <div style="font-size: 48px; color: #c0c4cc">+</div>
              <div class="el-upload__text">
                将文件拖到此处，或<em>点击上传</em>
              </div>
            </div>
            <template #tip>
              <div class="el-upload__tip">仅支持 .xlsx 格式文件</div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="handleUpload"
            :loading="uploadLoading"
            :disabled="!selectedFile"
          >
            开始导入
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-card v-if="importResult" style="margin-top: 20px">
        <template #header>
          <span>导入结果</span>
        </template>
        <p>导入状态：{{ importResult.success ? '成功' : '失败' }}</p>
        <p v-if="importResult.success">成功导入 {{ importResult.count }} 条数据</p>
        <p v-if="importResult.errors">错误信息：{{ importResult.errors }}</p>
      </el-card>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { importApi } from '../api/index.js'
import '../assets/management-common.css'
import '../assets/design-tokens.css'

const uploadRef = ref(null)
const uploadLoading = ref(false)
const selectedFile = ref(null)
const importResult = ref(null)

const importForm = reactive({
  type: ''
})

const typeMap = {
  room: '教室',
  teacher: '教师',
  class: '班级',
  course: '课程'
}

const typeLabel = computed(() => {
  return typeMap[importForm.type] || ''
})

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
  } catch (error) {
    console.error('下载模板失败:', error)
    ElMessage.error('下载模板失败')
  }
}

const handleFileChange = (file) => {
  selectedFile.value = file.raw
}

const handleFileRemove = () => {
  selectedFile.value = null
  importResult.value = null
}

const handleUpload = async () => {
  if (!importForm.type) {
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
    formData.append('type', importForm.type)

    const res = await importApi.upload(formData)
    importResult.value = {
      success: true,
      count: res.count || 0
    }
    ElMessage.success(`导入成功，共导入 ${res.count || 0} 条数据`)
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

const handleReset = () => {
  importForm.type = ''
  selectedFile.value = null
  importResult.value = null
  uploadRef.value?.clearFiles()
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.upload-area {
  padding: 40px 0;
  text-align: center;
}

/* 上传区域美化 */
:deep(.el-upload-dragger) {
  border-radius: var(--radius-lg);
  border: 2px dashed var(--border-base);
  transition: all var(--duration-base) var(--ease-out);
}

:deep(.el-upload-dragger:hover) {
  border-color: var(--color-primary-4);
  background: var(--color-primary-1);
}

:deep(.el-upload__tip) {
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
}

/* 结果卡片 */
:deep(.el-alert) {
  border-radius: var(--radius-lg);
}
</style>
