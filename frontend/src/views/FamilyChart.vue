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

    <!-- ================= SEARCH BOX =================
         Chỉ hiện khi KHÔNG ở chế độ isSearch — vì lúc đó trang cha
         (ví dụ trang tra cứu) sẽ tự vẽ ô tìm kiếm riêng và gọi
         focusPerson()/getSearchOptions() được expose bên dưới. -->
    <div
      v-if="!isSearch && !loading && !loadError"
      class="search-box"
      @focusout="handleSearchFocusOut"
    >
      <div class="search-row">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Tìm kiếm..."
          class="search-input"
          autocomplete="off"
          @focus="searchDropdownOpen = true"
          @input="searchDropdownOpen = true"
        />
        <button
          type="button"
          class="btn btn-outline reset-btn"
          title="Về thuỷ tổ"
          @click="resetToRoot"
        >
          ⟲
        </button>
      </div>
      <div
        v-if="searchDropdownOpen && filteredSearchOptions.length"
        class="search-dropdown"
      >
        <div
          v-for="opt in filteredSearchOptions"
          :key="opt.value"
          class="search-option"
          @mousedown.prevent="selectSearchPerson(opt.value)"
        >
          {{ opt.label }}
        </div>
      </div>
    </div>

    <button
      v-if="!loading && !loadError"
      class="btn btn-outline export-btn"
      @click="exportTreeToPdf"
      :disabled="exporting"
    >
      {{ exporting ? "Đang xuất..." : "In gia phả (PDF)" }}
    </button>

    <!-- ================= PANEL TRƯỢT TỪ BÊN PHẢI =================
         Không bao giờ mở khi isSearch = true (xem guard trong
         setOnCardClick bên dưới), nên có thể giữ nguyên khối này. -->
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
          <div class="field full">
            <label>Họ và tên</label>
            <input v-model="form.fullName" type="text" required />
          </div>
          <div class="field-radio-group" style="margin-bottom: 20px">
            <label style="display: flex">Giới tính</label>
            <select class="select-field" v-model="form.gender">
              <option value="M">Nam</option>
              <option value="F">Nữ</option>
            </select>
          </div>
          <div class="field full">
            <label>Ngày sinh</label>
            <div class="birthday-row">
              <input
                v-model.number="form.birthDay"
                type="number"
                min="1"
                max="31"
                placeholder="Ngày"
                class="date-part-input date-part-input-day"
              />
              <input
                v-model.number="form.birthMonth"
                type="number"
                min="1"
                max="12"
                placeholder="Tháng"
                class="date-part-input"
              />
              <input
                v-model.number="form.birthYear"
                type="number"
                placeholder="Năm"
                class="date-part-input date-part-input-year"
              />
              <label class="lunar-checkbox">
                <input type="checkbox" v-model="form.birthIsLunar" />
                Âm lịch
              </label>
            </div>
          </div>

          <!-- Con thứ mấy -->
          <div class="field full">
            <label>Con thứ</label>
            <select class="select-field" v-model="form.siblingIndex">
              <option v-for="n in 15" :key="n" :value="n">
                Con thứ {{ n }}
              </option>
            </select>
          </div>

          <div class="field full">
            <label>Quê quán</label>
            <input v-model="form.hometown" type="text" />
          </div>
          <div class="field full">
            <label> Nơi thường trú</label>
            <input v-model="form.currentAddress" type="text" />
          </div>
          <div class="field full">
            <label>Học vấn, trình độ(nghề nghiệp)</label>
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
            <label>Ngày mất / Ngày giỗ</label>
            <div class="birthday-row">
              <input
                v-model.number="form.deathDay"
                type="number"
                min="1"
                max="31"
                placeholder="Ngày"
                class="date-part-input date-part-input-day"
              />
              <input
                v-model.number="form.deathMonth"
                type="number"
                min="1"
                max="12"
                placeholder="Tháng"
                class="date-part-input"
              />
              <input
                v-model.number="form.deathYear"
                type="number"
                placeholder="Năm"
                class="date-part-input date-part-input-year"
              />
              <label class="lunar-checkbox" v-show="false">
                <input type="checkbox" v-model="form.deathIsLunar" />
                Âm lịch
              </label>
            </div>
          </div>
          <div class="field full">
            <label>Ghi chú</label>
            <textarea v-model="form.notes" type="text" />
          </div>

          <div class="panel-actions">
            <button
              type="button"
              class="btn btn-outline"
              @click="closePanel"
              :disabled="panel.submitting"
            >
              Huỷ
            </button>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="panel.submitting"
            >
              {{ panel.submitting ? "Đang lưu..." : "Xác nhận" }}
            </button>
          </div>

          <p v-if="panel.error" class="panel-error">{{ panel.error }}</p>
        </form>

        <!-- Chỉ hiện khi đang SỬA 1 người đã tồn tại -->
        <template
          v-if="
            panel.mode === 'edit' && (isAdmin || panel.createUserId == userId)
          "
        >
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
  </div>
