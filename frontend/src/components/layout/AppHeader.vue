<template>
  <header class="bg-white/80 backdrop-blur-sm border-b border-sakura-100 sticky top-0 z-50">
    <nav class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
      <router-link to="/dashboard" class="flex items-center gap-2 no-underline">
        <span class="text-2xl">🌸</span>
        <span class="font-display text-xl text-sakura-500">日记动漫化</span>
      </router-link>

      <div class="flex items-center gap-6">
        <router-link to="/dashboard" class="text-gray-600 hover:text-sakura-500 transition-colors text-sm">
          我的日记
        </router-link>
        <router-link to="/videos" class="text-gray-600 hover:text-sakura-500 transition-colors text-sm">
          我的视频
        </router-link>
        <router-link to="/diaries/new" class="bg-sakura-500 hover:bg-sakura-600 text-white px-4 py-2 rounded-full text-sm font-medium transition-all hover:shadow-lg">
          写日记
        </router-link>
        <div class="relative group">
          <button class="w-8 h-8 rounded-full bg-sakura-100 flex items-center justify-center text-sakura-600 font-medium text-sm">
            {{ auth.user?.username?.[0] || '?' }}
          </button>
          <div class="absolute right-0 top-full mt-2 bg-white rounded-xl shadow-lg border border-gray-100 py-2 w-40 hidden group-hover:block">
            <router-link to="/settings" class="block px-4 py-2 text-sm text-gray-600 hover:bg-sakura-50">设置</router-link>
            <button @click="handleLogout" class="block w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-sakura-50">退出登录</button>
          </div>
        </div>
      </div>
    </nav>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const auth = useAuthStore()

function handleLogout() {
  auth.logout()
  router.push('/')
}
</script>
