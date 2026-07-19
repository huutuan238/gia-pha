<template>
  <main id="main" class="section container">
    <div class="tree-toolbar">
      <div>
        <span class="eyebrow"
          >{{ albums.length }} album · {{ totalPhotos }} ảnh</span
        >
        <h1 style="font-size: 28px">Album ảnh gia đình</h1>
      </div>
      <button class="btn btn-primary" @click="showCreateModal = true">
        + Tạo album
      </button>
      <AlbumModal v-model:open="showCreateModal" @created="onAlbumCreated" />
    </div>

    <div v-if="loading" class="tree-status">Đang tải album...</div>

    <div v-else-if="loadError" class="tree-status tree-status-error">
      {{ loadError }}
      <button
        class="btn btn-outline"
        style="margin-left: 12px"
        @click="getAlbums"
      >
        Thử lại
      </button>
    </div>

    <template v-else>
      <p v-if="albums.length === 0" class="tree-status">Chưa có album nào.</p>

      <!-- DANH SÁCH ALBUM -->
      <div class="album-grid">
        <div
          class="paper album-card"
          v-for="album in albums"
          :key="album.id"
          style="cursor: pointer"
          @click="goToDetail(album.id)"
        >
          <div class="album-cover">
            <img
              v-if="album.coverPhotoUrl"
              :src="resolvePhotoUrl(album.coverPhotoUrl)"
              :alt="album.title"
              class="cover-img"
            />
            <span v-else class="cover-placeholder">Chưa có ảnh bìa</span>
          </div>
          <div class="album-info">
            <h3>{{ album.title }}</h3>
            <p>{{ album.description }}</p>
            <span class="count">{{ album.photoCount }} ảnh</span>
          </div>
        </div>
      </div>
    </template>
  </main>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from "vue";
import AlbumModal from "../components/AlbumModal.vue";
import { getAlbums as fetchAlbums, resolvePhotoUrl } from "../api/album.js";
import { useRouter } from "vue-router";

const router = useRouter();

const albums = reactive([]);
const loading = ref(false);
const loadError = ref("");
const showCreateModal = ref(false);

const totalPhotos = computed(() =>
  albums.reduce((sum, album) => sum + (album.photoCount || 0), 0),
);

async function getAlbums() {
  loading.value = true;
  loadError.value = "";
  try {
    const res = await fetchAlbums();
    const payload = res.data;
    const items = Array.isArray(payload)
      ? payload
      : payload.items || payload.data || [];
    albums.splice(0, albums.length, ...items);
  } catch (err) {
    console.error("Load albums error:", err);
    loadError.value = "Không thể tải danh sách album. Vui lòng thử lại.";
  } finally {
    loading.value = false;
  }
}

function onAlbumCreated(album) {
  albums.unshift(album);
}

function goToDetail(albumId) {
  router.push(`/albums/${albumId}`);
}

onMounted(getAlbums);
</script>
<style scoped>
.album-cover {
  aspect-ratio: 4/3;
  overflow: hidden;
  background: var(--paper-deep);
  display: flex;
  align-items: center;
  justify-content: center;
}
.cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.cover-placeholder {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--ink-soft);
}
</style>
