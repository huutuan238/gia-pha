<template>
  <main id="main" class="section container">
    <button class="btn btn-ghost btn-sm back-btn" @click="goBack">
      ← Quay lại danh sách album
    </button>

    <div v-if="loading" class="tree-status">Đang tải album...</div>

    <div v-else-if="loadError" class="tree-status tree-status-error">
      {{ loadError }}
      <button
        class="btn btn-outline"
        style="margin-left: 12px"
        @click="getAlbumDetail"
      >
        Thử lại
      </button>
    </div>

    <template v-else-if="album">
      <div class="tree-toolbar">
        <div>
          <span class="eyebrow">{{ album.photos.length }} ảnh</span>
          <h1 style="font-size: 26px">{{ album.title }}</h1>
          <p v-if="album.description" style="margin-top: 4px">
            {{ album.description }}
          </p>
        </div>
        <button
          class="delete-btn"
          @click="onDeleteAlbum"
          :disabled="deletingAlbum"
        >
          {{ deletingAlbum ? "Đang xoá..." : "Xoá album" }}
        </button>
      </div>

      <!-- KHU VỰC UPLOAD -->
      <div
        class="upload-drop"
        :class="{ 'is-dragover': isDragOver }"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop.prevent="onDrop"
        @click="$refs.fileInput.click()"
      >
        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          multiple
          style="display: none"
          @change="onFilePicked"
        />
        <strong>Chọn ảnh</strong> hoặc kéo-thả vào đây để upload
        <p v-if="uploading" style="margin-top: 8px">
          Đang upload {{ uploadingCount }} ảnh...
        </p>
      </div>
      <p v-if="uploadError" class="modal-error">{{ uploadError }}</p>

      <!-- LƯỚI ẢNH -->
      <div class="photo-grid" style="margin-top: 24px">
        <p v-if="album.photos.length === 0" class="tree-status">
          Album chưa có ảnh nào.
        </p>

        <div class="photo-tile" v-for="photo in album.photos" :key="photo.id">
          <img
            :src="resolvePhotoUrl(photo.url)"
            :alt="photo.caption || album.title"
            class="photo-img"
          />
          <div class="photo-overlay">
            <span v-if="photo.caption" class="photo-caption">{{
              photo.caption
            }}</span>
            <button
              class="photo-delete-btn"
              @click="onDeletePhoto(photo.id)"
              title="Xoá ảnh"
            >
              ✕
            </button>
          </div>
        </div>
      </div>
    </template>
  </main>
</template>

<script>
import {
  getAlbumDetail as fetchAlbumDetail,
  deleteAlbum,
  uploadPhoto,
  deletePhoto,
  resolvePhotoUrl,
} from "../api/album";

export default {
  data() {
    return {
      album: null,
      loading: false,
      loadError: "",
      deletingAlbum: false,
      isDragOver: false,
      uploading: false,
      uploadingCount: 0,
      uploadError: "",
    };
  },

  mounted() {
    this.getAlbumDetail();
  },

  methods: {
    resolvePhotoUrl,

    async getAlbumDetail() {
      this.loading = true;
      this.loadError = "";
      try {
        const res = await fetchAlbumDetail(this.$route.params.id);
        this.album = res.data;
      } catch (error) {
        console.error("Load album detail error:", error);
        this.loadError = "Không thể tải album. Vui lòng thử lại.";
      } finally {
        this.loading = false;
      }
    },

    async onDeleteAlbum() {
      if (!confirm(`Xoá album "${this.album.title}" và toàn bộ ảnh bên trong?`))
        return;
      this.deletingAlbum = true;
      try {
        await deleteAlbum(this.$route.params.id);
        this.goBack();
      } catch (error) {
        console.error("Xoá album thất bại:", error);
        alert("Không thể xoá album. Vui lòng thử lại.");
        this.deletingAlbum = false;
      }
    },

    onFilePicked(e) {
      const files = Array.from(e.target.files || []);
      this.uploadFiles(files);
      e.target.value = ""; // cho phép chọn lại cùng 1 file lần sau
    },

    onDrop(e) {
      this.isDragOver = false;
      const files = Array.from(e.dataTransfer.files || []).filter((f) =>
        f.type.startsWith("image/"),
      );
      this.uploadFiles(files);
    },

    async uploadFiles(files) {
      if (files.length === 0) return;
      this.uploadError = "";
      this.uploading = true;
      this.uploadingCount = files.length;

      for (const file of files) {
        try {
          const res = await uploadPhoto(this.$route.params.id, file);
          this.album.photos.unshift(res.data);
          // Nếu album chưa có ảnh bìa, cập nhật local cho khớp với backend
          if (!this.album.coverPhotoUrl) {
            this.album.coverPhotoUrl = res.data.url;
          }
        } catch (error) {
          console.error("Upload ảnh thất bại:", error);
          this.uploadError = `Không thể upload "${file.name}". Vui lòng thử lại.`;
        }
      }

      this.uploading = false;
    },

    async onDeletePhoto(photoId) {
      if (!confirm("Xoá ảnh này?")) return;
      try {
        await deletePhoto(photoId);
        this.album.photos = this.album.photos.filter((p) => p.id !== photoId);
      } catch (error) {
        console.error("Xoá ảnh thất bại:", error);
        alert("Không thể xoá ảnh. Vui lòng thử lại.");
      }
    },

    goBack() {
      this.$router.push("/albums");
    },
  },
};
</script>

<style scoped>
.back-btn {
  margin-bottom: var(--space-3);
  padding-left: 0;
}

.upload-drop {
  cursor: pointer;
  margin-top: var(--space-3);
  transition:
    border-color 0.15s ease,
    background 0.15s ease;
}
.upload-drop.is-dragover {
  border-color: var(--gold);
  background: rgba(168, 130, 59, 0.06);
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-2);
}

.photo-tile {
  position: relative;
  aspect-ratio: 1/1;
  overflow: hidden;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  background: var(--paper-deep);
}
.photo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.photo-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: 8px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.55), transparent 50%);
  opacity: 0;
  transition: opacity 0.15s ease;
}
.photo-tile:hover .photo-overlay {
  opacity: 1;
}

.photo-caption {
  color: #fff;
  font-size: 0.78rem;
}

.photo-delete-btn {
  margin-left: auto;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 26px;
  height: 26px;
  cursor: pointer;
  font-size: 13px;
}
.photo-delete-btn:hover {
  background: var(--lacquer);
}

.delete-btn {
  padding: 0.75rem 1.4rem;
  background: transparent;
  border: 1px solid var(--lacquer);
  color: var(--lacquer);
  border-radius: var(--radius);
  font-weight: 600;
  cursor: pointer;
}
.delete-btn:hover {
  background: rgba(156, 43, 32, 0.08);
}
.delete-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.modal-error {
  margin-top: 8px;
  font-size: 13px;
  color: var(--lacquer);
}
</style>
