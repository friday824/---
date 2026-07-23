<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <h1 class="font-display text-3xl text-sakura-600 mb-8">我的视频 🎬</h1>

    <LoadingSpinner v-if="loading" text="加载视频..." />
    <EmptyState v-else-if="videos.length === 0"
      icon="🎬"
      title="还没有视频"
      description="写一篇日记，让 AI 帮你生成第一个动画短片吧"
      link-to="/diaries/new"
      link-text="写日记" />

    <div v-else class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="v in videos" :key="v.id"
        class="bg-white rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-all cursor-pointer group relative">
        <div @click="$router.push(`/videos/${v.id}`)">
          <!-- Thumbnail placeholder -->
          <div class="aspect-video bg-gradient-to-br from-sakura-100 via-cream-100 to-sky-100 flex items-center justify-center relative overflow-hidden">
            <span v-if="v.status === 'completed'" class="text-5xl group-hover:scale-110 transition-transform">🌸</span>
            <span v-else-if="v.status === 'processing'" class="text-4xl animate-spin">⏳</span>
            <span v-else class="text-4xl">⏸️</span>
            <div v-if="v.status === 'completed' && v.total_duration_s"
              class="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-1 rounded">
              {{ Math.round(v.total_duration_s) }}s
            </div>
          </div>
          <div class="p-4">
            <h3 class="font-medium text-gray-700 truncate">{{ v.title || '未命名视频' }}</h3>
            <p class="text-xs text-gray-400 mt-1">
              {{ formatDate(v.created_at) }}
              <span v-if="v.status === 'processing'" class="ml-2 text-sakura-500">生成中 {{ v.progress }}%</span>
              <span v-else-if="v.status === 'failed'" class="ml-2 text-red-500">失败</span>
            </p>
          </div>
        </div>
        <!-- Delete button -->
        <button
          @click.stop="confirmDelete(v)"
          class="absolute top-2 right-2 w-8 h-8 bg-white/90 hover:bg-red-50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all shadow-sm"
          title="删除视频">
          <span class="text-red-400 hover:text-red-600 text-sm">🗑</span>
        </button>
      </div>
    </div>

    <!-- Delete confirmation modal -->
    <Teleport to="body">
      <div v-if="showDeleteModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
        <div class="bg-white rounded-2xl shadow-xl p-6 mx-4 max-w-sm w-full text-center">
          <div class="text-4xl mb-3">🗑</div>
          <h3 class="text-lg font-medium text-gray-800 mb-1">确认删除</h3>
          <p class="text-sm text-gray-400 mb-6">
            将永久删除「{{ deletingVideo?.title || '未命名视频' }}」，此操作不可撤销
          </p>
          <div class="flex gap-3">
            <button @click="showDeleteModal = false"
              class="flex-1 py-2 rounded-full border border-gray-200 text-gray-500 hover:bg-gray-50 transition-colors text-sm">
              取消
            </button>
            <button @click="doDelete"
              :disabled="deleting"
              class="flex-1 py-2 rounded-full bg-red-500 hover:bg-red-600 text-white transition-colors text-sm disabled:opacity-50">
              {{ deleting ? '删除中...' : '确认删除' }}
            </button>
          </div>
          <p v-if="deleteError" class="text-red-500 text-xs mt-3">{{ deleteError }}</p>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../composables/useApi'
import LoadingSpinner from '../components/common/LoadingSpinner.vue'
import EmptyState from '../components/common/EmptyState.vue'

const videos = ref([])
const loading = ref(true)
const showDeleteModal = ref(false)
const deletingVideo = ref(null)
const deleting = ref(false)
const deleteError = ref('')

onMounted(async () => {
  try {
    const res = await api.get('/api/videos')
    videos.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    loading.value = false
  }
})

function confirmDelete(video) {
  deletingVideo.value = video
  deleteError.value = ''
  showDeleteModal.value = true
}

async function doDelete() {
  deleting.value = true
  deleteError.value = ''
  try {
    await api.delete(`/api/videos/${deletingVideo.value.id}`)
    videos.value = videos.value.filter(v => v.id !== deletingVideo.value.id)
    showDeleteModal.value = false
    deletingVideo.value = null
  } catch (e) {
    deleteError.value = e.response?.data?.detail || '删除失败，请重试'
  } finally {
    deleting.value = false
  }
}

function formatDate(d) { return d ? new Date(d).toLocaleDateString('zh-CN') : '' }
</script>
