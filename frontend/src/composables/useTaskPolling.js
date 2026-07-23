import { ref, onMounted, onUnmounted } from 'vue'
import { api } from './useApi'

export function useTaskPolling(taskId) {
  const progress = ref(0)
  const status = ref('pending')
  const currentStage = ref('')
  const error = ref(null)
  const isComplete = ref(false)
  const videoId = ref(null)

  let pollTimer = null

  const stageLabels = {
    script_gen: '正在分析你的日记...',
    image_gen: '正在绘制动画场景...',
    tts: '正在录制温暖旁白...',
    bgm: '正在匹配背景音乐...',
    compositing: '正在合成视频...',
    done: '完成！',
  }

  const currentStageLabel = () => stageLabels[currentStage.value] || currentStage.value

  const startPolling = () => {
    let pendingStart = null

    pollTimer = setInterval(async () => {
      try {
        const res = await api.get(`/api/tasks/${taskId}`)
        progress.value = res.data.progress
        status.value = res.data.status
        currentStage.value = res.data.current_stage
        videoId.value = res.data.video_id

        if (res.data.status === 'pending') {
          if (!pendingStart) pendingStart = Date.now()
          if (Date.now() - pendingStart > 15000) {
            error.value = '任务启动超时，服务器可能已重启，请返回重试'
            stopPolling()
            return
          }
        }

        if (res.data.status === 'completed') {
          isComplete.value = true
          stopPolling()
        }
        if (res.data.status === 'failed') {
          error.value = res.data.error_message || '生成失败，请重试'
          stopPolling()
        }
      } catch (e) {
        error.value = '获取任务状态失败'
        stopPolling()
      }
    }, 2000)
  }

  const stopPolling = () => {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  onMounted(startPolling)
  onUnmounted(stopPolling)

  return { progress, status, currentStage, currentStageLabel, error, isComplete, videoId, stopPolling }
}
