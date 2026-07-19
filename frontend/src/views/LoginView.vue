<template>
  <main id="main" class="section container auth-shell">
    <div class="paper form-card auth-card">
      <h1 style="font-size: 24px; text-align: center; margin-bottom: 6px">
        Đăng nhập
      </h1>
      <p
        style="
          text-align: center;
          color: var(--color-ink-soft);
          font-size: 14px;
          margin-bottom: 28px;
        "
      >
        Đăng nhập để xem và cập nhật gia phả dòng họ.
      </p>

      <form @submit.prevent="submitLogin">
        <div class="form-grid" style="grid-template-columns: 1fr">
          <div class="field">
            <label for="login-email">Email hoặc tên đăng nhập</label>
            <input
              id="login-email"
              type="text"
              v-model="form.identifier"
              placeholder="ban@vidu.vn"
              autocomplete="username"
            />
          </div>
          <div class="field">
            <label for="login-password">Mật khẩu</label>
            <input
              id="login-password"
              type="password"
              v-model="form.password"
              placeholder="••••••••"
              autocomplete="current-password"
            />
          </div>
        </div>

        <div class="auth-row">
          <label class="auth-checkbox">
            <input type="checkbox" v-model="form.remember" />
            Ghi nhớ đăng nhập
          </label>
          <a href="#" class="auth-link">Quên mật khẩu?</a>
        </div>

        <div class="form-actions" style="justify-content: stretch">
          <button
            type="submit"
            class="btn btn-primary"
            style="width: 100%; justify-content: center"
          >
            Đăng nhập
          </button>
        </div>
      </form>

      <p class="auth-switch">
        Chưa có tài khoản?
        <a href="#" class="auth-link">Đăng ký ngay</a>
      </p>
    </div>
  </main>
</template>

<script setup>
// Form tĩnh — sau này sẽ gọi POST /api/auth/login
import { reactive } from "vue";

const form = reactive({
  identifier: "",
  password: "",
  remember: false,
});

function submitLogin() {
  console.log("Đăng nhập với:", form);
}
</script>

<style scoped>
.auth-shell {
  display: flex;
  justify-content: center;
  padding-top: 64px;
  padding-bottom: 64px;
}
.auth-card {
  width: 100%;
  max-width: 420px;
}
.auth-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 18px 0 24px;
  font-size: 13.5px;
}
.auth-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-ink-soft);
}
.auth-link {
  color: var(--color-seal);
  font-weight: 600;
}
.auth-link:hover {
  text-decoration: underline;
}
.auth-switch {
  text-align: center;
  margin-top: 24px;
  font-size: 14px;
  color: var(--color-ink-soft);
}
</style>
