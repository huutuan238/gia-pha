<template>
    <main id="main" class="section container" style="max-width:960px;">
      <div class="tree-toolbar">
        <div>
          <span class="eyebrow">Quản lý</span>
          <h1 style="font-size:28px;">Thông tin dòng họ</h1>
        </div>
        <!-- <button class="btn btn-primary" @click="openCreatePanel">+ Thêm dòng họ</button> -->
      </div>
  
      <p v-if="errorMessage" class="alert-error">{{ errorMessage }}</p>
      <p v-if="loading" style="color:var(--color-cream-dim);">Đang tải dữ liệu…</p>
  
      <!-- Danh sách dòng họ -->
      <div class="family-grid" v-if="!loading && families.length">
        <div class="paper family-card" v-for="family in families" :key="family.id">
          <h3>{{ family.name }}</h3>
          <p class="family-meta" v-if="family.foundedYear">Lập họ năm {{ family.foundedYear }}</p>
          <p class="family-meta" v-if="family.branchNumber">{{ family.branchNumber }} chi nhánh</p>
          <p class="family-address" v-if="family.ancestralHouseAddress">{{ family.ancestralHouseAddress }}</p>
          <p class="family-desc" v-if="family.description">{{ family.description }}</p>
          <div class="family-actions">
            <button class="btn btn-outline" style="color:var(--color-ink); border-color:var(--color-paper-line);" @click="openEditPanel(family)">
              Sửa
            </button>
            <button class="btn btn-outline" style="color:var(--color-seal); border-color:var(--color-seal);" @click="askDelete(family)">
              Xoá
            </button>
          </div>
        </div>
      </div>
  
      <p v-else-if="!loading" style="color:var(--color-cream-dim);">
        Chưa có dòng họ nào. Bấm "+ Thêm dòng họ" để bắt đầu.
      </p>
    </main>
  
    <!-- ============ PANEL THÊM / SỬA ============ -->
    <Teleport to="body">
      <div v-if="panel.open" class="modal-overlay" @click.self="closePanel">
        <div class="paper modal-card">
          <button class="modal-close" @click="closePanel" aria-label="Đóng">✕</button>
          <div class="seal-badge" style="margin-bottom:16px;">
            {{ panel.mode === 'edit' ? 'SỬA' : 'THÊM' }}
          </div>
          <h2 style="font-size:20px; margin-bottom:20px;">
            {{ panel.mode === 'edit' ? 'Sửa thông tin dòng họ' : 'Thêm dòng họ mới' }}
          </h2>
  
          <p v-if="formError" class="alert-error">{{ formError }}</p>
  
          <form @submit.prevent="submitPanel">
            <div class="form-grid">
              <div class="field full">
                <label>Tên dòng họ *</label>
                <input v-model="form.name" type="text" placeholder="Họ Nguyễn">
              </div>
              <div class="field">
                <label>Năm thành lập / khởi tổ</label>
                <input v-model="form.foundedYear" type="number" placeholder="1780">
              </div>
              <div class="field">
                <label>Số chi nhánh</label>
                <input v-model="form.branchNumber" type="number" placeholder="4">
              </div>
              <div class="field full">
                <label>Địa chỉ nhà thờ họ</label>
                <input v-model="form.ancestralHouseAddress" type="text" placeholder="Làng Đông Bàn, Hải Dương">
              </div>
              <div class="field">
                <label>Vĩ độ <span class="hint">(tuỳ chọn, cho Google Map)</span></label>
                <input v-model="form.latitude" type="number" step="any" placeholder="20.9410">
              </div>
              <div class="field">
                <label>Kinh độ <span class="hint">(tuỳ chọn)</span></label>
                <input v-model="form.longitude" type="number" step="any" placeholder="106.3330">
              </div>
              <div class="field full">
                <label>Mô tả / lịch sử dòng họ</label>
                <textarea v-model="form.description" rows="4" placeholder="Vài dòng giới thiệu nguồn gốc, truyền thống…"></textarea>
              </div>
            </div>
  
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="closePanel">Hủy</button>
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                {{ submitting ? 'Đang lưu…' : 'Lưu' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  
    <!-- ============ XÁC NHẬN XOÁ ============ -->
    <Teleport to="body">
      <div v-if="deleteTarget" class="modal-overlay" @click.self="deleteTarget = null">
        <div class="paper modal-card" style="max-width:420px;">
          <h2 style="font-size:19px; margin-bottom:12px;">Xoá dòng họ này?</h2>
          <p style="font-size:14px; color:var(--color-ink-soft); margin-bottom:24px;">
            Bạn có chắc muốn xoá <strong>{{ deleteTarget.name }}</strong>? Thao tác này không thể hoàn tác.
          </p>
          <div class="form-actions" style="justify-content:flex-end;">
            <button type="button" class="btn btn-outline" @click="deleteTarget = null">Hủy</button>
            <button type="button" class="btn btn-primary" style="background:var(--color-seal);" @click="confirmDelete">
              Xác nhận xoá
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </template>
  
  <script setup>
  import { reactive, ref, onMounted } from 'vue'
//   import { openAuthModal } from '../stores/ui.js'
  import { getAllFamily, addFamily, updateFamily, deleteFamily } from '../api/family'
  
  const families = ref([])
  const loading = ref(false)
  const errorMessage = ref('')
  const submitting = ref(false)
  const formError = ref('')
  const deleteTarget = ref(null)
  
  const panel = reactive({ open: false, mode: 'create', editingId: null })
  const form = reactive({
    name: '',
    foundedYear: '',
    branchNumber: '',
    ancestralHouseAddress: '',
    latitude: '',
    longitude: '',
    description: '',
  })
  
  function resetForm() {
    form.name = ''
    form.foundedYear = ''
    form.branchNumber = ''
    form.ancestralHouseAddress = ''
    form.latitude = ''
    form.longitude = ''
    form.description = ''
  }
  
  /* ================== GỌI API ================== */
  async function fetchFamilies() {
    loading.value = true
    errorMessage.value = ''
    try {
      const { data } = await getAllFamily()
      families.value = data
    } catch (err) {
      errorMessage.value = `Lỗi kết nối tới backend: ${err.message}. Kiểm tra Flask đã chạy và CORS đã bật chưa.`
    } finally {
      loading.value = false
    }
  }
  
  onMounted(fetchFamilies)
  
  function buildPayload() {
    return {
      name: form.name,
      founded_year: form.foundedYear === '' ? null : Number(form.foundedYear),
      branch_number: form.branchNumber === '' ? null : Number(form.branchNumber),
      ancestral_house_address: form.ancestralHouseAddress,
      latitude: form.latitude === '' ? null : Number(form.latitude),
      longitude: form.longitude === '' ? null : Number(form.longitude),
      description: form.description,
    }
  }
  
  function openCreatePanel() {
    panel.mode = 'create'
    panel.editingId = null
    formError.value = ''
    resetForm()
    panel.open = true
  }
  
  function openEditPanel(family) {
    panel.mode = 'edit'
    panel.editingId = family.id
    formError.value = ''
    form.name = family.name || ''
    form.foundedYear = family.foundedYear ?? ''
    form.branchNumber = family.branchNumber ?? ''
    form.ancestralHouseAddress = family.ancestralHouseAddress || ''
    form.latitude = family.latitude ?? ''
    form.longitude = family.longitude ?? ''
    form.description = family.description || ''
    panel.open = true
  }
  
  function closePanel() {
    panel.open = false
  }
  
  async function submitPanel() {
    if (!form.name.trim()) {
      formError.value = 'Tên dòng họ là bắt buộc.'
      return
    }
  
    submitting.value = true
    formError.value = ''
    try {
      const isEdit = panel.mode === 'edit'
      if (isEdit) {
        await updateFamily(panel.editingId, buildPayload())
      } else {
        await addFamily(buildPayload())
      }
      await fetchFamilies()
      closePanel()
    } catch (err) {
      const body = err.response?.data
      formError.value = (body?.errors && body.errors.join(', ')) || body?.error || `Lỗi kết nối: ${err.message}`
    } finally {
      submitting.value = false
    }
  }
  
  function askDelete(family) {
    deleteTarget.value = family
  }
  
  async function confirmDelete() {
    const family = deleteTarget.value
    if (!family) return
    try {
      await deleteFamily(family.id)
      families.value = families.value.filter((f) => f.id !== family.id)
    } catch (err) {
      errorMessage.value = `Lỗi khi xoá: ${err.response?.data?.error || err.message}`
    } finally {
      deleteTarget.value = null
    }
  }
  </script>
  
  <style scoped>
  .family-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
  .family-card { padding: 24px; }
  .family-card h3 { font-size: 18px; margin-bottom: 8px; }
  .family-meta { font-size: 13px; color: var(--color-ink-soft); margin: 0 0 2px; }
  .family-address { font-size: 13px; color: var(--color-ink-soft); margin: 8px 0 0; }
  .family-desc { font-size: 13.5px; color: var(--color-ink); margin: 10px 0 0; }
  .family-actions {
    display: flex;
    gap: 10px;
    margin-top: 18px;
    padding-top: 16px;
    border-top: 1px solid var(--color-paper-line);
  }
  
  .alert-error {
    background: rgba(165, 49, 43, 0.12);
    color: var(--color-seal);
    border: 1px solid var(--color-seal);
    border-radius: 4px;
    padding: 10px 14px;
    font-size: 13.5px;
    margin-bottom: 20px;
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
    max-width: 600px;
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
  .modal-close:hover { color: var(--color-seal); }
  
  @media (max-width: 640px) {
    .family-grid { grid-template-columns: 1fr; }
  }
  </style>
  