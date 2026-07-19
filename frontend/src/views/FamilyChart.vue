<template>
  <div class="tree-shell">
    <div v-if="loading" class="tree-status">Đang tải dữ liệu gia phả...</div>
    <div v-else-if="loadError" class="tree-status tree-status-error">
      {{ loadError }}
      <button class="btn btn-outline" style="margin-left:12px;" @click="retryLoad">Thử lại</button>
    </div>

    <div
      v-show="!loading && !loadError"
      id="FamilyChart"
      ref="chartEl"
      class="f3"
      style="width:100%;height:900px;background-color:black;color:#fff;"
    ></div>


    <!-- ================= PANEL TRƯỢT TỪ BÊN PHẢI ================= -->
    <transition name="slide">
      <div v-if="panel.open" class="side-panel paper">
        <button class="panel-close" @click="closePanel" aria-label="Đóng">✕</button>

        <div class="seal-badge" style="margin-bottom:16px;">
          {{ panel.mode === 'edit' ? 'SỬA' : 'THÊM' }}
        </div>
        <p v-if="panelSubtitle" class="panel-subtitle">{{ panelSubtitle }}</p>

        <form @submit.prevent="submitPanel">
          <!-- Giới tính -->
          <div class="field-radio-group" style="margin-bottom:20px;">
            <label><input type="radio" value="M" v-model="form.gender"> Nam</label>
            <label><input type="radio" value="F" v-model="form.gender"> Nữ</label>
          </div>

          <div class="field full">
            <label>Họ và tên</label>
            <input v-model="form.fullName" type="text">
          </div>
          <div class="field full">
            <label>Ngày sinh</label>
            <input v-model="form.birthday" type="date">
          </div>
          <div class="field full">
            <label>Quê quán</label>
            <input v-model="form.hometown" type="text">
          </div>
          <div class="field full">
            <label> Nơi thường trú</label>
            <input v-model="form.currentAddress" type="text">
          </div>
          <div class="field full">
            <label>Học vấn</label>
            <input v-model="form.education" type="text">
          </div>

          <!-- Checkbox Đã mất -> hiện thêm ô ngày mất -->
          <div class="field full" style="margin-top:6px;">
            <label style="display:flex; align-items:center; gap:8px; font-weight:600;">
              <input type="checkbox" v-model="form.isDeceased">
              Đã mất
            </label>
          </div>
          <div class="field full" v-if="form.isDeceased">
            <label>Ngày mất</label>
            <input v-model="form.deathDate" type="date">
          </div>
          <div class="field full">
            <label>Ghi chú</label>
            <input v-model="form.note" type="text">
          </div>

          <div class="panel-actions">
            <button type="button" class="btn btn-outline" @click="closePanel" :disabled="panel.submitting">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="panel.submitting">
              {{ panel.submitting ? 'Đang lưu...' : 'Submit' }}
            </button>
          </div>

          <p v-if="panel.error" class="panel-error">{{ panel.error }}</p>
        </form>

        <!-- Chỉ hiện khi đang SỬA 1 người đã tồn tại -->
        <template v-if="panel.mode === 'edit'">
          <div class="relation-actions">
            <button class="btn btn-paper" @click="openAddModal('child')">+ Thêm con</button>
            <button class="btn btn-paper" @click="openAddModal('spouse')">+ Thêm vợ/chồng</button>
          </div>
          <button class="delete-btn" @click="deleteCurrentPerson" :disabled="panel.submitting">Xoá</button>
        </template>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref, computed, nextTick } from 'vue'
import * as f3 from 'family-chart'
import 'family-chart/styles/family-chart.css'
import { getFamilyTree, addPerson, updatePerson, deletePerson } from '../api/familyApi'

const chartEl = ref(null)
let f3Chart = null
let f3Card = null

/* ================== DỮ LIỆU (lấy từ backend) ================== */
const data = reactive([])
const loading = ref(false)
const loadError = ref('')

/**
 * Lấy danh sách toàn bộ person từ backend qua getFamilyTree().
 * Kỳ vọng response.data là mảng [{ id, data, rels }, ...].
 * Nếu backend bọc trong { items: [...] } hoặc { data: [...] }, chỉnh lại chỗ đọc response bên dưới.
 */
async function fetchFamilyData() {
  const res = await getFamilyTree()
  const payload = res.data
  return Array.isArray(payload) ? payload : (payload.items || payload.data || [])
}

async function loadFamilyData() {
  loading.value = true
  loadError.value = ''
  try {
    const items = await fetchFamilyData()
    data.splice(0, data.length, ...items)
  } catch (err) {
    console.error('Không tải được dữ liệu gia phả:', err)
    loadError.value = 'Không thể tải dữ liệu từ server. Vui lòng thử lại.'
  } finally {
    loading.value = false
  }
}

