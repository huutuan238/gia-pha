<template>
    <main class="section container" style="max-width:1000px;">
      <div class="tree-toolbar">
        <div>
          <span class="eyebrow">Khu vực quản trị</span>
          <h1 style="font-size:28px;">Bảng điều khiển Admin</h1>
        </div>
      </div>
  
      <!-- Chặn nếu không phải admin -->
      <div v-if="!isAdmin" class="alert-error" style="margin-top:20px;">
        Bạn không có quyền truy cập trang này. Chỉ tài khoản admin mới xem được.
      </div>
  
      <template v-else>
        <!-- Tabs -->
        <div class="dash-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            class="dash-tab"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
  
        <!-- ================= TAB: SỰ KIỆN ================= -->
        <section v-show="activeTab === 'events'">
          <div class="tree-toolbar" style="margin-top:24px;">
            <p style="color:var(--color-cream-dim); font-size:14px; margin:0;">Quản lý sự kiện dòng họ</p>
            <button class="btn btn-primary" @click="openCreateEvent">+ Tạo sự kiện</button>
          </div>
  
          <p v-if="eventsError" class="alert-error">{{ eventsError }}</p>
  
          <div class="paper" style="overflow-x:auto;">
            <table class="user-table">
              <thead>
                <tr>
                  <th>Tiêu đề</th>
                  <th>Loại</th>
                  <th>Thời gian</th>
                  <th>Địa điểm</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="event in events" :key="event.id">
                  <td>{{ event.title }}</td>
                  <td>{{ eventTypeLabel(event.type) }}</td>
                  <td>{{ formatDateTime(event.datetime) }}</td>
                  <td>{{ event.location }}</td>
                  <td style="text-align:right; white-space:nowrap;">
                    <button class="btn btn-outline" style="color:var(--color-ink); border-color:var(--color-paper-line); padding:6px 12px; font-size:13px; margin-right:8px;" @click="openEditEvent(event)">
                      Sửa
                    </button>
                    <button class="btn btn-outline" style="color:var(--color-seal); border-color:var(--color-seal); padding:6px 12px; font-size:13px;" @click="removeEvent(event)">
                      Xoá
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-if="!events.length" style="color:var(--color-ink-soft); padding:16px;">Chưa có sự kiện nào.</p>
          </div>
        </section>
  
        <!-- ================= TAB: DÒNG HỌ ================= -->
        <section v-show="activeTab === 'families'">
          <div class="tree-toolbar" style="margin-top:24px;">
            <p style="color:var(--color-cream-dim); font-size:14px; margin:0;">Quản lý thông tin dòng họ</p>
            <button class="btn btn-primary" @click="openFamilyPanel()">+ Thêm dòng họ</button>
          </div>
  
          <p v-if="familiesError" class="alert-error">{{ familiesError }}</p>
  
          <div class="family-grid">
            <div class="paper family-card" v-for="family in families" :key="family.id">
              <h3>{{ family.name }}</h3>
              <p class="family-meta" v-if="family.foundedYear">Lập họ năm {{ family.foundedYear }}</p>
              <p class="family-meta" v-if="family.branchNumber">{{ family.branchNumber }} chi nhánh</p>
              <div class="family-actions">
                <button class="btn btn-outline" style="color:var(--color-ink); border-color:var(--color-paper-line);" @click="openFamilyPanel(family)">Sửa</button>
                <button class="btn btn-outline" style="color:var(--color-seal); border-color:var(--color-seal);" @click="removeFamily(family)">Xoá</button>
              </div>
            </div>
            <p v-if="!families.length" style="color:var(--color-cream-dim);">Chưa có dòng họ nào.</p>
          </div>
        </section>
  
        <!-- ================= TAB: QUẢN TRỊ VIÊN ================= -->
        <section v-show="activeTab === 'users'">
          <div class="tree-toolbar" style="margin-top:24px;">
            <p style="color:var(--color-cream-dim); font-size:14px; margin:0;">
              Cấp / thu hồi quyền admin cho tài khoản
            </p>
          </div>
  
          <p v-if="usersError" class="alert-error">{{ usersError }}</p>
  
          <div class="paper" style="overflow-x:auto;">
            <table class="user-table">
              <thead>
                <tr>
                  <th>Tên đăng nhập</th>
                  <th>Email</th>
                  <th>Vai trò</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in users" :key="u.id">
                  <td>{{ u.username }}</td>
                  <td>{{ u.email }}</td>
                  <td>
                    <span class="role-badge" :class="{ 'is-admin': u.role === 'admin' }">
                      {{ u.role === 'admin' ? 'Admin' : 'Thành viên' }}
                    </span>
                  </td>
                  <td style="text-align:right;">
                    <button
                      v-if="u.role !== 'admin'"
                      class="btn btn-paper"
                      style="font-size:13px; padding:7px 14px;"
                      @click="grantAdmin(u)"
                    >
                      Cấp quyền admin
                    </button>
                    <button
                      v-else
                      class="btn btn-outline"
                      style="font-size:13px; padding:7px 14px; color:var(--color-ink);"
                      :disabled="u.id === currentUserId"
                      @click="revokeAdmin(u)"
                    >
                      Thu hồi quyền
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-if="!users.length" style="color:var(--color-ink-soft); padding:16px;">Chưa có user nào.</p>
          </div>
        </section>
      </template>
    </main>
  
    <!-- Modal thêm/sửa sự kiện — dùng component EventModal đã có sẵn -->
    <EventModal
      v-model:open="showEventModal"
      :persons="[]"
      :event-to-edit="editingEvent"
      @created="onEventCreated"
      @updated="onEventCreated"
    />
  
    <!-- ============ PANEL DÒNG HỌ ============ -->
    <Teleport to="body">
      <div v-if="familyPanel.open" class="modal-overlay" @click.self="closeFamilyPanel">
        <div class="paper modal-card">
          <button class="modal-close" @click="closeFamilyPanel">✕</button>
          <h2 style="font-size:20px; margin-bottom:20px;">
            {{ familyPanel.editingId ? 'Sửa dòng họ' : 'Thêm dòng họ mới' }}
          </h2>
          <p v-if="familyFormError" class="alert-error">{{ familyFormError }}</p>
  
          <form @submit.prevent="submitFamily">
            <div class="form-grid">
              <div class="field full">
                <label>Tên dòng họ *</label>
                <input v-model="familyForm.name" type="text">
              </div>
              <div class="field">
                <label>Năm thành lập</label>
                <input v-model="familyForm.foundedYear" type="number">
              </div>
              <div class="field">
                <label>Số chi nhánh</label>
                <input v-model="familyForm.branchNumber" type="number">
              </div>
              <div class="field full">
                <label>Địa chỉ nhà thờ họ</label>
                <input v-model="familyForm.ancestralHouseAddress" type="text">
              </div>
              <div class="field full">
                <label>Mô tả</label>
                <textarea v-model="familyForm.description" rows="3"></textarea>
              </div>
            </div>
            <div class="form-actions">
              <button type="button" class="btn btn-outline" @click="closeFamilyPanel">Hủy</button>
              <button type="submit" class="btn btn-primary" :disabled="familySubmitting">
                {{ familySubmitting ? 'Đang lưu…' : 'Lưu' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </template>
  
  <script setup>
  import { reactive, ref, computed, onMounted } from 'vue'
  import { authStore } from '../stores/auth.js'
  import { getAllEvent, deleteEvent } from '../api/event.js'
  import { getAllFamily, addFamily, updateFamily, deleteFamily } from '../api/family.js'
  import { getAllUser, updateUserRole } from '../api/user.js'
  import EventModal from '../components/EventModal.vue'
  
  const isAdmin = computed(() => authStore.state.user?.role === 'admin')
  const currentUserId = computed(() => authStore.state.user?.id)
  
  const tabs = [
    { key: 'events', label: 'Sự kiện' },
    { key: 'families', label: 'Dòng họ' },
    { key: 'users', label: 'Quản trị viên' },
  ]
  const activeTab = ref('events')
  
  /* ================== SỰ KIỆN ================== */
  const events = ref([])
  const eventsError = ref('')
  const showEventModal = ref(false)
  const editingEvent = ref(null) // null = chế độ tạo mới; có giá trị = chế độ sửa
  
  function openCreateEvent() {
    editingEvent.value = null
    showEventModal.value = true
  }
  
  function openEditEvent(event) {
    editingEvent.value = event
    showEventModal.value = true
  }
  
  async function fetchEvents() {
    eventsError.value = ''
    try {
      const { data } = await getAllEvent()
      events.value = data
    } catch (err) {
      eventsError.value = `Không tải được sự kiện: ${err.response?.data?.error || err.message}`
    }
  }
  
  const EVENT_TYPE_LABELS = {
    gio: 'Giỗ',
    ho: 'Họ',
    'hop-mat': 'Họp mặt',
    khac: 'Khác',
  }
  
  function eventTypeLabel(type) {
    return EVENT_TYPE_LABELS[type] || type || '—'
  }
  
  function formatDateTime(iso) {
    if (!iso) return '—'
    const d = new Date(iso)
    const pad = (n) => String(n).padStart(2, '0')
    return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
  }
  
  // EventModal tự lưu qua addEvent() rồi emit "created" — mình chỉ cần
  // tải lại danh sách từ server để đồng bộ (thay vì tự chèn tay vào mảng).
  function onEventCreated() {
    fetchEvents()
  }
  
  async function removeEvent(event) {
    if (!confirm(`Xoá sự kiện "${event.title}"?`)) return
    try {
      await deleteEvent(event.id)
      events.value = events.value.filter((e) => e.id !== event.id)
    } catch (err) {
      eventsError.value = `Xoá thất bại: ${err.response?.data?.error || err.message}`
    }
  }
  
  /* ================== DÒNG HỌ ================== */
  const families = ref([])
  const familiesError = ref('')
  const familyPanel = reactive({ open: false, editingId: null })
  const familyForm = reactive({
    name: '', foundedYear: '', branchNumber: '', ancestralHouseAddress: '', description: '',
  })
  const familyFormError = ref('')
  const familySubmitting = ref(false)
  
  async function fetchFamilies() {
    familiesError.value = ''
    try {
      const { data } = await getAllFamily()
      families.value = data
    } catch (err) {
      familiesError.value = `Không tải được dòng họ: ${err.response?.data?.error || err.message}`
    }
  }
  
  function resetFamilyForm() {
    familyForm.name = ''
    familyForm.foundedYear = ''
    familyForm.branchNumber = ''
    familyForm.ancestralHouseAddress = ''
    familyForm.description = ''
  }
  
  function openFamilyPanel(family = null) {
    familyFormError.value = ''
    if (family) {
      familyPanel.editingId = family.id
      familyForm.name = family.name || ''
      familyForm.foundedYear = family.foundedYear ?? ''
      familyForm.branchNumber = family.branchNumber ?? ''
      familyForm.ancestralHouseAddress = family.ancestralHouseAddress || ''
      familyForm.description = family.description || ''
    } else {
      familyPanel.editingId = null
      resetFamilyForm()
    }
    familyPanel.open = true
  }
  function closeFamilyPanel() {
    familyPanel.open = false
  }
  
  async function submitFamily() {
    if (!familyForm.name.trim()) {
      familyFormError.value = 'Tên dòng họ là bắt buộc.'
      return
    }
    familySubmitting.value = true
    familyFormError.value = ''
    const payload = {
      name: familyForm.name,
      founded_year: familyForm.foundedYear === '' ? null : Number(familyForm.foundedYear),
      branch_number: familyForm.branchNumber === '' ? null : Number(familyForm.branchNumber),
      ancestral_house_address: familyForm.ancestralHouseAddress,
      description: familyForm.description,
    }
    try {
      if (familyPanel.editingId) {
        await updateFamily(familyPanel.editingId, payload)
      } else {
        await addFamily(payload)
      }
      await fetchFamilies()
      closeFamilyPanel()
    } catch (err) {
      const body = err.response?.data
      familyFormError.value = (body?.errors && body.errors.join(', ')) || body?.error || 'Lưu thất bại.'
    } finally {
      familySubmitting.value = false
    }
  }
  
  async function removeFamily(family) {
    if (!confirm(`Xoá dòng họ "${family.name}"?`)) return
    try {
      await deleteFamily(family.id)
      families.value = families.value.filter((f) => f.id !== family.id)
    } catch (err) {
      familiesError.value = `Xoá thất bại: ${err.response?.data?.error || err.message}`
    }
  }
  
  /* ================== QUẢN TRỊ VIÊN ================== */
  const users = ref([])
  const usersError = ref('')
  
  async function fetchUsers() {
    usersError.value = ''
    try {
      const { data } = await getAllUser()
      users.value = data
    } catch (err) {
      usersError.value = `Không tải được danh sách user: ${err.response?.data?.error || err.message}`
    }
  }
  
  async function grantAdmin(user) {
    if (!confirm(`Cấp quyền admin cho "${user.username}"?`)) return
    try {
      const { data } = await updateUserRole(user.id, 'admin')
      const idx = users.value.findIndex((u) => u.id === user.id)
      if (idx !== -1) users.value[idx] = data
    } catch (err) {
      usersError.value = `Cấp quyền thất bại: ${err.response?.data?.error || err.message}`
    }
  }
  
  async function revokeAdmin(user) {
    if (!confirm(`Thu hồi quyền admin của "${user.username}"?`)) return
    try {
      const { data } = await updateUserRole(user.id, 'member')
      const idx = users.value.findIndex((u) => u.id === user.id)
      if (idx !== -1) users.value[idx] = data
    } catch (err) {
      usersError.value = `Thu hồi thất bại: ${err.response?.data?.error || err.message}`
    }
  }
  
  onMounted(() => {
    if (!isAdmin.value) return
    fetchEvents()
    fetchFamilies()
    fetchUsers()
  })
  </script>
  
  <style scoped>
  .dash-tabs {
    display: flex;
    gap: 8px;
    border-bottom: 1px solid var(--color-gold-soft);
    margin-top: 24px;
  }
  .dash-tab {
    background: transparent;
    border: none;
    padding: 12px 18px;
    font-family: var(--font-body);
    font-size: 14px;
    font-weight: 600;
    color: var(--color-cream-dim);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
  }
  .dash-tab:hover { color: var(--color-cream); }
  .dash-tab.active {
    color: var(--color-gold);
    border-bottom-color: var(--color-gold);
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
  
  .family-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-top: 16px;
  }
  .family-card { padding: 20px; }
  .family-card h3 { font-size: 16px; margin-bottom: 6px; }
  .family-meta { font-size: 13px; color: var(--color-ink-soft); margin: 0 0 2px; }
  .family-actions {
    display: flex;
    gap: 10px;
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid var(--color-paper-line);
  }
  
  .user-table {
    width: 100%;
    border-collapse: collapse;
    color: var(--color-ink);
  }
  .user-table th {
    text-align: left;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--color-ink-soft);
    padding: 14px 18px;
    border-bottom: 1px solid var(--color-paper-line);
  }
  .user-table td {
    padding: 14px 18px;
    font-size: 14px;
    border-bottom: 1px solid var(--color-paper-line);
  }
  
  .role-badge {
    display: inline-block;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(86, 73, 47, 0.12);
    color: var(--color-ink-soft);
  }
  .role-badge.is-admin {
    background: rgba(165, 49, 43, 0.12);
    color: var(--color-seal);
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