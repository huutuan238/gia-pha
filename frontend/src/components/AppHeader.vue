<template>
  <header class="site-header">
    <div class="header-inner">
      <RouterLink class="brand" to="/">
        <span class="seal" aria-hidden="true">
          <svg viewBox="0 0 40 40" width="30" height="30">
            <circle
              cx="20"
              cy="20"
              r="18.5"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
            />
            <path
              d="M20 29 V15 M20 15 L13.5 8.5 M20 15 L26.5 8.5 M14.5 21 L20 15 L25.5 21"
              stroke="currentColor"
              stroke-width="1.6"
              fill="none"
              stroke-linecap="round"
            />
          </svg>
        </span>
        <span class="brand-text">Gia Phả Họ <em>Nguyễn Hữu</em></span>
      </RouterLink>
      <input type="checkbox" id="nav-toggle" class="nav-toggle-input" />
      <label for="nav-toggle" class="nav-toggle-label" aria-label="Mở menu"
        ><span></span
      ></label>
      <nav class="site-nav">
        <RouterLink to="/" active-class="is-active"> Giới thiệu </RouterLink>
        <RouterLink to="/gia-pha" active-class="is-active">Gia phả</RouterLink>
        <RouterLink to="/events" active-class="is-active">Sự kiện</RouterLink>
        <RouterLink to="/albums" active-class="is-active">Album ảnh</RouterLink>

        <!-- Chưa đăng nhập -->
        <a
          v-if="!authStore.state.user"
          href="#"
          class="nav-cta"
          @click.prevent="openAuthModal('login')"
        >
          Đăng nhập
        </a>

        <!-- Đã đăng nhập -->
        <div v-else class="nav-user">
          <span class="nav-user-name">{{ authStore.state.user.username }}</span>
          <a href="#" class="nav-cta" @click.prevent="authStore.logout()">
            Đăng xuất
          </a>
        </div>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { openAuthModal } from '../stores/ui.js'
import { authStore } from '../stores/auth.js'
</script>

<style scoped>
.nav-user {
  display: flex;
  align-items: center;
  gap: 12px;
}
.nav-user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-soft);
}
</style>