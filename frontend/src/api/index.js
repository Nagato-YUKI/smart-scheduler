import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ? `${import.meta.env.VITE_API_BASE_URL}/api` : '/api',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.response.use(
  response => response.data,
  error => { console.error('API Error:', error); return Promise.reject(error) }
)

export default api

export const roomApi = {
  getList: (params) => api.get('/rooms', { params }),
  getById: (id) => api.get(`/rooms/${id}`),
  create: (data) => api.post('/rooms', data),
  update: (id, data) => api.put(`/rooms/${id}`, data),
  delete: (id) => api.delete(`/rooms/${id}`)
}

export const teacherApi = {
  getList: (params) => api.get('/teachers', { params }),
  getById: (id) => api.get(`/teachers/${id}`),
  create: (data) => api.post('/teachers', data),
  update: (id, data) => api.put(`/teachers/${id}`, data),
  delete: (id) => api.delete(`/teachers/${id}`)
}

export const classApi = {
  getList: (params) => api.get('/classes', { params }),
  getById: (id) => api.get(`/classes/${id}`),
  create: (data) => api.post('/classes', data),
  update: (id, data) => api.put(`/classes/${id}`, data),
  delete: (id) => api.delete(`/classes/${id}`)
}

export const courseApi = {
  getList: (params) => api.get('/courses', { params }),
  getById: (id) => api.get(`/courses/${id}`),
  create: (data) => api.post('/courses', data),
  update: (id, data) => api.put(`/courses/${id}`, data),
  delete: (id) => api.delete(`/courses/${id}`)
}

export const holidayApi = {
  getList: (params) => api.get('/holidays', { params }),
  getById: (id) => api.get(`/holidays/${id}`),
  create: (data) => api.post('/holidays', data),
  update: (id, data) => api.put(`/holidays/${id}`, data),
  delete: (id) => api.delete(`/holidays/${id}`)
}

export const scheduleApi = {
  run: (data) => api.post('/schedule/run', data),
  getResults: (params) => api.get('/schedule/results', { params }),
  getWeekly: (params) => api.get('/schedule/weekly', { params }),
  adjust: (id, data) => api.put(`/schedule/adjust/${id}`, data),
  checkConflict: (teachingClassId, data) => api.post(`/schedule/check-conflict/${teachingClassId}`, data),
  getStatistics: (params) => api.get('/schedule/statistics', { params })
}

export const importApi = {
  upload: (formData) => api.post('/import/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } }),
  getTemplate: (type) => api.get(`/import/template/${type}`, { responseType: 'blob' })
}

export const statisticsApi = {
  getStatistics: (params) => api.get('/schedule/statistics', { params })
}

export const exportApi = {
  exportExcel: (params) => api.get('/export/excel', { params, responseType: 'blob' }),
  printSchedule: (params) => api.get('/export/print', { params })
}
