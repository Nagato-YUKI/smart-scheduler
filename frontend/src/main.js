import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

// GitHub Pages 404 重定向处理
const redirectPath = sessionStorage.getItem('redirect-path')
if (redirectPath) {
  sessionStorage.removeItem('redirect-path')
  // 替换掉 URL 中的 hash 部分
  const path = redirectPath.replace(/^\/smart-scheduler/, '')
  if (path && path !== '/') {
    router.replace(path)
  }
}

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.use(ElementPlus)
app.mount('#app')
