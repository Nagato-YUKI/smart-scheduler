<template>
  <div class="teacher-management management-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>教师管理</span>
          <el-button type="primary" @click="handleAdd">新增教师</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="teacher_number" label="教师编号" width="120" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="teachable_courses" label="可授课程" />
        <el-table-column prop="max_weekly_sessions" label="每周课次上限" width="130" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination v-model:current-page="pagination.currentPage" v-model:page-size="pagination.pageSize"
        :total="pagination.total" :page-sizes="[10, 20, 50]" layout="total, sizes, prev, pager, next"
        @size-change="fetchData" @current-change="fetchData" class="pagination" />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑教师' : '新增教师'" width="500px">
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="120px">
        <el-form-item label="教师编号" prop="teacher_number">
          <el-input v-model="formData.teacher_number" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="formData.name" />
        </el-form-item>
        <el-form-item label="可授课程" prop="teachable_courses">
          <el-select v-model="formData.teachable_courses" multiple style="width: 100%" placeholder="最多选择2门">
            <el-option label="高等数学" value="高等数学" />
            <el-option label="线性代数" value="线性代数" />
            <el-option label="大学英语" value="大学英语" />
            <el-option label="计算机基础" value="计算机基础" />
            <el-option label="数据库原理" value="数据库原理" />
            <el-option label="有机化学" value="有机化学" />
            <el-option label="普通物理" value="普通物理" />
          </el-select>
        </el-form-item>
        <el-form-item label="每周课次上限" prop="max_weekly_sessions">
          <el-input-number v-model="formData.max_weekly_sessions" :min="1" :max="5" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { teacherApi } from '../api/index.js'
import '../assets/management-common.css'
import '../assets/design-tokens.css'

const loading = ref(false); const submitLoading = ref(false); const dialogVisible = ref(false)
const isEdit = ref(false); const formRef = ref(null); const tableData = ref([])
const pagination = reactive({ currentPage: 1, pageSize: 20, total: 0 })
const formData = reactive({ id: null, teacher_number: '', name: '', teachable_courses: [], max_weekly_sessions: 5 })
const rules = {
  teacher_number: [{ required: true, message: '请输入教师编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  teachable_courses: [{ required: true, message: '请选择可授课程', trigger: 'change' }],
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await teacherApi.getList({ page: pagination.currentPage, per_page: pagination.pageSize })
    tableData.value = (res.teachers || []).map(t => ({ ...t, teachable_courses: Array.isArray(t.teachable_courses) ? t.teachable_courses.join(', ') : '' }))
    pagination.total = res.total || 0
  } catch (e) { console.error(e) } finally { loading.value = false }
}

const handleAdd = () => { isEdit.value = false; resetForm(); dialogVisible.value = true }
const handleEdit = (row) => {
  isEdit.value = true
  Object.assign(formData, { ...row, teachable_courses: row.teachable_courses?.split(', ') || [] })
  dialogVisible.value = true
}
const handleDelete = async (row) => {
  try { await ElMessageBox.confirm(`确定删除教师 "${row.name}" 吗？`, '确认删除', { type: 'warning' }); await teacherApi.delete(row.id); ElMessage.success('删除成功'); fetchData() }
  catch (e) { if (e !== 'cancel') console.error(e) }
}
const handleSubmit = async () => {
  await formRef.value.validate(); submitLoading.value = true
  try {
    if (isEdit.value) { await teacherApi.update(formData.id, { ...formData }); ElMessage.success('更新成功') }
    else { await teacherApi.create(formData); ElMessage.success('创建成功') }
    dialogVisible.value = false; fetchData()
  } catch (e) { console.error(e) } finally { submitLoading.value = false }
}
const resetForm = () => { formData.id = null; formData.teacher_number = ''; formData.name = ''; formData.teachable_courses = []; formData.max_weekly_sessions = 5; formRef.value?.resetFields() }
onMounted(() => fetchData())
</script>

<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center;}.pagination{margin-top:16px;justify-content:flex-end;}</style>
