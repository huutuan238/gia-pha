<template>
  <teleport to="body">
    <transition name="fade">
      <div v-if="open" class="album-modal-backdrop" @mousedown.self="onBackdropClick">
        <transition name="pop">
          <div v-if="open" class="album-modal card framed" role="dialog" aria-modal="true">
            <span class="corner tl"></span>
            <span class="corner tr"></span>
            <span class="corner bl"></span>
            <span class="corner br"></span>

            <button class="modal-close" @click="close" aria-label="Đóng">✕</button>

            <p class="eyebrow">Album ảnh</p>
            <h3>Tạo album mới</h3>

            <form @submit.prevent="submit">
              <div class="field">
                <label>Tên album</label>
                <input v-model.trim="form.title" type="text" placeholder="VD: Giỗ tổ 2026" required>
              </div>

              <div class="field">
                <label>Mô tả</label>
                <textarea v-model.trim="form.description" rows="3" placeholder="Mô tả ngắn về album..."></textarea>
              </div>

              <p v-if="error" class="modal-error">{{ error }}</p>

              <div class="modal-actions">
                <button type="button" class="btn btn-ghost" @click="close" :disabled="submitting">Huỷ</button>
                <button type="submit" class="btn btn-primary" :disabled="submitting">
                  {{ submitting ? "Đang tạo..." : "Tạo album" }}
                </button>
              </div>
            </form>
          </div>
        </transition>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { reactive, ref, watch } from "vue";
import { createAlbum } from "../api/album";

const props = defineProps({
  open: { type: Boolean, default: false },
});

const emit = defineEmits(["update:open", "created"]);

const submitting = ref(false);
const error = ref("");

const form = reactive({
  title: "",

  description: "",
});

function resetForm() {
  form.title = "";
  form.description = "";
  error.value = "";
}

watch(() => props.open, (isOpen) => {
  if (isOpen) resetForm();
});

function close() {
  emit("update:open", false);
}

function onBackdropClick() {
  if (!submitting.value) close();
}

async function submit() {
  error.value = "";
  submitting.value = true;
  try {
    const res = await createAlbum({
      title: form.title,
      description: form.description,
    });
    emit("created", res.data);
    submitting.value = false;
    close();
  } catch (err) {
    console.error("Tạo album thất bại:", err);
    error.value = err?.response?.data?.message || "Không thể tạo album. Vui lòng thử lại.";
    submitting.value = false;
  }
}
</script>
