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

        <div
          class="photo-tile"
          v-for="photo in album.photos"
          :key="photo.id"
          @click="closeMenuIfOutside($event, photo.id)"
        >
          <div class="photo-thumb">
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
  </main>
</template>

<script>
import {
  getAlbumDetail as fetchAlbumDetail,
  deleteAlbum,
  uploadPhoto,
  deletePhoto,
  resolvePhotoUrl,
  renamePhoto, // TODO: thêm hàm này trong ../api/album (xem gợi ý cuối file chat)
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
    };
  },

  mounted() {
    this.getAlbumDetail();
    document.addEventListener("click", this.onGlobalClick);
  },

  beforeUnmount() {
    document.removeEventListener("click", this.onGlobalClick);
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

    closeMenuIfOutside() {
      // giữ chỗ nếu sau này cần logic riêng theo từng tile
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
    async onDownloadPhoto(photo) {
      this.openMenuId = null;
      const url = resolvePhotoUrl(photo.url);
      const filename = photo.caption || `photo-${photo.id}`;

      try {
        const res = await fetch(url);
        const blob = await res.blob();
        const blobUrl = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = blobUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(blobUrl);
      } catch (error) {
        console.error("Tải ảnh thất bại, mở tab mới:", error);
        window.open(url, "_blank");
      }
    },

    goBack() {
      this.$router.push("/albums");
    },
  },
};
</script>