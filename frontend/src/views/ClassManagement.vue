<template>
  <div class="class-management management-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header__title">
            <el-icon><Reading /></el-icon>
            <span>班级管理</span>
          </div>
          <div class="card-header__actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              <span>新增班级</span>
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索班级名称/编号..."
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <el-table :data="filteredData" v-loading="loading" border stripe row-key="id" class="management-table">
        <el-table-column prop="class_number" label="班级编号" width="120">
          <template #default="{ row }">
            <span class="cell-code">{{ row.class_number }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="班级名称" />
        <el-table-column prop="department" label="所属专业/年级" />
        <el-table-column prop="student_count" label="学生人数" width="100">
          <template #default="{ row }">
            <span class="cell-number">{{ row.student_count }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_available ? 'success' : 'danger'" size="small">
              {{ row.is_available ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="operation-cell">
              <el-switch
                v-model="row.is_available"
                size="small"
                @change="handleToggleStatus(row)"
                inline-prompt
                active-text="开"
                inactive-text="关"
              />
              <el-button type="primary" link @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-popconfirm title="确定删除此班级吗？" @confirm="handleDelete(row)">
                <template #reference>
                  <el-button type="danger" link>
                    <el-icon><Delete /></el-icon>
                    删除
                  </el-button>
                </template>
              </el-popconfirm>
            </div>
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑班级' : '新增班级'" width="480px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="班级编号" prop="class_number">
          <el-input v-model="formData.class_number" :disabled="isEdit" placeholder="请输入班级编号" />
        </el-form-item>
        <el-form-item label="班级名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入班级名称" />
        </el-form-item>
        <el-form-item label="学生人数" prop="student_count">
          <el-input-number v-model="formData.student_count" :min="1" :max="200" style="width: 100%" />
        </el-form-item>
        <el-form-item label="专业/年级" prop="department">
          <el-input v-model="formData.department" placeholder="如：计算机2026级" />
        </el-form-item>
        <el-form-item label="启用状态">
          <el-switch v-model="formData.is_available" active-text="启用" inactive-text="禁用" />
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Reading, Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import { classApi } from '../api/index.js'
import '../assets/management-common.css'
import '../assets/design-tokens.css'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const tableData = ref([])
const searchKeyword = ref('')

const pagination = reactive({ currentPage: 1, pageSize: 20, total: 0 })
const formData = reactive({ id: null, class_number: '', name: '', student_count: 40, department: '', is_available: true })

const rules = {
  class_number: [{ required: true, message: '请输入班级编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入班级名称', trigger: 'blur' }],
  student_count: [{ required: true, message: '请输入学生人数', trigger: 'blur' }],
}

const filteredData = computed(() => {
  let data = tableData.value
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter(r =>
      r.name.toLowerCase().includes(keyword) ||
      r.class_number.toLowerCase().includes(keyword)
    )
  }
  return data
})

function handleSearch() {}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await classApi.getList({ page: pagination.currentPage, per_page: pagination.pageSize })
    tableData.value = res.classes || []
    pagination.total = res.total || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const handleAdd = () => { isEdit.value = false; resetForm(); dialogVisible.value = true }
const handleEdit = (row) => { isEdit.value = true; Object.assign(formData, row); dialogVisible.value = true }
const handleDelete = async (row) => {
  try { await classApi.delete(row.id); ElMessage.success('删除成功'); fetchData() }
  catch (e) { if (e !== 'cancel') console.error(e) }
}
const handleToggleStatus = async (row) => {
  try { await classApi.update(row.id, { is_available: row.is_available }); ElMessage.success(row.is_available ? '已启用' : '已禁用') }
  catch (e) { row.is_available = !row.is_available; console.error(e) }
}
const handleSubmit = async () => {
  await formRef.value.validate(); submitLoading.value = true
  try {
    if (isEdit.value) { await classApi.update(formData.id, { ...formData }); ElMessage.success('更新成功') }
    else { await classApi.create(formData); ElMessage.success('创建成功') }
    dialogVisible.value = false; fetchData()
  } catch (e) { console.error(e) }
  finally { submitLoading.value = false }
}
const resetForm = () => {
  formData.id = null; formData.class_number = ''; formData.name = ''; formData.student_count = 40; formData.department = ''; formData.is_available = true
  formRef.value?.resetFields()
}

onMounted(() => fetchData())
</script>

<style scoped>
.cell-code {
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-medium);
  color: var(--color-primary-6);
}
.cell-number {
  font-weight: var(--font-weight-semibold);
}
.operation-cell {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}
</style>
