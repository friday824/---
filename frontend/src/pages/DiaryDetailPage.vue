<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <LoadingSpinner v-if="loading" text="加载日记..." />
    <div v-else-if="diary">
      <router-link to="/dashboard" class="text-gray-400 hover:text-sakura-500 text-sm transition-colors">← 返回</router-link>
      <h1 class="font-display text-3xl text-sakura-600 mt-4">{{ diary.title }}</h1>
      <div class="flex items-center gap-3 mt-2 text-sm text-gray-400">
        <span>{{ formatDate(diary.created_at) }}</span>
        <span>{{ diary.word_count }} 字</span>
        <span v-if="diary.mood_tag">{{ moodEmoji(diary.mood_tag) }}</span>
      </div>

      <div class="bg-white rounded-2xl p-6 mt-6 shadow-sm whitespace-pre-wrap leading-relaxed text-gray-700">
        {{ diary.content }}
      </div>

      <div class="flex gap-4 mt-8">
        <router-link :to="`/diaries/${diary.id}/edit`"
          class="flex-1 bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 text-center py-3 rounded-full font-medium transition-all">
          编辑
        </router-link>
        <button @click="handleGenerate"
          :disabled="generating"
          class="flex-1 bg-sakura-500 hover:bg-sakura-600 disabled:bg-sakura-300 text-white py-3 rounded-full font-medium transition-all animate-pulse-glow">
          {{ generating ? '正在提交...' : '生成视频 🎬' }}
        </button>
      </div>

      <p v-if="errorMsg" class="text-red-500 text-sm text-center mt-4">{{ errorMsg }}</p>
    </div>
    <EmptyState v-else icon="📖" title="日记未找到" description="这篇日记不存在或已被删除" link-to="/dashboard" link-text="返回列表" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../composables/useApi'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import EmptyState from '../components/common/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const diary = ref(null)
const loading = ref(true)
const generating = ref(false)
const errorMsg = ref('')

onMounted(async () => {
  try {
    const res = await api.get(`/api/diaries/${route.params.id}`)
    diary.value = res.data
  } catch {
    diary.value = null
  } finally {
    loading.value = false
  }
})

async function handleGenerate() {
  errorMsg.value = ''
  generating.value = true
  try {
    const res = await api.post(`/api/tasks/generate/${route.params.id}`)
    router.push(`/tasks/${res.data.id}`)
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '生成失败'
  } finally {
    generating.value = false
  }
}

function formatDate(d) { return d ? new Date(d).toLocaleDateString('zh-CN') : '' }
function moodEmoji(tag) {
  const map = { happy: '😊', sad: '😢', nostalgic: '🥺', excited: '🎉', calm: '😌', romantic: '💕' }
  return map[tag] || ''
}
</script>
