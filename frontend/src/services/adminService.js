// Admin API service
const API_BASE_URL = 'http://localhost:8000'

class AdminService {
  // Get authentication headers
  getAuthHeaders() {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }

  // Check if user is admin
  isAdmin() {
    const user = sessionStorage.getItem('currentUser')
    if (!user) return false
    
    try {
      const userData = JSON.parse(user)
      return userData.role === 'admin' || userData.role_id === 3
    } catch (error) {
      return false
    }
  }

  // Check authentication status
  isAuthenticated() {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    return !!token
  }

  // Handle API response
  async handleResponse(response) {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      
      // Handle authentication error
      if (response.status === 401) {
        // Clear invalid token
        localStorage.removeItem('access_token')
        sessionStorage.removeItem('access_token')
        sessionStorage.removeItem('currentUser')
        
        // Redirect to login page
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
        
        throw new Error('Authentication failed, please login again')
      }
      
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }
    return response.json()
  }

  // ==================== Order Management APIs ====================

  /**
   * Get all orders
   * @param {Object} params - Query parameters
   * @param {string} params.status - Order status filter
   * @param {number} params.page - Page number
   * @param {number} params.limit - Items per page
   * @param {string} params.sort_by - Sort field
   * @param {string} params.order - Sort order
   */
  async getAllOrders(params = {}) {
    const queryParams = new URLSearchParams()
    
    if (params.status) queryParams.append('status', params.status)
    if (params.page) queryParams.append('page', params.page)
    if (params.limit) queryParams.append('limit', params.limit)
    if (params.sort_by) queryParams.append('sort_by', params.sort_by)
    if (params.order) queryParams.append('order', params.order)

    const url = `${API_BASE_URL}/admin/orders?${queryParams.toString()}`
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })
      return await this.handleResponse(response)
    } catch (error) {
      console.error('Failed to get order list:', error)
      throw error
    }
  }

  // ==================== User Management APIs ====================

  /**
   * Get all users
   * @param {Object} params - Query parameters
   * @param {number} params.role_id - Role filter (1=customer, 2=provider)
   * @param {number} params.page - Page number
   * @param {number} params.limit - Items per page
   * @param {string} params.sort_by - Sort field
   * @param {string} params.order - Sort order
   */
  async getAllUsers(params = {}) {
    const queryParams = new URLSearchParams()
    
    if (params.role_id) queryParams.append('role_id', params.role_id)
    if (params.page) queryParams.append('page', params.page)
    if (params.limit) queryParams.append('limit', params.limit)
    if (params.sort_by) queryParams.append('sort_by', params.sort_by)
    if (params.order) queryParams.append('order', params.order)

    const url = `${API_BASE_URL}/admin/users?${queryParams.toString()}`
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })
      return await this.handleResponse(response)
    } catch (error) {
      console.error('Failed to get user list:', error)
      throw error
    }
  }

  /**
   * Get user details by ID
   * @param {number} userId - User ID
   */
  async getUserById(userId) {
    const url = `${API_BASE_URL}/admin/users/${userId}`
    
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: this.getAuthHeaders()
      })
      return await this.handleResponse(response)
    } catch (error) {
      console.error('Failed to get user details:', error)
      throw error
    }
  }

  /**
   * Delete user
   * @param {number} userId - User ID
   */
  async deleteUser(userId) {
    const url = `${API_BASE_URL}/admin/users/${userId}`
    
    try {
      const response = await fetch(url, {
        method: 'DELETE',
        headers: this.getAuthHeaders()
      })
      return await this.handleResponse(response)
    } catch (error) {
      console.error('Failed to delete user:', error)
      throw error
    }
  }

  // ==================== Utility Methods ====================

  /**
   * Format order status display
   * @param {string} status - Order status
   */
  formatOrderStatus(status) {
    const statusMap = {
      'pending': 'Pending',
      'accepted': 'Accepted',
      'in_progress': 'In Progress',
      'completed': 'Completed',
      'reviewed': 'Reviewed',
      'cancelled': 'Cancelled'
    }
    return statusMap[status] || status
  }

  /**
   * Format role display
   * @param {number} roleId - Role ID
   */
  formatRole(roleId) {
    const roleMap = {
      1: 'Customer',
      2: 'Provider',
      3: 'Admin'
    }
    return roleMap[roleId] || 'Unknown'
  }

  /**
   * Format location display
   * @param {string} location - Location
   */
  formatLocation(location) {
    const locationMap = {
      'NORTH': 'North',
      'SOUTH': 'South',
      'EAST': 'East',
      'WEST': 'West',
      'CENTER': 'Center'
    }
    return locationMap[location] || location
  }
}

// Create singleton instance
const adminService = new AdminService()
export default adminService
