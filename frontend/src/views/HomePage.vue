<template>
  <div class="home-page" :class="{ 'customer-theme': isCustomer }">
    <NavBar />
    
    <div class="main-content">
      <SearchBox @search="handleSearch" />
      
      <div class="tasks-section">
        <div class="section-header">
          <h2>{{ isCustomer ? '我的发布' : '热门任务' }}</h2>
          <div class="header-actions">
            <div v-if="!isCustomer" class="sort-options">
              <select v-model="sortBy" @change="handleSort" class="sort-select">
                <option value="latest">最新发布</option>
                <option value="price-high">价格从高到低</option>
                <option value="price-low">价格从低到高</option>
                <option value="deadline">截止时间</option>
              </select>
            </div>
            <button v-if="isCustomer" class="publish-btn" @click="publishTask">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              发布任务
            </button>
          </div>
        </div>
        
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>正在加载任务...</p>
        </div>
        
        <div v-else-if="filteredTasks.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 11H15M9 15H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H17C18.1046 3 19 3.89543 19 5V19C19 20.1046 18.1046 21 17 21Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>暂无任务</h3>
          <p>没有找到符合条件的任务，请尝试调整搜索条件</p>
        </div>
        
        <div v-else class="tasks-grid">
          <div v-for="task in paginatedTasks" :key="task.id" class="task-wrapper">
            <TaskCard :task="task" />
            <div v-if="isCustomer" class="task-actions">
              <button class="action-btn edit-btn" @click="editTask(task)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13M18.5 2.5C18.8978 2.10218 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10218 21.5 2.5C21.8978 2.89782 22.1213 3.43739 22.1213 4C22.1213 4.56261 21.8978 5.10218 21.5 5.5L12 15L8 16L9 12L18.5 2.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                修改
              </button>
              <button class="action-btn delete-btn" @click="deleteTask(task)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M3 6H5H21M8 6V4C8 3.46957 8.21071 2.96086 8.58579 2.58579C8.96086 2.21071 9.46957 2 10 2H14C14.5304 2 15.0391 2.21071 15.4142 2.58579C15.7893 2.96086 16 3.46957 16 4V6M19 6V20C19 20.5304 18.7893 21.0391 18.4142 21.4142C18.0391 21.7893 17.5304 22 17 22H7C6.46957 22 5.96086 21.7893 5.58579 21.4142C5.21071 21.0391 5 20.5304 5 20V6H19Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                删除
              </button>
            </div>
          </div>
        </div>
        
        <Pagination
          :current-page="currentPage"
          :total-pages="totalPages"
          :total-items="filteredTasks.length"
          :items-per-page="itemsPerPage"
          @page-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import SearchBox from '@/components/SearchBox.vue'
import TaskCard from '@/components/TaskCard.vue'
import Pagination from '@/components/Pagination.vue'

