<template>
  <div class="task-card" @click="goToDetail">
    <div class="task-header">
      <h3 class="task-title">{{ task.title }}</h3>
      <span class="task-category">{{ task.category }}</span>
    </div>
    
    <div class="task-content">
      <div class="task-info">
        <div class="info-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 10C21 17 12 23 12 23S3 17 3 10C3 7.61305 3.94821 5.32387 5.63604 3.63604C7.32387 1.94821 9.61305 1 12 1C14.3869 1 16.6761 1.94821 18.364 3.63604C20.0518 5.32387 21 7.61305 21 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12 13C13.6569 13 15 11.6569 15 10C15 8.34315 13.6569 7 12 7C10.3431 7 9 8.34315 9 10C9 11.6569 10.3431 13 12 13Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>{{ task.location }}</span>
        </div>
        
        <div class="info-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>{{ task.type }}</span>
        </div>
        
        <div class="time-info">
          <div class="time-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
              <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
              <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
              <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
            </svg>
            <span class="time-label">开始：</span>
            <span class="time-value">{{ task.startTime }}</span>
          </div>
          
          <div class="time-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
              <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
              <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
              <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
            </svg>
            <span class="time-label">结束：</span>
            <span class="time-value">{{ task.endTime }}</span>
          </div>
        </div>
      </div>
      
      <div class="task-description">
        <p>{{ task.description }}</p>
      </div>
      
      <div class="task-footer">
        <div class="task-price">
          <span class="price-label">预算：</span>
          <span class="price-amount">¥{{ task.budget }}</span>
        </div>
      </div>
    </div>
    
  </div>
</template>

<script>
export default {
  name: 'TaskCard',
  props: {
    task: {
      type: Object,
      required: true
    }
  },
  methods: {
    goToDetail() {
      // 优先从登录用户获取角色，否则从路由参数获取，默认为 customer
      let role = 'customer'
      
      // 检查是否有登录用户
      const currentUser = sessionStorage.getItem('currentUser')
      if (currentUser) {
        const user = JSON.parse(currentUser)
        role = user.role
      } else {
        // 未登录时从路由参数获取
        role = this.$route.query.role || 'customer'
      }
      
      this.$router.push(`/task/${this.task.id}?role=${role}`)
    }
  }
}
</script>

<style scoped>
.task-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  border: 1px solid #f0f0f0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.task-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(116, 185, 255, 0.15);
  border-color: #74b9ff;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.task-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
  flex: 1;
  line-height: 1.4;
}

.task-category {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  margin-left: 10px;
}

.task-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 15px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.info-item svg {
  color: #74b9ff;
  flex-shrink: 0;
}

.time-info {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.time-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #666;
  font-size: 13px;
  margin-bottom: 4px;
}

.time-item:last-child {
  margin-bottom: 0;
}

.time-item svg {
  color: #00b894;
  flex-shrink: 0;
}

.time-label {
  font-weight: 500;
  color: #888;
}

.time-value {
  color: #333;
  font-weight: 500;
}

.task-description {
  margin-bottom: 15px;
  flex: 1;
}

.task-description p {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.task-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.task-price {
  display: flex;
  align-items: center;
  gap: 4px;
}

.price-label {
  color: #666;
  font-size: 14px;
}

.price-amount {
  color: #00b894;
  font-size: 16px;
  font-weight: 600;
}



@media (max-width: 768px) {
  .task-card {
    padding: 15px;
  }
  
  .task-title {
    font-size: 16px;
  }
  
  .task-category {
    font-size: 11px;
    padding: 3px 8px;
  }
  
  .task-description p {
    font-size: 13px;
  }
  
  .price-amount {
    font-size: 14px;
  }
}
</style>
