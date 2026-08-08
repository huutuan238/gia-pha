<template>
  <main class="section container" style="max-width: 1100px;">
    <RouterLink to="/cong-duc" class="back-link">← Quay lại Bảng vàng</RouterLink>

    <p v-if="loadError" class="alert-error">{{ loadError }}</p>
    <p v-if="loading" style="color: var(--color-cream-dim);">Đang tải…</p>

    <template v-else-if="entry">
      <div class="tree-toolbar" style="margin-top: 16px;">
        <div>
          <span class="eyebrow" v-if="entry.eventDate">{{ formatDate(entry.eventDate) }}</span>
          <h1 style="font-size: 26px;">{{ entry.title }}</h1>
          <p v-if="entry.description" style="color: var(--color-cream-dim); margin-top: 6px;">
            {{ entry.description }}
          </p>
        </div>
        <a :href="entry.excelUrl" target="_blank" rel="noopener" class="btn btn-outline">
          Mở trong Google Sheets
        </a>
      </div>

      <p v-if="!sheetEmbedUrl" class="alert-error" style="margin-top: 20px;">
        Không nhận diện được link Google Sheet — kiểm tra lại URL (phải có dạng
        https://docs.google.com/spreadsheets/d/&lt;ID&gt;/...), và đảm bảo sheet đã
        chia sẻ "Anyone with the link can view".
      </p>

      <iframe
        v-else
        :src="sheetEmbedUrl"
        class="sheet-embed"
        frameborder="0"
      ></iframe>
    </template>
  </main>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { getContributionById } from "../api/contribution.js";

const route = useRoute();

const entry = ref(null);
const loading = ref(false);
const loadError = ref("");

function formatDate(iso) {
  const d = new Date(iso);
  const pad = (n) => String(n).padStart(2, "0");
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()}`;
}

async function loadEntry() {
  loading.value = true;
  loadError.value = "";
  try {
    const { data } = await getContributionById(route.params.id);
    entry.value = data;
  } catch (err) {
    loadError.value = `Không tải được mục này: ${err.response?.data?.error || err.message}`;
  } finally {
    loading.value = false;
  }
}

// Google Sheets cho phép nhúng trực tiếp qua iframe với URL dạng
// /preview — không cần fetch/parse gì cả, không vướng CORS (khác hẳn
// cách làm với file .xlsx tải từ S3 trước đó). Chỉ cần trích đúng SHEET_ID
// từ link chia sẻ, và sheet phải để chế độ chia sẻ "Anyone with the link
// can view" (File -> Share -> General access).
//
// Link chia sẻ gốc dạng:
//   https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit?usp=sharing
// Link nhúng cần dùng:
//   https://docs.google.com/spreadsheets/d/<SHEET_ID>/preview
const sheetEmbedUrl = computed(() => {
  const url = entry.value?.excelUrl;
  if (!url) return "";
  const match = url.match(/\/d\/([a-zA-Z0-9-_]+)/);
  const sheetId = match ? match[1] : null;
  if (!sheetId) return "";
  return `https://docs.google.com/spreadsheets/d/${sheetId}/preview`;
});

onMounted(loadEntry);
</script>

<style scoped>
.back-link {
  display: inline-block;
  color: var(--color-cream-dim);
  font-size: 13.5px;
  margin-bottom: 8px;
}
.back-link:hover {
  color: var(--color-gold);
}

.sheet-embed {
  margin-top: 20px;
  width: 100%;
  height: 700px;
  border: 1px solid var(--color-paper-line, #cdb989);
  border-radius: 6px;
  background: #fff;
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
</style>