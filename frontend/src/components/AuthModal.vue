<template>
  <Teleport to="body">
    <div v-if="uiStore.showAuthModal" class="auth-overlay" @click.self="closeAuthModal">
      <div class="auth-card">
        <button class="auth-close" @click="closeAuthModal" aria-label="Đóng">✕</button>
        <div class="auth-seal">GP</div>

        <!-- ================= ĐĂNG NHẬP ================= -->
        <template v-if="uiStore.authModalMode === 'login'">
          <h2 class="auth-title">Đăng nhập</h2>
          <p class="auth-subtitle">Đăng nhập để xem và cập nhật gia phả dòng họ.</p>

          <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>

          <form @submit.prevent="submitLogin" class="auth-form">
            <div class="auth-field">
              <label>Email hoặc tên đăng nhập</label>
              <input v-model="loginForm.identifier" type="text" autocomplete="username">
            </div>
            <div class="auth-field">
              <label>Mật khẩu</label>
              <input v-model="loginForm.password" type="password" autocomplete="current-password">
            </div>

            <button type="submit" class="auth-submit" :disabled="loading">
              {{ loading ? 'Đang đăng nhập…' : 'Đăng nhập' }}
            </button>
          </form>

          <p class="auth-switch">
            Chưa có tài khoản?
            <a href="#" @click.prevent="switchMode('register')">Đăng ký ngay</a>
          </p>
        </template>

        <!-- ================= ĐĂNG KÝ ================= -->
        <template v-else>
          <h2 class="auth-title">Đăng ký tài khoản</h2>
          <p class="auth-subtitle">Tạo tài khoản để tham gia cập nhật gia phả dòng họ.</p>

          <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>

          <form @submit.prevent="submitRegister" class="auth-form">
            <div class="auth-field">
              <label>Tên đăng nhập</label>
              <input v-model="registerForm.username" type="text" autocomplete="username">
            </div>
            <div class="auth-field">
              <label>Email</label>
              <input v-model="registerForm.email" type="email" autocomplete="email">
            </div>
            <div class="auth-field">
              <label>Mật khẩu</label>
              <input v-model="registerForm.password" type="password" autocomplete="new-password" placeholder="Tối thiểu 6 ký tự">
            </div>
            <div class="auth-field">
              <label>Xác nhận mật khẩu</label>
              <input v-model="registerForm.confirmPassword" type="password" autocomplete="new-password">
              <span v-if="passwordMismatch" class="auth-hint-error">Mật khẩu xác nhận chưa khớp</span>
            </div>

            <button type="submit" class="auth-submit" :disabled="loading || passwordMismatch">
              {{ loading ? 'Đang đăng ký…' : 'Đăng ký' }}
            </button>
          </form>

          <p class="auth-switch">
            Đã có tài khoản?
            <a href="#" @click.prevent="switchMode('login')">Đăng nhập</a>
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
/* CSS tự chứa hoàn toàn — không phụ thuộc class .paper/.field ở style.css
   ngoài, dùng var() có fallback cứng để dù project chưa load biến theme
   gốc, modal vẫn hiển thị đúng màu (không bị trong suốt/trôi chữ). */

.auth-overlay {
  position: fixed;
  inset: 0;
  background: rgba(10, 16, 13, 0.78);
  backdrop-filter: blur(3px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 420px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 40px 36px;
  position: relative;
  box-sizing: border-box;

  background: var(--color-paper, #f1e4c6);
  color: var(--color-ink, #241b12);
  border: 1px solid var(--color-paper-line, #cdb989);
  border-radius: 8px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
}

.auth-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  font-size: 15px;
  color: var(--color-ink-soft, #56492f);
  cursor: pointer;
  border-radius: 4px;
}
.auth-close:hover {
  color: var(--color-seal, #a5312b);
  background: rgba(0, 0, 0, 0.05);
}

.auth-seal {
  width: 46px;
  height: 46px;
  margin: 0 auto 20px;
  border: 2px solid var(--color-seal, #a5312b);
  border-radius: 6px;
  color: var(--color-seal, #a5312b);
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Noto Serif', serif;
  font-weight: 700;
  font-size: 13px;
  transform: rotate(-6deg);
}

.auth-title {
  font-family: 'Noto Serif', serif;
  font-size: 22px;
  font-weight: 700;
  text-align: center;
  margin: 0 0 6px;
  color: var(--color-ink, #241b12);
}

.auth-subtitle {
  text-align: center;
  font-size: 13.5px;
  color: var(--color-ink-soft, #56492f);
  margin: 0 0 26px;
}

.auth-error {
  background: rgba(165, 49, 43, 0.12);
  color: var(--color-seal, #a5312b);
  border: 1px solid var(--color-seal, #a5312b);
  border-radius: 4px;
  padding: 10px 14px;
  font-size: 13.5px;
  margin-bottom: 18px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.auth-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.auth-field label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-ink-soft, #56492f);
}
.auth-field input {
  font-family: 'Be Vietnam Pro', system-ui, sans-serif;
  font-size: 14.5px;
  padding: 11px 14px;
  border: 1px solid var(--color-paper-line, #cdb989);
  border-radius: 4px;
  background: #fbf6ea;
  color: var(--color-ink, #241b12);
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.auth-field input:focus {
  border-color: var(--color-seal, #a5312b);
  box-shadow: 0 0 0 3px rgba(165, 49, 43, 0.12);
}

/* Chặn Chrome/Edge tô nền xanh/vàng khi autofill email/password */
.auth-field input:-webkit-autofill,
.auth-field input:-webkit-autofill:hover,
.auth-field input:-webkit-autofill:focus {
  -webkit-box-shadow: 0 0 0 1000px #fbf6ea inset;
  -webkit-text-fill-color: var(--color-ink, #241b12);
  transition: background-color 9999s ease-in-out 0s;
}

.auth-hint-error {
  font-size: 12px;
  color: var(--color-seal, #a5312b);
}

.auth-submit {
  margin-top: 6px;
  width: 100%;
  padding: 12px;
  font-family: 'Be Vietnam Pro', system-ui, sans-serif;
  font-size: 15px;
  font-weight: 600;
  color: var(--color-cream, #f4ecd8);
  background: var(--color-seal, #a5312b);
  border: 1px solid var(--color-seal-dark, #7c2320);
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.15s ease, transform 0.15s ease;
}
.auth-submit:hover:not(:disabled) {
  background: var(--color-seal-dark, #7c2320);
  transform: translateY(-1px);
}
.auth-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.auth-switch {
  text-align: center;
  margin: 22px 0 0;
  font-size: 13.5px;
  color: var(--color-ink-soft, #56492f);
}
.auth-switch a {
  color: var(--color-seal, #a5312b);
  font-weight: 600;
  text-decoration: none;
}
.auth-switch a:hover {
  text-decoration: underline;
}
</style>