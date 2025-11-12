<template>
  <nav class="navbar" :class="{ 'customer-theme': currentRole === 'customer' }">
    <div class="navbar-container">
      <div class="navbar-brand">
        <h2>任务平台</h2>
      </div>
      
      <!-- 已登录用户菜单 -->
      <ul v-if="isLoggedIn" class="navbar-menu">
        <li class="navbar-item" v-for="item in menuItems" :key="item.path">
          <router-link :to="item.path" class="navbar-link" :class="{ active: $route.path === item.path }">
            {{ item.label }}
          </router-link>
        </li>
      </ul>
      
      <!-- 用户状态区域 -->
      <div class="navbar-user">
        <div v-if="isLoggedIn" class="user-info">
          <span class="user-name">{{ currentUser.username }}</span>
          <span class="user-role">{{ 
            currentUser.role === 'customer' ? '客户' : 
            currentUser.role === 'provider' ? '服务提供者' : 
            currentUser.role === 'admin' ? '管理员' : '用户' 
          }}</span>
          <button @click="handleLogout" class="logout-btn">退出</button>
        </div>
        <div v-else class="auth-buttons">
          <router-link to="/login" class="auth-btn login-btn">登录</router-link>
          <router-link to="/register" class="auth-btn register-btn">注册</router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
export default {
  name: 'NavBar',
  data() {
    return {
      currentUser: null
    }
  },
  computed: {
    isLoggedIn() {
      return !!this.currentUser
    },
    currentRole() {
      if (this.currentUser) {
        return this.currentUser.role
      }
      // 从路由参数获取角色（用于未登录时的默认显示）
      return this.$route.query.role || 'customer'
    },
    menuItems() {
      if (this.currentRole === 'provider') {
        return [
          { path: '/?role=provider', label: '寻找任务' },
          { path: '/my-tasks?role=provider', label: '我的任务' },
          { path: '/messages?role=provider', label: '我的消息' },
          { path: '/profile?role=provider', label: '个人信息' }
        ]
      } else if (this.currentRole === 'admin') {
        return [
          { path: '/admin', label: '管理员控制台' }
        ]
      } else {
        return [
          { path: '/?role=customer', label: '我的发布' },
          { path: '/customer/orders?role=customer', label: '我的订单' },
          { path: '/my-tasks?role=customer', label: '我的任务' },
          { path: '/messages?role=customer', label: '我的消息' },
          { path: '/profile?role=customer', label: '个人信息' }
        ]
      }
    }
  },
  created() {
    this.checkLoginStatus()
  },
  methods: {
    checkLoginStatus() {
      const user = sessionStorage.getItem('currentUser')
      if (user) {
        this.currentUser = JSON.parse(user)
      }
    },
    handleLogout() {
      sessionStorage.removeItem('currentUser')
      this.currentUser = null
      alert('已退出登录')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.navbar {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.navbar.customer-theme {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
}

.user-name {
  font-weight: 600;
  font-size: 14px;
}

.user-role {
  background: rgba(255, 255, 255, 0.2);
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.auth-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.auth-btn {
  padding: 8px 16px;
  border-radius: 6px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.login-btn {
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
}

.login-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}

.register-btn {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.register-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.navbar-brand h2 {
  color: white;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.navbar-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 30px;
}

.navbar-item {
  margin: 0;
}

.navbar-link {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  transition: all 0.3s ease;
  font-weight: 500;
  position: relative;
}

.navbar-link:hover {
  background-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.navbar-link.active {
  background-color: rgba(255, 255, 255, 0.25);
  font-weight: 600;
}

.navbar-link.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 2px;
  background-color: white;
  border-radius: 1px;
}

@media (max-width: 768px) {
  .navbar-container {
    flex-direction: column;
    height: auto;
    padding: 15px 20px;
  }
  
  .navbar-menu {
    margin-top: 15px;
    gap: 15px;
  }
  
  .navbar-brand h2 {
    font-size: 20px;
  }
}
</style>
