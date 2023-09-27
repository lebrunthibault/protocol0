import { createRouter, createWebHistory } from 'vue-router'
import AbletonSetView from '../views/AbletonSetView.vue'
import ActionView from '../views/ScriptActionsView.vue'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/set',
      name: 'abletonSet',
      component: AbletonSetView
    },
    {
      path: '/actions',
      name: 'actions',
      component: ActionView
    }
  ]
})

export default router
