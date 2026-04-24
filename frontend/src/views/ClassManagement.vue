<template>
  <div class="class-management management-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>班级管理</span>
          <el-button type="primary" @click="handleAdd">新增班级</el-button>
        </div>
      </template>
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="class_number" label="班级编号" width="120" />
        <el-table-column prop="name" label="班级名称" />
        <el-table-column prop="student_count" label="学生人数" width="100" />
        <el-table-column prop="department" label="所属专业/年级" />
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑班级' : '新增班级'" width="450px">
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="班级编号" prop="class_number"><el-input v-model="formData.class_number" :disabled="isEdit" /></el-form-item>
        <el-form-item label="班级名称" prop="name"><el-input v-model="formData.name" /></el-form-item>
        <el-form-item label="学生人数" prop="student_count"><el-input-number v-model="formData.student_count" :min="1" :max="200" style="width:100%" /></el-form-item>
        <el-form-item label="专业/年级" prop="department"><el-input v-model="formData.department" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import {ref,reactive,onMounted} from 'vue'
import {ElMessage,ElMessageBox} from 'element-plus'
import {classApi} from '../api/index.js'
import '../assets/management-common.css'
import '../assets/design-tokens.css'
const loading=ref(false);const submitLoading=ref(false);const dialogVisible=ref(false);const isEdit=ref(false);const formRef=ref(null);const tableData=ref([])
const pagination=reactive({currentPage:1,pageSize:20,total:0})
const formData=reactive({id:null,class_number:'',name:'',student_count:40,department:''})
const rules={class_number:[{required:true,message:'请输入班级编号',trigger:'blur'}],name:[{required:true,message:'请输入班级名称',trigger:'blur'}],student_count:[{required:true,message:'请输入学生人数',trigger:'blur'}]}
const fetchData=async()=>{loading.value=true;try{const res=await classApi.getList({page:pagination.currentPage,per_page:pagination.pageSize});tableData.value=res.classes||[];pagination.total=res.total||0}catch(e){console.error(e)}finally{loading.value=false}}
const handleAdd=()=>{isEdit.value=false;resetForm();dialogVisible.value=true}
const handleEdit=(row)=>{isEdit.value=true;Object.assign(formData,row);dialogVisible.value=true}
const handleDelete=async(row)=>{try{await ElMessageBox.confirm(`确定删除班级 "${row.name}" 吗？`,'确认删除',{type:'warning'});await classApi.delete(row.id);ElMessage.success('删除成功');fetchData()}catch(e){if(e!=='cancel')console.error(e)}}
const handleSubmit=async()=>{await formRef.value.validate();submitLoading.value=true;try{if(isEdit.value){await classApi.update(formData.id,{...formData});ElMessage.success('更新成功')}else{await classApi.create(formData);ElMessage.success('创建成功')}dialogVisible.value=false;fetchData()}catch(e){console.error(e)}finally{submitLoading.value=false}}
const resetForm=()=>{formData.id=null;formData.class_number='';formData.name='';formData.student_count=40;formData.department='';formRef.value?.resetFields()}
onMounted(()=>fetchData())
</script>
<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center;}.pagination{margin-top:16px;justify-content:flex-end;}</style>
