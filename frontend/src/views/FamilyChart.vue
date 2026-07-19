<template>
  <div class="tree-shell">
    <div v-if="loading" class="tree-status">Đang tải dữ liệu gia phả...</div>
    <div v-else-if="loadError" class="tree-status tree-status-error">
      {{ loadError }}
      <button
        class="btn btn-outline"
        style="margin-left: 12px"
        @click="retryLoad"
      >
        Thử lại
      </button>
    </div>

    <div
      v-show="!loading && !loadError"
      id="FamilyChart"
      ref="chartEl"
      class="f3"
      style="width: 100%; height: 900px; background-color: #8fa08f; color: #fff"
    ></div>

    <button
      v-if="!loading && !loadError"
      class="btn btn-outline export-btn"
      @click="exportTreeToPdf"
      :disabled="exporting"
    >
      {{ exporting ? "Đang xuất..." : "In gia phả (PDF)" }}
    </button>

    <!-- ================= PANEL TRƯỢT TỪ BÊN PHẢI ================= -->
    <transition name="slide">
      <div v-if="panel.open" class="side-panel paper">
        <button class="panel-close" @click="closePanel" aria-label="Đóng">
          ✕
        </button>
        <template v-if="panel.mode === 'edit'">
          <div class="relation-actions">
            <button class="btn btn-paper" @click="openAddModal('child')">
              + Thêm con
            </button>
            <button class="btn btn-paper" @click="openAddModal('spouse')">
              + Thêm vợ/chồng
            </button>
          </div>
        </template>
        <div class="seal-badge" style="margin-bottom: 16px; margin-top: 16px">
          {{ panel.mode === "edit" ? "SỬA" : "THÊM" }}
        </div>
        <p v-if="panelSubtitle" class="panel-subtitle">{{ panelSubtitle }}</p>

        <form @submit.prevent="submitPanel">
          <!-- Giới tính -->
          <div class="field-radio-group" style="margin-bottom: 20px">
            <label
              ><input type="radio" value="M" v-model="form.gender" /> Nam</label
            >
            <label
              ><input type="radio" value="F" v-model="form.gender" /> Nữ</label
            >
          </div>

          <div class="field full">
            <label>Họ và tên</label>
            <input v-model="form.fullName" type="text" required />
          </div>
          <div class="field full">
            <label>Ngày sinh</label>
            <input v-model="form.birthday" type="date" required />
          </div>
          <div class="field full">
            <label>Quê quán</label>
            <input v-model="form.hometown" type="text" required />
          </div>
          <div class="field full">
            <label> Nơi thường trú</label>
            <input v-model="form.currentAddress" type="text" />
          </div>
          <div class="field full">
            <label>Học vấn</label>
            <input v-model="form.education" type="text" />
          </div>

          <!-- Checkbox Đã mất -> hiện thêm ô ngày mất -->
          <div class="field full" style="margin-top: 6px">
            <label
              style="
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 600;
              "
            >
              <input type="checkbox" v-model="form.isDeceased" />
              Đã mất
            </label>
          </div>
          <div class="field full" v-if="form.isDeceased">
            <label>Ngày mất</label>
            <input v-model="form.deathDate" type="date" />
          </div>
          <div class="field full">
            <label>Ghi chú</label>
            <input v-model="form.note" type="text" />
          </div>

          <div class="panel-actions">
            <button
              type="button"
              class="btn btn-outline"
              @click="closePanel"
              :disabled="panel.submitting"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="panel.submitting"
            >
              {{ panel.submitting ? "Đang lưu..." : "Submit" }}
            </button>
          </div>

          <p v-if="panel.error" class="panel-error">{{ panel.error }}</p>
        </form>

        <!-- Chỉ hiện khi đang SỬA 1 người đã tồn tại -->
        <template v-if="panel.mode === 'edit'">
          <button
            class="delete-btn"
            @click="deleteCurrentPerson"
            :disabled="panel.submitting"
          >
            Xoá
          </button>
        </template>
      </div>
    </transition>
  </div></template>

