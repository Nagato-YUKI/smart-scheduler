<template>
  <div class="room-management management-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>教室管理</span>
          <el-button type="primary" @click="handleAdd">新增教室</el-button>
        </div>
      </template>

      <el-table :data="tableData" v-loading="loading" border stripe style="width: 100%">
        <el-table-column prop="room_number" label="教室编号" width="120" />
        <el-table-column prop="name" label="教室名称" />
        <el-table-column prop="room_type" label="教室类型" width="130" />
        <el-table-column prop="capacity" label="容量" width="100" />
        <el-table-column prop="is_available" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_available ? 'success' : 'danger'">
              {{ row.is_available ? '可用' : '不可用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        @size-change="fetchData"
        @current-change="fetchData"
        class="pagination"
      />
    </el-card>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑教室' : '新增教室'" width="450px">
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="教室编号" prop="room_number">
          <el-input v-model="formData.room_number" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="教室名称" prop="name">
          <el-input v-model="formData.name" />
        </el-form-item>
        <el-form-item label="教室类型" prop="room_type">
          <el-select v-model="formData.room_type" style="width: 100%">
            <el-option label="普通教室" value="普通教室" />
            <el-option label="多媒体教室" value="多媒体教室" />
            <el-option label="机房" value="机房" />
            <el-option label="实验室" value="实验室" />
          </el-select>
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="formData.capacity" :min="1" :max="500" style="width: 100%" />
        </el-form-item>
        <el-form-item label="可用状态">
          <el-switch v-model="formData.is_available" active-text="可用" inactive-text="不可用" />
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
import { roomApi } from '../api/index.js'
import '../assets/management-common.css'
import '../assets/design-tokens.css'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const tableData = ref([])

const pagination = reactive({ currentPage: 1, pageSize: 20, total: 0 })

const formData = reactive({ id: null, room_number: '', name: '', room_type: '', capacity: 50, is_available: true })

const rules = {
  room_number: [{ required: true, message: '请输入教室编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入教室名称', trigger: 'blur' }],
  room_type: [{ required: true, message: '请选择教室类型', trigger: 'change' }],
  capacity: [{ required: true, message: '请输入容量', trigger: 'blur' }],
}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await roomApi.getList({ page: pagination.currentPage, per_page: pagination.pageSize })
    tableData.value = res.rooms || []
    pagination.total = res.total || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const handleAdd = () => { isEdit.value = false; resetForm(); dialogVisible.value = true }
const handleEdit = (row) => { isEdit.value = true; Object.assign(formData, row); dialogVisible.value = true }

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除教室 "${row.name}" 吗？`, '确认删除', { type: 'warning' })
    await roomApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) { if (e !== 'cancel') console.error(e) }
}

const handleSubmit = async () => {
  await formRef.value.validate()
  submitLoading.value = true
  try {
    if (isEdit.value) { await roomApi.update(formData.id, { ...formData }); ElMessage.success('更新成功') }
    else { await roomApi.create(formData); ElMessage.success('创建成功') }
    dialogVisible.value = false
    fetchData()
  } catch (e) { console.error(e) }
  finally { submitLoading.value = false }
}

const resetForm = () => {
  formData.id = null; formData.room_number = ''; formData.name = ''; formData.room_type = ''; formData.capacity = 50; formData.is_available = true
  formRef.value?.resetFields()
}

onMounted(() => fetchData())
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.pagination { margin-top: 16px; justify-content: flex-end; }
</style>
