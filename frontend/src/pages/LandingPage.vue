<template>
  <div class="min-h-screen bg-gradient-to-b from-sakura-50 via-cream-50 to-sky-50 overflow-hidden">
    <!-- Floating petals -->
    <div class="fixed inset-0 pointer-events-none z-0">
      <div v-for="i in 15" :key="i"
        class="absolute animate-float-petal"
        :style="{
          left: Math.random() * 100 + '%',
          animationDuration: (8 + Math.random() * 12) + 's',
          animationDelay: (Math.random() * 10) + 's',
          fontSize: (12 + Math.random() * 20) + 'px',
          opacity: 0.3 + Math.random() * 0.4,
        }">
        🌸
      </div>
    </div>

    <!-- Hero -->
    <section class="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 text-center">
      <h1 class="font-display text-5xl md:text-7xl text-sakura-500 mb-6 animate-fade-in-up">
        把你的日记<br/>变成一部<span class="text-sakura-600">温暖的小动画</span>
      </h1>
      <p class="text-lg md:text-xl text-gray-500 max-w-lg mb-10 animate-fade-in-up" style="animation-delay: 0.2s">
        AI 为你写剧本、画动漫、配旁白，把每一篇日记都变成独一无二的短片
      </p>
      <router-link to="/auth/register"
        class="bg-sakura-500 hover:bg-sakura-600 text-white text-lg px-10 py-4 rounded-full font-medium transition-all hover:shadow-xl hover:scale-105 animate-pulse-glow"
        style="animation-delay: 0.4s">
        开始创作 ✨
      </router-link>
      <p class="mt-4 text-gray-400 text-sm">
        已有账号？<router-link to="/auth/login" class="text-sakura-500 hover:underline">登录</router-link>
      </p>
    </section>

    <!-- Features -->
    <section class="relative z-10 max-w-5xl mx-auto px-4 pb-32">
      <div class="grid md:grid-cols-3 gap-8">
        <div class="bg-white/60 backdrop-blur-sm rounded-2xl p-8 text-center shadow-sm hover:shadow-md transition-shadow">
          <div class="text-4xl mb-4">📝</div>
          <h3 class="font-display text-xl text-sakura-600 mb-2">AI 智能编剧</h3>
          <p class="text-gray-500 text-sm">深度分析你的日记，提取美好瞬间，编写温暖动画剧本</p>
        </div>
        <div class="bg-white/60 backdrop-blur-sm rounded-2xl p-8 text-center shadow-sm hover:shadow-md transition-shadow">
          <div class="text-4xl mb-4">🎨</div>
          <h3 class="font-display text-xl text-sakura-600 mb-2">动漫风格绘制</h3>
          <p class="text-gray-500 text-sm">每个场景都生成精美的吉卜力风动漫画面，温暖治愈</p>
        </div>
        <div class="bg-white/60 backdrop-blur-sm rounded-2xl p-8 text-center shadow-sm hover:shadow-md transition-shadow">
          <div class="text-4xl mb-4">🎙️</div>
          <h3 class="font-display text-xl text-sakura-600 mb-2">温暖配音旁白</h3>
          <p class="text-gray-500 text-sm">AI 温柔声线朗读你的故事，配上精选背景音乐</p>
        </div>
      </div>
    </section>
  </div>
</template>
