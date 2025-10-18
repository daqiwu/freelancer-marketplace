// Admin API服务
const API_BASE_URL = 'http://localhost:8000'

class AdminService {
  // 获取认证头
  getAuthHeaders() {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  }

  // 检查是否为管理员
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

  // 检查认证状态
  isAuthenticated() {
    const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token')
    return !!token
  }

  // 处理API响应
  async handleResponse(response) {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      
      // 处理认证错误
      if (response.status === 401) {
        // 清除无效token
        localStorage.removeItem('access_token')
        sessionStorage.removeItem('access_token')
        sessionStorage.removeItem('currentUser')
        
        // 跳转到登录页面
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
        
        throw new Error('认证失败，请重新登录')
      }
      
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
    }
    return response.json()
  }

  // ==================== 订单管理 API ====================

  /**
   * 获取所有订单
   * @param {Object} params - 查询参数
   * @param {string} params.status - 订单状态筛选
   * @param {number} params.page - 页码
   * @param {number} params.limit - 每页数量
   * @param {string} params.sort_by - 排序字段
   * @param {string} params.order - 排序顺序
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
      console.error('获取订单列表失败:', error)
      throw error
    }
  }

  // ==================== 用户管理 API ====================

  /**
   * 获取所有用户
   * @param {Object} params - 查询参数
   * @param {number} params.role_id - 角色筛选 (1=客户, 2=服务提供者)
   * @param {number} params.page - 页码
   * @param {number} params.limit - 每页数量
   * @param {string} params.sort_by - 排序字段
   * @param {string} params.order - 排序顺序
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
      console.error('获取用户列表失败:', error)
      throw error
    }
  }

  /**
   * 获取单个用户详情
   * @param {number} userId - 用户ID
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
      console.error('获取用户详情失败:', error)
      throw error
    }
  }

  /**
   * 删除用户
   * @param {number} userId - 用户ID
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
      console.error('删除用户失败:', error)
      throw error
    }
  }

  // ==================== 工具方法 ====================

  /**
   * 格式化订单状态显示
   * @param {string} status - 订单状态
   */
  formatOrderStatus(status) {
    const statusMap = {
      'pending': '待处理',
      'accepted': '已接受',
      'in_progress': '进行中',
      'completed': '已完成',
      'reviewed': '已评价',
      'cancelled': '已取消'
    }
    return statusMap[status] || status
  }

  /**
   * 格式化角色显示
   * @param {number} roleId - 角色ID
   */
  formatRole(roleId) {
    const roleMap = {
      1: '客户',
      2: '服务提供者',
      3: '管理员'
    }
    return roleMap[roleId] || '未知'
  }

  /**
   * 格式化地点显示
   * @param {string} location - 地点
   */
  formatLocation(location) {
    const locationMap = {
      'NORTH': '北区',
      'SOUTH': '南区',
      'EAST': '东区',
      'WEST': '西区',
      'CENTER': '中区'
    }
    return locationMap[location] || location
  }
}

// 创建单例实例
const adminService = new AdminService()
export default adminService
