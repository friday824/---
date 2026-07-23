<template>
  <div class="flex flex-col items-center justify-center py-16 text-center">
    <div class="text-6xl mb-4">{{ icon }}</div>
    <h3 class="text-lg font-medium text-gray-600 mb-2">{{ title }}</h3>
    <p class="text-gray-400 text-sm mb-6">{{ description }}</p>
    <router-link v-if="linkTo" :to="linkTo" class="bg-sakura-500 hover:bg-sakura-600 text-white px-6 py-2 rounded-full text-sm font-medium transition-all">
      {{ linkText }}
    </router-link>
  </div>
</template>

<script setup>
defineProps({
  icon: { type: String, default: '📭' },
  title: { type: String, default: '' },
  description: { type: String, default: '' },
  linkTo: { type: String, default: '' },
  linkText: { type: String, default: '' },
})
</script>
