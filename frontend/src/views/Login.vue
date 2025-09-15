<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-header">
        <h1>欢迎回来</h1>
        <p>请登录您的账户</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="form.username" 
            required
            placeholder="请输入用户名"
            :class="{ 'error': errors.username }"
          >
          <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="form.password" 
            required
            placeholder="请输入密码"
            :class="{ 'error': errors.password }"
          >
          <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
        </div>

        <div class="form-group">
          <label for="role">角色</label>
          <select id="role" v-model="form.role" required :class="{ 'error': errors.role }">
            <option value="">请选择角色</option>
            <option value="customer">客户 (Customer)</option>
            <option value="provider">服务提供者 (Provider)</option>
          </select>
          <span v-if="errors.role" class="error-message">{{ errors.role }}</span>
        </div>

        <button type="submit" class="login-btn" :disabled="loading">
          <svg v-if="loading" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z" fill="currentColor"/>
          </svg>
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <div class="login-footer">
        <p>还没有账户？ <router-link to="/register" class="register-link">立即注册</router-link></p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginPage',
  data() {
    return {
      loading: false,
      form: {
        username: '',
        password: '',
        role: ''
      },
      errors: {}
    }
  },
  methods: {
    validateForm() {
      this.errors = {}
      
      if (!this.form.username.trim()) {
        this.errors.username = '请输入用户名'
      }
      
      if (!this.form.password.trim()) {
        this.errors.password = '请输入密码'
      }
      
      if (!this.form.role) {
        this.errors.role = '请选择角色'
      }
      
      return Object.keys(this.errors).length === 0
    },
    async handleLogin() {
      if (!this.validateForm()) {
        return
      }
      
      this.loading = true
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      // 从本地存储获取用户数据
      const users = JSON.parse(localStorage.getItem('users') || '[]')
      const user = users.find(u => 
        u.username === this.form.username && 
        u.password === this.form.password && 
        u.role === this.form.role
      )
      
      if (user) {
        // 登录成功，保存用户信息到sessionStorage
        sessionStorage.setItem('currentUser', JSON.stringify({
          id: user.id,
          username: user.username,
          role: user.role
        }))
        
        this.loading = false
        alert('登录成功！')
        
        // 根据角色跳转到不同页面
        if (this.form.role === 'customer') {
          this.$router.push('/?role=customer')
        } else {
          this.$router.push('/?role=provider')
        }
      } else {
        this.loading = false
        alert('用户名、密码或角色错误，请检查后重试')
      }
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0 0 10px 0;
}

.login-header p {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select {
  padding: 12px 16px;
  border: 2px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: white;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group input.error,
.form-group select.error {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 12px;
  margin-top: 4px;
}

.login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.login-footer {
  text-align: center;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

.login-footer p {
  color: #666;
  font-size: 14px;
  margin: 0;
}

.register-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s ease;
}

.register-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

@media (max-width: 480px) {
  .login-container {
    padding: 30px 20px;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
}
</style>