/* ================== KHỞI TẠO CHART ================== */
function initChart() {
  if (f3Chart) return // đã khởi tạo rồi thì thôi

  f3Chart = f3.createChart(chartEl.value, data)
    .setTransitionTime(1000)
    .setCardXSpacing(250)
    .setCardYSpacing(150)

  f3Card = f3Chart.setCardHtml()
    .setCardDisplay([['full_name'], ['birthday']])

  // Không dùng f3EditTree — mọi click mở panel tự custom
  f3Card.setOnCardClick((e, d) => openEditPanel(d.data))

  f3Chart.updateTree({ initial: true })
}

// Được gọi từ nút "Thử lại" trong template khi lần tải trước bị lỗi
async function retryLoad() {
  await loadFamilyData()
  if (!loadError.value && data.length > 0) {
    // chartEl chỉ tồn tại trong DOM khi loading=false && loadError='' (v-show ở trên vẫn giữ el trong DOM,
    // nhưng để chắc chắn ta chờ 1 tick trước khi tạo chart)
    await nextTick()
    initChart()
  }
}

onMounted(async () => {
  await loadFamilyData()

  // Nếu tải lỗi hoặc không có dữ liệu, không khởi tạo chart
  if (loadError.value || data.length === 0) return

  initChart()
})

function refreshChart() {
  f3Chart.updateData(data)
  f3Chart.updateTree({ tree_position: 'inherit' })
}

/* ================== STATE PANEL ================== */
const panel = reactive({
  open: false,
  mode: 'edit',
  targetId: null,
  relativeOfId: null,
  submitting: false,
  error: '',
})

const form = reactive({
  fullName: '',  gender: 'M',
  birthday: '', isDeceased: false, deathday: '',
  note: '', education: '', hometown: '', currentAddress: '',
})

function personName(id) {
  const person = data.find((p) => p.id === id)
  if (!person) return ''
  return `${person.data['full_name'] || ''}`.trim()
}

const panelSubtitle = computed(() => {
  if (panel.mode === 'edit') return `Đang sửa: ${personName(panel.targetId)}`
  if (panel.mode === 'add-child') return `Thêm con của: ${personName(panel.relativeOfId)}`
  if (panel.mode === 'add-spouse') return `Thêm vợ/chồng của: ${personName(panel.relativeOfId)}`
  return '' // mode 'create' — người gốc, không có quan hệ với ai
})

function resetForm() {
  form.fullName = ''
  form.gender = 'M'
  form.birthday = ''
  form.isDeceased = false
  form.deathday = ''
  form.note = ''
  form.education = ''
  form.hometown = ''
  form.currentAddress = ''
}

function fillForm(person) {
  const d = person.data
  form.fullName = d['full_name'] || ''
  form.gender = d.gender || 'M'
  form.birthday = d.birthday || ''
  form.isDeceased = d.deathday != ''
  form.deathDate = d.death_date || ''
  form.note = d.note || ''
  form.education = d.education || ''
  form.hometown = d.hometown || ''
  form.currentAddress = d.current_address || ''
}

function openEditPanel(person) {
  panel.mode = 'edit'
  panel.targetId = person.id
  panel.relativeOfId = null
  panel.error = ''
  fillForm(person)
  panel.open = true
}

function openCreatePanel() {
  panel.mode = 'create'
  panel.targetId = null
  panel.relativeOfId = null
  panel.error = ''
  resetForm()
  panel.open = true
}

function openAddModal(kind) {
  panel.mode = kind === 'child' ? 'add-child' : 'add-spouse'
  panel.relativeOfId = panel.targetId
  panel.error = ''
  resetForm()
  panel.open = true
}

function closePanel() {
  panel.open = false
}

// Trên thẻ chỉ hiện năm, không hiện ngày/tháng đầy đủ:
// - Còn sống: "1998 –"
// - Đã mất:   "1928 – 2005"
function yearOf(dateStr) {
  return dateStr ? dateStr.slice(0, 4) : ''
}

function buildYearsLabel(isDeceased, birthday, deathday) {
  const by = yearOf(birthday)
  if (isDeceased) return `${by} – ${yearOf(deathday)}`
  return by
}

function buildDataFromForm() {
  const deathday = form.isDeceased ? form.deathday : ''
  return {
    fullName: form.fullName,
    gender: form.gender,
    birthday: form.birthday,
    isDeceased: form.isDeceased,
    deathday,
    note: form.note,
    education: form.education,
    hometown: form.hometown,
    years: buildYearsLabel(form.isDeceased, form.birthday, deathday),
  }
}

function nextId() {
  const maxId = data.reduce((max, p) => Math.max(max, parseInt(p.id, 10) || 0), 0)
  return String(maxId + 1)
}

