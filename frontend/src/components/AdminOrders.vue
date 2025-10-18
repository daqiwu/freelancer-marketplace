<template>
  <div class="admin-orders">
    <div class="header">
      <h2>订单管理</h2>
      <div class="filters">
        <!-- 状态筛选 -->
        <select v-model="filters.status" @change="loadOrders" class="filter-select">
          <option value="">所有状态</option>
          <option value="pending">待处理</option>
          <option value="accepted">已接受</option>
          <option value="in_progress">进行中</option>
          <option value="completed">已完成</option>
          <option value="reviewed">已评价</option>
          <option value="cancelled">已取消</option>
        </select>

        <!-- 排序选择 -->
        <select v-model="filters.sort_by" @change="loadOrders" class="filter-select">
          <option value="created_at">创建时间</option>
          <option value="price">价格</option>
          <option value="status">状态</option>
        </select>

        <select v-model="filters.order" @change="loadOrders" class="filter-select">
          <option value="desc">降序</option>
          <option value="asc">升序</option>
        </select>

        <!-- 每页数量 -->
        <select v-model="filters.limit" @change="loadOrders" class="filter-select">
          <option value="10">10条/页</option>
          <option value="20">20条/页</option>
          <option value="50">50条/页</option>
        </select>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 错误信息 -->
    <div v-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadOrders" class="retry-btn">重试</button>
    </div>

    <!-- 订单列表 -->
    <div v-if="!loading && !error" class="orders-content">
      <div class="stats">
        <p>共找到 <strong>{{ total }}</strong> 个订单</p>
      </div>

      <div class="orders-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>标题</th>
              <th>价格</th>
              <th>地点</th>
              <th>状态</th>
              <th>客户ID</th>
              <th>服务商ID</th>
              <th>创建时间</th>
              <th>更新时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="order in orders" :key="order.id" class="order-row">
              <td>{{ order.id }}</td>
              <td class="title-cell">{{ order.title }}</td>
              <td class="price-cell">¥{{ order.price.toFixed(2) }}</td>
              <td>{{ adminService.formatLocation(order.location) }}</td>
              <td>
                <span :class="['status-badge', order.status]">
                  {{ adminService.formatOrderStatus(order.status) }}
                </span>
              </td>
              <td>{{ order.customer_id }}</td>
              <td>{{ order.provider_id || '-' }}</td>
              <td>{{ formatDate(order.created_at) }}</td>
              <td>{{ formatDate(order.updated_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <button 
          @click="prevPage" 
          :disabled="filters.page <= 1"
          class="page-btn"
        >
          上一页
        </button>
        
        <span class="page-info">
          第 {{ filters.page }} 页，共 {{ Math.ceil(total / filters.limit) }} 页
        </span>
        
        <button 
          @click="nextPage" 
          :disabled="filters.page >= Math.ceil(total / filters.limit)"
          class="page-btn"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import adminService from '@/services/adminService.js'

export default {
  name: 'AdminOrders',
  data() {
    return {
      orders: [],
      total: 0,
      loading: false,
      error: null,
      filters: {
        status: '',
        sort_by: 'created_at',
        order: 'desc',
        page: 1,
        limit: 20
      }
    }
  },
  created() {
    this.loadOrders()
  },
  methods: {
    async loadOrders() {
      this.loading = true
      this.error = null
      
      try {
        const response = await adminService.getAllOrders(this.filters)
        this.orders = response.items || []
        this.total = response.total || 0
      } catch (error) {
        this.error = error.message
        console.error('加载订单失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    prevPage() {
      if (this.filters.page > 1) {
        this.filters.page--
        this.loadOrders()
      }
    },
    
    nextPage() {
      const maxPage = Math.ceil(this.total / this.filters.limit)
      if (this.filters.page < maxPage) {
        this.filters.page++
        this.loadOrders()
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN')
    }
  },
  computed: {
    adminService() {
      return adminService
    }
  }
}
</script>

<style scoped>
.admin-orders {
  padding: 20px 0;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.header h2 {
  color: #333;
  margin: 0;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 14px;
}

.loading {
  text-align: center;
  padding: 40px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 40px;
  color: #dc3545;
}

.retry-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.stats {
  margin-bottom: 20px;
  color: #666;
}

.orders-table {
  overflow-x: auto;
  margin-bottom: 20px;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

th, td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.order-row:hover {
  background: #f8f9fa;
}

.title-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price-cell {
  font-weight: 600;
  color: #28a745;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
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

.status-badge.reviewed {
  background: #e2e3e5;
  color: #383d41;
}

.status-badge.cancelled {
  background: #f8d7da;
  color: #721c24;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}
</style>
