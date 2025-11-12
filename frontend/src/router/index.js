import { createRouter, createWebHistory } from 'vue-router'
import HomePage from '@/views/HomePage.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import ProviderTaskDetail from '@/views/ProviderTaskDetail.vue'
import CustomerTaskDetail from '@/views/CustomerTaskDetail.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/task/:id',
    name: 'TaskDetail',
    component: (route) => {
      // Decide which component to use based on role parameter
      const role = route?.query?.role
      if (role === 'customer') {
        return CustomerTaskDetail
      } else {
        return ProviderTaskDetail
      }
    },
    props: true
  },
  {
    path: '/publish-task',
    name: 'PublishTask',
    component: () => import('@/views/PublishTask.vue')
  },
  {
    path: '/my-tasks',
    name: 'MyTasks',
    component: () => import('@/views/MyTasks.vue')
  },
  {
    path: '/messages',
    name: 'Messages',
    component: () => import('@/views/Messages.vue')
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue')
  },
  {
    path: '/customer/orders',
    name: 'CustomerOrders',
    component: () => import('@/views/CustomerOrders.vue')
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('@/views/AdminDashboard.vue')
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

