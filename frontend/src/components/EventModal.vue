<template>
    <teleport to="body">
      <transition name="fade">
        <div v-if="open" class="event-modal-backdrop" @mousedown.self="onBackdropClick">
          <transition name="pop">
            <div v-if="open" class="event-modal card framed" role="dialog" aria-modal="true">
              <span class="corner tl"></span>
              <span class="corner tr"></span>
              <span class="corner bl"></span>
              <span class="corner br"></span>
  
              <button class="modal-close" @click="close" aria-label="Đóng">✕</button>
  
              <p class="eyebrow">Sự kiện dòng họ</p>
              <h3>Thêm sự kiện</h3>
  
              <form @submit.prevent="submit">
                <div class="field">
                  <label>Tiêu đề</label>
                  <input v-model.trim="form.title" type="text" placeholder="VD: Giỗ Tổ" required>
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
                    <input v-model="form.datetime" type="datetime-local" required>
                  </div>
                </div>
  
                <div class="field" v-if="persons && persons.length">
                  <label>Liên quan tới thành viên</label>
                  <select v-model="form.personId">
                    <option value="">— Không chọn —</option>
                    <option v-for="p in persons" :key="p.id" :value="p.id">{{ p.name }}</option>
                  </select>
                </div>
  
                <div class="field">
                  <label>Địa điểm</label>
                  <input v-model.trim="form.location" type="text" placeholder="VD: Nhà thờ họ Hữu đại tôn" required>
                </div>
  
                <div class="field">
                  <label>Nội dung chi tiết</label>
                  <textarea v-model.trim="form.note" rows="3" placeholder="Chi tiết thêm về sự kiện..."></textarea>
                </div>
                <p v-if="error" class="modal-error">{{ error }}</p>
  
                <div class="modal-actions">
                  <button type="button" class="btn btn-ghost" @click="close" :disabled="submitting">Huỷ</button>
                  <button type="submit" class="btn btn-primary" :disabled="submitting">
                    {{ submitting ? 'Đang lưu...' : 'Lưu sự kiện' }}
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
  import { reactive, ref, watch } from 'vue'
//   import { addEvent } from '../api/eventApi'
  
  const props = defineProps({
    open: { type: Boolean, default: false },
    // Danh sách thành viên để chọn "liên quan tới ai": [{ id, name }]
    persons: { type: Array, default: () => [] },
  })
  
  const emit = defineEmits(['update:open', 'created'])
  
  const submitting = ref(false)
  const error = ref('')
  
  const form = reactive({
    title: '',
    type: 'gio',
    datetime: '',
    personId: '',
    location: '',
    note: '',
  })
  
  function resetForm() {
    form.title = ''
    form.type = 'gio'
    form.datetime = ''
    form.personId = ''
    form.location = ''
    form.note = ''
    error.value = ''
  }
  
  // Reset form mỗi khi modal được mở lại
  watch(() => props.open, (isOpen) => {
    if (isOpen) resetForm()
  })
  
  function close() {
    emit('update:open', false)
  }
  
  function onBackdropClick() {
    if (!submitting.value) close()
  }
  
  async function submit() {
    error.value = ''
    submitting.value = true
    // try {
    //   const payload = {
    //     title: form.title,
    //     type: form.type,
    //     date: form.date,
    //     personId: form.personId || null,
    //     location: form.location,
    //     note: form.note,
    //   }
    //   const res = await addEvent(payload)
    //   emit('created', res?.data ?? payload)
    //   submitting.value = false
    //   close()
    // } catch (err) {
    //   console.error('Lưu sự kiện thất bại:', err)
    //   error.value = err?.response?.data?.message || 'Không thể lưu sự kiện. Vui lòng thử lại.'
    //   submitting.value = false
    // }
  }
  </script>
  