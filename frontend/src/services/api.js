// API service file - Unified management of all backend API calls
const API_BASE_URL = 'http://localhost:8000'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  // Get authentication token
  getAuthToken() {
    return localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
  }

  // Set authentication token
  setAuthToken(token) {
    localStorage.setItem('access_token', token)
  }

  // Clear authentication token
  clearAuthToken() {
    localStorage.removeItem('access_token')
    sessionStorage.removeItem('access_token')
  }

  // Common request method
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
        const errorData = await response.json().catch(() => ({ detail: 'Request failed' }))
        throw new Error(errorData.detail || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // ========== Authentication APIs ==========

  // User registration
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    })
  }

  // User login
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

  // User logout
  async logout() {
    try {
      await this.request('/auth/logout', {
        method: 'POST'
      })
    } finally {
      this.clearAuthToken()
    }
  }

  // ========== Customer Order APIs ==========

  // Publish order
  async publishOrder(orderData) {
    return this.request('/customer/orders/publish', {
      method: 'POST',
      body: JSON.stringify(orderData)
    })
  }

  // Cancel order
  async cancelOrder(orderId) {
    return this.request(`/customer/orders/cancel/${orderId}`, {
      method: 'POST'
    })
  }

  // Get my orders (incomplete)
  async getMyOrders() {
    return this.request('/customer/orders/my')
  }

  // Get order details
  async getOrderDetail(orderId) {
    return this.request(`/customer/orders/my/${orderId}`)
  }

  // Get order history
  async getOrderHistory() {
    return this.request('/customer/orders/history')
  }

  // Review order
  async reviewOrder(reviewData) {
    return this.request('/customer/orders/review', {
      method: 'POST',
      body: JSON.stringify(reviewData)
    })
  }

  // ========== Payment APIs ==========

  // Recharge balance
  async rechargeBalance(amount) {
    return this.request('/customer/payments/recharge', {
      method: 'POST',
      body: JSON.stringify({ amount })
    })
  }

  // Pay order
  async payOrder(orderId) {
    return this.request('/customer/payments/pay', {
      method: 'POST',
      body: JSON.stringify({ order_id: orderId })
    })
  }

  // ========== User Profile APIs ==========

  // Get user profile
  async getUserProfile() {
    return this.request('/profile/me')
  }

  // Update customer profile
  async updateCustomerProfile(profileData) {
    return this.request('/profile/update_customer_profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    })
  }

  // Update provider profile
  async updateProviderProfile(profileData) {
    return this.request('/profile/update_provider_profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    })
  }

  // Update user basic info
  async updateUserInfo(userData) {
    return this.request('/profile/update_user_info', {
      method: 'PUT',
      body: JSON.stringify(userData)
    })
  }

  // ========== Notification APIs ==========

  // Get customer inbox
  async getCustomerInbox() {
    return this.request('/notification/customer_inbox')
  }

  // Get provider inbox
  async getProviderInbox() {
    return this.request('/notification/provider_inbox')
  }
}

// Create API service instance
const apiService = new ApiService()

export default apiService
