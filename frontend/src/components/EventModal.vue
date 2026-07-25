<template>
    <teleport to="body">
      <transition name="fade">
        <div
          v-if="open"
          class="event-modal-backdrop"
          @mousedown.self="onBackdropClick"
        >
          <transition name="pop">
            <div
              v-if="open"
              class="event-modal card framed"
              role="dialog"
              aria-modal="true"
            >
              <span class="corner tl"></span>
              <span class="corner tr"></span>
              <span class="corner bl"></span>
              <span class="corner br"></span>
  
              <button class="modal-close" @click="close" aria-label="Đóng">
                ✕
              </button>
  
              <p class="eyebrow">Sự kiện dòng họ</p>
              <h3>{{ isEdit ? "Sửa sự kiện" : "Thêm sự kiện" }}</h3>
  
              <form @submit.prevent="submit">
                <div class="field">
                  <label>Tiêu đề</label>
                  <input
                    v-model.trim="form.title"
                    type="text"
                    placeholder="VD: Giỗ Tổ"
                    required
                  />
                </div>
  
                <div class="field-grid">
                  <div class="field">
                    <label>Loại sự kiện</label>
                    <select v-model="form.type">
                      <option value="gio">Giỗ</option>
                      <option value="ho">Họ</option>
                      <option value="hop-mat">Họp mặt</option>
                      <option value="khac">Khác</option>
                    </select>
                  </div>
                  <div class="field">
                    <label>Ngày diễn ra</label>
                    <div class="birthday-row">
                      <input
                        v-model="form.datetime"
                        type="datetime-local"
                        required
                      />
                  </div>
                  </div>
                </div>
  
                <div class="field">
                  <label>Địa điểm</label>
                  <input
                    v-model.trim="form.location"
                    type="text"
                    placeholder="VD: Nhà thờ họ Hữu đại tôn"
                    required
                  />
                </div>
  
                <div class="field">
                  <label>Nội dung chi tiết</label>
                  <textarea
                    v-model.trim="form.description"
                    rows="3"
                    placeholder="Chi tiết thêm về sự kiện..."
                  ></textarea>
                </div>
                <p v-if="error" class="modal-error">{{ error }}</p>
  
                <div class="modal-actions">
                  <button
                    type="button"
                    class="btn btn-ghost"
                    @click="close"
                    :disabled="submitting"
                  >
                    Huỷ
                  </button>
                  <button
                    type="submit"
                    class="btn btn-primary"
                    :disabled="submitting"
                  >
                    {{ submitting ? "Đang lưu..." : "Lưu sự kiện" }}
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
  import { reactive, ref, computed, watch } from "vue";
  import { addEvent, updateEvent } from "../api/event";
  
  const props = defineProps({
    open: { type: Boolean, default: false },
    // Danh sách thành viên để chọn "liên quan tới ai": [{ id, name }]
    persons: { type: Array, default: () => [] },
    // Truyền vào 1 event (từ to_dict() của backend) để mở modal ở chế độ SỬA.
    // Để null/không truyền -> modal ở chế độ THÊM MỚI.
    eventToEdit: { type: Object, default: null },
  });
  
  const emit = defineEmits(["update:open", "created", "updated"]);
  
  const isEdit = computed(() => !!props.eventToEdit);
  
  const submitting = ref(false);
  const error = ref("");
  
  const form = reactive({
    title: "",
    type: "gio",
    datetime: "",
    personId: "",
    location: "",
    description: "",
  });
  
  function resetForm() {
    form.title = "";
    form.type = "gio";
    form.datetime = "";
    form.personId = "";
    form.location = "";
    form.description = "";
    error.value = "";
  }
  
  function fillFormFromEvent(event) {
    form.title = event.title || "";
    form.type = event.type || "gio";
    // input datetime-local cần dạng "YYYY-MM-DDTHH:mm", cắt bớt giây/timezone
    form.datetime = event.datetime ? event.datetime.slice(0, 16) : "";
    form.personId = event.personId || "";
    form.location = event.location || "";
    form.description = event.description || "";
    error.value = "";
  }
  
  // Reset (hoặc điền sẵn nếu đang sửa) mỗi khi modal được mở lại
  watch(
    () => props.open,
    (isOpen) => {
      if (!isOpen) return;
      if (props.eventToEdit) {
        fillFormFromEvent(props.eventToEdit);
      } else {
        resetForm();
      }
    },
  );
  
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
      const payload = {
        title: form.title,
        type: form.type,
        datetime: form.datetime,
        personId: form.personId || null,
        location: form.location,
        description: form.description,
      };
  
      if (isEdit.value) {
        const res = await updateEvent(props.eventToEdit.id, payload);
        emit("updated", res?.data ?? payload);
      } else {
        const res = await addEvent(payload);
        emit("created", res?.data ?? payload);
      }
  
      submitting.value = false;
      close();
    } catch (err) {
      console.error("Lưu sự kiện thất bại:", err);
      error.value =
        err?.response?.data?.message ||
        "Không thể lưu sự kiện. Vui lòng thử lại.";
      submitting.value = false;
    }
  }
  </script>