</template>

<style scoped>
.date-part-input {
  width: 85px !important;
  flex: 0 0 auto;
}
.date-part-input-day {
  width: 65px !important;
}
.date-part-input-year {
  width: 80px !important;
}
</style>

<script setup>
import { onMounted, reactive, ref, computed, nextTick } from "vue";
import * as f3 from "family-chart";
import "family-chart/styles/family-chart.css";
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import { authStore } from "../stores/auth.js";
import {
  getFamilyTree,
  addPerson,
  updatePerson,
  deletePerson,
  updateRelationships,
} from "../api/familyApi";

// isSearch = true  -> chế độ chỉ xem/tra cứu: tắt panel sửa/thêm/xoá và
//                      tắt luôn search box nội bộ (trang cha tự vẽ search
//                      riêng, gọi vào focusPerson()/getSearchOptions()).
// isSearch = false -> hành vi mặc định như cũ (có thể sửa/thêm/xoá).
const props = defineProps({
  isSearch: { type: Boolean, default: false },
});

const emit = defineEmits(["person-click"]);

const chartEl = ref(null);
let f3Chart = null;
let f3Card = null;

// id của người muốn focus làm main person khi mở cây (thuỷ tổ)
const MAIN_PERSON_ID = "538d86e8-67f3-4a4c-8da2-46d94a41dd22";

/* ================== DỮ LIỆU (lấy từ backend) ================== */
const data = reactive([]);
const loading = ref(false);
const loadError = ref("");
const exporting = ref(false);

/* ================== SEARCH STATE (chỉ dùng khi !isSearch) ================== */
const searchQuery = ref("");
const searchDropdownOpen = ref(false);
const isAdmin = computed(() => authStore.isAdmin());
const userId = computed(() => authStore.state.user?.id);
const allSearchOptions = computed(() => {
  const seen = new Set();
  const options = [];
  data.forEach((d) => {
    if (seen.has(d.id)) return;
    seen.add(d.id);
    options.push({ label: d.data?.search_label || "", value: d.id });
  });
  return options;
});

const filteredSearchOptions = computed(() => {
  const q = searchQuery.value.toLowerCase();
  return allSearchOptions.value.filter((o) =>
    o.label.toLowerCase().includes(q),
  );
});