<style scoped>
.tree-shell {
  position: relative;
}
.export-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
}
</style>

<script setup>
import { onMounted, reactive, ref, computed, nextTick } from "vue";
import * as f3 from "family-chart";
import "family-chart/styles/family-chart.css";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import {
  getFamilyTree,
  addPerson,
  updatePerson,
  deletePerson,
} from "../api/familyApi";

const chartEl = ref(null);
let f3Chart = null;
let f3Card = null;

// id của người muốn focus làm main person khi mở cây (thuỷ tổ)
const MAIN_PERSON_ID = "1";

/* ================== DỮ LIỆU (lấy từ backend) ================== */
const data = reactive([]);
const loading = ref(false);
const loadError = ref("");
const exporting = ref(false);

/**
 * Lấy danh sách toàn bộ person từ backend qua getFamilyTree().
 * Kỳ vọng response.data là mảng [{ id, data, rels }, ...].
 * Nếu backend bọc trong { items: [...] } hoặc { data: [...] }, chỉnh lại chỗ đọc response bên dưới.
 */
async function fetchFamilyData() {
  const res = await getFamilyTree();
  const payload = res.data;
  return Array.isArray(payload) ? payload : payload.items || payload.data || [];
}

async function loadFamilyData() {
  loading.value = true;
  loadError.value = "";
  try {
    const items = await fetchFamilyData();
    items.forEach((p) => {
      if (p?.data) attachYears(p.data);
    });
    data.splice(0, data.length, ...items);
  } catch (err) {
    console.error("Không tải được dữ liệu gia phả:", err);
    loadError.value = "Không thể tải dữ liệu từ server. Vui lòng thử lại.";
  } finally {
    loading.value = false;
  }
}

/* ================== KHỞI TẠO CHART ================== */
function initChart() {
  if (f3Chart) return; // đã khởi tạo rồi thì thôi

  f3Chart = f3
    .createChart(chartEl.value, data)
    .setTransitionTime(1000)
    .setCardXSpacing(250)
    .setCardYSpacing(150)
    .setShowSiblingsOfMain(true); // hiện đầy đủ anh/chị/em ruột của main person

  f3Card = f3Chart.setCardHtml().setCardDisplay([["fullName"], ["years"]]);

  // Click vào card: vừa focus (đổi main person -> viền sáng + tự recalculate cây quanh người này),
  // vừa mở panel sửa custom của mình.
  f3Card.setOnCardClick((e, d) => {
    f3Chart.updateMainId(d.data.id);
    f3Chart.updateTree({ tree_position: "inherit" });
    openEditPanel(d.data);
  });

  // Focus main person vào MAIN_PERSON_ID nếu tồn tại trong data,
  // tránh để family-chart mặc định chọn data[0] (thường không phải thuỷ tổ,
  // khiến cây chỉ hiện 1 nhánh thay vì toàn bộ con cháu).
  if (data.some((p) => p.id === MAIN_PERSON_ID)) {
    f3Chart.updateMainId(MAIN_PERSON_ID);
  }

  f3Chart.updateTree({ initial: true });
}

// Xuất toàn bộ cây gia phả hiện tại ra file PDF
async function exportTreeToPdf() {
  if (!f3Chart || !chartEl.value) return;

  exporting.value = true;
  try {
    // Thu phóng để toàn bộ cây (mọi nhánh) vừa khít trong khung nhìn trước khi chụp,
    // tránh bị cắt mất phần đang nằm ngoài viewport do đang zoom/pan.
    f3Chart.updateTree({ tree_position: "fit" });
    await nextTick();
    // Đợi transition vẽ lại xong (transition_time đang set 1000ms trong initChart)
    await new Promise((resolve) => setTimeout(resolve, 350));

    const canvas = await html2canvas(chartEl.value, {
      backgroundColor: "#8fa08f", // khớp màu nền chart đang set trong template
      scale: 2, // chụp độ phân giải gấp đôi cho nét khi in
      useCORS: true,
    });

    const imgData = canvas.toDataURL("image/png");
    const pdf = new jsPDF({
      orientation: canvas.width > canvas.height ? "landscape" : "portrait",
      unit: "px",
      format: [canvas.width, canvas.height],
    });
    pdf.addImage(imgData, "PNG", 0, 0, canvas.width, canvas.height);
    pdf.save("gia-pha.pdf");
  } catch (err) {
    console.error("Xuất PDF thất bại:", err);
    alert("Không thể xuất PDF. Vui lòng thử lại.");
  } finally {
    exporting.value = false;
  }
}

