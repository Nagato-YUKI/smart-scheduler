<template>
  <div class="room-management management-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header__title">
            <el-icon><OfficeBuilding /></el-icon>
            <span>教室管理</span>
          </div>
          <div class="card-header__actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              <span>新增教室</span>
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索教室名称/编号..."
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="filterType" placeholder="类型筛选" clearable @change="handleSearch" style="width: 150px">
          <el-option label="普通教室" value="普通教室" />
          <el-option label="多媒体教室" value="多媒体教室" />
          <el-option label="机房" value="机房" />
          <el-option label="实验室" value="实验室" />
        </el-select>
      </div>

      <el-table :data="filteredData" v-loading="loading" border stripe row-key="id" class="management-table">
        <el-table-column prop="room_number" label="教室编号" width="120">
          <template #default="{ row }">
            <span class="cell-code">{{ row.room_number }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="教室名称" />
        <el-table-column prop="room_type" label="教室类型" width="130">
          <template #default="{ row }">
            <el-tag :type="getRoomTypeTag(row.room_type)" size="small">
              {{ row.room_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="capacity" label="容量" width="100">
          <template #default="{ row }">
            <span class="cell-number">{{ row.capacity }}</span>
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
              <el-popconfirm
                title="确定删除此教室吗？"
                confirm-button-text="确定"
                cancel-button-text="取消"
                @confirm="handleDelete(row)"
              >
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑教室' : '新增教室'" width="480px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="教室编号" prop="room_number">
          <el-input v-model="formData.room_number" :disabled="isEdit" placeholder="请输入教室编号" />
        </el-form-item>
        <el-form-item label="教室名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入教室名称" />
        </el-form-item>
        <el-form-item label="教室类型" prop="room_type">
          <el-select v-model="formData.room_type" style="width: 100%" placeholder="请选择教室类型">
            <el-option label="普通教室" value="普通教室" />
            <el-option label="多媒体教室" value="多媒体教室" />
            <el-option label="机房" value="机房" />
            <el-option label="实验室" value="实验室" />
          </el-select>
        </el-form-item>
        <el-form-item label="容量" prop="capacity">
          <el-input-number v-model="formData.capacity" :min="1" :max="500" style="width: 100%" />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { OfficeBuilding, Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import { roomApi } from '../api/index.js'
import '../assets/management-common.css'
import '../assets/design-tokens.css'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const tableData = ref([])
const searchKeyword = ref('')
const filterType = ref('')

const pagination = reactive({ currentPage: 1, pageSize: 20, total: 0 })

const formData = reactive({ id: null, room_number: '', name: '', room_type: '', capacity: 50, is_available: true })

const rules = {
  room_number: [{ required: true, message: '请输入教室编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入教室名称', trigger: 'blur' }],
  room_type: [{ required: true, message: '请选择教室类型', trigger: 'change' }],
  capacity: [{ required: true, message: '请输入容量', trigger: 'blur' }],
}

const filteredData = computed(() => {
  let data = tableData.value
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter(r =>
      r.name.toLowerCase().includes(keyword) ||
      r.room_number.toLowerCase().includes(keyword)
    )
  }
  if (filterType.value) {
    data = data.filter(r => r.room_type === filterType.value)
  }
  return data
})

function getRoomTypeTag(type) {
  const map = {
    '普通教室': 'info',
    '多媒体教室': 'warning',
    '机房': '',
    '实验室': 'success',
  }
  return map[type] || 'info'
}

function handleSearch() {
  // 前端筛选，不需要重新请求
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
    await roomApi.delete(row.id)
    ElMessage.success('删除成功')
    fetchData()
  } catch (e) { console.error(e) }
}
const handleToggleStatus = async (row) => {
  try {
    await roomApi.update(row.id, { is_available: row.is_available })
    ElMessage.success(row.is_available ? '已启用' : '已禁用')
  } catch (e) {
    row.is_available = !row.is_available
    console.error(e)
  }
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
/* 单元格编码样式 */
.cell-code {
  font-family: var(--font-family-mono);
  font-weight: var(--font-weight-medium);
  color: var(--color-primary-6);
}

/* 单元格数字样式 */
.cell-number {
  font-weight: var(--font-weight-semibold);
}

/* 操作列样式 */
.operation-cell {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

/* 表格样式增强 */
.management-table :deep(.el-table__header th) {
  font-weight: var(--font-weight-semibold);
}
</style>
