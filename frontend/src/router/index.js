// router/index.js
import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import TreeView from "../views/TreeView.vue";
import EventView from "../views/EventView.vue";
import AlbumView from "../views/AlbumView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import EventDetailView from "../views/EventDetailView.vue";
import AlbumDetail from "../views/AlbumDetail.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: HomeView },
    { path: "/gia-pha", component: TreeView },
    { path: "/events", component: EventView },
    { path: "/albums", component: AlbumView },
    { path: "/login", component: LoginView },
    { path: "/register", component: RegisterView },
    { path: "/events/:id", component: EventDetailView },
    { path: "/albums/:id", component: AlbumDetail },
  ],
});
