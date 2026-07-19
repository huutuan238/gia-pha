<template>
    <Teleport to="body">
      <div v-if="uiStore.showAuthModal" class="modal-overlay" @click.self="closeAuthModal">
        <div class="paper modal-card">
          <button class="modal-close" @click="closeAuthModal" aria-label="Đóng">✕</button>
          <div class="seal-badge" style="margin:0 auto 20px;">GP</div>
  
          <!-- ================= ĐĂNG NHẬP ================= -->
          <template v-if="uiStore.authModalMode === 'login'">
            <h2 style="font-size:22px; text-align:center; margin-bottom:6px;">Đăng nhập</h2>
            <p style="text-align:center; color:var(--color-ink-soft); font-size:14px; margin-bottom:24px;">
              Đăng nhập để xem và cập nhật gia phả dòng họ.
            </p>
  
            <p v-if="errorMessage" class="alert-error">{{ errorMessage }}</p>
  
            <form @submit.prevent="submitLogin">
              <div class="field" style="margin-bottom:16px;">
                <label>Email hoặc tên đăng nhập</label>
                <input v-model="loginForm.identifier" type="text" autocomplete="username">
              </div>
              <div class="field" style="margin-bottom:8px;">
                <label>Mật khẩu</label>
                <input v-model="loginForm.password" type="password" autocomplete="current-password">
              </div>
  
              <button type="submit" class="btn btn-primary" style="width:100%; justify-content:center; margin-top:16px;" :disabled="loading">
                {{ loading ? 'Đang đăng nhập…' : 'Đăng nhập' }}
              </button>
            </form>
  
            <p class="auth-switch">
              Chưa có tài khoản?
              <a href="#" class="auth-link" @click.prevent="switchMode('register')">Đăng ký ngay</a>
            </p>
          </template>
  
          <!-- ================= ĐĂNG KÝ ================= -->
          <template v-else>
            <h2 style="font-size:22px; text-align:center; margin-bottom:6px;">Đăng ký tài khoản</h2>
            <p style="text-align:center; color:var(--color-ink-soft); font-size:14px; margin-bottom:24px;">
              Tạo tài khoản để tham gia cập nhật gia phả dòng họ.
            </p>
  
            <p v-if="errorMessage" class="alert-error">{{ errorMessage }}</p>
  
            <form @submit.prevent="submitRegister">
              <div class="field" style="margin-bottom:16px;">
                <label>Tên đăng nhập</label>
                <input v-model="registerForm.username" type="text" autocomplete="username">
              </div>
              <div class="field" style="margin-bottom:16px;">
                <label>Email</label>
                <input v-model="registerForm.email" type="email" autocomplete="email">
              </div>
              <div class="field" style="margin-bottom:16px;">
                <label>Mật khẩu</label>
                <input v-model="registerForm.password" type="password" autocomplete="new-password" placeholder="Tối thiểu 6 ký tự">
              </div>
              <div class="field" style="margin-bottom:8px;">
                <label>Xác nhận mật khẩu</label>
                <input v-model="registerForm.confirmPassword" type="password" autocomplete="new-password">
                <span class="hint" v-if="passwordMismatch" style="color:var(--color-seal);">
                  Mật khẩu xác nhận chưa khớp
                </span>
              </div>
  
              <button type="submit" class="btn btn-primary" style="width:100%; justify-content:center; margin-top:16px;" :disabled="loading || passwordMismatch">
                {{ loading ? 'Đang đăng ký…' : 'Đăng ký' }}
              </button>
            </form>
  
            <p class="auth-switch">
              Đã có tài khoản?
              <a href="#" class="auth-link" @click.prevent="switchMode('login')">Đăng nhập</a>
            </p>
          </template>
        </div>
      </div>
    </Teleport>
  </template>
  
  <script setup>
  import { reactive, ref, computed, watch } from 'vue'
  import { uiStore, closeAuthModal } from '../stores/ui.js'
  import { authStore } from '../stores/auth.js'
  
  const loading = ref(false)
  const errorMessage = ref('')
  
  const loginForm = reactive({ identifier: '', password: '' })
  const registerForm = reactive({ username: '', email: '', password: '', confirmPassword: '' })
  
  const passwordMismatch = computed(
    () => registerForm.confirmPassword.length > 0 && registerForm.password !== registerForm.confirmPassword
  )
  
  // Xoá thông báo lỗi + reset form mỗi khi đổi chế độ hoặc mở lại modal
  watch(() => uiStore.showAuthModal, (open) => {
    if (open) {
      errorMessage.value = ''
      loginForm.identifier = ''
      loginForm.password = ''
      registerForm.username = ''
      registerForm.email = ''
      registerForm.password = ''
      registerForm.confirmPassword = ''
    }
  })
  
  function switchMode(mode) {
    errorMessage.value = ''
    uiStore.authModalMode = mode
  }
  
  async function submitLogin() {
    loading.value = true
    errorMessage.value = ''
    try {
      await authStore.login({ identifier: loginForm.identifier, password: loginForm.password })
      closeAuthModal()
    } catch (err) {
      errorMessage.value = err.message
    } finally {
      loading.value = false
    }
  }
  
  async function submitRegister() {
    if (passwordMismatch.value) return
    loading.value = true
    errorMessage.value = ''
    try {
      await authStore.register({
        username: registerForm.username,
        email: registerForm.email,
        password: registerForm.password,
      })
      closeAuthModal()
    } catch (err) {
      errorMessage.value = err.message
    } finally {
      loading.value = false
    }
  }
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(14, 24, 19, 0.72);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 24px;
  }
  .modal-card {
    width: 100%;
    max-width: 420px;
    max-height: 90vh;
    overflow-y: auto;
    padding: 36px;
    position: relative;
  }
  .modal-close {
    position: absolute;
    top: 16px;
    right: 16px;
    background: transparent;
    border: none;
    font-size: 16px;
    color: var(--color-ink-soft);
    cursor: pointer;
  }
  .modal-close:hover { color: var(--color-seal); }
  
  .auth-switch {
    text-align: center;
    margin-top: 22px;
    font-size: 14px;
    color: var(--color-ink-soft);
  }
  .auth-link { color: var(--color-seal); font-weight: 600; }
  .auth-link:hover { text-decoration: underline; }
  
  .alert-error {
    background: rgba(165, 49, 43, 0.12);
    color: var(--color-seal);
    border: 1px solid var(--color-seal);
    border-radius: 4px;
    padding: 10px 14px;
    font-size: 13.5px;
    margin-bottom: 18px;
  }
  </style>