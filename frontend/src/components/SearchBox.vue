<template>
  <div class="search-container">
    <div class="search-box">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="搜索任务名称、地点或类别..."
        class="search-input"
        @keyup.enter="handleSearch"
      />
      <button @click="handleSearch" class="search-button">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 21L16.514 16.506L21 21ZM19 10.5C19 15.194 15.194 19 10.5 19C5.806 19 2 15.194 2 10.5C2 5.806 5.806 2 10.5 2C15.194 2 19 5.806 19 10.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        搜索
      </button>
    </div>
    <div class="filter-tags">
      <span class="filter-label">快速筛选：</span>
      <button
        v-for="category in categories"
        :key="category"
        @click="selectCategory(category)"
        :class="['filter-tag', { active: selectedCategory === category }]"
      >
        {{ category }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchBox',
  data() {
    return {
      searchQuery: '',
      selectedCategory: '全部',
      categories: ['全部', '技术开发', '设计创意', '营销推广', '生活服务', '教育培训']
    }
  },
  methods: {
    handleSearch() {
      this.$emit('search', {
        query: this.searchQuery,
        category: this.selectedCategory
      })
    },
    selectCategory(category) {
      this.selectedCategory = category
      this.handleSearch()
    }
  }
}
</script>

<style scoped>
.search-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 30px 20px;
  background: white;
}

.search-box {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}

.search-input {
  flex: 1;
  padding: 12px 20px;
  border: 2px solid #e1e5e9;
  border-radius: 25px;
  font-size: 16px;
  outline: none;
  transition: all 0.3s ease;
  background: #f8f9fa;
}

.search-input:focus {
  border-color: #74b9ff;
  background: white;
  box-shadow: 0 0 0 3px rgba(116, 185, 255, 0.1);
}

.search-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  border: none;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.search-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(116, 185, 255, 0.4);
}

.search-button:active {
  transform: translateY(0);
}

.filter-tags {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
}

.filter-label {
  color: #666;
  font-weight: 500;
  margin-right: 10px;
}

.filter-tag {
  padding: 6px 16px;
  background: #f1f3f4;
  color: #666;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-tag:hover {
  background: #e8eaf0;
  color: #333;
}

.filter-tag.active {
  background: linear-gradient(135deg, #74b9ff 0%, #a29bfe 100%);
  color: white;
  font-weight: 600;
}

@media (max-width: 768px) {
  .search-box {
    flex-direction: column;
    gap: 10px;
  }
  
  .search-input {
    font-size: 14px;
    padding: 10px 16px;
  }
  
  .search-button {
    padding: 10px 20px;
    font-size: 14px;
  }
  
  .filter-tags {
    justify-content: flex-start;
  }
  
  .filter-tag {
    font-size: 12px;
    padding: 4px 12px;
  }
}
</style>
