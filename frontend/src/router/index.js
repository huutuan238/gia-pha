// router/index.js
import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import TreeView from "../views/TreeView.vue";
import EventView from "../views/EventView.vue";
import AlbumView from "../views/AlbumView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: HomeView },
    { path: "/gia-pha", component: TreeView },
    { path: "/event", component: EventView },
    { path: "/album", component: AlbumView },
    { path: "/login", component: LoginView },
    { path: "/register", component: RegisterView },
  ],
});
