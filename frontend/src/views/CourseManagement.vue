<template>
  <div class="course-management management-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="card-header__title">
            <el-icon><Notebook /></el-icon>
            <span>课程管理</span>
          </div>
          <div class="card-header__actions">
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>
              <span>新增课程</span>
            </el-button>
          </div>
        </div>
      </template>

      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索课程名称/编号..."
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="filterType" placeholder="课程类型" clearable @change="handleSearch" style="width: 140px">
          <el-option label="普通授课" value="普通授课" />
          <el-option label="实验" value="实验" />
          <el-option label="上机" value="上机" />
        </el-select>
      </div>

      <el-table :data="filteredData" v-loading="loading" border stripe row-key="id" class="management-table">
        <el-table-column prop="course_number" label="课程编号" width="120">
          <template #default="{ row }">
            <span class="cell-code">{{ row.course_number }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="课程名称" />
        <el-table-column prop="course_type" label="课程类型" width="110">
          <template #default="{ row }">
            <el-tag :type="getCourseTypeTag(row.course_type)" size="small">{{ row.course_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_hours" label="总课时" width="90">
          <template #default="{ row }">
            <span class="cell-number">{{ row.total_hours }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="teacher_name" label="授课教师" width="120" />
        <el-table-column prop="class_name" label="授课班级" width="120" />
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <div class="operation-cell">
              <el-button type="primary" link @click="handleEdit(row)">
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-popconfirm title="确定删除此课程吗？" @confirm="handleDelete(row)">
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

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑课程' : '新增课程'" width="520px" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="课程编号" prop="course_number">
          <el-input v-model="formData.course_number" :disabled="isEdit" placeholder="请输入课程编号" />
        </el-form-item>
        <el-form-item label="课程名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入课程名称" />
        </el-form-item>
        <el-form-item label="课程类型" prop="course_type">
          <el-select v-model="formData.course_type" style="width: 100%" placeholder="请选择课程类型">
            <el-option label="普通授课" value="普通授课" />
            <el-option label="实验" value="实验" />
            <el-option label="上机" value="上机" />
          </el-select>
        </el-form-item>
        <el-form-item label="授课教师" prop="teacher_id">
          <el-select v-model="formData.teacher_id" style="width: 100%" placeholder="请选择授课教师" clearable filterable>
            <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="授课班级" prop="class_id">
          <el-select v-model="formData.class_id" style="width: 100%" placeholder="请选择授课班级" clearable filterable>
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="总课时" prop="total_hours">
          <el-input-number v-model="formData.total_hours" :min="1" :max="128" style="width: 100%" />
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
import { Notebook, Plus, Search, Edit, Delete } from '@element-plus/icons-vue'
import { courseApi, teacherApi, classApi } from '../api/index.js'
import '../assets/management-common.css'
import '../assets/design-tokens.css'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const formRef = ref(null)
const tableData = ref([])
const teachers = ref([])
const classes = ref([])
const searchKeyword = ref('')
const filterType = ref('')

const pagination = reactive({ currentPage: 1, pageSize: 20, total: 0 })
const formData = reactive({ id: null, course_number: '', name: '', course_type: '普通授课', total_hours: 64, teacher_id: null, class_id: null })

const rules = {
  course_number: [{ required: true, message: '请输入课程编号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入课程名称', trigger: 'blur' }],
  course_type: [{ required: true, message: '请选择课程类型', trigger: 'change' }],
}

const filteredData = computed(() => {
  let data = tableData.value
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    data = data.filter(r =>
      r.name.toLowerCase().includes(keyword) ||
      r.course_number.toLowerCase().includes(keyword)
    )
  }
  if (filterType.value) {
    data = data.filter(r => r.course_type === filterType.value)
  }
  return data
})

function getCourseTypeTag(type) {
  const map = { '普通授课': '', '实验': 'warning', '上机': 'success' }
  return map[type] || ''
}

function handleSearch() {}

const fetchData = async () => {
  loading.value = true
  try {
    const res = await courseApi.getList({ page: pagination.currentPage, per_page: pagination.pageSize })
    tableData.value = (res.courses || []).map(c => ({
      ...c,
      teacher_name: c.teacher_id ? '教师' + c.teacher_id : '-',
      class_name: c.class_id ? '班级' + c.class_id : '-',
    }))
    pagination.total = res.total || 0
  } catch (e) { console.error(e) }
  finally { loading.value = false }
}

const fetchOptions = async () => {
  try {
    const [tRes, cRes] = await Promise.all([
      teacherApi.getList({ page: 1, per_page: 100 }),
      classApi.getList({ page: 1, per_page: 100 }),
    ])
    teachers.value = tRes.teachers || []
    classes.value = cRes.classes || []
  } catch (e) { console.error(e) }
}

const handleAdd = () => { isEdit.value = false; resetForm(); dialogVisible.value = true }
const handleEdit = (row) => { isEdit.value = true; Object.assign(formData, row); dialogVisible.value = true }
const handleDelete = async (row) => {
  try { await courseApi.delete(row.id); ElMessage.success('删除成功'); fetchData() }
  catch (e) { if (e !== 'cancel') console.error(e) }
}
const handleSubmit = async () => {
  await formRef.value.validate(); submitLoading.value = true
  try {
    if (isEdit.value) { await courseApi.update(formData.id, { ...formData }); ElMessage.success('更新成功') }
    else { await courseApi.create(formData); ElMessage.success('创建成功') }
    dialogVisible.value = false; fetchData()
  } catch (e) { console.error(e) }
  finally { submitLoading.value = false }
}
const resetForm = () => {
  formData.id = null; formData.course_number = ''; formData.name = ''; formData.course_type = '普通授课'; formData.total_hours = 64; formData.teacher_id = null; formData.class_id = null
  formRef.value?.resetFields()
}

onMounted(() => { fetchData(); fetchOptions() })
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
