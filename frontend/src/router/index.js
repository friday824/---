import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', name: 'landing', component: () => import('../pages/LandingPage.vue') },
  { path: '/auth/login', name: 'login', component: () => import('../pages/LoginPage.vue'), meta: { guest: true } },
  { path: '/auth/register', name: 'register', component: () => import('../pages/RegisterPage.vue'), meta: { guest: true } },
  { path: '/dashboard', name: 'dashboard', component: () => import('../pages/DashboardPage.vue'), meta: { requiresAuth: true } },
  { path: '/diaries/new', name: 'new-diary', component: () => import('../pages/NewDiaryPage.vue'), meta: { requiresAuth: true } },
  { path: '/diaries/:id', name: 'diary-detail', component: () => import('../pages/DiaryDetailPage.vue'), meta: { requiresAuth: true } },
  { path: '/diaries/:id/edit', name: 'edit-diary', component: () => import('../pages/EditDiaryPage.vue'), meta: { requiresAuth: true } },
  { path: '/videos', name: 'videos', component: () => import('../pages/VideoGalleryPage.vue'), meta: { requiresAuth: true } },
  { path: '/videos/:id', name: 'video-player', component: () => import('../pages/VideoPlayerPage.vue'), meta: { requiresAuth: true } },
  { path: '/tasks/:id', name: 'task-status', component: () => import('../pages/TaskStatusPage.vue'), meta: { requiresAuth: true } },
  { path: '/settings', name: 'settings', component: () => import('../pages/SettingsPage.vue'), meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('../pages/NotFoundPage.vue') },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.meta.guest && auth.isLoggedIn) {
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
