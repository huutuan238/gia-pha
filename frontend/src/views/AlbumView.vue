<template>
  <main id="main" class="section container">
    <div class="tree-toolbar">
      <div>
        <span class="eyebrow"
          >{{ albums.length }} album · {{ totalPhotos }} ảnh</span
        >
        <h1 style="font-size: 28px">Album ảnh gia đình</h1>
      </div>
      <a href="#" class="btn btn-primary">+ Tạo album</a>
    </div>

    <!-- DANH SÁCH ALBUM -->
    <div class="album-grid">
      <div
        class="paper album-card"
        v-for="album in albums"
        :key="album.id"
        :class="{ 'is-selected': album.id === selectedAlbumId }"
        @click="selectedAlbumId = album.id"
        style="cursor: pointer"
      >
        <div class="album-cover">{{ album.coverLabel }}</div>
        <div class="album-info">
          <h3>{{ album.title }}</h3>
          <p>{{ album.description }}</p>
          <span class="count">{{ album.photos.length }} ảnh</span>
        </div>
      </div>
    </div>

    <!-- ẢNH TRONG ALBUM ĐANG CHỌN -->
    <div v-if="selectedAlbum" style="margin-top: 56px">
      <div class="generation-label">
        <span class="line" style="max-width: 0"></span>
        <span>{{ selectedAlbum.title }}</span>
        <span class="line"></span>
      </div>
      <div class="photo-grid">
        <div
          class="photo-tile"
          v-for="photo in selectedAlbum.photos"
          :key="photo.id"
        >
          {{ photo.caption }}
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
// Dữ liệu tĩnh khai báo ngay trong component.
// Sau này sẽ thay bằng dữ liệu lấy từ API Flask:
// GET /api/albums, GET /api/albums/<id>/photos
import { reactive, ref, computed } from "vue";

const albums = reactive([
  {
    id: 1,
    title: "Giỗ tổ 2025",
    description: "Ảnh chụp buổi lễ giỗ tổ tại nhà thờ họ, làng Đông Bàn.",
    coverLabel: "Ảnh bìa",
    photos: [
      { id: 1, caption: "Ảnh 1" },
      { id: 2, caption: "Ảnh 2" },
      { id: 3, caption: "Ảnh 3" },
      { id: 4, caption: "Ảnh 4" },
      { id: 5, caption: "Ảnh 5" },
      { id: 6, caption: "Ảnh 6" },
      { id: 7, caption: "Ảnh 7" },
      { id: 8, caption: "Ảnh 8" },
    ],
  },
  {
    id: 2,
    title: "Họp mặt chi thứ 3",
    description: "Kỷ niệm buổi họp mặt thường niên năm 2025.",
    coverLabel: "Ảnh bìa",
    photos: [
      { id: 1, caption: "Ảnh 1" },
      { id: 2, caption: "Ảnh 2" },
      { id: 3, caption: "Ảnh 3" },
      { id: 4, caption: "Ảnh 4" },
    ],
  },
  {
    id: 3,
    title: "Nhà thờ họ qua các năm",
    description: "Ảnh tư liệu về nhà thờ họ từ 1980 đến nay.",
    coverLabel: "Ảnh bìa",
    photos: [
      { id: 1, caption: "Ảnh 1" },
      { id: 2, caption: "Ảnh 2" },
      { id: 3, caption: "Ảnh 3" },
    ],
  },
]);

const selectedAlbumId = ref(albums[0].id);
const selectedAlbum = computed(() =>
  albums.find((album) => album.id === selectedAlbumId.value),
);
const totalPhotos = computed(() =>
  albums.reduce((sum, album) => sum + album.photos.length, 0),
);
</script>

<style scoped>
.album-card.is-selected {
  outline: 2px solid var(--color-seal);
  outline-offset: -1px;
}
</style>