// Tô nền xám cho thẻ của người đã mất (dựa vào deathDay/deathMonth/deathYear).
// LƯU Ý: family-chart không có khái niệm "đã mất" tích hợp sẵn, nên đây là
// cách can thiệp DOM trực tiếp sau mỗi lần vẽ cây — giả định thẻ card render
// ra có `id` trùng với person.id (quy ước phổ biến của thư viện D3 dạng
// này, nhưng CHƯA có tài liệu chính thức xác nhận). Nếu chạy xong vẫn không
// đổi màu, bấm F12 -> Inspect vào 1 thẻ bất kỳ, xem thẻ đó (hoặc cha của nó)
// có đúng attribute id="<person.id>" không, rồi báo lại để chỉnh selector.
function applyDeceasedStyling() {
  if (!chartEl.value) return;
  data.forEach((p) => {
    const d = p.data || {};
    const isDeceased = !!(d.deathDay || d.deathMonth || d.deathYear);
    const wrapperEl = chartEl.value.querySelector(`[data-id="${p.id}"]`);
    if (!wrapperEl) return;
    const cardEl = wrapperEl.querySelector(".card") || wrapperEl;
    if (isDeceased) {
      cardEl.style.backgroundColor = "darkgray";
      cardEl.style.opacity = "0.9";
    } else {
      cardEl.style.backgroundColor = "";
      cardEl.style.opacity = "";
    }
  });
}

// Vì initChart() dùng setTransitionTime(1000) (có animation khi vẽ lại),
// đợi thêm 1 nhịp sau nextTick để chắc chắn DOM đã render/ổn định trước
// khi query — nếu vẫn thấy tô muộn/nhấp nháy, có thể tăng thời gian chờ.
function scheduleApplyDeceasedStyling() {
  nextTick(() => {
    setTimeout(applyDeceasedStyling, 50);
  });
}

function selectSearchPerson(personId) {
  if (!f3Chart) return;
  f3Chart.updateMainId(personId);
  f3Chart.updateTree({ initial: true });
  scheduleApplyDeceasedStyling();
  searchDropdownOpen.value = false;
  searchQuery.value = "";
}

function resetToRoot() {
  if (!f3Chart) return;
  f3Chart.updateMainId(MAIN_PERSON_ID);
  f3Chart.updateTree({ initial: true });
  scheduleApplyDeceasedStyling();
  searchDropdownOpen.value = false;
  searchQuery.value = "";
}

function handleSearchFocusOut() {
  // đợi 1 chút để click vào option kịp xử lý trước khi đóng dropdown
  setTimeout(() => {
    searchDropdownOpen.value = false;
  }, 200);
}

/* ================== API MÀ TRANG CHA CÓ THỂ GỌI VÀO ================== */
// Trang cha (chế độ isSearch) tự vẽ ô tìm kiếm riêng, rồi gọi 2 hàm này
// qua template ref, ví dụ:
//   const chartRef = ref(null)
//   chartRef.value.focusPerson(personId)
//   const options = chartRef.value.getSearchOptions()
defineExpose({
  focusPerson: selectSearchPerson,
  resetToRoot,
  getSearchOptions: () => allSearchOptions.value,
});

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
    .setAncestryDepth(3) // chỉ hiện tối đa 3 đời ông bà lên trên
    .setProgenyDepth(3) // chỉ hiện tối đa 3 đời con cháu xuống dưới
    .setCardXSpacing(350)
    .setCardYSpacing(250)
    .setShowSiblingsOfMain(true); // hiện đầy đủ anh/chị/em ruột của main person

  f3Card = f3Chart.setCardHtml().setCardDisplay([["fullName"], ["years"]]);

  // Click vào card: luôn focus (đổi main person -> viền sáng + tự
  // recalculate cây quanh người này) và báo lên trang cha qua sự kiện
  // "person-click". Chỉ mở panel sửa khi KHÔNG ở chế độ isSearch.
  f3Card.setOnCardClick((e, d) => {
    f3Chart.updateMainId(d.data.id);
    f3Chart.updateTree({ tree_position: "inherit" });
    scheduleApplyDeceasedStyling();
    emit("person-click", d.data);

    if (!props.isSearch && userId.value) {
      openEditPanel(d.data);
    }
  });

  // Focus main person vào MAIN_PERSON_ID nếu tồn tại trong data,
  // tránh để family-chart mặc định chọn data[0] (thường không phải thuỷ tổ,
  // khiến cây chỉ hiện 1 nhánh thay vì toàn bộ con cháu).
  if (data.some((p) => p.id === MAIN_PERSON_ID)) {
    f3Chart.updateMainId(MAIN_PERSON_ID);
  }

  f3Chart.updateTree({ initial: true });
  scheduleApplyDeceasedStyling();
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
    // Đợi transition vẽ lại xong
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

