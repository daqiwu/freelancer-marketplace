<template>
  <div class="customer-orders-page">
    <NavBar />
    
    <div class="main-content">
      <div class="page-header">
        <h1>我的订单</h1>
        <p>管理您的所有订单</p>
      </div>

      <!-- 订单统计 -->
      <div class="order-stats">
        <div class="stat-item">
          <div class="stat-number">{{ totalOrders }}</div>
          <div class="stat-label">总订单</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ pendingOrders }}</div>
          <div class="stat-label">待处理</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">{{ completedOrders }}</div>
          <div class="stat-label">已完成</div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <button @click="showPublishModal = true" class="btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 5V19M5 12H19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          发布新订单
        </button>
        <button @click="loadOrders" class="btn-secondary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 4V20H20V4H4ZM2 2H22V22H2V2Z" fill="currentColor"/>
          </svg>
          刷新
        </button>
      </div>

      <!-- 订单列表 -->
      <div class="orders-section">
        <div class="section-header">
          <h2>订单列表</h2>
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

        <div v-if="loading" class="loading-container">
          <div class="loading-spinner"></div>
          <p>正在加载订单...</p>
        </div>
        
        <div v-else-if="filteredOrders.length === 0" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="#74b9ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>暂无订单</h3>
          <p>您还没有发布任何订单</p>
          <button @click="showPublishModal = true" class="btn-primary">发布第一个订单</button>
        </div>

        <div v-else class="order-list">
          <div 
            v-for="order in filteredOrders" 
            :key="order.id" 
            class="order-card"
            :class="getOrderStatusClass(order.status)"
          >
            <div class="order-header">
              <div class="order-title">
                <h3>{{ order.title }}</h3>
                <span class="order-id">#{{ order.id }}</span>
              </div>
              <div class="order-status">
                <span :class="['status-badge', order.status]">
                  {{ getStatusText(order.status) }}
                </span>
              </div>
            </div>
            
            <div class="order-content">
              <div class="order-info">
                <div class="info-item">
                  <span class="label">价格:</span>
                  <span class="value">¥{{ order.price }}</span>
                </div>
                <div class="info-item">
                  <span class="label">地点:</span>
                  <span class="value">{{ order.location }}</span>
                </div>
                <div class="info-item">
                  <span class="label">创建时间:</span>
                  <span class="value">{{ formatDate(order.created_at) }}</span>
                </div>
              </div>
              
              <div class="order-actions">
                <button @click="viewOrderDetail(order)" class="btn-outline">
                  查看详情
                </button>
                <button 
                  v-if="canCancelOrder(order)" 
                  @click="cancelOrder(order)" 
                  class="btn-danger"
                >
                  取消订单
                </button>
                <button 
                  v-if="canPayOrder(order)" 
                  @click="payOrder(order)" 
                  class="btn-success"
                >
                  支付订单
                </button>
                <button 
                  v-if="canReviewOrder(order)" 
                  @click="openReviewModal(order)" 
                  class="btn-primary"
                >
                  评价订单
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 发布订单模态框 -->
    <div v-if="showPublishModal" class="modal-overlay" @click="closePublishModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>发布新订单</h3>
          <button @click="closePublishModal" class="close-btn">&times;</button>
        </div>
        
        <form @submit.prevent="publishOrder" class="modal-body">
          <div class="form-group">
            <label for="title">订单标题 *</label>
            <input 
              type="text" 
              id="title" 
              v-model="publishForm.title" 
              required
              placeholder="请输入订单标题"
            >
          </div>
          
          <div class="form-group">
            <label for="description">订单描述</label>
            <textarea 
              id="description" 
              v-model="publishForm.description" 
              placeholder="请详细描述您的需求"
              rows="4"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="price">价格 *</label>
            <input 
              type="number" 
              id="price" 
              v-model="publishForm.price" 
              required
              min="0"
              step="0.01"
              placeholder="请输入价格"
            >
          </div>
          
          <div class="form-group">
            <label for="location">地点 *</label>
            <select id="location" v-model="publishForm.location" required>
              <option value="">请选择地点</option>
              <option value="NORTH">北区</option>
              <option value="SOUTH">南区</option>
              <option value="EAST">东区</option>
              <option value="WEST">西区</option>
              <option value="MID">中区</option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="address">详细地址</label>
            <input 
              type="text" 
              id="address" 
              v-model="publishForm.address" 
              placeholder="请输入详细地址"
            >
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="closePublishModal" class="btn-secondary">取消</button>
            <button type="submit" :disabled="publishing" class="btn-primary">
              {{ publishing ? '发布中...' : '发布订单' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 评价订单模态框 -->
    <div v-if="showReviewModal" class="modal-overlay" @click="closeReviewModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>评价订单</h3>
          <button @click="closeReviewModal" class="close-btn">&times;</button>
        </div>
        
        <form @submit.prevent="submitReview" class="modal-body">
          <div class="form-group">
            <label>评分 *</label>
            <div class="star-rating">
              <button 
                v-for="star in 5" 
                :key="star"
                type="button"
                @click="reviewForm.stars = star"
                :class="['star', { active: star <= reviewForm.stars }]"
              >
                ★
              </button>
            </div>
          </div>
          
          <div class="form-group">
            <label for="content">评价内容</label>
            <textarea 
              id="content" 
              v-model="reviewForm.content" 
              placeholder="请分享您的使用体验"
              rows="4"
            ></textarea>
          </div>
          
          <div class="modal-footer">
            <button type="button" @click="closeReviewModal" class="btn-secondary">取消</button>
            <button type="submit" :disabled="reviewing" class="btn-primary">
              {{ reviewing ? '提交中...' : '提交评价' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import apiService from '@/services/api.js'

export default {
  name: 'CustomerOrdersPage',
  components: {
    NavBar
  },
  data() {
    return {
      loading: false,
      activeTab: 'all',
      tabs: [
        { key: 'all', label: '全部' },
        { key: 'pending', label: '待处理' },
        { key: 'accepted', label: '已接受' },
        { key: 'in_progress', label: '进行中' },
        { key: 'completed', label: '已完成' },
        { key: 'cancelled', label: '已取消' }
      ],
      orders: [],
      showPublishModal: false,
      showReviewModal: false,
      publishing: false,
      reviewing: false,
      publishForm: {
        title: '',
        description: '',
        price: '',
        location: '',
        address: ''
      },
      reviewForm: {
        order_id: null,
        stars: 5,
        content: ''
      }
    }
  },
  computed: {
    totalOrders() {
      return this.orders.length
    },
    pendingOrders() {
      return this.orders.filter(order => order.status === 'pending').length
    },
    completedOrders() {
      return this.orders.filter(order => order.status === 'completed' || order.status === 'reviewed').length
    },
    filteredOrders() {
      if (this.activeTab === 'all') {
        return this.orders
      }
      return this.orders.filter(order => order.status === this.activeTab)
    }
  },
  async mounted() {
    await this.loadOrders()
  },
  methods: {
    async loadOrders() {
      this.loading = true
      try {
        // 加载未完成订单
        const myOrders = await apiService.getMyOrders()
        // 加载历史订单
        const historyOrders = await apiService.getOrderHistory()
        
        // 合并并去重
        const allOrders = [...myOrders, ...historyOrders]
        const uniqueOrders = allOrders.filter((order, index, self) => 
          index === self.findIndex(o => o.id === order.id)
        )
        
        this.orders = uniqueOrders.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      } catch (error) {
        console.error('加载订单失败:', error)
        // 显示示例数据
        this.orders = this.getSampleOrders()
      } finally {
        this.loading = false
      }
    },
    
    getSampleOrders() {
      return [
        {
          id: 1,
          title: '网站开发项目',
          description: '需要一个响应式网站',
          status: 'pending',
          price: 5000,
          location: 'NORTH',
          created_at: '2025-01-10T10:00:00'
        },
        {
          id: 2,
          title: '移动应用设计',
          description: 'UI/UX设计服务',
          status: 'accepted',
          price: 3000,
          location: 'SOUTH',
          created_at: '2025-01-09T14:30:00'
        }
      ]
    },
    
    async publishOrder() {
      this.publishing = true
      try {
        const orderData = {
          title: this.publishForm.title,
          description: this.publishForm.description,
          price: parseFloat(this.publishForm.price),
          location: this.publishForm.location,
          address: this.publishForm.address
        }
        
        await apiService.publishOrder(orderData)
        
        alert('订单发布成功！')
        this.closePublishModal()
        await this.loadOrders()
        
      } catch (error) {
        console.error('发布订单失败:', error)
        alert('发布订单失败，请重试')
      } finally {
        this.publishing = false
      }
    },
    
    async cancelOrder(order) {
      if (!confirm(`确定要取消订单 "${order.title}" 吗？`)) {
        return
      }
      
      try {
        await apiService.cancelOrder(order.id)
        alert('订单已取消')
        await this.loadOrders()
      } catch (error) {
        console.error('取消订单失败:', error)
        alert('取消订单失败，请重试')
      }
    },
    
    async payOrder(order) {
      if (!confirm(`确定要支付订单 "${order.title}" (¥${order.price}) 吗？`)) {
        return
      }
      
      try {
        await apiService.payOrder(order.id)
        alert('支付成功！')
        await this.loadOrders()
      } catch (error) {
        console.error('支付失败:', error)
        alert('支付失败，请重试')
      }
    },
    
    openReviewModal(order) {
      this.reviewForm.order_id = order.id
      this.reviewForm.stars = 5
      this.reviewForm.content = ''
      this.showReviewModal = true
    },
    
    async submitReview() {
      this.reviewing = true
      try {
        await apiService.reviewOrder(this.reviewForm)
        alert('评价提交成功！')
        this.closeReviewModal()
        await this.loadOrders()
      } catch (error) {
        console.error('提交评价失败:', error)
        alert('提交评价失败，请重试')
      } finally {
        this.reviewing = false
      }
    },
    
    viewOrderDetail(order) {
      // 显示订单详情信息
      alert(`订单详情：\n标题：${order.title}\n状态：${this.getStatusText(order.status)}\n价格：¥${order.price}\n地点：${order.location}`)
    },
    
    closePublishModal() {
      this.showPublishModal = false
      this.publishForm = {
        title: '',
        description: '',
        price: '',
        location: '',
        address: ''
      }
    },
    
    closeReviewModal() {
      this.showReviewModal = false
      this.reviewForm = {
        order_id: null,
        stars: 5,
        content: ''
      }
    },
    
    getOrderStatusClass(status) {
      return `status-${status}`
    },
    
    getStatusText(status) {
      const statusMap = {
        'pending': '待处理',
        'accepted': '已接受',
        'in_progress': '进行中',
        'completed': '已完成',
        'cancelled': '已取消',
        'reviewed': '已评价'
      }
      return statusMap[status] || status
    },
    
    canCancelOrder(order) {
      return order.status === 'pending' || order.status === 'accepted'
    },
    
    canPayOrder(order) {
      return order.status === 'completed' && !order.paid
    },
    
    canReviewOrder(order) {
      return order.status === 'completed' && order.paid
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.customer-orders-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 32px;
  font-weight: 700;
  color: #333;
  margin: 0 0 10px 0;
}

.page-header p {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.order-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-item {
  background: white;
  padding: 20px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #74b9ff;
  margin-bottom: 5px;
}

.stat-label {
  color: #666;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 30px;
}

.btn-primary, .btn-secondary, .btn-outline, .btn-danger, .btn-success {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #74b9ff;
  color: white;
}

.btn-primary:hover {
  background: #0984e3;
}

.btn-secondary {
  background: #ddd;
  color: #333;
}

.btn-secondary:hover {
  background: #ccc;
}

.btn-outline {
  background: transparent;
  color: #74b9ff;
  border: 1px solid #74b9ff;
}

.btn-outline:hover {
  background: #74b9ff;
  color: white;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background: #c0392b;
}

.btn-success {
  background: #00b894;
  color: white;
}

.btn-success:hover {
  background: #00a085;
}

.orders-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.filter-tabs {
  display: flex;
  gap: 5px;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  color: #666;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
}

.tab-btn:hover {
  background: #f8f9fa;
}

.tab-btn.active {
  background: #74b9ff;
  color: white;
  border-color: #74b9ff;
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
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
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

.order-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.order-card {
  border: 1px solid #e1e5e9;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.order-card:hover {
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.order-title h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0 0 5px 0;
}

.order-id {
  color: #999;
  font-size: 12px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.pending {
  background: #fff3cd;
  color: #856404;
}

.status-badge.accepted {
  background: #d1ecf1;
  color: #0c5460;
}

.status-badge.in_progress {
  background: #d4edda;
  color: #155724;
}

.status-badge.completed {
  background: #cce5ff;
  color: #004085;
}

.status-badge.cancelled {
  background: #f8d7da;
  color: #721c24;
}

.order-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 15px;
}

.order-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  gap: 10px;
}

.info-item .label {
  color: #666;
  font-size: 14px;
  min-width: 60px;
}

.info-item .value {
  color: #333;
  font-size: 14px;
  font-weight: 500;
}

.order-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e1e5e9;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #74b9ff;
  box-shadow: 0 0 0 3px rgba(116, 185, 255, 0.1);
}

.star-rating {
  display: flex;
  gap: 5px;
}

.star {
  background: none;
  border: none;
  font-size: 24px;
  color: #ddd;
  cursor: pointer;
  transition: color 0.3s ease;
}

.star.active {
  color: #ffd700;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #e1e5e9;
}

@media (max-width: 768px) {
  .main-content {
    padding: 15px;
  }
  
  .order-stats {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-tabs {
    flex-wrap: wrap;
  }
  
  .order-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .order-actions {
    justify-content: stretch;
  }
  
  .order-actions button {
    flex: 1;
  }
}
</style>
