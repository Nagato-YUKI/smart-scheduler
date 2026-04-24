<template>
  <div class="course-management management-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>课程管理</span>
          <el-button type="primary" @click="handleAdd">新增课程</el-button>
        </div>
      </template>
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="course_number" label="课程编号" width="120" />
        <el-table-column prop="name" label="课程名称" />
        <el-table-column prop="course_type" label="课程类型" width="110" />
        <el-table-column prop="total_hours" label="总课时" width="90" />
        <el-table-column prop="teacher_name" label="授课教师" width="120" />
        <el-table-column prop="class_name" label="授课班级" width="120" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-pagination v-model:current-page="pagination.currentPage" v-model:page-size="pagination.pageSize"
        :total="pagination.total" :page-sizes="[10,20,50]" layout="total, sizes, prev, pager, next"
        @size-change="fetchData" @current-change="fetchData" class="pagination" />
    </el-card>
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑课程' : '新增课程'" width="500px">
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="课程编号" prop="course_number"><el-input v-model="formData.course_number" :disabled="isEdit" /></el-form-item>
        <el-form-item label="课程名称" prop="name"><el-input v-model="formData.name" /></el-form-item>
        <el-form-item label="课程类型" prop="course_type">
          <el-select v-model="formData.course_type" style="width:100%">
            <el-option label="普通授课" value="普通授课" />
            <el-option label="实验" value="实验" />
            <el-option label="上机" value="上机" />
          </el-select>
        </el-form-item>
        <el-form-item label="授课教师" prop="teacher_id">
          <el-select v-model="formData.teacher_id" style="width:100%" placeholder="请选择">
            <el-option v-for="t in teachers" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="授课班级" prop="class_id">
          <el-select v-model="formData.class_id" style="width:100%" placeholder="请选择">
            <el-option v-for="c in classes" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="总课时"><el-input-number v-model="formData.total_hours" :min="1" :max="128" style="width:100%" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import {ref,reactive,onMounted} from 'vue'
import {ElMessage,ElMessageBox} from 'element-plus'
import {courseApi,teacherApi,classApi} from '../api/index.js'
import '../assets/management-common.css'
import '../assets/design-tokens.css'
const loading=ref(false);const submitLoading=ref(false);const dialogVisible=ref(false);const isEdit=ref(false);const formRef=ref(null);const tableData=ref([])
const teachers=ref([]);const classes=ref([])
const pagination=reactive({currentPage:1,pageSize:20,total:0})
const formData=reactive({id:null,course_number:'',name:'',course_type:'普通授课',total_hours:64,teacher_id:null,class_id:null})
const rules={course_number:[{required:true,message:'请输入课程编号',trigger:'blur'}],name:[{required:true,message:'请输入课程名称',trigger:'blur'}],course_type:[{required:true,message:'请选择课程类型',trigger:'change'}]}
const fetchData=async()=>{loading.value=true;try{const res=await courseApi.getList({page:pagination.currentPage,per_page:pagination.pageSize});tableData.value=(res.courses||[]).map(c=>({...c,teacher_name:c.teacher_id?'教师'+c.teacher_id:'-',class_name:c.class_id?'班级'+c.class_id:'-'}));pagination.total=res.total||0}catch(e){console.error(e)}finally{loading.value=false}}
const fetchOptions=async()=>{try{const[tRes,cRes]=await Promise.all([teacherApi.getList({page:1,per_page:100}),classApi.getList({page:1,per_page:100})]);teachers.value=tRes.teachers||[];classes.value=cRes.classes||[]}catch(e){console.error(e)}}
const handleAdd=()=>{isEdit.value=false;resetForm();dialogVisible.value=true}
const handleEdit=(row)=>{isEdit.value=true;Object.assign(formData,row);dialogVisible.value=true}
const handleDelete=async(row)=>{try{await ElMessageBox.confirm(`确定删除课程 "${row.name}" 吗？`,'确认删除',{type:'warning'});await courseApi.delete(row.id);ElMessage.success('删除成功');fetchData()}catch(e){if(e!=='cancel')console.error(e)}}
const handleSubmit=async()=>{await formRef.value.validate();submitLoading.value=true;try{if(isEdit.value){await courseApi.update(formData.id,{...formData});ElMessage.success('更新成功')}else{await courseApi.create(formData);ElMessage.success('创建成功')}dialogVisible.value=false;fetchData()}catch(e){console.error(e)}finally{submitLoading.value=false}}
const resetForm=()=>{formData.id=null;formData.course_number='';formData.name='';formData.course_type='普通授课';formData.total_hours=64;formData.teacher_id=null;formData.class_id=null;formRef.value?.resetFields()}
onMounted(()=>{fetchData();fetchOptions()})
</script>
<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center;}.pagination{margin-top:16px;justify-content:flex-end;}</style>
