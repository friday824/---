<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-b from-sakura-50 to-cream-50 px-4">
    <div class="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
      <div class="text-center mb-8">
        <span class="text-4xl">🌸</span>
        <h1 class="font-display text-2xl text-sakura-500 mt-2">开始创作之旅</h1>
        <p class="text-gray-400 text-sm mt-1">注册账号，把你的日记变成动画</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-600 mb-1">用户名</label>
          <input v-model="username" type="text" required minlength="2"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-sakura-300 focus:ring-2 focus:ring-sakura-100 outline-none transition-all"
            placeholder="你的昵称" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-600 mb-1">邮箱</label>
          <input v-model="email" type="email" required
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-sakura-300 focus:ring-2 focus:ring-sakura-100 outline-none transition-all"
            placeholder="your@email.com" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-600 mb-1">密码</label>
          <input v-model="password" type="password" required minlength="6"
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-sakura-300 focus:ring-2 focus:ring-sakura-100 outline-none transition-all"
            placeholder="至少6位密码" />
        </div>
        <p v-if="errorMsg" class="text-red-500 text-sm text-center">{{ errorMsg }}</p>
        <button type="submit" :disabled="loading"
          class="w-full bg-sakura-500 hover:bg-sakura-600 disabled:bg-sakura-300 text-white py-3 rounded-full font-medium transition-all">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <p class="text-center text-gray-400 text-sm mt-6">
        已有账号？<router-link to="/auth/login" class="text-sakura-500 hover:underline">登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

async function handleSubmit() {
  errorMsg.value = ''
  loading.value = true
  try {
    await auth.register(email.value, username.value, password.value)
    router.push('/dashboard')
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>
