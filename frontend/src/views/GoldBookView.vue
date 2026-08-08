<template>
    <main class="section container" style="max-width: 900px;">
      <div class="tree-toolbar">
        <div>
          <span class="eyebrow">Ghi công đức</span>
          <h1 style="font-size: 28px;">Bảng vàng đóng góp</h1>
        </div>
        <button v-if="isAdmin" class="btn btn-primary" @click="openCreatePanel">
          + Thêm mục đóng góp
        </button>
      </div>
  
      <p v-if="loadError" class="alert-error">{{ loadError }}</p>
      <p v-if="loading" style="color: var(--color-cream-dim);">Đang tải…</p>
  
      <div v-else class="entry-list">
        <RouterLink
          v-for="item in items"
          :key="item.id"
          :to="`/cong-duc/${item.id}`"
          class="paper entry-row"
        >
          <div class="entry-main">
            <h3>{{ item.title }}</h3>
            <p v-if="item.description">{{ item.description }}</p>
          </div>
          <div class="entry-meta">
            <span v-if="item.eventDate">{{ formatDate(item.eventDate) }}</span>
            <span class="entry-arrow">Xem chi tiết →</span>
          </div>
        </RouterLink>
  
        <p v-if="!items.length" style="color: var(--color-cream-dim);">
          Chưa có mục đóng góp nào.
        </p>
      </div>
    </main>
  
    <!-- ============ PANEL THÊM (chỉ admin) ============ -->
    <Teleport to="body">
      <div v-if="panel.open" class="modal-overlay" @click.self="closePanel">
        <div class="paper modal-card">
          <button class="modal-close" @click="closePanel">✕</button>
          <h2 style="font-size: 20px; margin-bottom: 20px;">Thêm mục đóng góp</h2>
          <p v-if="formError" class="alert-error">{{ formError }}</p>
  
          <form @submit.prevent="submitPanel">
            <div class="form-grid">
              <div class="field full">
                <label>Tiêu đề *</label>
                <input v-model="form.title" type="text" placeholder="Đóng góp xây nhà thờ họ 2026">
              </div>
              <div class="field full">
                <label>Link Google Sheet *</label>
                <input v-model="form.excelUrl" type="text" placeholder="https://docs.google.com/spreadsheets/d/.../edit?usp=sharing">
              </div>
              <div class="field">
                <label>Ngày</label>
                <input v-model="form.eventDate" type="date">
              </div>
              <div class="field full">
                <label>Mô tả</label>
                <textarea v-model="form.description" rows="3"></textarea>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="closePanel">Hủy</button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                {{ submitting ? "Đang lưu…" : "Lưu" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted, computed } from "vue";
  import { authStore } from "../stores/auth.js";
  import { getAllContribution, addContribution } from "../api/contribution.js";
  
  const isAdmin = computed(() => authStore.state.user?.role === "admin");
  
  const items = ref([]);
  const loading = ref(false);
  const loadError = ref("");
  
  async function fetchItems() {
    loading.value = true;
    loadError.value = "";
    try {
      const { data } = await getAllContribution();
      items.value = data;
    } catch (err) {
      loadError.value = `Không tải được danh sách: ${err.response?.data?.error || err.message}`;
    } finally {
      loading.value = false;
    }
  }
  
  onMounted(fetchItems);
  
  function formatDate(iso) {
    const d = new Date(iso);
    const pad = (n) => String(n).padStart(2, "0");
    return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;
  }
  
  const panel = reactive({ open: false });
  const form = reactive({ title: "", excelUrl: "", eventDate: "", description: "" });
  const formError = ref("");
  const submitting = ref(false);
  
  function openCreatePanel() {
    form.title = "";
    form.excelUrl = "";
    form.eventDate = "";
    form.description = "";
    formError.value = "";
    panel.open = true;
  }
  function closePanel() {
    panel.open = false;
  }
  
  async function submitPanel() {
    if (!form.title.trim() || !form.excelUrl.trim()) {
      formError.value = "Vui lòng nhập Tiêu đề và Link file Excel.";
      return;
    }
    submitting.value = true;
    formError.value = "";
    try {
      await addContribution({
        title: form.title,
        excelUrl: form.excelUrl,
        eventDate: form.eventDate || null,
        description: form.description,
      });
      await fetchItems();
      closePanel();
    } catch (err) {
      const body = err.response?.data;
      formError.value = (body?.errors && body.errors.join(", ")) || body?.error || "Lưu thất bại.";
    } finally {
      submitting.value = false;
    }
  }
  </script>
  
  <style scoped>
  .entry-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .entry-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    padding: 20px 24px;
    text-decoration: none;
    color: inherit;
    transition: transform 0.15s ease;
  }
  .entry-row:hover {
    transform: translateY(-1px);
  }
  .entry-main h3 {
    font-size: 16px;
    margin: 0 0 4px;
  }
  .entry-main p {
    font-size: 13.5px;
    color: var(--color-ink-soft);
    margin: 0;
  }
  .entry-meta {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 6px;
    font-size: 13px;
    color: var(--color-ink-soft);
    white-space: nowrap;
  }
  .entry-arrow {
    color: var(--color-seal);
    font-weight: 600;
  }
  
  .alert-error {
    background: rgba(165, 49, 43, 0.12);
    color: var(--color-seal);
    border: 1px solid var(--color-seal);
    border-radius: 4px;
    padding: 10px 14px;
    font-size: 13.5px;
    margin-bottom: 18px;
  }
  
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
    max-width: 560px;
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
  </style>