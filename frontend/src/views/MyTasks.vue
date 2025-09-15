<template>
  <div class="my-tasks-page" :class="{ 'customer-theme': isCustomer }">
    <NavBar />
    
    <div class="main-content">
      <div class="page-header">
        <h1>我的任务</h1>
        <p>{{ isCustomer ? '管理您发布的任务进度' : '管理您正在进行和已完成的任务' }}</p>
      </div>

      <!-- 正在进行中的任务 -->
      <div class="section">
        <div class="section-header">
          <h2>正在进行中的任务</h2>
          <span class="task-count">{{ inProgressTasks.length }} 个任务</span>
        </div>
        
        <div v-if="inProgressTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 11H15M9 15H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H12.5858C12.851 3 13.1054 3.10536 13.2929 3.29289L19.7071 9.70711C19.8946 9.89464 20 10.149 20 10.4142V19C20 20.1046 19.1046 21 18 21H17Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>暂无进行中的任务</h3>
          <p>您当前没有正在进行的任务</p>
          <router-link to="/" class="browse-btn">浏览任务</router-link>
        </div>
        
        <div v-else class="task-list">
          <div v-for="task in inProgressTasks" :key="task.id" class="task-card">
            <div class="task-info">
              <h3 class="task-name">{{ task.name }}</h3>
              <div class="task-meta">
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                    <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <span>{{ task.date }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.location }}</span>
                </div>
                <div class="meta-item status">
                  <span :class="['status-badge', task.status]">{{ getStatusText(task.status) }}</span>
                </div>
              </div>
            </div>
            <div class="task-actions">
              <!-- Provider操作 -->
              <template v-if="!isCustomer">
                <button v-if="task.status === 'pending'" class="action-btn cancel-btn" @click="cancelTask(task.id)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
                    <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  取消任务
                </button>
                <button v-if="task.status === 'in-progress'" class="action-btn complete-btn" @click="completeTask(task.id)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  我已完成
                </button>
              </template>
              
              <!-- Customer操作 -->
              <template v-else>
                <button v-if="task.status === 'pending'" class="action-btn cancel-btn" @click="cancelTask(task.id)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
                    <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  取消任务
                </button>
                <button v-if="task.status === 'completed'" class="action-btn confirm-btn" @click="confirmComplete(task.id)">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  确认完成
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- 历史任务 -->
      <div class="section">
        <div class="section-header">
          <h2>历史任务</h2>
          <span class="task-count">{{ historyTasks.length }} 个任务</span>
        </div>
        
        <div v-if="historyTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>暂无历史任务</h3>
          <p>您还没有完成过任何任务</p>
        </div>
        
        <div v-else class="task-list">
          <div v-for="task in historyTasks" :key="task.id" class="task-card history">
            <div class="task-info">
              <h3 class="task-name">{{ task.name }}</h3>
              <div class="task-meta">
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                    <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                    <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <span>{{ task.date }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>{{ task.location }}</span>
                </div>
                <div class="meta-item">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  <span>完成时间：{{ task.completedAt }}</span>
                </div>
              </div>
            </div>
            <div class="task-status">
              <span class="status-badge completed">已完成</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'

export default {
  name: 'MyTasks',
  components: {
    NavBar
  },
  data() {
    return {
      inProgressTasks: [
        {
          id: 1,
          name: '网站前端开发项目',
          date: '2024-01-15',
          location: '北京市朝阳区',
          status: 'in-progress'
        },
        {
          id: 2,
          name: '移动应用UI设计',
          date: '2024-01-20',
          location: '上海市浦东新区',
          status: 'pending'
        }
      ],
      historyTasks: [
        {
          id: 3,
          name: '企业官网改版',
          date: '2024-01-10',
          location: '深圳市南山区',
          completedAt: '2024-01-12 18:30'
        },
        {
          id: 4,
          name: '电商平台开发',
          date: '2024-01-05',
          location: '广州市天河区',
          completedAt: '2024-01-08 16:45'
        },
        {
          id: 5,
          name: '数据分析报告',
          date: '2024-01-01',
          location: '杭州市西湖区',
          completedAt: '2024-01-03 14:20'
        }
      ]
    }
  },
  computed: {
    isCustomer() {
      return this.$route.query.role === 'customer'
    }
  },
  methods: {
    getStatusText(status) {
      const statusMap = {
        'pending': '待开始',
        'in-progress': '进行中',
        'completed': '已完成',
        'cancelled': '已取消'
      }
      return statusMap[status] || '未知'
    },
    cancelTask(taskId) {
      if (confirm('确定要取消这个任务吗？')) {
        const task = this.inProgressTasks.find(t => t.id === taskId)
        if (task) {
          task.status = 'cancelled'
          // 这里可以调用API取消任务
          alert('任务已取消')
        }
      }
    },
    completeTask(taskId) {
      if (confirm('确定要标记这个任务为已完成吗？')) {
        const taskIndex = this.inProgressTasks.findIndex(t => t.id === taskId)
        if (taskIndex !== -1) {
          const task = this.inProgressTasks[taskIndex]
          task.status = 'completed'
          task.completedAt = new Date().toLocaleString('zh-CN')
          
          // 移动到历史任务
          this.historyTasks.unshift({
            id: task.id,
            name: task.name,
            date: task.date,
            location: task.location,
            completedAt: task.completedAt
          })
          
          // 从进行中任务移除
          this.inProgressTasks.splice(taskIndex, 1)
          
          alert('任务已完成！')
        }
      }
    },
    confirmComplete(taskId) {
      if (confirm('确定要确认任务已完成吗？')) {
        const task = this.inProgressTasks.find(t => t.id === taskId)
        if (task) {
          task.status = 'confirmed'
          task.confirmedAt = new Date().toLocaleString('zh-CN')
          
          // 移动到历史任务
          this.historyTasks.unshift({
            id: task.id,
            name: task.name,
            date: task.date,
            location: task.location,
            completedAt: task.confirmedAt
          })
          
          // 从进行中任务移除
          const taskIndex = this.inProgressTasks.findIndex(t => t.id === taskId)
          if (taskIndex !== -1) {
            this.inProgressTasks.splice(taskIndex, 1)
          }
          
          alert('任务已确认完成！')
        }
      }
    }
  }
}
</script>

<style scoped>
.my-tasks-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;
  padding: 40px 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 0 10px 0;
}

