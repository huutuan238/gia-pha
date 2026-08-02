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

      <!-- LƯỚI ẢNH KIỂU GOOGLE DRIVE -->
      <div class="photo-grid" style="margin-top: 24px">
        <p v-if="album.photos.length === 0" class="tree-status">
          Album chưa có ảnh nào.
        </p>

        <div
          class="photo-tile"
          v-for="(photo, index) in album.photos"
          :key="photo.id"
        >
          <div class="photo-thumb" @click="openViewer(index)">
            <img
              :src="resolvePhotoUrl(photo.url)"
              :alt="photo.caption || album.title"
              class="photo-img"
            />
          </div>

          <div class="photo-meta">
            <template v-if="renamingId === photo.id">
              <input
                ref="renameInput"
                v-model="renameValue"
                class="rename-input"
                @keyup.enter="confirmRename(photo)"
                @keyup.esc="cancelRename"
                @blur="confirmRename(photo)"
                @click.stop
              />
            </template>
            <span
              v-else
              class="photo-name"
              :title="photo.caption || 'Ảnh chưa có tên'"
            >
              {{ photo.caption || "Ảnh chưa có tên" }}
            </span>

            <div class="photo-menu-wrap">
              <button
                class="photo-menu-btn"
                @click.stop="toggleMenu(photo.id)"
                title="Tuỳ chọn"
              >
                ⋮
              </button>

              <div v-if="openMenuId === photo.id" class="photo-menu" @click.stop>
                <button class="photo-menu-item" @click="startRename(photo)">
                  ✎ Đổi tên
                </button>
                <button class="photo-menu-item" @click="onDownloadPhoto(photo)">
                  ⬇ Tải xuống
                </button>
                <button
                  class="photo-menu-item photo-menu-item-danger"
                  @click="onDeletePhoto(photo.id)"
                >
                  ✕ Xoá
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- MODAL XEM CHI TIẾT ẢNH -->
    <transition name="fade">
      <div
        v-if="viewerPhoto"
        class="photo-viewer-backdrop"
        @click.self="closeViewer"
        @keydown.esc="closeViewer"
      >
        <button class="photo-viewer-close" @click="closeViewer" title="Đóng">
          ✕
        </button>

        <button
          v-if="album.photos.length > 1"
          class="photo-viewer-nav photo-viewer-nav-prev"
          @click.stop="prevPhoto"
          title="Ảnh trước"
        >
          ‹
        </button>

        <div class="photo-viewer" @click.stop>
          <img
            :src="resolvePhotoUrl(viewerPhoto.url)"
            :alt="viewerPhoto.caption || album.title"
            class="photo-viewer-image"
          />
          <div class="photo-viewer-footer">
            <span class="photo-viewer-caption">
              {{ viewerPhoto.caption || "Ảnh chưa có tên" }}
            </span>
            <div class="photo-viewer-actions">
              <span class="photo-viewer-index">
                {{ viewerIndex + 1 }} / {{ album.photos.length }}
              </span>
              <button
                class="photo-viewer-action-btn"
                @click="onDownloadPhoto(viewerPhoto)"
                title="Tải xuống"
              >
                ⬇
              </button>
              <button
                class="photo-viewer-action-btn photo-viewer-action-btn-danger"
                @click="onDeletePhotoFromViewer(viewerPhoto.id)"
                title="Xoá ảnh"
              >
                ✕
              </button>
            </div>
          </div>
        </div>

        <button
          v-if="album.photos.length > 1"
          class="photo-viewer-nav photo-viewer-nav-next"
          @click.stop="nextPhoto"
          title="Ảnh sau"
        >
          ›
        </button>
      </div>
    </transition>
  </main>
</template>