// Bản nhẹ — không gọi API, chỉ vẽ lại cây từ state hiện có trong bộ nhớ.
// Dùng cho các trường hợp KHÔNG đụng tới node "ADD" ảo (sửa người đã có,
// thêm con bình thường, xoá) — những trường hợp này đã chạy đúng ngay lập
// tức mà không cần F5.
function refreshChartLocal() {
  f3Chart.updateData(data);
  f3Chart.updateTree({ tree_position: "inherit" });
  scheduleApplyDeceasedStyling();
}

// Bản tải lại từ server — CHỈ dùng riêng cho trường hợp "biến node ADD ảo
// thành người thật" (thêm vợ/chồng). Đây là trường hợp DUY NHẤT bị lỗi
// hiển thị sai cho tới khi F5, vì node ADD là placeholder do family-chart
// tự tính ra khi dựng cây (không nằm trong `data`), nên patch tay không
// đảm bảo family-chart tính lại đúng. Gọi lại loadFamilyData() để đồng bộ
// tuyệt đối với backend, đổi lấy 1 lần gọi API thêm cho riêng case này.
async function refreshChartFromServer() {
  await loadFamilyData();
  f3Chart.updateData(data);
  f3Chart.updateTree({ tree_position: "inherit" });
  scheduleApplyDeceasedStyling();
}

/* ================== STATE PANEL ================== */
const panel = reactive({
  open: false,
  mode: "edit",
  isADD: false,
  addNodeId: null, // id thật của node "ADD" do family-chart tự sinh (nếu đang ở node ADD)
  targetId: null,
  gender: "M",
  relativeOfId: null,
  submitting: false,
  error: "",
  createUserId: null,
});

const form = reactive({
  fullName: "",
  gender: "M",
  birthDay: null,
  birthMonth: null,
  birthYear: null,
  birthIsLunar: false,
  isDeceased: false,
  deathDay: null,
  deathMonth: null,
  deathYear: null,
  deathIsLunar: true,
  notes: "",
  education: "",
  hometown: "",
  currentAddress: "",
  siblingIndex: "1",
});

function personName(id) {
  const person = data.find((p) => p.id === id);
  if (!person) return "";
  return `${person.data["fullName"] || ""}`.trim();
}

// Ghép ngày/tháng/năm (có thể thiếu 1 hoặc nhiều phần) thành chuỗi hiển thị.
// Ví dụ: "15/03 (ÂL)", "~1870", "Tháng 3/1990", hoặc "" nếu trống hết.
function formatPartialDate(day, month, year, isLunar) {
  if (!day && !month && !year) return "";

  const dm =
    day && month
      ? `${String(day).padStart(2, "0")}/${String(month).padStart(2, "0")}`
      : month
        ? `Tháng ${month}`
        : "";

  const parts = [dm, year ? String(year) : dm ? "?" : ""].filter(Boolean);
  const label = parts.join("/");
  return label;
}

function attachYears(personData) {
  const birthLabel = formatPartialDate(
    personData.birthDay,
    personData.birthMonth,
    personData.birthYear,
    personData.birthIsLunar,
  );
  const deathLabel = formatPartialDate(
    personData.deathDay,
    personData.deathMonth,
    personData.deathYear,
    personData.deathIsLunar,
  );

  if (!birthLabel && !deathLabel) {
    personData.years = "";
  } else if (deathLabel && !birthLabel) {
    personData.years = `${deathLabel}`;
  } else if (personData.birthYear && personData.deathYear) {
    personData.years = `${personData.birthYear} - ${personData.deathYear}`;
  } else if (deathLabel) {
    personData.years = `${birthLabel || "?"} – ${deathLabel}`;
  } else {
    personData.years = birthLabel; // còn sống (hoặc không rõ năm mất)
  }
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
  form.gender = panel.mode == "add-spouse" && panel.gender == "M" ? "F" : "M";
  form.birthDay = null;
  form.birthMonth = null;
  form.birthYear = null;
  form.birthIsLunar = false;
  form.isDeceased = false;
  form.deathDay = null;
  form.deathMonth = null;
  form.deathYear = null;
  form.deathIsLunar = true;
  form.notes = "";
  form.education = "";
  form.hometown = "";
  form.currentAddress = "";
  form.siblingIndex = "1";
}