export default {
  name: 'HomePage',
  components: {
    NavBar,
    SearchBox,
    TaskCard,
    Pagination
  },
  data() {
    return {
      loading: false,
      searchQuery: '',
      selectedCategory: '全部',
      sortBy: 'latest',
      currentPage: 1,
      itemsPerPage: 8,
      tasks: [
        {
          id: 1,
          title: '网站前端开发项目',
          category: '技术开发',
          location: '北京市朝阳区',
          type: 'Web开发',
          description: '需要开发一个响应式的企业官网，包含首页、产品展示、关于我们等页面，要求使用Vue.js框架。',
          budget: 15000,
          startTime: '2024-01-20',
          endTime: '2024-02-15',
          status: 'open'
        },
        {
          id: 2,
          title: '品牌Logo设计',
          category: '设计创意',
          location: '上海市浦东新区',
          type: '平面设计',
          description: '为新兴科技公司设计现代化Logo，要求简洁大气，符合科技感定位。',
          budget: 3000,
          startTime: '2024-01-15',
          endTime: '2024-01-30',
          status: 'open'
        },
        {
          id: 3,
          title: '社交媒体营销推广',
          category: '营销推广',
          location: '广州市天河区',
          type: '数字营销',
          description: '负责公司在微信、微博、抖音等平台的日常运营和内容创作，提升品牌知名度。',
          budget: 8000,
          startTime: '2024-02-01',
          endTime: '2024-03-01',
          status: 'open'
        },
        {
          id: 4,
          title: '英语口语培训',
          category: '教育培训',
          location: '深圳市南山区',
          type: '在线教育',
          description: '为职场人士提供一对一英语口语培训，帮助提升商务英语沟通能力。',
          budget: 200,
          startTime: '2024-02-01',
          endTime: '2024-02-28',
          status: 'open'
        },
        {
          id: 5,
          title: '移动App UI设计',
          category: '设计创意',
          location: '杭州市西湖区',
          type: 'UI/UX设计',
          description: '设计一款电商类移动应用的完整UI界面，包括用户界面、交互流程等。',
          budget: 12000,
          startTime: '2024-01-25',
          endTime: '2024-02-20',
          status: 'open'
        },
        {
          id: 6,
          title: '数据分析报告',
          category: '技术开发',
          location: '成都市锦江区',
          type: '数据分析',
          description: '对用户行为数据进行深度分析，生成可视化报告，为产品优化提供建议。',
          budget: 5000,
          startTime: '2024-01-20',
          endTime: '2024-02-10',
          status: 'open'
        },
        {
          id: 7,
          title: '视频拍摄制作',
          category: '生活服务',
          location: '武汉市江汉区',
          type: '视频制作',
          description: '为企业拍摄宣传视频，包括脚本编写、拍摄、后期剪辑等全流程服务。',
          budget: 6000,
          startTime: '2024-02-15',
          endTime: '2024-03-15',
          status: 'open'
        },
        {
          id: 8,
          title: '微信公众号运营',
          category: '营销推广',
          location: '西安市雁塔区',
          type: '内容运营',
          description: '负责微信公众号的日常运营，包括内容策划、文章撰写、粉丝互动等。',
          budget: 4000,
          startTime: '2024-02-01',
          endTime: '2024-02-25',
          status: 'open'
        }
      ]
    }
  },
  computed: {
    isCustomer() {
      // 默认显示 customer 角色，除非明确指定为 provider
      return this.$route.query.role !== 'provider'
    },
    filteredTasks() {
      let filtered = this.tasks.filter(task => {
        const matchesSearch = !this.searchQuery || 
          task.title.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          task.description.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          task.location.toLowerCase().includes(this.searchQuery.toLowerCase())
        
        const matchesCategory = this.selectedCategory === '全部' || 
          task.category === this.selectedCategory
        
        return matchesSearch && matchesCategory
      })
      
      // 排序
      filtered.sort((a, b) => {
        switch (this.sortBy) {
          case 'price-high':
            return b.budget - a.budget
          case 'price-low':
            return a.budget - b.budget
          case 'deadline':
            return new Date(a.endTime) - new Date(b.endTime)
          case 'latest':
          default:
            return b.id - a.id
        }
      })
      
      return filtered
    },
    totalPages() {
      return Math.ceil(this.filteredTasks.length / this.itemsPerPage)
    },
    paginatedTasks() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredTasks.slice(start, end)
    }
  },
  methods: {
    handleSearch(searchData) {
      this.searchQuery = searchData.query
      this.selectedCategory = searchData.category
      this.currentPage = 1
    },
    handleSort() {
      this.currentPage = 1
    },
    handlePageChange(page) {
      this.currentPage = page
      window.scrollTo({ top: 0, behavior: 'smooth' })
    },
    publishTask() {
      // 获取当前用户角色
      const role = this.getCurrentRole()
      this.$router.push(`/publish-task?role=${role}`)
    },
    editTask(task) {
      // 获取当前用户角色
      const role = this.getCurrentRole()
      this.$router.push(`/task/${task.id}?role=${role}&edit=true`)
    },
    deleteTask(task) {
      if (confirm(`确定要删除任务"${task.title}"吗？`)) {
        const index = this.tasks.findIndex(t => t.id === task.id)
        if (index !== -1) {
          this.tasks.splice(index, 1)
          alert('任务已删除')
        }
      }
    },
    getCurrentRole() {
      // 优先从登录用户获取角色，否则从路由参数获取，默认为 customer
      const currentUser = sessionStorage.getItem('currentUser')
      if (currentUser) {
        const user = JSON.parse(currentUser)
        return user.role
      }
      return this.$route.query.role || 'customer'
    }
  }
}
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  min-height: calc(100vh - 60px);
}

.tasks-section {
  padding: 0 20px 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-top: 20px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
}

.section-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sort-select {
  padding: 8px 12px;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  background: white;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  outline: none;
  transition: all 0.3s ease;
}

.sort-select:focus {
  border-color: #74b9ff;
  box-shadow: 0 0 0 2px rgba(116, 185, 255, 0.1);
}

.publish-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.publish-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

/* Customer主题颜色 */
.customer-theme .publish-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .publish-btn:hover {
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

.task-wrapper {
  position: relative;
}

.task-actions {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.task-wrapper:hover .task-actions {
  opacity: 1;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-btn {
  background: #e3f2fd;
  color: #1976d2;
}

.edit-btn:hover {
  background: #bbdefb;
}

.delete-btn {
  background: #ffebee;
  color: #d32f2f;
}

.delete-btn:hover {
  background: #ffcdd2;
}

.tasks-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #666;
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

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
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

@media (max-width: 768px) {
  .tasks-section {
    padding: 0 15px 15px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
    margin-bottom: 20px;
  }
  
  .section-header h2 {
    font-size: 20px;
  }
  
  .tasks-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .sort-select {
    width: 100%;
  }
}
</style>
