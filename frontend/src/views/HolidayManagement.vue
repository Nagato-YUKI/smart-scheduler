<template>
  <div class="holiday-management management-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header__title">
            <el-icon><Sunny /></el-icon>
            <span>节假日管理</span>
          </div>
          <div class="card-header__actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              <span>新增节假日</span>
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索节假日名称..."
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
        <el-table-column prop="date" label="日期" width="180">
          <template #default="{ row }">
            <div class="date-cell">
              <el-icon><Calendar /></el-icon>
              <span>{{ row.date }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="节假日名称">
          <template #default="{ row }">
            <div class="holiday-name-cell">
              <el-tag size="small" type="warning">{{ row.name }}</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div class="operation-cell">
              <el-button type="primary" link @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-popconfirm title="确定删除此节假日吗？" @confirm="handleDelete(row)">
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑节假日' : '新增节假日'" width="420px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="日期" prop="date">
          <el-date-picker v-model="formData.date" type="date" value-format="YYYY-MM-DD" style="width: 100%" placeholder="请选择日期" />
        </el-form-item>
        <el-form-item label="名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入节假日名称" />
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
import { Sunny, Plus, Search, Calendar, Edit, Delete } from '@element-plus/icons-vue'
import { holidayApi } from '../api/index.js'
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
const formData = reactive({ id: null, date: '', name: '' })

const rules = {
  date: [{ required: true, message: '请选择日期', trigger: 'change' }],
  name: [{ required: true, message: '请输入节假日名称', trigger: 'blur' }],
}

const filteredData = computed(() => {
  let data = tableData.value
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter(r => r.name.toLowerCase().includes(keyword))
  }
  return data
})

function handleSearch() {}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await holidayApi.getList({ page: pagination.currentPage, per_page: pagination.pageSize })
    tableData.value = (res.holidays || []).map(h => ({ ...h, date: h.date || '' }))
    pagination.total = res.total || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const handleAdd = () => { isEdit.value = false; resetForm(); dialogVisible.value = true }
const handleEdit = (row) => { isEdit.value = true; Object.assign(formData, row); dialogVisible.value = true }
const handleDelete = async (row) => {
  try { await holidayApi.delete(row.id); ElMessage.success('删除成功'); fetchData() }
  catch (e) { if (e !== 'cancel') console.error(e) }
}
const handleSubmit = async () => {
  await formRef.value.validate(); submitLoading.value = true
  try {
    if (isEdit.value) { await holidayApi.update(formData.id, { ...formData }); ElMessage.success('更新成功') }
    else { await holidayApi.create(formData); ElMessage.success('创建成功') }
    dialogVisible.value = false; fetchData()
  } catch (e) { console.error(e) }
  finally { submitLoading.value = false }
}
const resetForm = () => {
  formData.id = null; formData.date = ''; formData.name = ''
  formRef.value?.resetFields()
}

onMounted(() => fetchData())
</script>

<style scoped>
.date-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-primary-6);
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-medium);
}

.holiday-name-cell {
  display: flex;
  align-items: center;
}

.operation-cell {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}
</style>