function fillForm(person) {
  const d = person.data || {};
  form.fullName = d.fullName || "";
  form.gender = d.gender || "M";
  form.birthDay = d.birthDay ?? null;
  form.birthMonth = d.birthMonth ?? null;
  form.birthYear = d.birthYear ?? null;
  form.birthIsLunar = !!d.birthIsLunar;
  form.isDeceased = !!(d.deathDay || d.deathMonth || d.deathYear);
  form.deathDay = d.deathDay ?? null;
  form.deathMonth = d.deathMonth ?? null;
  form.deathYear = d.deathYear ?? null;
  form.deathIsLunar = !!d.deathIsLunar || true;
  form.notes = d.notes || "";
  form.education = d.education || "";
  form.hometown = d.hometown || "";
  form.currentAddress = d.currentAddress || "";
  form.siblingIndex = d.siblingIndex || "";
}

function openEditPanel(person) {
  if (person.data?.fullName) {
    panel.mode = "edit";
    panel.isADD = false;
    panel.addNodeId = null;
    panel.targetId = person.id;
    panel.createUserId = person.data?.userId;
    panel.gender = person.data?.gender;
    panel.relativeOfId = null;
    panel.error = "";
    fillForm(person);
  } else {
    // Đây là node "ADD" ma do family-chart tự vẽ khi thiếu vợ/chồng.
    // Lưu lại person.id NGAY TẠI ĐÂY (lúc click) vào panel.addNodeId, vì
    // khi submitPanel() chạy, biến `person` cục bộ ở đó sẽ trỏ tới người
    // thật (fg) chứ không còn là node ADD nữa -> không lấy lại được id này.
    panel.mode = "add-spouse";
    panel.isADD = true;
    panel.addNodeId = person.id;
    panel.targetId = null;
    panel.relativeOfId = person.rels?.spouses?.[0] ?? null;
    panel.gender = null;
    panel.error = "";
    resetForm();
  }
  panel.open = true;
}

function openAddModal(kind) {
  panel.mode = kind === "child" ? "add-child" : "add-spouse";
  panel.isADD = false;
  panel.addNodeId = null;
  panel.relativeOfId = panel.targetId;
  panel.error = "";
  resetForm();
  panel.open = true;
}

function closePanel() {
  panel.open = false;
}