async function submitPanel() {
  panel.error = ''
  panel.submitting = true

  try {
    if (panel.mode === 'edit') {
      const person = data.find((p) => p.id === panel.targetId)
      if (!person) return

      // Cập nhật data local trước
      person.data = buildDataFromForm()

      // Gửi lên backend đúng shape { id, data, rels }
      await updatePerson(person.id, person)
    } else if (panel.mode === 'create') {
      const payload = { data: buildDataFromForm(), rels: {} }
      const res = await addPerson(payload)
      const created = res.data
      // Dùng id thật do server sinh (fallback nextId() nếu server không trả id)
      const newPerson = {
        id: created?.id ?? nextId(),
        data: created?.data ?? payload.data,
        rels: created?.rels ?? payload.rels,
      }
      data.push(newPerson)
    } else if (panel.mode === 'add-child') {
      const parent = data.find((p) => p.id === panel.relativeOfId)
      if (!parent) return

      const spouseId = parent.rels?.spouses?.[0]
      const parentIds = spouseId ? [panel.relativeOfId, spouseId] : [panel.relativeOfId]
      const payload = { data: buildDataFromForm(), rels: { parents: parentIds } }

      const res = await addPerson(payload)
      const created = res.data
      const newId = created?.id ?? nextId()
      const newPerson = {
        id: newId,
        data: created?.data ?? payload.data,
        rels: created?.rels ?? payload.rels,
      }
      data.push(newPerson)

      parent.rels.children = [...(parent.rels.children || []), newId]
      if (spouseId) {
        const spouse = data.find((p) => p.id === spouseId)
        if (spouse) spouse.rels.children = [...(spouse.rels.children || []), newId]
      }
    } else if (panel.mode === 'add-spouse') {
      const person = data.find((p) => p.id === panel.relativeOfId)
      if (!person) return

      const payload = { data: buildDataFromForm(), rels: { spouses: [panel.relativeOfId] } }
      const res = await addPerson(payload)
      const created = res.data
      const newId = created?.id ?? nextId()
      const newPerson = {
        id: newId,
        data: created?.data ?? payload.data,
        rels: created?.rels ?? payload.rels,
      }
      data.push(newPerson)

      person.rels.spouses = [...(person.rels.spouses || []), newId]
    }
  } catch (err) {
    console.error('Lưu thất bại:', err)
    panel.error = 'Không thể lưu thay đổi lên server. Vui lòng thử lại.'
    panel.submitting = false
    return // dừng lại, không đóng panel / không refresh chart nếu lỗi
  }

  panel.submitting = false
  refreshChart()
  closePanel()
}

async function deleteCurrentPerson() {
  const id = panel.targetId
  const idx = data.findIndex((p) => p.id === id)
  if (idx === -1) return
  if (!confirm('Xoá thành viên này khỏi gia phả?')) return

  panel.error = ''
  panel.submitting = true
  try {
    await deletePerson(id)
  } catch (err) {
    console.error('Xoá thất bại:', err)
    panel.error = 'Không thể xoá trên server. Vui lòng thử lại.'
    panel.submitting = false
    return
  }
  panel.submitting = false

  data.forEach((p) => {
    if (p.rels?.children) p.rels.children = p.rels.children.filter((c) => c !== id)
    if (p.rels?.spouses) p.rels.spouses = p.rels.spouses.filter((s) => s !== id)
    if (p.rels?.parents) p.rels.parents = p.rels.parents.filter((pr) => pr !== id)
  })
  data.splice(idx, 1)

  refreshChart()
  closePanel()
}
</script>

<style scoped>
.tree-shell {
  position: relative;
  width: 100%;
}

.tree-status {
  padding: 40px 20px;
  text-align: center;
  font-family: var(--font-body);
  color: var(--color-ink-soft);
}
.tree-status-error {
  color: var(--color-seal, #a5312b);
}

.add-member-btn {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 10;
  background: var(--color-seal);
  color: var(--color-cream);
  border: 1px solid var(--color-seal-dark);
  border-radius: 3px;
  padding: 10px 18px;
  font-family: var(--font-body);
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
}
.add-member-btn:hover { background: var(--color-seal-dark); }

/* ---------- Panel trượt từ phải ---------- */
.side-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 380px;
  max-width: 100%;
  height: 100%;
  overflow-y: auto;
  padding: 32px 28px;
  z-index: 20;
  box-sizing: border-box;
}
.slide-enter-active, .slide-leave-active {
  transition: transform 0.28s ease, opacity 0.28s ease;
}
.slide-enter-from, .slide-leave-to {
  transform: translateX(24px);
  opacity: 0;
}

.panel-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: transparent;
  border: none;
  font-size: 16px;
  color: var(--color-ink-soft);
  cursor: pointer;
}
.panel-close:hover { color: var(--color-seal); }

.panel-subtitle {
  font-size: 13px;
  color: var(--color-ink-soft);
  margin-bottom: 20px;
}

.panel-error {
  margin-top: 12px;
  font-size: 13px;
  color: var(--color-seal, #a5312b);
}

.panel-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--color-paper-line);
}
.panel-actions .btn-outline {
  color: var(--color-ink);
  border-color: var(--color-paper-line);
}
.panel-actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.relation-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-paper-line);
}
.relation-actions .btn { font-size: 13px; padding: 9px 14px; }

.delete-btn {
  width: 100%;
  margin-top: 16px;
  padding: 10px;
  background: transparent;
  border: 1px solid var(--color-seal);
  color: var(--color-seal);
  border-radius: 3px;
  font-weight: 600;
  cursor: pointer;
}
.delete-btn:hover { background: rgba(165, 49, 43, 0.08); }
</style>
