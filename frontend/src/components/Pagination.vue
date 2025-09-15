<template>
  <div class="pagination-container">
    <div class="pagination">
      <button
        @click="goToPage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="pagination-btn prev-btn"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M15 18L9 12L15 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        上一页
      </button>
      
      <div class="pagination-pages">
        <button
          v-for="page in visiblePages"
          :key="page"
          @click="goToPage(page)"
          :class="['pagination-page', { active: page === currentPage }]"
        >
          {{ page }}
        </button>
        
        <span v-if="showEllipsis" class="pagination-ellipsis">...</span>
      </div>
      
      <button
        @click="goToPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="pagination-btn next-btn"
      >
        下一页
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 18L15 12L9 6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
    
    <div class="pagination-jump">
      <span>跳转到</span>
      <input
        v-model.number="jumpPage"
        type="number"
        :min="1"
        :max="totalPages"
        class="jump-input"
        @keyup.enter="jumpToPage"
      />
      <span>页</span>
      <button @click="jumpToPage" class="jump-btn">确定</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TaskPagination',
  props: {
    currentPage: {
      type: Number,
      required: true
    },
    totalPages: {
      type: Number,
      required: true
    },
    totalItems: {
      type: Number,
      required: true
    },
    itemsPerPage: {
      type: Number,
      default: 8
    }
  },
  data() {
    return {
      jumpPage: this.currentPage
    }
  },
  computed: {
    visiblePages() {
      const pages = []
      const maxVisible = 5
      
      if (this.totalPages <= maxVisible) {
        for (let i = 1; i <= this.totalPages; i++) {
          pages.push(i)
        }
      } else {
        const start = Math.max(1, this.currentPage - 2)
        const end = Math.min(this.totalPages, start + maxVisible - 1)
        
        for (let i = start; i <= end; i++) {
          pages.push(i)
        }
      }
      
      return pages
    },
    showEllipsis() {
      return this.totalPages > 5 && this.currentPage < this.totalPages - 2
    }
  },
  watch: {
    currentPage(newPage) {
      this.jumpPage = newPage
    }
  },
  methods: {
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages && page !== this.currentPage) {
        this.$emit('page-change', page)
      }
    },
    jumpToPage() {
      const page = parseInt(this.jumpPage)
      if (page >= 1 && page <= this.totalPages) {
        this.goToPage(page)
      } else {
        this.jumpPage = this.currentPage
      }
    }
  }
}
</script>

<style scoped>
.pagination-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 30px 20px;
  background: white;
  border-top: 1px solid #f0f0f0;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pagination-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #74b9ff;
  color: #74b9ff;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-pages {
  display: flex;
  align-items: center;
  gap: 5px;
}

.pagination-page {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid #e1e5e9;
  border-radius: 6px;
  color: #666;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.pagination-page:hover {
  background: #f8f9fa;
  border-color: #74b9ff;
  color: #74b9ff;
}

.pagination-page.active {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  border-color: #74b9ff;
  color: white;
  font-weight: 600;
}

.pagination-ellipsis {
  padding: 0 10px;
  color: #999;
  font-size: 14px;
}

.pagination-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
  font-size: 14px;
}

.jump-input {
  width: 60px;
  padding: 6px 8px;
  border: 1px solid #e1e5e9;
  border-radius: 4px;
  text-align: center;
  font-size: 14px;
  outline: none;
}

.jump-input:focus {
  border-color: #74b9ff;
  box-shadow: 0 0 0 2px rgba(116, 185, 255, 0.1);
}

.jump-btn {
  padding: 6px 12px;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.jump-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(116, 185, 255, 0.3);
}

@media (max-width: 768px) {
  .pagination-container {
    padding: 20px 15px;
    gap: 15px;
  }
  
  .pagination {
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
  }
  
  .pagination-btn {
    padding: 6px 12px;
    font-size: 13px;
  }
  
  .pagination-page {
    width: 35px;
    height: 35px;
    font-size: 13px;
  }
  
  .pagination-jump {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .jump-input {
    width: 50px;
    font-size: 13px;
  }
  
  .jump-btn {
    padding: 5px 10px;
    font-size: 13px;
  }
}
</style>
