<template>
  <div class="publish-task-page" :class="{ 'customer-theme': true }">
    <NavBar />
    
    <div class="main-content">
      <div class="page-header">
        <h1>{{ isEditMode ? '编辑任务' : '发布任务' }}</h1>
        <p>{{ isEditMode ? '修改任务信息，更新您的需求' : '填写任务信息，发布您的需求' }}</p>
      </div>

      <div class="form-container">
        <form @submit.prevent="publishTask" class="task-form">
          <div class="form-section">
            <h3>基本信息</h3>
            <div class="form-row">
              <div class="form-group">
                <label for="title">任务标题 *</label>
                <input 
                  type="text" 
                  id="title" 
                  v-model="form.title" 
                  required
                  placeholder="请输入任务标题"
                  maxlength="50"
                >
                <span class="char-count">{{ form.title.length }}/50</span>
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="category">任务类别 *</label>
                <select id="category" v-model="form.category" required>
                  <option value="">请选择类别</option>
                  <option value="技术开发">技术开发</option>
                  <option value="设计创意">设计创意</option>
                  <option value="营销推广">营销推广</option>
                  <option value="教育培训">教育培训</option>
                  <option value="生活服务">生活服务</option>
                  <option value="其他">其他</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="type">任务类型 *</label>
                <input 
                  type="text" 
                  id="type" 
                  v-model="form.type" 
                  required
                  placeholder="如：Web开发、UI设计等"
                >
              </div>
            </div>
            
            <div class="form-row">
              <div class="form-group">
                <label for="location">工作地点 *</label>
                <input 
                  type="text" 
                  id="location" 
                  v-model="form.location" 
                  required
                  placeholder="请输入工作地点"
                >
              </div>
              
              <div class="form-group">
                <label for="budget">预算金额 *</label>
                <div class="budget-input">
                  <span class="currency">¥</span>
                  <input 
                    type="number" 
                    id="budget" 
                    v-model.number="form.budget" 
                    required
                    placeholder="0"
                    min="1"
                  >
                </div>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3>时间安排</h3>
            <div class="form-row">
              <div class="form-group">
                <label for="startTime">开始时间 *</label>
                <input 
                  type="datetime-local" 
                  id="startTime" 
                  v-model="form.startTime" 
                  required
                >
              </div>
              
              <div class="form-group">
                <label for="endTime">结束时间 *</label>
                <input 
                  type="datetime-local" 
                  id="endTime" 
                  v-model="form.endTime" 
                  required
                >
              </div>
            </div>
          </div>

          <div class="form-section">
            <h3>任务详情</h3>
            <div class="form-group">
              <label for="description">任务描述 *</label>
              <textarea 
                id="description" 
                v-model="form.description" 
                required
                placeholder="请详细描述您的任务需求..."
                rows="6"
                maxlength="1000"
              ></textarea>
              <span class="char-count">{{ form.description.length }}/1000</span>
            </div>
            
            <div class="form-group">
              <label for="requirements">任务要求</label>
              <div class="requirements-input">
                <div class="requirement-item" v-for="(req, index) in form.requirements" :key="index">
                  <input 
                    type="text" 
                    v-model="form.requirements[index]" 
                    placeholder="请输入要求"
                    maxlength="100"
                  >
                  <button type="button" @click="removeRequirement(index)" class="remove-btn">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                </div>
                <button type="button" @click="addRequirement" class="add-requirement-btn">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  </svg>
                  添加要求
                </button>
              </div>
            </div>
            
            <div class="form-group">
              <label for="skills">所需技能</label>
              <div class="skills-input">
                <div class="skill-tag" v-for="(skill, index) in form.skills" :key="index">
                  {{ skill }}
                  <button type="button" @click="removeSkill(index)" class="remove-skill-btn">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                      <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                </div>
                <input 
                  type="text" 
                  v-model="skillInput" 
                  @keyup.enter="addSkill"
                  placeholder="输入技能后按回车添加"
                  maxlength="20"
                >
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="cancel-btn" @click="goBack">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 12H5M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              取消
            </button>
            <button type="submit" class="publish-btn" :disabled="publishing">
              <svg v-if="publishing" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="spinner">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2Z" fill="currentColor"/>
              </svg>
              {{ publishing ? (isEditMode ? '保存中...' : '发布中...') : (isEditMode ? '保存修改' : '发布任务') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'

export default {
  name: 'PublishTask',
  components: {
    NavBar
  },
  data() {
    return {
      publishing: false,
      skillInput: '',
      isEditMode: false,
      editingTaskId: null,
      form: {
        title: '',
        category: '',
        type: '',
        location: '',
        budget: null,
        startTime: '',
        endTime: '',
        description: '',
        requirements: [''],
        skills: []
      }
    }
  },
  created() {
    this.checkEditMode()
  },
  methods: {
    checkEditMode() {
      const query = this.$route.query
      if (query.edit === 'true' && query.id) {
        this.isEditMode = true
        this.editingTaskId = parseInt(query.id)
        this.loadTaskForEdit()
      }
    },
    loadTaskForEdit() {
      // 从本地存储加载任务数据
      const tasks = JSON.parse(localStorage.getItem('tasks') || '[]')
      const task = tasks.find(t => t.id === this.editingTaskId)
      
      if (task) {
        this.form = {
          title: task.title || '',
          category: task.category || '',
          type: task.type || '',
          location: task.location || '',
          budget: task.budget || null,
          startTime: task.startTime || '',
          endTime: task.endTime || '',
          description: task.description || '',
          requirements: task.requirements && task.requirements.length > 0 ? task.requirements : [''],
          skills: task.skills || []
        }
      } else {
        alert('任务不存在，将返回首页')
        this.$router.push('/?role=customer')
      }
    },
    addRequirement() {
      this.form.requirements.push('')
    },
    removeRequirement(index) {
      if (this.form.requirements.length > 1) {
        this.form.requirements.splice(index, 1)
      }
    },
    addSkill() {
      if (this.skillInput.trim() && !this.form.skills.includes(this.skillInput.trim())) {
        this.form.skills.push(this.skillInput.trim())
        this.skillInput = ''
      }
    },
    removeSkill(index) {
      this.form.skills.splice(index, 1)
    },
    async publishTask() {
      // 验证表单
      if (!this.validateForm()) {
        return
      }
      
      this.publishing = true
      
      // 模拟API调用
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // 过滤空的要求
      const requirements = this.form.requirements.filter(req => req.trim())
      
      // 获取现有任务列表
      const existingTasks = JSON.parse(localStorage.getItem('tasks') || '[]')
      
      if (this.isEditMode) {
        // 编辑模式：更新现有任务
        const taskIndex = existingTasks.findIndex(t => t.id === this.editingTaskId)
        if (taskIndex !== -1) {
          existingTasks[taskIndex] = {
            ...existingTasks[taskIndex],
            title: this.form.title,
            category: this.form.category,
            type: this.form.type,
            location: this.form.location,
            budget: this.form.budget,
            startTime: this.form.startTime,
            endTime: this.form.endTime,
            description: this.form.description,
            requirements: requirements,
            skills: this.form.skills,
            updatedAt: new Date().toISOString()
          }
          localStorage.setItem('tasks', JSON.stringify(existingTasks))
          this.publishing = false
          alert(`任务"${this.form.title}"修改成功！`)
        } else {
          this.publishing = false
          alert('任务不存在，修改失败')
          return
        }
      } else {
        // 新建模式：创建新任务
        const newTask = {
          id: Date.now(), // 简单的ID生成
          title: this.form.title,
          category: this.form.category,
          type: this.form.type,
          location: this.form.location,
          budget: this.form.budget,
          startTime: this.form.startTime,
          endTime: this.form.endTime,
          description: this.form.description,
          requirements: requirements,
          skills: this.form.skills,
          status: 'open',
          publisher: '当前用户',
          createdAt: new Date().toISOString()
        }
        
        existingTasks.push(newTask)
        localStorage.setItem('tasks', JSON.stringify(existingTasks))
        
        this.publishing = false
        alert(`任务"${newTask.title}"发布成功！`)
      }
      
      // 返回首页
      this.$router.push('/?role=customer')
    },
    validateForm() {
      if (!this.form.title.trim()) {
        alert('请输入任务标题')
        return false
      }
      if (!this.form.category) {
        alert('请选择任务类别')
        return false
      }
      if (!this.form.type.trim()) {
        alert('请输入任务类型')
        return false
      }
      if (!this.form.location.trim()) {
        alert('请输入工作地点')
        return false
      }
      if (!this.form.budget || this.form.budget <= 0) {
        alert('请输入有效的预算金额')
        return false
      }
      if (!this.form.startTime) {
        alert('请选择开始时间')
        return false
      }
      if (!this.form.endTime) {
        alert('请选择结束时间')
        return false
      }
      if (new Date(this.form.endTime) <= new Date(this.form.startTime)) {
        alert('结束时间必须晚于开始时间')
        return false
      }
      if (!this.form.description.trim()) {
        alert('请输入任务描述')
        return false
      }
      return true
    },
    goBack() {
      this.$router.go(-1)
    }
  }
}
</script>

<style scoped>
.publish-task-page {
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

.form-container {
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.task-form {
  max-width: 100%;
}

.form-section {
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 2px solid #f0f0f0;
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
}

.form-section h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin: 0 0 25px 0;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
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
.form-group select,
.form-group textarea {
  padding: 12px 16px;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #74b9ff;
  box-shadow: 0 0 0 3px rgba(116, 185, 255, 0.1);
}

.budget-input {
  position: relative;
  display: flex;
  align-items: center;
}

.currency {
  position: absolute;
  left: 16px;
  color: #666;
  font-weight: 500;
  z-index: 1;
}

.budget-input input {
  padding-left: 30px;
}

.char-count {
  font-size: 12px;
  color: #999;
  text-align: right;
}

.requirements-input {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.requirement-item {
  display: flex;
  gap: 10px;
  align-items: center;
}

.requirement-item input {
  flex: 1;
}

.remove-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: #ffebee;
  color: #d32f2f;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  background: #ffcdd2;
}

.add-requirement-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: #f8f9fa;
  color: #74b9ff;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: flex-start;
}

.add-requirement-btn:hover {
  background: #74b9ff;
  color: white;
  border-color: #74b9ff;
}

.skills-input {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  padding: 12px 16px;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  min-height: 50px;
}

.skill-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.remove-skill-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 16px;
  height: 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s ease;
}

.remove-skill-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.skills-input input {
  border: none;
  outline: none;
  background: transparent;
  font-size: 16px;
  flex: 1;
  min-width: 200px;
}

.form-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-top: 40px;
  padding-top: 30px;
  border-top: 2px solid #f0f0f0;
}

.cancel-btn,
.publish-btn {
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

.cancel-btn {
  background: #f8f9fa;
  color: #666;
  border: 1px solid #e9ecef;
}

.cancel-btn:hover {
  background: #e9ecef;
  color: #333;
}

.publish-btn {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
}

.publish-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

/* Customer主题颜色 */
.customer-theme .publish-btn {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .publish-btn:hover:not(:disabled) {
  box-shadow: 0 4px 15px rgba(0, 184, 148, 0.4);
}

.customer-theme .form-group input:focus,
.customer-theme .form-group select:focus,
.customer-theme .form-group textarea:focus {
  border-color: #00b894;
  box-shadow: 0 0 0 3px rgba(0, 184, 148, 0.1);
}

.customer-theme .skill-tag {
  background: linear-gradient(135deg, #00b894 0%, #00a085 100%);
}

.customer-theme .add-requirement-btn {
  color: #00b894;
  border-color: #00b894;
}

.customer-theme .add-requirement-btn:hover {
  background: #00b894;
  color: white;
  border-color: #00b894;
}

.publish-btn:disabled {
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
  
  .form-container {
    padding: 20px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .cancel-btn,
  .publish-btn {
    width: 100%;
    justify-content: center;
  }
  
  .skills-input {
    flex-direction: column;
    align-items: stretch;
  }
  
  .skills-input input {
    min-width: auto;
  }
}
</style>