.page-header p {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.task-count {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  color: #74b9ff;
  margin-bottom: 20px;
}

.empty-state h3 {
  font-size: 20px;
  color: #666;
  margin: 0 0 10px 0;
}

.empty-state p {
  color: #999;
  font-size: 14px;
  margin: 0 0 20px 0;
}

.browse-btn {
  display: inline-block;
  padding: 10px 20px;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.browse-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.task-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.task-card:hover {
  border-color: #74b9ff;
  box-shadow: 0 2px 8px rgba(116, 185, 255, 0.1);
}

.task-card.history {
  background: #f8f9fa;
  opacity: 0.8;
}

.task-info {
  flex: 1;
}

.task-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 10px 0;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 14px;
}

.meta-item svg {
  color: #74b9ff;
  flex-shrink: 0;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.in-progress {
  background: #d1ecf1;
  color: #0c5460;
}

.status-badge.completed {
  background: #d4edda;
  color: #155724;
}

.status-badge.cancelled {
  background: #f8d7da;
  color: #721c24;
}

.task-actions {
  display: flex;
  gap: 10px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.cancel-btn:hover {
  background: #f5c6cb;
  color: #721c24;
}

.complete-btn {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
}

.complete-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(116, 185, 255, 0.3);
}

.confirm-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  color: white;
}

.confirm-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 184, 148, 0.3);
}

/* Customer主题颜色 */
.customer-theme .task-count {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .browse-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .browse-btn:hover {
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

.customer-theme .meta-item svg {
  color: #00b894;
}

.customer-theme .complete-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .complete-btn:hover {
  box-shadow: 0 4px 12px rgba(0, 184, 148, 0.3);
}

.task-status {
  display: flex;
  align-items: center;
}

@media (max-width: 768px) {
  .main-content {
    padding: 15px;
  }
  
  .page-header {
    padding: 30px 20px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .section {
    padding: 20px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .task-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .task-meta {
    flex-direction: column;
    gap: 10px;
  }
  
  .task-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>