// Được gọi từ nút "Thử lại" trong template khi lần tải trước bị lỗi
async function retryLoad() {
  await loadFamilyData();
  if (!loadError.value && data.length > 0) {
    // chartEl chỉ tồn tại trong DOM khi loading=false && loadError='' (v-show ở trên vẫn giữ el trong DOM,
    // nhưng để chắc chắn ta chờ 1 tick trước khi tạo chart)
    await nextTick();
    initChart();
  }
}

onMounted(async () => {
  await loadFamilyData();

  // Nếu tải lỗi hoặc không có dữ liệu, không khởi tạo chart
  if (loadError.value || data.length === 0) return;

  initChart();
});

function refreshChart() {
  f3Chart.updateData(data);
  f3Chart.updateTree({ tree_position: "inherit" });
}

/* ================== STATE PANEL ================== */
const panel = reactive({
  open: false,
  mode: "edit",
  targetId: null,
  relativeOfId: null,
  submitting: false,
  error: "",
});

const form = reactive({
  fullName: "",
  gender: "M",
  birthday: "",
  isDeceased: false,
  deathDate: "",
  note: "",
  education: "",
  hometown: "",
  currentAddress: "",
});

function personName(id) {
  const person = data.find((p) => p.id === id);
  if (!person) return "";
  return `${person.data["fullName"] || ""}`.trim();
}

function attachYears(personData) {
  personData.years = buildYearsLabel(
    personData.birthday,
    personData.death_date,
  );
  return personData;
}

const panelSubtitle = computed(() => {
  if (panel.mode === "edit") return `Đang sửa: ${personName(panel.targetId)}`;
  if (panel.mode === "add-child")
    return `Thêm con của: ${personName(panel.relativeOfId)}`;
  if (panel.mode === "add-spouse")
    return `Thêm vợ/chồng của: ${personName(panel.relativeOfId)}`;
  return ""; // mode 'create' — người gốc, không có quan hệ với ai
});

function resetForm() {
  form.fullName = "";
  form.gender = "M";
  form.birthday = "";
  form.isDeceased = false;
  form.deathDate = "";
  form.note = "";
  form.education = "";
  form.hometown = "";
  form.currentAddress = "";
}

function fillForm(person) {
  const d = person.data;
  form.fullName = d.fullName || "";
  form.gender = d.gender || "M";
  form.birthday = d.birthday || "";
  form.isDeceased = !!d.death_date;
  form.deathDate = d.death_date || "";
  form.note = d.note || "";
  form.education = d.education || "";
  form.hometown = d.hometown || "";
  form.currentAddress = d.current_address || "";
}

function openEditPanel(person) {
  panel.mode = "edit";
  panel.targetId = person.id;
  panel.relativeOfId = null;
  panel.error = "";
  fillForm(person);
  panel.open = true;
}

function openAddModal(kind) {
  panel.mode = kind === "child" ? "add-child" : "add-spouse";
  panel.relativeOfId = panel.targetId;
  panel.error = "";
  resetForm();
  panel.open = true;
}

function closePanel() {
  panel.open = false;
}

// Trên thẻ chỉ hiện năm, không hiện ngày/tháng đầy đủ:
// - Còn sống: "1998 –"
// - Đã mất:   "1928 – 2005"
function yearOf(dateStr) {
  return dateStr ? dateStr.slice(0, 4) : "";
}

