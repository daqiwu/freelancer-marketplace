<template>
  <div class="messages-page" :class="{ 'customer-theme': $route.query.role === 'customer' }">
    <NavBar />
    
    <div class="main-content">
      <div class="page-header">
        <h1>我的消息</h1>
        <p>查看系统通知和重要消息</p>
      </div>

      <!-- 消息统计 -->
      <div class="message-stats">
        <div class="stat-item">
          <div class="stat-number">{{ totalMessages }}</div>
          <div class="stat-label">总消息</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ unreadMessages }}</div>
          <div class="stat-label">未读消息</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ todayMessages }}</div>
          <div class="stat-label">今日消息</div>
        </div>
      </div>

      <!-- 消息列表 -->
      <div class="messages-section">
        <div class="section-header">
          <h2>系统消息</h2>
          <div class="filter-tabs">
            <button 
              v-for="tab in tabs" 
              :key="tab.key"
              :class="['tab-btn', { active: activeTab === tab.key }]"
              @click="activeTab = tab.key"
            >
              {{ tab.label }}
            </button>
          </div>
        </div>

        <div v-if="filteredMessages.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>暂无消息</h3>
          <p>您当前没有{{ getCurrentTabLabel() }}消息</p>
        </div>

        <div v-else class="message-list">
          <div v-for="message in filteredMessages" :key="message.id" class="message-card" :class="{ unread: !message.read }">
            <div class="message-header">
              <div class="message-title">
                <h3>{{ message.title }}</h3>
                <span v-if="!message.read" class="unread-badge">未读</span>
              </div>
              <div class="message-meta">
                <span class="message-time">{{ formatTime(message.createdAt) }}</span>
                <span class="message-type" :class="message.type">{{ getTypeLabel(message.type) }}</span>
              </div>
            </div>
            
            <div class="message-content">
              <div class="content-preview" :class="{ expanded: message.expanded }">
                <p>{{ message.content }}</p>
              </div>
              <button 
                v-if="message.content.length > 100" 
                class="expand-btn" 
                @click="toggleExpand(message.id)"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path v-if="!message.expanded" d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path v-else d="M18 15L12 9L6 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                {{ message.expanded ? '收起' : '展开' }}
              </button>
            </div>

            <div class="message-actions">
              <button 
                v-if="!message.read" 
                class="action-btn mark-read" 
                @click="markAsRead(message.id)"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                标记已读
              </button>
              <button class="action-btn delete" @click="deleteMessage(message.id)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 6H5H21M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                删除
              </button>
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
  name: 'MessagesPage',
  components: {
    NavBar
  },
  data() {
    return {
      activeTab: 'all',
      tabs: [
        { key: 'all', label: '全部' },
        { key: 'unread', label: '未读' },
        { key: 'system', label: '系统通知' },
        { key: 'task', label: '任务相关' }
      ],
      messages: [
        {
          id: 1,
          title: '欢迎使用任务平台！',
          content: '欢迎您加入我们的任务平台！在这里您可以找到各种有趣的任务，也可以发布自己的需求。我们致力于为每一位用户提供优质的服务体验。如果您在使用过程中遇到任何问题，请随时联系我们的客服团队。祝您使用愉快！',
          type: 'system',
          read: false,
          createdAt: new Date('2024-01-15 10:30:00'),
          expanded: false
        },
        {
          id: 2,
          title: '您的新任务申请已通过',
          content: '恭喜！您申请的"网站前端开发项目"任务已通过审核，现在可以开始工作了。请及时与客户联系，确认具体的项目细节和时间安排。',
          type: 'task',
          read: true,
          createdAt: new Date('2024-01-14 15:20:00'),
          expanded: false
        },
        {
          id: 3,
          title: '系统维护通知',
          content: '为了提供更好的服务，我们将在今晚22:00-24:00进行系统维护升级。维护期间可能会影响部分功能的使用，请您提前做好相关准备。给您带来的不便敬请谅解。',
          type: 'system',
          read: false,
          createdAt: new Date('2024-01-13 09:15:00'),
          expanded: false
        },
        {
          id: 4,
          title: '任务完成确认',
          content: '您的任务"移动应用UI设计"已完成，客户已确认验收。任务款项将在3个工作日内到账，请注意查收。感谢您的优质服务！',
          type: 'task',
          read: true,
          createdAt: new Date('2024-01-12 16:45:00'),
          expanded: false
        },
        {
          id: 5,
          title: '平台功能更新',
          content: '我们很高兴地宣布，平台新增了以下功能：1. 任务搜索优化，支持更精准的筛选条件；2. 消息推送功能，重要通知及时送达；3. 个人资料管理，支持头像上传和详细信息编辑；4. 任务进度跟踪，实时了解任务状态。这些更新将为您提供更好的使用体验，欢迎体验新功能！',
          type: 'system',
          read: true,
          createdAt: new Date('2024-01-10 14:00:00'),
          expanded: false
        }
      ]
    }
  },
  computed: {
    totalMessages() {
      return this.messages.length
    },
    unreadMessages() {
      return this.messages.filter(m => !m.read).length
    },
    todayMessages() {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      return this.messages.filter(m => {
        const messageDate = new Date(m.createdAt)
        messageDate.setHours(0, 0, 0, 0)
        return messageDate.getTime() === today.getTime()
      }).length
    },
    filteredMessages() {
      if (this.activeTab === 'all') {
        return this.messages
      } else if (this.activeTab === 'unread') {
        return this.messages.filter(m => !m.read)
      } else {
        return this.messages.filter(m => m.type === this.activeTab)
      }
    }
  },
  methods: {
    getCurrentTabLabel() {
      const tab = this.tabs.find(t => t.key === this.activeTab)
      return tab ? tab.label : ''
    },
    getTypeLabel(type) {
      const typeMap = {
        'system': '系统通知',
        'task': '任务相关'
      }
      return typeMap[type] || '其他'
    },
    formatTime(date) {
      const now = new Date()
      const messageDate = new Date(date)
      const diffTime = now - messageDate
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) {
        return messageDate.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      } else if (diffDays === 1) {
        return '昨天 ' + messageDate.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
      } else if (diffDays < 7) {
        return diffDays + '天前'
      } else {
        return messageDate.toLocaleDateString('zh-CN')
      }
    },
    toggleExpand(messageId) {
      const message = this.messages.find(m => m.id === messageId)
      if (message) {
        message.expanded = !message.expanded
      }
    },
    markAsRead(messageId) {
      const message = this.messages.find(m => m.id === messageId)
      if (message) {
        message.read = true
      }
    },
    deleteMessage(messageId) {
      if (confirm('确定要删除这条消息吗？')) {
        const index = this.messages.findIndex(m => m.id === messageId)
        if (index !== -1) {
          this.messages.splice(index, 1)
        }
      }
    }
  }
}
</script>

