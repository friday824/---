<template>
  <div class="flex flex-col items-center justify-center py-12">
    <div class="w-10 h-10 border-3 border-sakura-200 border-t-sakura-500 rounded-full animate-spin"></div>
    <p v-if="text" class="mt-4 text-gray-500 text-sm">{{ text }}</p>
  </div>
</template>

<script setup>
defineProps({ text: { type: String, default: '' } })
</script>
