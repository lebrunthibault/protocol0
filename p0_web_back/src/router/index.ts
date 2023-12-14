import {createRouter, createWebHistory} from 'vue-router'
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
      path: '/actions',
      name: 'actions',
      component: ActionView
    }
  ]
})

export default router
