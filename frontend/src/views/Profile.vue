<template>
  <div class="profile-page" :class="{ 'customer-theme': $route.query.role === 'customer' }">
    <NavBar />
    
    <div class="main-content">
      <div class="page-header">
        <h1>个人信息</h1>
        <p>管理您的个人资料和账户设置</p>
      </div>

      <div class="profile-container">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-container">
          <div class="loading-spinner">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
              <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z" fill="currentColor"/>
            </svg>
          </div>
          <p>加载用户信息中...</p>
        </div>

        <!-- 个人信息展示 -->
        <div v-else-if="!isEditing" class="profile-display">
          <div class="profile-card">
            <div class="avatar-section">
              <div class="avatar">
                <img v-if="userInfo.avatar" :src="userInfo.avatar" :alt="userInfo.username">
                <div v-else class="avatar-placeholder">
                  <svg width="60" height="60" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                </div>
              </div>
              <button class="edit-avatar-btn" @click="editAvatar">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13M18.5 2.5C18.8978 2.10218 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10218 21.5 2.5C21.8978 2.89782 22.1213 3.43739 22.1213 4C22.1213 4.56261 21.8978 5.10218 21.5 5.5L12 15L8 16L9 12L18.5 2.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                更换头像
              </button>
            </div>
            
            <div class="user-info">
              <h2 class="username">{{ userInfo.username }}</h2>
              <div class="info-grid">
                <div class="info-item">
                  <div class="info-label">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M20 21V19C20 17.9391 19.5786 16.9217 18.8284 16.1716C18.0783 15.4214 17.0609 15 16 15H8C6.93913 15 5.92172 15.4214 5.17157 16.1716C4.42143 16.9217 4 17.9391 4 19V21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    用户名
                  </div>
                  <div class="info-value">{{ userInfo.username }}</div>
                </div>
                
                <div class="info-item">
                  <div class="info-label">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M22 16.92V19.92C22.0011 20.1985 21.9441 20.4742 21.8325 20.7293C21.7209 20.9845 21.5573 21.2136 21.3521 21.4019C21.1468 21.5901 20.9046 21.7335 20.6407 21.8227C20.3769 21.9119 20.0974 21.9451 19.82 21.92C16.7428 21.5856 13.787 20.5341 11.19 18.85C8.77382 17.3147 6.72533 15.2662 5.18999 12.85C3.49997 10.2412 2.44824 7.27099 2.11999 4.18C2.095 3.90347 2.12787 3.62476 2.21649 3.36162C2.30512 3.09849 2.44756 2.85669 2.63476 2.65162C2.82196 2.44655 3.0498 2.28271 3.30379 2.17052C3.55777 2.05833 3.83233 2.00026 4.10999 2H7.10999C7.59531 1.99522 8.06679 2.16708 8.43376 2.48353C8.80073 2.79999 9.04207 3.23945 9.11999 3.72C9.28562 4.68007 9.60683 5.62273 10.07 6.5C10.199 6.76126 10.2701 7.05063 10.2781 7.34562C10.2861 7.6406 10.2308 7.93387 10.1156 8.20657C10.0004 8.47927 9.82789 8.72483 9.60999 8.92L8.38999 10.14C9.62999 12.41 11.58 14.36 13.85 15.6L15.07 14.38C15.2652 14.1621 15.5107 13.9896 15.7834 13.8744C16.0561 13.7592 16.3494 13.7039 16.6444 13.7119C16.9394 13.7199 17.2287 13.791 17.49 13.92C18.3673 14.3832 19.3099 14.7044 20.27 14.87C20.7505 14.9479 21.1899 15.1892 21.5064 15.5562C21.8228 15.9231 21.9947 16.3946 21.99 16.88L22 16.92Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    手机号码
                  </div>
                  <div class="info-value">{{ userInfo.phone }}</div>
                </div>
                
                <div class="info-item">
                  <div class="info-label">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M4 4H20C21.1 4 22 4.9 22 6V18C22 19.1 21.1 20 20 20H4C2.9 20 2 19.1 2 18V6C2 4.9 2.9 4 4 4Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <polyline points="22,6 12,13 2,6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                    邮箱地址
                  </div>
                  <div class="info-value">{{ userInfo.email }}</div>
                </div>
                
                <div class="info-item">
                  <div class="info-label">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                      <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                      <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                      <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    注册时间
                  </div>
                  <div class="info-value">{{ userInfo.registerDate }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="action-buttons">
            <button class="edit-btn" @click="startEdit">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M11 4H4C3.46957 4 2.96086 4.21071 2.58579 4.58579C2.21071 4.96086 2 5.46957 2 6V20C2 20.5304 2.21071 21.0391 2.58579 21.4142C2.96086 21.7893 3.46957 22 4 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V13M18.5 2.5C18.8978 2.10218 19.4374 1.87868 20 1.87868C20.5626 1.87868 21.1022 2.10218 21.5 2.5C21.8978 2.89782 22.1213 3.43739 22.1213 4C22.1213 4.56261 21.8978 5.10218 21.5 5.5L12 15L8 16L9 12L18.5 2.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              编辑信息
            </button>
            <button class="change-password-btn" @click="changePassword">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                <circle cx="12" cy="16" r="1" stroke="currentColor" stroke-width="2"/>
                <path d="M7 11V7C7 5.67392 7.52678 4.40215 8.46447 3.46447C9.40215 2.52678 10.6739 2 12 2C13.3261 2 14.5979 2.52678 15.5355 3.46447C16.4732 4.40215 17 5.67392 17 7V11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              修改密码
            </button>
          </div>
        </div>

        <!-- 编辑模式 -->
        <div v-else class="profile-edit">
          <div class="edit-card">
            <div class="edit-header">
              <h2>编辑个人信息</h2>
              <button class="cancel-btn" @click="cancelEdit">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
                  <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
                </svg>
              </button>
            </div>
            
            <form @submit.prevent="saveProfile" class="edit-form">
              <div class="form-group">
                <label for="username">用户名</label>
                <input 
                  type="text" 
                  id="username" 
                  v-model="editForm.username" 
                  required
                  placeholder="请输入用户名"
                >
              </div>
              
              <div class="form-group">
                <label for="phone">手机号码</label>
                <input 
                  type="tel" 
                  id="phone" 
                  v-model="editForm.phone" 
                  required
                  placeholder="请输入手机号码"
                >
              </div>
              
              <div class="form-group">
                <label for="email">邮箱地址</label>
                <input 
                  type="email" 
                  id="email" 
                  v-model="editForm.email" 
                  required
                  placeholder="请输入邮箱地址"
                >
              </div>
              
              <div class="form-actions">
                <button type="button" class="cancel-btn" @click="cancelEdit">取消</button>
                <button type="submit" class="save-btn" :disabled="saving">
                  <svg v-if="saving" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z" fill="currentColor"/>
                  </svg>
                  {{ saving ? '保存中...' : '保存' }}
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- 修改密码模态框 -->
        <div v-if="showPasswordModal" class="modal-overlay" @click="closePasswordModal">
          <div class="password-modal" @click.stop>
            <div class="modal-header">
              <h3>修改密码</h3>
              <button class="close-btn" @click="closePasswordModal">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
              </button>
            </div>
            
            <form @submit.prevent="savePassword" class="password-form">
              <div class="form-group">
                <label for="currentPassword">当前密码</label>
                <input 
                  type="password" 
                  id="currentPassword" 
                  v-model="passwordForm.currentPassword" 
                  required
                  placeholder="请输入当前密码"
                >
              </div>
              
              <div class="form-group">
                <label for="newPassword">新密码</label>
                <input 
                  type="password" 
                  id="newPassword" 
                  v-model="passwordForm.newPassword" 
                  required
                  placeholder="请输入新密码"
                  minlength="6"
                >
              </div>
              
              <div class="form-group">
                <label for="confirmPassword">确认新密码</label>
                <input 
                  type="password" 
                  id="confirmPassword" 
                  v-model="passwordForm.confirmPassword" 
                  required
                  placeholder="请再次输入新密码"
                >
              </div>
              
              <div class="form-actions">
                <button type="button" class="cancel-btn" @click="closePasswordModal">取消</button>
                <button type="submit" class="save-btn" :disabled="savingPassword">
                  <svg v-if="savingPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z" fill="currentColor"/>
                  </svg>
                  {{ savingPassword ? '保存中...' : '保存' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import apiService from '@/services/api.js'

export default {
  name: 'ProfilePage',
  components: {
    NavBar
  },
  data() {
    return {
      isEditing: false,
      saving: false,
      showPasswordModal: false,
      savingPassword: false,
      loading: true,
      userInfo: {
        username: '',
        phone: '',
        email: '',
        registerDate: '',
        avatar: null
      },
      editForm: {
        username: '',
        phone: '',
        email: ''
      },
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    }
  },
  async created() {
    await this.loadUserProfile()
  },
  methods: {
    async loadUserProfile() {
      try {
        this.loading = true
        const profile = await apiService.getUserProfile()
        
        // 根据用户角色设置信息
        this.userInfo = {
          username: profile.username,
          email: profile.email,
          phone: '138-0000-1234',  // 临时硬编码，手机号功能暂时不实现
          registerDate: profile.created_at ? new Date(profile.created_at).toLocaleDateString() : '',
          avatar: null
        }
        
        this.loading = false
      } catch (error) {
        console.error('加载用户资料失败:', error)
        this.loading = false
        alert('加载用户资料失败，请重试')
      }
    },
    startEdit() {
      this.editForm = {
        username: this.userInfo.username,
        phone: this.userInfo.phone,
        email: this.userInfo.email
      }
      this.isEditing = true
    },
    cancelEdit() {
      this.isEditing = false
      this.editForm = {
        username: '',
        phone: '',
        email: ''
      }
    },
    async saveProfile() {
      try {
        this.saving = true
        
        console.log('开始保存用户资料...')
        console.log('编辑表单数据:', this.editForm)
        
        // 先测试获取用户信息
        console.log('获取当前用户信息...')
        const currentProfile = await apiService.getUserProfile()
        console.log('当前用户信息:', currentProfile)
        
        // 先更新用户基本信息
        console.log('更新用户基本信息...')
        await apiService.updateUserInfo({
          username: this.editForm.username,
          email: this.editForm.email
        })
        console.log('用户基本信息更新成功')
        
        // 根据角色调用不同的API
        if (currentProfile.role === 'customer') {
          console.log('更新客户资料...')
          await apiService.updateCustomerProfile({
            location: 'NORTH',
            address: this.editForm.phone || '未设置',
            budget_preference: 1000,
            balance: currentProfile.customer_profile?.balance || 0
          })
          console.log('客户资料更新成功')
        } else if (currentProfile.role === 'provider') {
          console.log('更新服务商资料...')
          await apiService.updateProviderProfile({
            skills: currentProfile.provider_profile?.skills || '',
            experience_years: currentProfile.provider_profile?.experience_years || 1,
            hourly_rate: currentProfile.provider_profile?.hourly_rate || 50,
            availability: currentProfile.provider_profile?.availability || 'Weekdays'
          })
          console.log('服务商资料更新成功')
        }
        
        // 更新本地用户信息
        this.userInfo.username = this.editForm.username
        this.userInfo.phone = this.editForm.phone
        this.userInfo.email = this.editForm.email
        
        this.saving = false
        this.isEditing = false
        
        console.log('保存完成')
        alert('个人信息保存成功！')
      } catch (error) {
        console.error('保存用户资料失败:', error)
        console.error('错误详情:', error.message)
        console.error('错误堆栈:', error.stack)
        this.saving = false
        alert(`保存失败: ${error.message}`)
      }
    },
    changePassword() {
      this.passwordForm = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
      this.showPasswordModal = true
    },
    closePasswordModal() {
      this.showPasswordModal = false
      this.passwordForm = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    },
    async savePassword() {
      if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
        alert('两次输入的新密码不一致，请重新输入')
        return
      }
      
      if (this.passwordForm.newPassword.length < 6) {
        alert('新密码长度不能少于6位')
        return
      }
      
      this.savingPassword = true
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      this.savingPassword = false
      this.closePasswordModal()
      
      alert('密码修改成功！')
    },
    editAvatar() {
      // 这里可以实现头像上传功能
      alert('头像上传功能待开发')
    }
  }
}
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f8f9fa;
}

.main-content {
  max-width: 800px;
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

.profile-container {
  position: relative;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.loading-spinner {
  margin-bottom: 20px;
}

.loading-spinner .spinner {
  color: #74b9ff;
  animation: spin 1s linear infinite;
}

.loading-container p {
  color: #666;
  font-size: 16px;
  margin: 0;
}

.profile-display {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.profile-card {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 4px solid #f0f0f0;
  position: relative;
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

/* Customer主题颜色 */
.customer-theme .avatar-placeholder {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .edit-avatar-btn {
  color: #00b894;
  border-color: #00b894;
}

.customer-theme .edit-avatar-btn:hover {
  background: #00b894;
  color: white;
  border-color: #00b894;
}

.customer-theme .info-label svg {
  color: #00b894;
}

.customer-theme .edit-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .edit-btn:hover {
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

.customer-theme .change-password-btn {
  color: #00b894;
  border-color: #00b894;
}

.customer-theme .change-password-btn:hover {
  background: #00b894;
  color: white;
}

.customer-theme .form-group input:focus,
.customer-theme .form-group select:focus,
.customer-theme .form-group textarea:focus {
  border-color: #00b894;
  box-shadow: 0 0 0 3px rgba(0, 184, 148, 0.1);
}

.customer-theme .save-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .save-btn:hover:not(:disabled) {
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

.edit-avatar-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #f8f9fa;
  color: #74b9ff;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-avatar-btn:hover {
  background: #74b9ff;
  color: white;
  border-color: #74b9ff;
}

.user-info {
  flex: 1;
}

.username {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin: 0 0 25px 0;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
  font-weight: 500;
}

.info-label svg {
  color: #74b9ff;
  flex-shrink: 0;
}

.info-value {
  color: #333;
  font-size: 16px;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
}

.edit-btn, .change-password-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-btn {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
}

.edit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

.change-password-btn {
  background: white;
  color: #74b9ff;
  border: 2px solid #74b9ff;
}

.change-password-btn:hover {
  background: #74b9ff;
  color: white;
}

.profile-edit {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #f0f0f0;
}

.edit-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.cancel-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: #f8f9fa;
  color: #666;
  border: 1px solid #e9ecef;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background: #e9ecef;
  color: #333;
}

.edit-form {
  max-width: 500px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #333;
  font-weight: 500;
  font-size: 14px;
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #74b9ff;
  box-shadow: 0 0 0 3px rgba(116, 185, 255, 0.1);
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;
  margin-top: 30px;
}

.save-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

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

.password-modal {
  background: white;
  border-radius: 12px;
  padding: 30px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.modal-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #f8f9fa;
  color: #666;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: #e9ecef;
  color: #333;
}

.password-form {
  max-width: 100%;
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
  
  .profile-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .action-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .edit-btn, .change-password-btn {
    width: 100%;
    justify-content: center;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .password-modal {
    margin: 20px;
    width: calc(100% - 40px);
  }
}
</style>