<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-b from-sakura-50 to-cream-50 px-4">
    <div class="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
      <div class="text-center mb-8">
        <span class="text-4xl">🌸</span>
        <h1 class="font-display text-2xl text-sakura-500 mt-2">欢迎回来</h1>
        <p class="text-gray-400 text-sm mt-1">登录继续你的创作</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-600 mb-1">邮箱</label>
          <input v-model="email" type="email" required
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-sakura-300 focus:ring-2 focus:ring-sakura-100 outline-none transition-all"
            placeholder="your@email.com" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-600 mb-1">密码</label>
          <input v-model="password" type="password" required
            class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-sakura-300 focus:ring-2 focus:ring-sakura-100 outline-none transition-all"
            placeholder="输入密码" />
        </div>
        <p v-if="errorMsg" class="text-red-500 text-sm text-center">{{ errorMsg }}</p>
        <button type="submit" :disabled="loading"
          class="w-full bg-sakura-500 hover:bg-sakura-600 disabled:bg-sakura-300 text-white py-3 rounded-full font-medium transition-all">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <p class="text-center text-gray-400 text-sm mt-6">
        还没有账号？<router-link to="/auth/register" class="text-sakura-500 hover:underline">注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const errorMsg = ref('')

async function handleSubmit() {
  errorMsg.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    const redirect = route.query.redirect || '/dashboard'
    router.push(redirect)
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '登录失败，请检查邮箱和密码'
  } finally {
    loading.value = false
  }
}
</script>
