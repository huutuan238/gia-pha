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
        <RouterLink to="/event" active-class="is-active">Sự kiện</RouterLink>
        <RouterLink to="/album" active-class="is-active">Album ảnh</RouterLink>
        <RouterLink to="/login" active-class="is-active">Đăng nhập</RouterLink>
      </nav>
    </div>
  </header>
</template>
