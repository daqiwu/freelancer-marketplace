<template>
  <div class="admin-dashboard">
    <div class="container">
      <h1 class="page-title">管理员控制台</h1>
      
      <!-- 导航标签 -->
      <div class="tabs">
        <button 
          @click="activeTab = 'orders'" 
          :class="['tab', { active: activeTab === 'orders' }]"
        >
          订单管理
        </button>
        <button 
          @click="activeTab = 'users'" 
          :class="['tab', { active: activeTab === 'users' }]"
        >
          用户管理
        </button>
      </div>

      <!-- 订单管理 -->
      <div v-if="activeTab === 'orders'" class="tab-content">
        <AdminOrders />
      </div>

      <!-- 用户管理 -->
      <div v-if="activeTab === 'users'" class="tab-content">
        <AdminUsers />
      </div>

      <!-- 访问拒绝 -->
      <div v-if="showAccessDenied" class="access-denied">
        <div class="denied-content">
          <h2>🚫 访问被拒绝</h2>
          <p>您没有管理员权限，无法访问此页面。</p>
          <p>请联系系统管理员获取权限。</p>
          <button @click="$router.push('/')" class="back-btn">返回首页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import AdminOrders from '@/components/AdminOrders.vue'
import AdminUsers from '@/components/AdminUsers.vue'
import adminService from '@/services/adminService.js'

export default {
  name: 'AdminDashboard',
  components: {
    AdminOrders,
    AdminUsers
  },
  data() {
    return {
      activeTab: 'orders',
      showAccessDenied: false
    }
  },
  created() {
    this.checkAdminAccess()
  },
  methods: {
    checkAdminAccess() {
      if (!adminService.isAuthenticated()) {
        alert('请先登录')
        this.$router.push('/login')
        return
      }
      
      if (!adminService.isAdmin()) {
        this.showAccessDenied = true
        return
      }
    }
  }
}
</script>

<style scoped>
.admin-dashboard {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.page-title {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
  font-size: 2.5rem;
  font-weight: bold;
}

.tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  border-bottom: 2px solid #e0e0e0;
}

.tab {
  padding: 15px 30px;
  border: none;
  background: none;
  font-size: 1.1rem;
  font-weight: 500;
  color: #666;
  cursor: pointer;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
}

.tab:hover {
  color: #007bff;
  background-color: #f8f9fa;
}

.tab.active {
  color: #007bff;
  border-bottom-color: #007bff;
  background-color: #f8f9fa;
}

.tab-content {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 30px;
}

.access-denied {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.denied-content {
  text-align: center;
  padding: 40px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  max-width: 400px;
}

.denied-content h2 {
  color: #dc3545;
  margin-bottom: 20px;
}

.denied-content p {
  color: #666;
  margin-bottom: 10px;
}

.back-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 20px;
  font-size: 16px;
}

.back-btn:hover {
  background: #0056b3;
}
</style>
