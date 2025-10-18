<template>
  <div class="admin-users">
    <div class="header">
      <h2>用户管理</h2>
      <div class="filters">
        <!-- 角色筛选 -->
        <select v-model="filters.role_id" @change="loadUsers" class="filter-select">
          <option value="">所有角色</option>
          <option value="1">客户</option>
          <option value="2">服务提供者</option>
          <option value="3">管理员</option>
        </select>

        <!-- 排序选择 -->
        <select v-model="filters.sort_by" @change="loadUsers" class="filter-select">
          <option value="created_at">注册时间</option>
          <option value="username">用户名</option>
          <option value="email">邮箱</option>
        </select>

        <select v-model="filters.order" @change="loadUsers" class="filter-select">
          <option value="desc">降序</option>
          <option value="asc">升序</option>
        </select>

        <!-- 每页数量 -->
        <select v-model="filters.limit" @change="loadUsers" class="filter-select">
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
      <button @click="loadUsers" class="retry-btn">重试</button>
    </div>

    <!-- 用户列表 -->
    <div v-if="!loading && !error" class="users-content">
      <div class="stats">
        <p>共找到 <strong>{{ total }}</strong> 个用户</p>
      </div>

      <div class="users-table">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>用户名</th>
              <th>邮箱</th>
              <th>角色</th>
              <th>注册时间</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id" class="user-row">
              <td>{{ user.id }}</td>
              <td class="username-cell">{{ user.username }}</td>
              <td class="email-cell">{{ user.email }}</td>
              <td>
                <span :class="['role-badge', `role-${user.role_id}`]">
                  {{ adminService.formatRole(user.role_id) }}
                </span>
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>{{ formatDate(user.updated_at) }}</td>
              <td class="actions">
                <button @click="viewUser(user)" class="action-btn view-btn">
                  查看
                </button>
                <button @click="deleteUser(user)" class="action-btn delete-btn">
                  删除
                </button>
              </td>
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

    <!-- 用户详情模态框 -->
    <div v-if="showUserModal" class="modal-overlay" @click="closeUserModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>用户详情</h3>
          <button @click="closeUserModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div v-if="selectedUser" class="user-details">
            <div class="detail-row">
              <label>用户ID:</label>
              <span>{{ selectedUser.id }}</span>
            </div>
            <div class="detail-row">
              <label>用户名:</label>
              <span>{{ selectedUser.username }}</span>
            </div>
            <div class="detail-row">
              <label>邮箱:</label>
              <span>{{ selectedUser.email }}</span>
            </div>
            <div class="detail-row">
              <label>角色:</label>
              <span :class="['role-badge', `role-${selectedUser.role_id}`]">
                {{ adminService.formatRole(selectedUser.role_id) }}
              </span>
            </div>
            <div class="detail-row">
              <label>注册时间:</label>
              <span>{{ formatDate(selectedUser.created_at) }}</span>
            </div>
            <div class="detail-row">
              <label>更新时间:</label>
              <span>{{ formatDate(selectedUser.updated_at) }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="closeUserModal" class="btn btn-secondary">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import adminService from '@/services/adminService.js'

export default {
  name: 'AdminUsers',
  data() {
    return {
      users: [],
      total: 0,
      loading: false,
      error: null,
      showUserModal: false,
      selectedUser: null,
      filters: {
        role_id: '',
        sort_by: 'created_at',
        order: 'desc',
        page: 1,
        limit: 20
      }
    }
  },
  created() {
    this.loadUsers()
  },
  methods: {
    async loadUsers() {
      this.loading = true
      this.error = null
      
      try {
        const response = await adminService.getAllUsers(this.filters)
        this.users = response.items || []
        this.total = response.total || 0
      } catch (error) {
        this.error = error.message
        console.error('加载用户失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    async viewUser(user) {
      try {
        this.selectedUser = await adminService.getUserById(user.id)
        this.showUserModal = true
      } catch (error) {
        alert('获取用户详情失败: ' + error.message)
      }
    },
    
    async deleteUser(user) {
      if (!confirm(`确定要删除用户 "${user.username}" 吗？此操作不可撤销！`)) {
        return
      }
      
      try {
        await adminService.deleteUser(user.id)
        alert('用户删除成功！')
        this.loadUsers() // 重新加载用户列表
      } catch (error) {
        alert('删除用户失败: ' + error.message)
      }
    },
    
    closeUserModal() {
      this.showUserModal = false
      this.selectedUser = null
    },
    
    prevPage() {
      if (this.filters.page > 1) {
        this.filters.page--
        this.loadUsers()
      }
    },
    
    nextPage() {
      const maxPage = Math.ceil(this.total / this.filters.limit)
      if (this.filters.page < maxPage) {
        this.filters.page++
        this.loadUsers()
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
.admin-users {
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

.users-table {
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

.user-row:hover {
  background: #f8f9fa;
}

.username-cell, .email-cell {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.role-badge.role-1 {
  background: #d1ecf1;
  color: #0c5460;
}

.role-badge.role-2 {
  background: #d4edda;
  color: #155724;
}

.role-badge.role-3 {
  background: #f8d7da;
  color: #721c24;
}

.actions {
  white-space: nowrap;
}

.action-btn {
  padding: 4px 8px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  margin-right: 5px;
  transition: all 0.2s;
}

.view-btn {
  background: #007bff;
  color: white;
}

.view-btn:hover {
  background: #0056b3;
}

.delete-btn {
  background: #dc3545;
  color: white;
}

.delete-btn:hover {
  background: #c82333;
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

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 20px;
}

.user-details {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.detail-row label {
  font-weight: 600;
  color: #333;
  min-width: 80px;
}

.detail-row span {
  color: #666;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}
</style>
