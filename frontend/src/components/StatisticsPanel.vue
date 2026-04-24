<template>
  <div class="statistics-panel">
    <h3 class="panel-title">课时统计</h3>
    
    <el-card class="stat-card" v-for="item in statistics" :key="item.className">
      <template #header>
        <div class="card-header">
          <span>{{ item.className }}</span>
          <el-tag :type="item.status === '充足' ? 'success' : 'danger'" size="small">
            {{ item.status }}
          </el-tag>
        </div>
      </template>
      
      <div class="stat-details">
        <div class="stat-row">
          <span class="stat-label">上午课时：</span>
          <span class="stat-value">{{ item.morningCount }} 次 × 4 = {{ item.morningHours }} 课时</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">下午课时：</span>
          <span class="stat-value">{{ item.afternoonCount }} 次 × 4 = {{ item.afternoonHours }} 课时</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">晚上课时：</span>
          <span class="stat-value">{{ item.eveningCount }} 次 × 3 = {{ item.eveningHours }} 课时</span>
        </div>
        
        <el-divider />
        
        <div class="stat-row total">
          <span class="stat-label">总课时：</span>
          <span class="stat-value">{{ item.totalHours }} 课时</span>
        </div>
        
        <div class="stat-row difference" :class="{ 'is-negative': item.difference < 0 }">
          <span class="stat-label">与64课时差值：</span>
          <span class="stat-value">{{ item.difference > 0 ? '+' : '' }}{{ item.difference }} 课时</span>
        </div>
        
        <el-alert
          v-if="item.difference < 0"
          :title="`缺课${Math.abs(item.difference)}课时，需教师补课`"
          type="warning"
          show-icon
          :closable="false"
          class="warning-alert"
        />
      </div>
    </el-card>

    <el-card class="stat-card" v-if="classList.length > 0">
      <template #header>
        <div class="card-header">
          <span>教学班排入大时段明细</span>
        </div>
      </template>
      
      <el-table :data="classList" border stripe class="detail-table">
        <el-table-column prop="className" label="教学班" width="150" />
        <el-table-column prop="courseName" label="课程" width="120" />
        <el-table-column prop="teacherName" label="教师" width="120" />
        <el-table-column label="大时段">
          <template #default="{ row }">
            <el-tag :type="getPeriodType(row.period)" size="small">
              {{ row.period }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="weekCount" label="周次数量" width="100" />
        <el-table-column prop="totalHours" label="总课时" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  scheduleData: {
    type: Array,
    default: () => []
  },
  classList: {
    type: Array,
    default: () => []
  }
})

const statistics = computed(() => {
  const classMap = new Map()
  
  props.scheduleData.forEach(item => {
    const key = item.className
    if (!classMap.has(key)) {
      classMap.set(key, {
        className: key,
        morningCount: 0,
        afternoonCount: 0,
        eveningCount: 0
      })
    }
    
    const stats = classMap.get(key)
    if (item.period === '上午') {
      stats.morningCount++
    } else if (item.period === '下午') {
      stats.afternoonCount++
    } else if (item.period === '晚上') {
      stats.eveningCount++
    }
  })
  
  return Array.from(classMap.values()).map(stats => {
    const morningHours = stats.morningCount * 4
    const afternoonHours = stats.afternoonCount * 4
    const eveningHours = stats.eveningCount * 3
    const totalHours = morningHours + afternoonHours + eveningHours
    const difference = totalHours - 64
    
    return {
      ...stats,
      morningHours,
      afternoonHours,
      eveningHours,
      totalHours,
      difference,
      status: difference >= 0 ? '充足' : '不足'
    }
  })
})

function getPeriodType(period) {
  switch (period) {
    case '上午':
      return 'primary'
    case '下午':
      return 'success'
    case '晚上':
      return 'warning'
    default:
      return 'info'
  }
}
</script>

<style scoped>
.statistics-panel {
  padding: 20px;
}

.panel-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #303133;
}

.stat-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-details {
  padding: 10px 0;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  font-size: 14px;
}

.stat-row.total {
  font-weight: bold;
  font-size: 16px;
}

.stat-row.difference {
  font-weight: bold;
}

.stat-row.difference.is-negative {
  color: #e6a23c;
}

.stat-label {
  color: #606266;
}

.stat-value {
  color: #303133;
  font-weight: 500;
}

.warning-alert {
  margin-top: 10px;
}

.detail-table {
  width: 100%;
}
</style>
