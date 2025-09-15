<template>
  <div class="customer-task-detail-page">
    <NavBar />
    
    <div class="main-content">
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在加载任务详情...</p>
      </div>
      
      <div v-else-if="!task" class="error-state">
        <div class="error-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
            <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
          </svg>
        </div>
        <h3>任务不存在</h3>
        <p>抱歉，您访问的任务不存在或已被删除</p>
        <router-link to="/?role=customer" class="back-btn">返回首页</router-link>
      </div>
      
      <div v-else class="task-detail">
        <!-- 返回按钮和面包屑 -->
        <div class="task-header">
          <div class="back-button" @click="goBack">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            返回
          </div>
          
          <div class="breadcrumb">
            <router-link to="/?role=customer" class="breadcrumb-link">我的发布</router-link>
            <span class="breadcrumb-separator">></span>
            <span class="breadcrumb-current">任务详情</span>
          </div>
        </div>

        <!-- 任务基本信息 -->
        <div class="task-basic-info">
          <h1 class="task-title">{{ task.title }}</h1>
          <div class="task-meta">
            <div class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7 7H17V17H7V7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 3V5M17 3V5M7 19V21M17 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="category">{{ task.category }}</span>
            </div>
            <div class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.3639 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="location">{{ task.location }}</span>
            </div>
            <div class="meta-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="time">{{ task.startTime }} - {{ task.endTime }}</span>
            </div>
            <div class="meta-item price">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="12" y1="1" x2="12" y2="23" stroke="currentColor" stroke-width="2"/>
                <path d="M17 5H9.5C8.11929 5 7 6.11929 7 7.5S8.11929 10 9.5 10H14.5C15.8807 10 17 11.1193 17 12.5S15.8807 15 14.5 15H7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="amount">¥{{ task.price }}</span>
            </div>
          </div>
        </div>

        <!-- 分隔线 -->
        <div class="divider"></div>

        <!-- 任务详细信息 -->
        <div class="task-details">
          <h3>任务详情</h3>
          <div class="detail-content">
            <p>{{ task.description }}</p>
          </div>
        </div>

        <!-- 任务要求 -->
        <div class="task-requirements">
          <h3>任务要求</h3>
          <ul class="requirements-list">
            <li v-for="requirement in task.requirements" :key="requirement">
              {{ requirement }}
            </li>
          </ul>
        </div>

        <!-- 分隔线 -->
        <div class="divider"></div>

        <!-- 任务状态信息 -->
        <div class="task-status-info">
          <h3>任务状态</h3>
          <div class="status-content">
            <div class="status-item">
              <span class="status-label">当前状态：</span>
              <span :class="['status-badge', task.status]">{{ getStatusText(task.status) }}</span>
            </div>
            <div class="status-item">
              <span class="status-label">发布时间：</span>
              <span class="status-value">{{ formatTime(task.createdAt) }}</span>
            </div>
            <div v-if="task.applicantCount" class="status-item">
              <span class="status-label">申请人数：</span>
              <span class="status-value">{{ task.applicantCount }} 人</span>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <button class="edit-btn" @click="editTask">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13M18.5 2.5C18.8978 2.10218 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10218 21.5 2.5C21.8978 2.89782 22.1213 3.43739 22.1213 4C22.1213 4.56261 21.8978 5.10218 21.5 5.5L12 15L8 16L9 12L18.5 2.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            修改任务
          </button>
          <button class="delete-btn" @click="deleteTask">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 6H5H21M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            删除任务
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'

