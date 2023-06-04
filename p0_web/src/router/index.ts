import { createRouter, createWebHistory } from 'vue-router'
import ActionView from '../views/ScriptActions.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: ActionView
    }
  ]
})

export default router
