<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <LoadingSpinner v-if="loading" text="加载视频..." />
    <div v-else-if="video">
      <router-link to="/videos" class="text-gray-400 hover:text-sakura-500 text-sm transition-colors">← 我的视频</router-link>

      <!-- Player -->
      <div class="mt-4 bg-black rounded-2xl overflow-hidden shadow-lg">
        <video v-if="video.video_url"
          :src="video.video_url"
          controls
          class="w-full aspect-video"
          poster="">
          你的浏览器不支持视频播放
        </video>
        <div v-else class="aspect-video flex items-center justify-center text-white text-gray-400">
          视频文件暂不可用
        </div>
      </div>

      <!-- Info -->
      <div class="mt-6">
        <h1 class="font-display text-2xl text-sakura-600">{{ scriptTitle }}</h1>
        <div class="flex items-center gap-4 mt-2 text-sm text-gray-400">
          <span v-if="video.total_duration_s">时长 {{ Math.round(video.total_duration_s) }}秒</span>
          <span v-if="video.video_size_bytes">大小 {{ (video.video_size_bytes / 1024 / 1024).toFixed(1) }}MB</span>
          <span>{{ formatDate(video.created_at) }}</span>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-4 mt-6">
        <a v-if="video.video_url"
          :href="video.video_url"
          download
          class="flex-1 bg-sakura-500 hover:bg-sakura-600 text-white text-center py-3 rounded-full font-medium transition-all">
          下载视频 ⬇️
        </a>
        <button @click="handleRegenerate"
          :disabled="regenerating"
          class="flex-1 bg-white border border-sakura-200 text-sakura-500 hover:bg-sakura-50 py-3 rounded-full font-medium transition-all disabled:opacity-50">
          {{ regenerating ? '正在提交...' : '重新生成 🔄' }}
        </button>
      </div>
      <p v-if="errorMsg" class="text-red-500 text-sm text-center mt-4">{{ errorMsg }}</p>
    </div>
    <EmptyState v-else icon="🎬" title="视频未找到" link-to="/videos" link-text="返回列表" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../composables/useApi'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import EmptyState from '../components/common/EmptyState.vue'

const route = useRoute()
const router = useRouter()
const video = ref(null)
const loading = ref(true)
const regenerating = ref(false)
const errorMsg = ref('')

const scriptTitle = computed(() => video.value?.script_output?.title || '未命名')

onMounted(async () => {
  try {
    const res = await api.get(`/api/videos/${route.params.id}`)
    video.value = res.data
  } catch { video.value = null } finally { loading.value = false }
})

async function handleRegenerate() {
  errorMsg.value = ''
  regenerating.value = true
  try {
    const res = await api.post(`/api/tasks/generate/${video.value.diary_id}`)
    router.push(`/tasks/${res.data.id}`)
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '提交失败'
  } finally { regenerating.value = false }
}

function formatDate(d) { return d ? new Date(d).toLocaleDateString('zh-CN') : '' }
</script>
