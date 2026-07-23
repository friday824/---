<template>
  <div class="max-w-lg mx-auto px-4 py-16">
    <div class="bg-white rounded-2xl shadow-lg p-8 text-center">
      <!-- Success -->
      <template v-if="status === 'completed'">
        <div class="text-6xl mb-4">🌸</div>
        <h2 class="font-display text-2xl text-sakura-600 mb-2">视频生成完成！</h2>
        <p class="text-gray-400 text-sm mb-6">你的日记已经变成一部温馨的小动画</p>
        <router-link :to="`/videos/${videoId}`"
          class="inline-block bg-sakura-500 hover:bg-sakura-600 text-white px-8 py-3 rounded-full font-medium transition-all">
          观看视频 🎬
        </router-link>
      </template>

      <!-- Failed -->
      <template v-else-if="status === 'failed'">
        <div class="text-6xl mb-4">😢</div>
        <h2 class="font-display text-2xl text-gray-600 mb-2">生成失败</h2>
        <p class="text-gray-400 text-sm mb-6">{{ error || '遇到了一些问题，请重试' }}</p>
        <button @click="$router.back()"
          class="inline-block bg-white border border-sakura-200 text-sakura-500 hover:bg-sakura-50 px-8 py-3 rounded-full font-medium transition-all">
          返回重试
        </button>
      </template>

      <!-- Processing -->
      <template v-else>
        <div class="text-5xl mb-4">🎬</div>
        <h2 class="font-display text-2xl text-sakura-600 mb-2">正在生成你的动画</h2>
        <p class="text-gray-400 text-sm mb-6">{{ currentStageLabel() }}</p>

        <!-- Progress bar -->
        <div class="w-full bg-gray-100 rounded-full h-4 mb-4 overflow-hidden">
          <div class="h-full rounded-full bg-gradient-to-r from-sakura-300 to-sakura-500 animate-progress transition-all duration-500"
            :style="{ width: progress + '%' }"></div>
        </div>
        <p class="text-sakura-500 font-medium text-lg">{{ progress }}%</p>

        <!-- Stage info -->
        <div class="mt-6 space-y-2">
          <div v-for="stage in stages" :key="stage.key"
            class="flex items-center gap-3 text-sm"
            :class="stageStatus(stage.key)">
            <span>{{ stageStatus(stage.key) === 'done' ? '✅' : stageStatus(stage.key) === 'active' ? '⏳' : '⚪' }}</span>
            <span>{{ stage.label }}</span>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useTaskPolling } from '../composables/useTaskPolling'

const route = useRoute()
const { progress, status, currentStage, currentStageLabel, error, videoId } = useTaskPolling(route.params.id)

const stages = [
  { key: 'script_gen', label: 'AI 编写剧本' },
  { key: 'image_gen', label: '绘制动画场景' },
  { key: 'tts', label: '录制温暖旁白' },
  { key: 'bgm', label: '匹配背景音乐' },
  { key: 'compositing', label: '合成最终视频' },
]

const stageOrder = stages.map(s => s.key)

function stageStatus(key) {
  const cur = currentStage.value
  const curIdx = stageOrder.indexOf(cur)
  const keyIdx = stageOrder.indexOf(key)
  if (status.value === 'completed') return 'done'
  if (keyIdx < curIdx) return 'done'
  if (key === cur) return 'active'
  return 'pending'
}
</script>
