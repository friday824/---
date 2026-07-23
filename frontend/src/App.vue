<template>
  <div class="min-h-screen flex flex-col bg-cream-50">
    <AppHeader v-if="showHeader" />
    <main class="flex-1">
      <router-view v-slot="{ Component, route }">
        <Transition name="page" mode="out-in">
          <component :is="Component" :key="route.path" />
        </Transition>
      </router-view>
    </main>
    <AppFooter v-if="showHeader" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AppHeader from './components/layout/AppHeader.vue'
import AppFooter from './components/layout/AppFooter.vue'

const route = useRoute()
const showHeader = computed(() => route.name !== 'landing')
</script>

<style>
.page-enter-active,
.page-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
