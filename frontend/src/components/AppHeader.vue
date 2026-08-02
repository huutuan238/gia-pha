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
        <RouterLink to="/tra-cuu" active-class="is-active">Tra cứu</RouterLink>
        <RouterLink to="/events" active-class="is-active">Sự kiện</RouterLink>
        <RouterLink to="/albums" active-class="is-active">Album ảnh</RouterLink>
        <RouterLink v-if="isAdmin" to="/admin" active-class="is-active">Quản trị</RouterLink>

        <!-- ================= KHU VỰC TÀI KHOẢN ================= -->
        <div class="account-area" ref="accountAreaRef">
          <!-- Chưa đăng nhập: bấm icon -> mở thẳng modal đăng nhập -->
          <button
            v-if="!authStore.state.user"
            type="button"
            class="account-icon-btn"
            title="Đăng nhập"
            aria-label="Đăng nhập"
            @click="openAuthModal('login')"
          >
            <svg viewBox="0 0 24 24" width="20" height="20">
              <path
                d="M15 17l5-5-5-5M20 12H9M13 5H6a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h7"
                fill="none"
                stroke="currentColor"
                stroke-width="1.8"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>

          <!-- Đã đăng nhập: bấm avatar -> sổ dropdown -->
          <template v-else>
            <button
              type="button"
              class="account-icon-btn account-avatar-btn"
              :aria-expanded="dropdownOpen"
              aria-label="Tài khoản"
              @click="dropdownOpen = !dropdownOpen"
            >
              <span class="avatar-initial">{{ userInitial }}</span>
            </button>

            <transition name="dropdown-fade">
              <div v-if="dropdownOpen" class="account-dropdown">
                <div class="account-dropdown-header">
                  <span class="account-dropdown-greeting">Xin chào</span>
                  <span class="account-dropdown-name">{{ authStore.state.user.username }}</span>
                </div>
                <button
                  type="button"
                  class="account-dropdown-item account-dropdown-logout"
                  @click="handleLogout"
                >
                  <svg viewBox="0 0 24 24" width="16" height="16">
                    <path
                      d="M9 7l-5 5 5 5M4 12h11M15 5h4a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2h-4"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  Đăng xuất
                </button>
              </div>
            </transition>
          </template>
        </div>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { openAuthModal } from '../stores/ui.js'
import { authStore } from '../stores/auth.js'

const isAdmin = computed(() => authStore.state.user?.role === 'admin')

const dropdownOpen = ref(false)
const accountAreaRef = ref(null)

const userInitial = computed(() => {
  const name = authStore.state.user?.username || ''
  return name.trim().charAt(0).toUpperCase() || '?'
})

function handleLogout() {
  dropdownOpen.value = false
  authStore.logout()
}

function handleClickOutside(e) {
  if (accountAreaRef.value && !accountAreaRef.value.contains(e.target)) {
    dropdownOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside))
onBeforeUnmount(() => document.removeEventListener('click', handleClickOutside))
</script>

<style scoped>
.account-area {
  position: relative;
  display: flex;
  align-items: center;
}

.account-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--ink-soft, #6b6455);
  background: transparent;
  color: var(--ink, #2c281f);
  cursor: pointer;
  transition: background 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}
.account-icon-btn:hover {
  background: var(--gold-soft, rgba(197, 160, 60, 0.14));
  border-color: var(--gold, #c5a03c);
  color: var(--gold, #c5a03c);
}

.account-avatar-btn {
  border-color: var(--gold, #c5a03c);
}
.avatar-initial {
  font-size: 14px;
  font-weight: 700;
  color: inherit;
}

.account-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  min-width: 200px;
  background: var(--paper, #fff);
  border: 1px solid var(--paper-line, #e2ddce);
  border-radius: 10px;
  box-shadow: 0 10px 28px rgba(14, 24, 19, 0.16);
  padding: 8px;
  z-index: 50;
}

.account-dropdown-header {
  display: flex;
  flex-direction: column;
  padding: 10px 12px 12px;
  margin-bottom: 6px;
  border-bottom: 1px solid var(--paper-line, #e2ddce);
}
.account-dropdown-greeting {
  font-size: 11.5px;
  color: var(--ink-soft, #6b6455);
}
.account-dropdown-name {
  font-size: 14.5px;
  font-weight: 700;
  color: var(--ink, #2c281f);
}

.account-dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 12px;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-family: inherit;
  font-size: 14px;
  color: var(--ink, #2c281f);
  cursor: pointer;
  text-align: left;
}
.account-dropdown-item:hover {
  background: rgba(86, 73, 47, 0.08);
}
.account-dropdown-logout {
  color: var(--seal, #a5312b);
}
.account-dropdown-logout:hover {
  background: rgba(165, 49, 43, 0.1);
}

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>