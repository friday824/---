<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <LoadingSpinner v-if="loading" text="加载日记..." />
    <form v-else-if="diary" @submit.prevent="handleSave" class="space-y-6">
      <h1 class="font-display text-3xl text-sakura-600">编辑日记</h1>
      <div>
        <input v-model="diary.title" type="text" required
          class="w-full text-xl font-medium px-4 py-3 rounded-xl border border-gray-200 focus:border-sakura-300 focus:ring-2 focus:ring-sakura-100 outline-none transition-all" />
      </div>
      <div>
        <textarea v-model="diary.content" required rows="12"
          class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-sakura-300 focus:ring-2 focus:ring-sakura-100 outline-none transition-all resize-none"></textarea>
        <p class="text-right text-xs text-gray-400 mt-1">{{ diary.content.length }} 字</p>
      </div>
      <p v-if="errorMsg" class="text-red-500 text-sm text-center">{{ errorMsg }}</p>
      <div class="flex gap-4">
        <router-link :to="`/diaries/${diary.id}`"
          class="flex-1 bg-white border border-gray-200 text-gray-600 hover:bg-gray-50 text-center py-3 rounded-full font-medium transition-all">取消</router-link>
        <button type="submit" :disabled="saving"
          class="flex-1 bg-sakura-500 hover:bg-sakura-600 disabled:bg-sakura-300 text-white py-3 rounded-full font-medium transition-all">
          {{ saving ? '保存中...' : '保存修改' }}
        </button>
      </div>
    </form>
    <EmptyState v-else icon="📖" title="日记未找到" link-to="/dashboard" link-text="返回列表" />
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
const saving = ref(false)
const errorMsg = ref('')

onMounted(async () => {
  try {
    const res = await api.get(`/api/diaries/${route.params.id}`)
    diary.value = res.data
  } catch { diary.value = null } finally { loading.value = false }
})

async function handleSave() {
  errorMsg.value = ''
  saving.value = true
  try {
    await api.put(`/api/diaries/${route.params.id}`, { title: diary.value.title, content: diary.value.content })
    router.push(`/diaries/${route.params.id}`)
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '保存失败'
  } finally { saving.value = false }
}
</script>
