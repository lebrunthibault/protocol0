import { createRouter, createWebHistory } from 'vue-router'
import AbletonSetView from '../views/AbletonSet.vue'
import ActionView from '../views/ScriptActions.vue'
import HomeView from '../views/Home.vue'

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