export default {
  name: 'CustomerTaskDetail',
  components: {
    NavBar
  },
  data() {
    return {
      loading: true,
      task: null
    }
  },
  created() {
    this.loadTask()
  },
  methods: {
    loadTask() {
      const taskId = this.$route.params.id
      
      // 模拟API调用
      setTimeout(() => {
        const tasks = [
          {
            id: 1,
            title: '网站前端开发项目',
            category: '技术开发',
            location: '北京市朝阳区',
            startTime: '2024-01-15 09:00',
            endTime: '2024-01-20 18:00',
            price: 15000,
            description: '需要开发一个响应式的企业官网，包含首页、产品展示、关于我们等页面，要求使用Vue.js框架。项目周期预计2个月，需要与后端团队密切配合。',
            requirements: [
              '熟练掌握Vue.js框架',
              '具备响应式设计经验',
              '熟悉HTML5、CSS3、JavaScript',
              '有企业官网开发经验',
              '能够按时交付项目'
            ],
            status: 'open',
            createdAt: '2024-01-10 14:30:00',
            applicantCount: 3
          }
        ]
        
        this.task = tasks.find(t => t.id == taskId) || null
        this.loading = false
      }, 1000)
    },
    getStatusText(status) {
      const statusMap = {
        'open': '招募中',
        'in-progress': '进行中',
        'completed': '已完成',
        'cancelled': '已取消'
      }
      return statusMap[status] || '未知'
    },
    formatTime(dateString) {
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    },
    goBack() {
      this.$router.go(-1)
    },
    editTask() {
      this.$router.push(`/publish-task?role=customer&edit=true&id=${this.task.id}`)
    },
    deleteTask() {
      if (confirm(`确定要删除任务"${this.task.title}"吗？`)) {
        // 这里应该调用API删除任务
        alert('任务已删除')
        this.$router.push('/?role=customer')
      }
    }
  }
}
</script>

<style scoped>
.customer-task-detail-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-content {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  min-height: calc(100vh - 60px);
  padding: 20px;
}

.loading-container, .error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #00b894;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  color: #e74c3c;
  margin-bottom: 20px;
}

.error-state h3 {
  font-size: 20px;
  color: #666;
  margin: 0 0 10px 0;
}

.error-state p {
  color: #999;
  font-size: 14px;
  margin: 0 0 20px 0;
}

.back-btn {
  display: inline-block;
  padding: 10px 20px;
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

.task-detail {
  max-width: 100%;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #f8f9fa;
  color: #00b894;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: #00b894;
  color: white;
  border-color: #00b894;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.breadcrumb-link {
  color: #00b894;
  text-decoration: none;
}

.breadcrumb-link:hover {
  text-decoration: underline;
}

.breadcrumb-separator {
  color: #ccc;
}

.breadcrumb-current {
  color: #999;
}

.task-basic-info {
  margin-bottom: 30px;
}

.task-title {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 0 20px 0;
  line-height: 1.3;
}

.task-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 16px;
}

.meta-item svg {
  color: #00b894;
  flex-shrink: 0;
}

.category {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.price .amount {
  color: #00b894;
  font-weight: 600;
  font-size: 18px;
}

.divider {
  height: 1px;
  background: #e9ecef;
  margin: 30px 0;
}

.task-details, .task-requirements, .task-status-info {
  margin-bottom: 30px;
}

.task-details h3, .task-requirements h3, .task-status-info h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 15px 0;
}

.detail-content p {
  color: #666;
  line-height: 1.6;
  font-size: 16px;
  margin: 0;
}

.requirements-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.requirements-list li {
  padding: 8px 0;
  padding-left: 20px;
  position: relative;
  color: #666;
  line-height: 1.5;
  font-size: 16px;
}

.requirements-list li::before {
  content: '•';
  color: #00b894;
  font-weight: bold;
  position: absolute;
  left: 0;
}

.status-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.status-label {
  color: #666;
  font-size: 14px;
  min-width: 80px;
}

.status-value {
  color: #333;
  font-weight: 500;
  font-size: 16px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.open {
  background: #d4edda;
  color: #155724;
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

.action-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 40px;
  padding-top: 30px;
  border-top: 2px solid #f0f0f0;
}

.edit-btn,
.delete-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
  color: white;
}

.edit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 184, 148, 0.4);
}

.delete-btn {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  color: white;
}

.delete-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
}

@media (max-width: 768px) {
  .main-content {
    padding: 15px;
  }
  
  .task-title {
    font-size: 24px;
  }
  
  .task-meta {
    flex-direction: column;
    gap: 15px;
  }
  
  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .status-content {
    gap: 10px;
  }
  
  .status-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .status-label {
    min-width: auto;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 15px;
  }
  
  .edit-btn,
  .delete-btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
