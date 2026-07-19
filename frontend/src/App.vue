<template>
  <AppHeader />
  <router-view />
  <AppFooter />
  <AuthModal />
</template>
<script setup>
import AppHeader from "./components/AppHeader.vue";
import AppFooter from "./components/AppFooter.vue";
import AuthModal from "./components/AuthModal.vue";
</script>
