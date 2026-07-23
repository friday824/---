<template>
  <div class="max-w-2xl mx-auto px-4 py-8">
    <h1 class="font-display text-3xl text-sakura-600 mb-8">写日记 ✍️</h1>

    <form @submit.prevent="handleSaveAndGenerate" class="space-y-6">
      <div>
        <input v-model="title" type="text" required
          class="w-full text-xl font-medium px-4 py-3 rounded-xl border border-gray-200 focus:border-sakura-300 focus:ring-2 focus:ring-sakura-100 outline-none transition-all"
          placeholder="给今天的日记起个标题..." />
      </div>

      <div>
        <textarea v-model="content" required rows="12"
          class="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-sakura-300 focus:ring-2 focus:ring-sakura-100 outline-none transition-all resize-none"
          placeholder="今天发生了什么让你印象深刻的事情呢？写下你的心情和故事..."></textarea>
        <p class="text-right text-xs text-gray-400 mt-1">{{ content.length }} 字</p>
      </div>

      <!-- Mood selector -->
      <div>
        <label class="block text-sm font-medium text-gray-600 mb-2">今天的心情</label>
        <div class="flex gap-3">
          <button v-for="m in moods" :key="m.value" type="button" @click="mood = m.value"
            :class="['px-4 py-2 rounded-full text-sm transition-all',
              mood === m.value ? 'bg-sakura-100 text-sakura-600 ring-2 ring-sakura-300' : 'bg-gray-100 text-gray-500 hover:bg-gray-200']">
            {{ m.emoji }} {{ m.label }}
          </button>
        </div>
      </div>

      <p v-if="errorMsg" class="text-red-500 text-sm text-center">{{ errorMsg }}</p>

      <div class="flex gap-4">
        <button type="button" @click="handleSave"
          :disabled="saving"
          class="flex-1 bg-white border border-sakura-200 text-sakura-500 hover:bg-sakura-50 py-3 rounded-full font-medium transition-all disabled:opacity-50">
          {{ saving ? '保存中...' : '仅保存' }}
        </button>
        <button type="submit"
          :disabled="generating"
          class="flex-1 bg-sakura-500 hover:bg-sakura-600 text-white py-3 rounded-full font-medium transition-all disabled:bg-sakura-300 animate-pulse-glow">
          {{ generating ? '正在提交...' : '保存并生成视频 🎬' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../composables/useApi'

const router = useRouter()

const title = ref('')
const content = ref('')
const mood = ref('')
const saving = ref(false)
const generating = ref(false)
const errorMsg = ref('')

const moods = [
  { value: 'happy', label: '开心', emoji: '😊' },
  { value: 'calm', label: '平静', emoji: '😌' },
  { value: 'nostalgic', label: '怀念', emoji: '🥺' },
  { value: 'excited', label: '兴奋', emoji: '🎉' },
  { value: 'sad', label: '难过', emoji: '😢' },
  { value: 'romantic', label: '甜蜜', emoji: '💕' },
]

async function handleSave() {
  if (!title.value || !content.value) return
  errorMsg.value = ''
  saving.value = true
  try {
    const res = await api.post('/api/diaries', { title: title.value, content: content.value, mood_tag: mood.value || null })
    router.push(`/diaries/${res.data.id}`)
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '保存失败'
  } finally {
    saving.value = false
  }
}

async function handleSaveAndGenerate() {
  if (!title.value || !content.value) return
  errorMsg.value = ''
  generating.value = true
  try {
    const res = await api.post('/api/diaries', { title: title.value, content: content.value, mood_tag: mood.value || null })
    const diaryId = res.data.id
    const taskRes = await api.post(`/api/tasks/generate/${diaryId}`)
    router.push(`/tasks/${taskRes.data.id}`)
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || '提交失败'
  } finally {
    generating.value = false
  }
}
</script>