<style scoped>
.messages-page {
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
  margin-bottom: 30px;
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

.message-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  background: white;
  padding: 25px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #74b9ff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.messages-section {
  background: white;
  border-radius: 12px;
  padding: 30px;
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

.filter-tabs {
  display: flex;
  gap: 10px;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid #e9ecef;
  background: white;
  color: #666;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  border-color: #74b9ff;
  color: #74b9ff;
}

.tab-btn.active {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border-color: transparent;
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
  margin: 0;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-card {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.3s ease;
}

.message-card:hover {
  border-color: #74b9ff;
  box-shadow: 0 2px 8px rgba(116, 185, 255, 0.1);
}

.message-card.unread {
  background: #f0f8ff;
  border-color: #74b9ff;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.message-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
}

.message-title h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.unread-badge {
  background: #ff6b6b;
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
}

.message-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 5px;
}

.message-time {
  color: #999;
  font-size: 12px;
}

.message-type {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.message-type.system {
  background: #e3f2fd;
  color: #1976d2;
}

.message-type.task {
  background: #e8f5e8;
  color: #2e7d32;
}

.message-content {
  margin-bottom: 15px;
}

.content-preview {
  position: relative;
}

.content-preview p {
  color: #666;
  line-height: 1.6;
  margin: 0;
  font-size: 14px;
}

.content-preview:not(.expanded) p {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.expand-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 10px;
  padding: 4px 8px;
  background: none;
  border: none;
  color: #74b9ff;
  font-size: 12px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.expand-btn:hover {
  color: #a29bfe;
}

.message-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mark-read {
  background: #d4edda;
  color: #155724;
}

.mark-read:hover {
  background: #c3e6cb;
}

.delete {
  background: #f8d7da;
  color: #721c24;
}

.delete:hover {
  background: #f5c6cb;
}

/* Customer主题颜色 */
.customer-theme .stat-number {
  color: #00b894;
}

.customer-theme .tab-btn.active {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .tab-btn:hover {
  border-color: #00b894;
  color: #00b894;
}

.customer-theme .empty-icon {
  color: #00b894;
}

.customer-theme .browse-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .browse-btn:hover {
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

.customer-theme .message-card.unread {
  background: #f0fff4;
  border-color: #00b894;
}

.customer-theme .unread-badge {
  background: #00b894;
}

.customer-theme .expand-btn {
  color: #00b894;
}

.customer-theme .expand-btn:hover {
  color: #00a085;
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
  
  .message-stats {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .messages-section {
    padding: 20px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .filter-tabs {
    width: 100%;
    justify-content: space-between;
  }
  
  .message-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .message-meta {
    align-items: flex-start;
  }
  
  .message-actions {
    justify-content: flex-start;
  }
}
</style>