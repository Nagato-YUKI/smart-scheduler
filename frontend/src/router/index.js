import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue')
  },
  {
    path: '/rooms',
    name: 'RoomManagement',
    component: () => import('../views/RoomManagement.vue')
  },
  {
    path: '/teachers',
    name: 'TeacherManagement',
    component: () => import('../views/TeacherManagement.vue')
  },
  {
    path: '/classes',
    name: 'ClassManagement',
    component: () => import('../views/ClassManagement.vue')
  },
  {
    path: '/courses',
    name: 'CourseManagement',
    component: () => import('../views/CourseManagement.vue')
  },
  {
    path: '/holidays',
    name: 'HolidayManagement',
    component: () => import('../views/HolidayManagement.vue')
  },
  {
    path: '/import',
    name: 'DataImport',
    component: () => import('../views/DataImport.vue')
  },
  {
    path: '/schedules',
    name: 'ScheduleView',
    component: () => import('../views/ScheduleView.vue')
  },
  {
    path: '/schedules/class',
    name: 'ClassSchedule',
    component: () => import('../views/ClassSchedule.vue')
  },
  {
    path: '/schedules/teacher',
    name: 'TeacherSchedule',
    component: () => import('../views/TeacherSchedule.vue')
  },
  {
    path: '/schedules/room',
    name: 'RoomSchedule',
    component: () => import('../views/RoomSchedule.vue')
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () => import('../views/StatisticsView.vue')
  },
  {
    path: '/adjust-schedule',
    name: 'AdjustSchedule',
    component: () => import('../views/AdjustSchedule.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
