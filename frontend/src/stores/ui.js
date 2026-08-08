import { reactive } from "vue";

export const uiStore = reactive({
  showAuthModal: false,
  authModalMode: "login", // 'login' | 'register'
});

export function openAuthModal(mode = "login") {
  uiStore.authModalMode = mode;
  uiStore.showAuthModal = true;
}

export function closeAuthModal() {
  uiStore.showAuthModal = false;
}
