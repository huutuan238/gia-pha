// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import TreeView from '../views/TreeView.vue'
// import MemberView from '../views/FamilyChart.vue/index.js'
// import EventsView from '../views/EventsView.vue'
// import AlbumView from '../views/AlbumView.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: HomeView },
    { path: '/gia-pha', component: TreeView },
    // { path: '/them-thanh-vien', component: MemberView },
    // { path: '/su-kien', component: EventsView },
    // { path: '/album', component: AlbumView },
  ]
})