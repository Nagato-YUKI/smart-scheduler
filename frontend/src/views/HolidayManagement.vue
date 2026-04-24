<template>
  <div class="holiday-management management-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>节假日管理</span>
          <el-button type="primary" @click="handleAdd">新增节假日</el-button>
        </div>
      </template>
      <el-table :data="tableData" v-loading="loading" border stripe>
        <el-table-column prop="date" label="日期" width="180" />
        <el-table-column prop="name" label="节假日名称" />
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
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑节假日' : '新增节假日'" width="400px">
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="日期" prop="date"><el-date-picker v-model="formData.date" type="date" value-format="YYYY-MM-DD" style="width:100%" /></el-form-item>
        <el-form-item label="名称" prop="name"><el-input v-model="formData.name" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="dialogVisible=false">取消</el-button><el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup>
import {ref,reactive,onMounted} from 'vue'
import {ElMessage,ElMessageBox} from 'element-plus'
import {holidayApi} from '../api/index.js'
import '../assets/management-common.css'
import '../assets/design-tokens.css'
const loading=ref(false);const submitLoading=ref(false);const dialogVisible=ref(false);const isEdit=ref(false);const formRef=ref(null);const tableData=ref([])
const pagination=reactive({currentPage:1,pageSize:20,total:0})
const formData=reactive({id:null,date:'',name:''})
const rules={date:[{required:true,message:'请选择日期',trigger:'change'}],name:[{required:true,message:'请输入节假日名称',trigger:'blur'}]}
const fetchData=async()=>{loading.value=true;try{const res=await holidayApi.getList({page:pagination.currentPage,per_page:pagination.pageSize});tableData.value=(res.holidays||[]).map(h=>({...h,date:h.date||''}));pagination.total=res.total||0}catch(e){console.error(e)}finally{loading.value=false}}
const handleAdd=()=>{isEdit.value=false;resetForm();dialogVisible.value=true}
const handleEdit=(row)=>{isEdit.value=true;Object.assign(formData,row);dialogVisible.value=true}
const handleDelete=async(row)=>{try{await ElMessageBox.confirm(`确定删除 "${row.name}" 吗？`,'确认删除',{type:'warning'});await holidayApi.delete(row.id);ElMessage.success('删除成功');fetchData()}catch(e){if(e!=='cancel')console.error(e)}}
const handleSubmit=async()=>{await formRef.value.validate();submitLoading.value=true;try{if(isEdit.value){await holidayApi.update(formData.id,{...formData});ElMessage.success('更新成功')}else{await holidayApi.create(formData);ElMessage.success('创建成功')}dialogVisible.value=false;fetchData()}catch(e){console.error(e)}finally{submitLoading.value=false}}
const resetForm=()=>{formData.id=null;formData.date='';formData.name='';formRef.value?.resetFields()}
onMounted(()=>fetchData())
</script>
<style scoped>.card-header{display:flex;justify-content:space-between;align-items:center;}.pagination{margin-top:16px;justify-content:flex-end;}</style>
