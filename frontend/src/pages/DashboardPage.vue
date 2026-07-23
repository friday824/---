<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <!-- Welcome -->
    <div class="mb-8">
      <h1 class="font-display text-3xl text-sakura-600">
        你好，{{ auth.user?.username || '朋友' }} 👋
      </h1>
      <p class="text-gray-400 mt-1">今天想写点什么吗？</p>
    </div>

    <!-- Stats -->
    <div class="grid grid-cols-3 gap-4 mb-8">
      <div class="bg-white rounded-xl p-4 text-center shadow-sm">
        <div class="text-2xl font-bold text-sakura-500">{{ diaries.length }}</div>
        <div class="text-xs text-gray-400 mt-1">日记总数</div>
      </div>
      <div class="bg-white rounded-xl p-4 text-center shadow-sm">
        <div class="text-2xl font-bold text-sakura-500">{{ videos.length }}</div>
        <div class="text-xs text-gray-400 mt-1">视频总数</div>
      </div>
      <div class="bg-white rounded-xl p-4 text-center shadow-sm">
        <div class="text-2xl font-bold text-sakura-500">{{ monthlyCount }}</div>
        <div class="text-xs text-gray-400 mt-1">本月创作</div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="flex gap-4 mb-8">
      <router-link to="/diaries/new"
        class="flex-1 bg-sakura-500 hover:bg-sakura-600 text-white text-center py-3 rounded-full font-medium transition-all hover:shadow-lg">
        ✍️ 写新日记
      </router-link>
      <router-link to="/videos"
        class="flex-1 bg-white hover:bg-sakura-50 text-sakura-500 text-center py-3 rounded-full font-medium border border-sakura-200 transition-all">
        🎬 我的视频
      </router-link>
    </div>

    <!-- Diaries list -->
    <LoadingSpinner v-if="loading" text="加载日记中..." />
    <EmptyState v-else-if="diaries.length === 0"
      icon="📖"
      title="还没有日记"
      description="写下你的第一篇日记，让 AI 把它变成动画吧"
      link-to="/diaries/new"
      link-text="写日记" />
    <div v-else class="space-y-3">
      <div v-for="d in diaries" :key="d.id"
        class="bg-white rounded-xl p-4 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
        @click="$router.push(`/diaries/${d.id}`)">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="font-medium text-gray-700">{{ d.title }}</h3>
            <p class="text-xs text-gray-400 mt-1">
              {{ formatDate(d.created_at) }} · {{ d.word_count }} 字
              <span v-if="d.mood_tag" class="ml-2">{{ moodEmoji(d.mood_tag) }}</span>
            </p>
          </div>
          <div class="flex items-center gap-2">
            <span v-if="d.has_video" class="text-xs bg-sakura-100 text-sakura-600 px-2 py-1 rounded-full">🎬 已生成</span>
            <span class="text-gray-300">›</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../composables/useApi'
import { useAuthStore } from '../stores/auth'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import EmptyState from '../components/common/EmptyState.vue'

const auth = useAuthStore()
const diaries = ref([])
const videos = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [dRes, vRes] = await Promise.all([
      api.get('/api/diaries'),
      api.get('/api/videos'),
    ])
    diaries.value = dRes.data
    videos.value = vRes.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

const monthlyCount = ref(0) // computed from diaries

function formatDate(dateStr) {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

function moodEmoji(tag) {
  const map = { happy: '😊', sad: '😢', nostalgic: '🥺', excited: '🎉', calm: '😌', romantic: '💕' }
  return map[tag] || ''
}
</script>
