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
import FamilyView from "../views/FamilyView.vue";
import AdminDashBoard from "../views/AdminDashBoard.vue";
import FamilyChartInfo from "../views/FamilyChartInfo.vue";
import GoldBookView from "../views/GoldBookView.vue";
import GoldBookDetailView from "../views/GoldBookDetailView.vue";
import { authStore } from "../stores/auth.js";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: HomeView },
    { path: "/gia-pha", component: TreeView },
    { path: "/tra-cuu", component: FamilyChartInfo },
    { path: "/family", component: FamilyView },
    { path: "/events", component: EventView },
    { path: "/albums", component: AlbumView },
    { path: "/login", component: LoginView },
    { path: "/register", component: RegisterView },
    { path: "/events/:id", component: EventDetailView },
    { path: "/albums/:id", component: AlbumDetail },
    { path: "/cong-duc", component: GoldBookView },
    { path: "/cong-duc/:id", component: GoldBookDetailView },
    {
      path: "/admin",
      component: AdminDashBoard,
      meta: { requiresAdmin: true },
    },
  ],
});

// Chặn vào /admin (và mọi route có meta.requiresAdmin) nếu chưa đăng nhập
// hoặc không phải role admin.
router.beforeEach((to) => {
  if (to.meta.requiresAdmin && authStore.state.user?.role !== "admin") {
    return "/"; // hoặc trang 403 riêng nếu bạn có
  }
});

export default router;
