// API服务文件 - 统一管理所有后端API调用
const API_BASE_URL = 'http://localhost:8000'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  // 获取认证token
  getAuthToken() {
    return localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
  }

  // 设置认证token
  setAuthToken(token) {
    localStorage.setItem('access_token', token)
  }

  // 清除认证token
  clearAuthToken() {
    localStorage.removeItem('access_token')
    sessionStorage.removeItem('access_token')
  }

  // 通用请求方法
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`
    const token = this.getAuthToken()
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    }

    const config = {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers
      }
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: '请求失败' }))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API请求失败:', error)
      throw error
    }
  }

  // ========== 认证相关 API ==========

  // 用户注册
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    })
  }

  // 用户登录
  async login(credentials) {
    const response = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    })
    
    if (response.access_token) {
      this.setAuthToken(response.access_token)
    }
    
    return response
  }

  // 用户登出
  async logout() {
    try {
      await this.request('/auth/logout', {
        method: 'POST'
      })
    } finally {
      this.clearAuthToken()
    }
  }

  // ========== 客户订单相关 API ==========

  // 发布订单
  async publishOrder(orderData) {
    return this.request('/customer/orders/publish', {
      method: 'POST',
      body: JSON.stringify(orderData)
    })
  }

  // 取消订单
  async cancelOrder(orderId) {
    return this.request(`/customer/orders/cancel/${orderId}`, {
      method: 'POST'
    })
  }

  // 获取我的订单（未完成）
  async getMyOrders() {
    return this.request('/customer/orders/my')
  }

  // 获取订单详情
  async getOrderDetail(orderId) {
    return this.request(`/customer/orders/my/${orderId}`)
  }

  // 获取历史订单
  async getOrderHistory() {
    return this.request('/customer/orders/history')
  }

  // 评价订单
  async reviewOrder(reviewData) {
    return this.request('/customer/orders/review', {
      method: 'POST',
      body: JSON.stringify(reviewData)
    })
  }

  // ========== 支付相关 API ==========

  // 充值余额
  async rechargeBalance(amount) {
    return this.request('/customer/payments/recharge', {
      method: 'POST',
      body: JSON.stringify({ amount })
    })
  }

  // 支付订单
  async payOrder(orderId) {
    return this.request('/customer/payments/pay', {
      method: 'POST',
      body: JSON.stringify({ order_id: orderId })
    })
  }

  // ========== 用户信息相关 API ==========

  // 获取用户信息
  async getUserProfile() {
    return this.request('/profile/me')
  }

  // 更新客户资料
  async updateCustomerProfile(profileData) {
    return this.request('/profile/update_customer_profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    })
  }

  // 更新服务提供者资料
  async updateProviderProfile(profileData) {
    return this.request('/profile/update_provider_profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    })
  }

  // 更新用户基本信息
  async updateUserInfo(userData) {
    return this.request('/profile/update_user_info', {
      method: 'PUT',
      body: JSON.stringify(userData)
    })
  }

  // ========== 通知相关 API ==========

  // 获取客户收件箱
  async getCustomerInbox() {
    return this.request('/notification/customer_inbox')
  }

  // 获取服务提供者收件箱
  async getProviderInbox() {
    return this.request('/notification/provider_inbox')
  }
}

// 创建API服务实例
const apiService = new ApiService()

export default apiService
