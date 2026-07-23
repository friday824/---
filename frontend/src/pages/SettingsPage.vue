<template>
  <div class="max-w-lg mx-auto px-4 py-8">
    <h1 class="font-display text-3xl text-sakura-600 mb-8">设置 ⚙️</h1>

    <div class="bg-white rounded-2xl p-6 shadow-sm space-y-6">
      <div>
        <label class="block text-sm font-medium text-gray-600 mb-2">用户名</label>
        <p class="text-gray-700">{{ auth.user?.username || '-' }}</p>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 mb-2">邮箱</label>
        <p class="text-gray-700">{{ auth.user?.email || '-' }}</p>
      </div>
      <div>
        <label class="block text-sm font-medium text-gray-600 mb-2">注册时间</label>
        <p class="text-gray-700">{{ auth.user?.created_at ? new Date(auth.user.created_at).toLocaleDateString('zh-CN') : '-' }}</p>
      </div>
    </div>

    <div class="mt-8">
      <button @click="handleLogout"
        class="w-full bg-white border border-red-200 text-red-500 hover:bg-red-50 py-3 rounded-full font-medium transition-all">
        退出登录
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

function handleLogout() {
  auth.logout()
  router.push('/')
}
</script>
