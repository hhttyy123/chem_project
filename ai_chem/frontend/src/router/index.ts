import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import MoleculeViewer from '@/views/MoleculeViewer.vue'
import Practice from '@/views/Practice.vue'
import Favorites from '@/views/Favorites.vue'
import Profile from '@/views/Profile.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/viewer',
      name: 'viewer',
      component: MoleculeViewer
    },
    {
      path: '/practice',
      name: 'practice',
      component: Practice
    },
    {
      path: '/favorites',
      name: 'favorites',
      component: Favorites
    },
    {
      path: '/profile',
      name: 'profile',
      component: Profile
    }
  ]
})

export default router