function buildYearsLabel(birthday, deathday) {
  const by = yearOf(birthday);
  if (!!deathday) return `${by} – ${yearOf(deathday)}`;
  return by;
}

function buildDataFromForm() {
  const personData = {
    fullName: form.fullName,
    gender: form.gender,
    birthday: form.birthday,
    death_date: form.isDeceased ? form.deathDate : null,
    note: form.note,
    education: form.education,
    hometown: form.hometown,
    current_address: form.currentAddress,
  };
  attachYears(personData);
  return personData;
}
function generateId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback cho môi trường không có crypto.randomUUID (HTTP không secure context, trình duyệt cũ)
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

async function submitPanel() {
  panel.error = "";
  panel.submitting = true;

  try {
    if (panel.mode === "edit") {
      const person = data.find((p) => p.id === panel.targetId);
      if (!person) return;

      // Cập nhật data local trước
      person.data = buildDataFromForm();

      // Gửi lên backend đúng shape { id, data, rels }
      await updatePerson(person.id, person);
    } else if (panel.mode === "add-child") {
      const parent = data.find((p) => p.id === panel.relativeOfId);
      if (!parent) return;
      const newId = generateId();
      const spouseId = parent.rels?.spouses?.[0];
      const parentIds = spouseId
        ? [panel.relativeOfId, spouseId]
        : [panel.relativeOfId];
      const payload = {
        id: newId,
        data: buildDataFromForm(),
        rels: { parents: parentIds },
      };

      const res = await addPerson(payload);
      const newPerson = {
        id: newId,
        data: payload.data,
        rels: payload.rels,
      };
      data.push(newPerson);

      parent.rels.children = [...(parent.rels.children || []), newId];
      if (spouseId) {
        const spouse = data.find((p) => p.id === spouseId);
        if (spouse)
          spouse.rels.children = [...(spouse.rels.children || []), newId];
      }
    } else if (panel.mode === "add-spouse") {
      const person = data.find((p) => p.id === panel.relativeOfId);
      if (!person) return;
      const newId = generateId();

      const payload = {
        id: newId,
        data: buildDataFromForm(),
        rels: { spouses: [panel.relativeOfId] },
      };
      const res = await addPerson(payload);
      const created = res.data;
      const newPerson = {
        id: newId,
        data: created?.data ?? payload.data,
        rels: created?.rels ?? payload.rels,
      };
      data.push(newPerson);

      person.rels.spouses = [...(person.rels.spouses || []), newId];
    }
  } catch (err) {
    console.error("Lưu thất bại:", err);
    panel.error = "Không thể lưu thay đổi lên server. Vui lòng thử lại.";
    panel.submitting = false;
    return; // dừng lại, không đóng panel / không refresh chart nếu lỗi
  }

  panel.submitting = false;
  refreshChart();
  closePanel();
}

async function deleteCurrentPerson() {
  const id = panel.targetId;
  const idx = data.findIndex((p) => p.id === id);
  if (idx === -1) return;
  if (!confirm("Xoá thành viên này khỏi gia phả?")) return;

  panel.error = "";
  panel.submitting = true;
  try {
    await deletePerson(id);
  } catch (err) {
    console.error("Xoá thất bại:", err);
    panel.error = "Không thể xoá trên server. Vui lòng thử lại.";
    panel.submitting = false;
    return;
  }
  panel.submitting = false;

  data.forEach((p) => {
    if (p.rels?.children)
      p.rels.children = p.rels.children.filter((c) => c !== id);
    if (p.rels?.spouses)
      p.rels.spouses = p.rels.spouses.filter((s) => s !== id);
    if (p.rels?.parents)
      p.rels.parents = p.rels.parents.filter((pr) => pr !== id);
  });
  data.splice(idx, 1);

  refreshChart();
  closePanel();
}
</script>