<script>
import {
  getAlbumDetail as fetchAlbumDetail,
  deleteAlbum,
  uploadPhoto,
  deletePhoto,
  resolvePhotoUrl,
  renamePhoto, 
  getPhotoDownloadUrl,
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

      openMenuId: null,
      renamingId: null,
      renameValue: "",

      viewerIndex: -1,
    };
  },

  computed: {
    viewerPhoto() {
      if (!this.album || this.viewerIndex < 0) return null;
      return this.album.photos[this.viewerIndex] || null;
    },
  },

  mounted() {
    this.getAlbumDetail();
    document.addEventListener("click", this.onGlobalClick);
    document.addEventListener("keydown", this.onViewerKeydown);
  },

  beforeUnmount() {
    document.removeEventListener("click", this.onGlobalClick);
    document.removeEventListener("keydown", this.onViewerKeydown);
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
      this.openMenuId = null;
      if (!confirm("Xoá ảnh này?")) return;
      try {
        await deletePhoto(photoId);
        this.album.photos = this.album.photos.filter((p) => p.id !== photoId);
      } catch (error) {
        console.error("Xoá ảnh thất bại:", error);
        alert("Không thể xoá ảnh. Vui lòng thử lại.");
      }
    },

    // ----- MENU BA CHẤM -----
    toggleMenu(photoId) {
      this.openMenuId = this.openMenuId === photoId ? null : photoId;
    },

    onGlobalClick(e) {
      // Đóng menu nếu click ra ngoài khu vực menu/nút ba chấm
      if (!e.target.closest(".photo-menu-wrap")) {
        this.openMenuId = null;
      }
    },

    // ----- ĐỔI TÊN -----
    startRename(photo) {
      this.openMenuId = null;
      this.renamingId = photo.id;
      this.renameValue = photo.caption || "";
      this.$nextTick(() => {
        const input = this.$refs.renameInput;
        const el = Array.isArray(input) ? input[0] : input;
        el && el.focus();
      });
    },

    cancelRename() {
      this.renamingId = null;
      this.renameValue = "";
    },

    async confirmRename(photo) {
      if (this.renamingId !== photo.id) return;
      const newName = this.renameValue.trim();
      this.renamingId = null;

      if (!newName || newName === photo.caption) return;

      try {
        const res = await renamePhoto(photo.id, newName);
        photo.caption = res?.data?.caption ?? newName;
      } catch (error) {
        console.error("Đổi tên ảnh thất bại:", error);
        alert("Không thể đổi tên ảnh. Vui lòng thử lại.");
      }
    },

    // ----- TẢI XUỐNG -----
    // Ảnh lưu trên S3: xin backend một presigned URL có sẵn header
    // "Content-Disposition: attachment; filename=..." rồi điều hướng tới đó.
    // Cách này KHÔNG cần fetch/blob nên không bị chặn bởi CORS của bucket S3.
    async onDownloadPhoto(photo) {
      try {
        const res = await getPhotoDownloadUrl(photo.id)
        const downloadUrl = res.data.downloadUrl
        window.location.href = downloadUrl // hoặc window.open(downloadUrl, '_blank')
      } catch (err) {
        console.error('Tải ảnh thất bại:', err)
      }
    },

    // ----- XEM CHI TIẾT ẢNH -----
    openViewer(index) {
      this.viewerIndex = index;
    },

    closeViewer() {
      this.viewerIndex = -1;
    },

    prevPhoto() {
      if (!this.album || this.album.photos.length === 0) return;
      const total = this.album.photos.length;
      this.viewerIndex = (this.viewerIndex - 1 + total) % total;
    },

    nextPhoto() {
      if (!this.album || this.album.photos.length === 0) return;
      const total = this.album.photos.length;
      this.viewerIndex = (this.viewerIndex + 1) % total;
    },

    onViewerKeydown(e) {
      if (this.viewerIndex < 0) return;
      if (e.key === "Escape") this.closeViewer();
      else if (e.key === "ArrowLeft") this.prevPhoto();
      else if (e.key === "ArrowRight") this.nextPhoto();
    },

    async onDeletePhotoFromViewer(photoId) {
      if (!confirm("Xoá ảnh này?")) return;
      try {
        await deletePhoto(photoId);
        this.album.photos = this.album.photos.filter((p) => p.id !== photoId);
        if (this.album.photos.length === 0) {
          this.closeViewer();
        } else {
          this.viewerIndex = Math.min(this.viewerIndex, this.album.photos.length - 1);
        }
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
/* ---------- Modal xem chi tiết ảnh ---------- */
.photo-viewer-backdrop {
  position: fixed;
  inset: 0;
  z-index: 200;
  background: rgba(20, 16, 12, 0.86);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}

.photo-viewer {
  position: relative;
  max-width: min(880px, 92vw);
  max-height: 88vh;
  background: var(--paper-card);
  border-radius: var(--radius);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.photo-viewer-image {
  display: block;
  max-width: 100%;
  max-height: 72vh;
  width: auto;
  height: auto;
  object-fit: contain;
  background: #000;
  margin: 0 auto;
}

.photo-viewer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  border-top: 1px solid var(--line);
}

.photo-viewer-caption {
  font-size: 0.92rem;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.photo-viewer-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.photo-viewer-index {
  font-family: var(--font-mono);
  font-size: 0.72rem;
  color: var(--ink-soft);
  white-space: nowrap;
}

.photo-viewer-action-btn {
  background: transparent;
  border: 1px solid var(--line-strong);
  border-radius: var(--radius);
  color: var(--ink);
  padding: 0.35rem 0.6rem;
  cursor: pointer;
  font-size: 0.85rem;
}
.photo-viewer-action-btn:hover {
  border-color: var(--ink);
}
.photo-viewer-action-btn-danger {
  border-color: var(--lacquer);
  color: var(--lacquer);
}
.photo-viewer-action-btn-danger:hover {
  background: rgba(156, 43, 32, 0.08);
}

.photo-viewer-close {
  position: absolute;
  top: 20px;
  right: 24px;
  background: rgba(0, 0, 0, 0.35);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 16px;
  cursor: pointer;
  z-index: 210;
}
.photo-viewer-close:hover {
  background: rgba(0, 0, 0, 0.55);
}

.photo-viewer-nav {
  background: rgba(0, 0, 0, 0.35);
  color: #fff;
  border: none;
  border-radius: 50%;
  width: 44px;
  height: 44px;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  flex-shrink: 0;
  z-index: 210;
}
.photo-viewer-nav:hover {
  background: rgba(0, 0, 0, 0.55);
}
.photo-viewer-nav-prev {
  margin-right: 16px;
}
.photo-viewer-nav-next {
  margin-left: 16px;
}

@media (max-width: 700px) {
  .photo-viewer-backdrop {
    padding: 12px;
  }
  .photo-viewer-nav {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
  }
  .photo-viewer-nav-prev {
    left: 12px;
    margin-right: 0;
  }
  .photo-viewer-nav-next {
    right: 12px;
    margin-left: 0;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>