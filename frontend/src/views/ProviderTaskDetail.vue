<template>
  <div class="provider-task-detail-page">
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
        <router-link to="/?role=provider" class="back-btn">返回首页</router-link>
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
            <router-link to="/?role=provider" class="breadcrumb-link">寻找任务</router-link>
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

        <!-- 客户信息 -->
        <div class="customer-info">
          <h3>客户信息</h3>
          <div class="customer-details">
            <div class="customer-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="label">账户ID：</span>
              <span class="value">{{ task.customerId }}</span>
            </div>
            <div class="customer-item">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 16.92V19.92C22.0011 20.1985 21.9441 20.4742 21.8325 20.7293C21.7209 20.9845 21.5573 21.2136 21.3521 21.4019C21.1468 21.5901 20.9046 21.7335 20.6407 21.8227C20.3769 21.9119 20.0974 21.9451 19.82 21.92C16.7428 21.5856 13.787 20.5341 11.19 18.85C8.77382 17.3147 6.72533 15.2662 5.18999 12.85C3.49997 10.2412 2.44824 7.27099 2.11999 4.18C2.095 3.90347 2.12787 3.62476 2.21649 3.36162C2.30512 3.09849 2.44756 2.85669 2.63476 2.65162C2.82196 2.44655 3.0498 2.28271 3.30379 2.17052C3.55777 2.05833 3.83233 2.00026 4.10999 2H7.10999C7.59531 1.99522 8.06679 2.16708 8.43376 2.48353C8.80073 2.79999 9.04207 3.23945 9.11999 3.72C9.28562 4.68007 9.60683 5.62273 10.07 6.5C10.199 6.76126 10.2701 7.05063 10.2781 7.34562C10.2861 7.6406 10.2308 7.93387 10.1156 8.20657C10.0004 8.47927 9.82789 8.72483 9.60999 8.92L8.38999 10.14C9.62999 12.41 11.58 14.36 13.85 15.6L15.07 14.38C15.2652 14.1621 15.5107 13.9896 15.7834 13.8744C16.0561 13.7592 16.3494 13.7039 16.6444 13.7119C16.9394 13.7199 17.2287 13.791 17.49 13.92C18.3673 14.3832 19.3099 14.7044 20.27 14.87C20.7505 14.9479 21.1899 15.1892 21.5064 15.5562C21.8228 15.9231 21.9947 16.3946 21.99 16.88L22 16.92Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span class="label">联系电话：</span>
              <span class="value">{{ task.customerPhone }}</span>
            </div>
          </div>
        </div>

        <!-- 接取任务按钮 -->
        <div class="action-buttons">
          <button class="apply-btn" @click="applyTask">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            接取任务
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'

export default {
  name: 'ProviderTaskDetail',
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
            customerId: 'CUST_2024_001',
            customerPhone: '138-0000-1234'
          }
        ]
        
        this.task = tasks.find(t => t.id == taskId) || null
        this.loading = false
      }, 1000)
    },
    goBack() {
      this.$router.go(-1)
    },
    applyTask() {
      alert('接取任务功能待开发')
    }
  }
}
</script>

<style scoped>
.provider-task-detail-page {
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
  border-top: 4px solid #74b9ff;
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
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
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
  color: #74b9ff;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.back-button:hover {
  background: #74b9ff;
  color: white;
  border-color: #74b9ff;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.breadcrumb-link {
  color: #74b9ff;
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
  color: #74b9ff;
  flex-shrink: 0;
}

.category {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
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

.task-details, .task-requirements, .customer-info {
  margin-bottom: 30px;
}

.task-details h3, .task-requirements h3, .customer-info h3 {
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
  color: #74b9ff;
  font-weight: bold;
  position: absolute;
  left: 0;
}

.customer-details {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.customer-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.customer-item svg {
  color: #74b9ff;
  flex-shrink: 0;
}

.label {
  color: #666;
  font-size: 14px;
  min-width: 80px;
}

.value {
  color: #333;
  font-weight: 500;
  font-size: 16px;
}

.action-buttons {
  margin-top: 40px;
  text-align: center;
}

.apply-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.3);
}

.apply-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(116, 185, 255, 0.4);
}

.apply-btn:active {
  transform: translateY(0);
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
  
  .customer-details {
    gap: 10px;
  }
  
  .customer-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .label {
    min-width: auto;
  }
}
</style>
