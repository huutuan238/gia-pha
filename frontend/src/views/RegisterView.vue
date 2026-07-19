<template>
  <main id="main" class="section container auth-shell">
    <div class="paper form-card auth-card">
      <h1 style="font-size: 24px; text-align: center; margin-bottom: 6px">
        Đăng ký tài khoản
      </h1>
      <p
        style="
          text-align: center;
          color: var(--color-ink-soft);
          font-size: 14px;
          margin-bottom: 28px;
        "
      >
        Tạo tài khoản để tham gia xây dựng và cập nhật gia phả dòng họ.
      </p>

      <form @submit.prevent="submitRegister">
        <div class="form-grid" style="grid-template-columns: 1fr">
          <div class="field">
            <label for="reg-name">Họ và tên</label>
            <input
              id="reg-name"
              type="text"
              v-model="form.fullName"
              placeholder="Ví dụ: Nguyễn Văn An"
              autocomplete="name"
            />
          </div>
          <div class="field">
            <label for="reg-email">Email</label>
            <input
              id="reg-email"
              type="email"
              v-model="form.email"
              placeholder="ban@vidu.vn"
              autocomplete="email"
            />
          </div>
          <div class="field">
            <label for="reg-password">Mật khẩu</label>
            <input
              id="reg-password"
              type="password"
              v-model="form.password"
              placeholder="Tối thiểu 8 ký tự"
              autocomplete="new-password"
            />
          </div>
          <div class="field">
            <label for="reg-confirm">Xác nhận mật khẩu</label>
            <input
              id="reg-confirm"
              type="password"
              v-model="form.confirmPassword"
              placeholder="Nhập lại mật khẩu"
              autocomplete="new-password"
            />
            <span
              class="hint"
              v-if="passwordMismatch"
              style="color: var(--color-seal)"
            >
              Mật khẩu xác nhận chưa khớp
            </span>
          </div>
        </div>

        <label class="auth-checkbox" style="margin: 18px 0 24px">
          <input type="checkbox" v-model="form.agree" />
          Tôi đồng ý với điều khoản sử dụng gia phả điện tử
        </label>

        <div class="form-actions" style="justify-content: stretch">
          <button
            type="submit"
            class="btn btn-primary"
            style="width: 100%; justify-content: center"
            :disabled="!canSubmit"
          >
            Đăng ký
          </button>
        </div>
      </form>

      <p class="auth-switch">
        Đã có tài khoản?
        <a href="#" class="auth-link">Đăng nhập</a>
      </p>
    </div>
  </main>
</template>

<script setup>
// Form tĩnh — sau này sẽ gọi POST /api/auth/register
import { reactive, computed } from "vue";

const form = reactive({
  fullName: "",
  email: "",
  password: "",
  confirmPassword: "",
  agree: false,
});

const passwordMismatch = computed(
  () =>
    form.confirmPassword.length > 0 && form.password !== form.confirmPassword,
);

const canSubmit = computed(
  () =>
    form.fullName &&
    form.email &&
    form.password &&
    form.password === form.confirmPassword &&
    form.agree,
);

function submitRegister() {
  console.log("Đăng ký với:", form);
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
  max-width: 440px;
}
.auth-checkbox {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-ink-soft);
  font-size: 13.5px;
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
.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}
</style>