function buildDataFromForm() {
  const personData = {
    fullName: form.fullName,
    gender: form.gender,
    birthDay: form.birthDay || null,
    birthMonth: form.birthMonth || null,
    birthYear: form.birthYear || null,
    birthIsLunar: form.birthIsLunar,
    siblingIndex: form.siblingIndex === "" ? null : Number(form.siblingIndex),
    deathDay: form.isDeceased ? form.deathDay || null : null,
    deathMonth: form.isDeceased ? form.deathMonth || null : null,
    deathYear: form.isDeceased ? form.deathYear || null : null,
    deathIsLunar: form.isDeceased ? form.deathIsLunar : false,
    notes: form.notes,
    education: form.education,
    hometown: form.hometown,
    current_address: form.currentAddress,
    userId: userId.value,
    avatar: form.gender == "M" ? "/male.png" : "/female.png",
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
  // Chỉ bật true đúng 1 trường hợp: biến node "ADD" ảo thành người thật.
  // Mọi trường hợp khác dùng bản refresh nhẹ (không gọi thêm API).
  let needsServerRefresh = false;

  try {
    if (panel.mode === "edit") {
      const person = data.find((p) => p.id === panel.targetId);
      if (!person) {
        panel.error = "Không tìm thấy thành viên để cập nhật.";
        panel.submitting = false;
        return;
      }

      // Cập nhật data local trước
      person.data = buildDataFromForm();

      // Gửi lên backend đúng shape { id, data, rels }
      await updatePerson(person.id, person);
    } else if (panel.mode === "add-child") {
      const parent = data.find((p) => p.id === panel.relativeOfId);
      if (!parent) {
        panel.error = "Không tìm thấy người để gán làm cha/mẹ.";
        panel.submitting = false;
        return;
      }
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
      if (!person) {
        panel.error = "Không tìm thấy người để gán làm vợ/chồng.";
        panel.submitting = false;
        return;
      }

      // Nếu đang từ node "ADD" ma -> dùng lại đúng id mà family-chart đã
      // gán cho node đó (lưu từ lúc click, xem openEditPanel), coi như
      // "update/hiện thực hoá" node ảo này thành 1 Person thật. Ngược lại
      // (bấm "+ Thêm vợ/chồng" thủ công từ panel Sửa) -> sinh id mới.
      const newId =
        panel.isADD && panel.addNodeId ? panel.addNodeId : generateId();
      const children = person.rels?.children || [];

      // Chỉ khi person đã CÓ SẴN CON mới cần refresh từ server. Trường hợp
      // này (dù bấm vào node "ADD" ma hay bấm nút "+ Thêm vợ/chồng" thủ
      // công) đều đụng tới đúng 1 node ADD ảo do family-chart đã render sẵn
      // cho các con đó — cần refresh từ server để chắc chắn thay thế đúng
      // (xem lý do ở refreshChartFromServer bên dưới). Nếu person chưa có
      // con nào, không hề có node ADD ảo liên quan -> refresh nhẹ là đủ.
      needsServerRefresh = children.length > 0;

      const payload = {
        id: newId,
        data: buildDataFromForm(),
        rels: { spouses: [panel.relativeOfId], children },
      };

      let res;
      try {
        res = await addPerson(payload);
      } catch (err) {
        // Trường hợp hiếm: id của node ADD trùng với 1 Person có thật đã
        // tồn tại trong DB (409) -> fallback sinh id mới rồi thử lại 1 lần
        if (err.response?.status === 409) {
          payload.id = generateId();
          res = await addPerson(payload);
        } else {
          throw err;
        }
      }

      const created = res.data;
      const newPerson = {
        id: payload.id,
        data: created?.data ?? payload.data,
        rels: created?.rels ?? payload.rels,
      };
      data.push(newPerson);

      person.rels.spouses = [...(person.rels.spouses || []), payload.id];

      if (children.length) {
        try {
          await updateRelationships(payload.id, children);

          // Đồng bộ luôn state cục bộ để family-chart nhận diện đủ 2 phụ
          // huynh ngay lập tức, không cần F5 lại trang mới thấy.
          children.forEach((childId) => {
            const child = data.find((p) => p.id === childId);
            if (child && !child.rels.parents?.includes(payload.id)) {
              child.rels.parents = [...(child.rels.parents || []), payload.id];
            }
          });
        } catch (err) {
          console.error("Cập nhật quan hệ cha/mẹ - con thất bại:", err);
        }
      }
    }
  } catch (err) {
    console.error("Lưu thất bại:", err);
    panel.error = "Không thể lưu thay đổi lên server. Vui lòng thử lại.";
    panel.submitting = false;
    return; // dừng lại, không đóng panel / không refresh chart nếu lỗi
  }

  panel.submitting = false;
  if (needsServerRefresh) {
    await refreshChartFromServer();
  } else {
    refreshChartLocal();
  }
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

  refreshChartLocal();
  closePanel();
}
</script>
