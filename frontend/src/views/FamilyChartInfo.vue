<template>
  <main>
    <section style="padding-bottom: 0">
      <div class="container">
        <span class="eyebrow">Sơ đồ phả hệ</span>
        <h1>Xem gia phả</h1>
        <p class="lede" style="max-width: 60ch">
          Duyệt cây gia phả theo từng đời. Bấm vào một thành viên để xem chi
          tiết, hoặc thu gọn một nhánh để dễ theo dõi.
        </p>
      </div>
    </section>

    <section>
      <div class="container">
        <div class="tree-toolbar">
          <div class="filters">
            <select class="select-field">
              <option>Toàn bộ chi nhánh</option>
              <option>Chi trưởng</option>
              <option>Chi thứ hai</option>
              <option>Chi thứ ba</option>
            </select>
            <select class="select-field">
              <option>Toàn bộ các đời</option>
              <option>Đời 9 — 12</option>
              <option>Đời 5 — 8</option>
              <option>Đời 1 — 4</option>
            </select>
          
            <!-- ================= SEARCH BOX ================= -->
            <div
              class="search-box"
              @focusout="handleSearchFocusOut"
            >
              <div class="search-row">
                <label>Tên: </label>
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Tìm kiếm..."
                  class="search-input select-field"
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
                  @click="selectSearchPerson(opt.value)"
                >
                  {{ opt.label }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="legend">
          <span
            ><span class="dot" style="background: var(--lacquer)"></span>Thành
            viên gốc của nhánh</span
          >
          <span
            ><span class="dot" style="background: #cfc6b3"></span>Đã mất</span
          >
          <span
            ><span class="dot" style="background: var(--gold-soft)"></span>Còn
            sống</span
          >
        </div>
      </div>
    </section>
  </main>
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

    <!-- ================= SEARCH BOX ================= -->
    <!-- <div
      v-if="!loading && !loadError"
      class="search-box"
      @focusout="handleSearchFocusOut"
    >
      <div class="search-row">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Tìm kiếm..."
          class="search-input"
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
          @click="selectSearchPerson(opt.value)"
        >
          {{ opt.label }}
        </div>
      </div>
    </div> -->

    <button
      v-if="!loading && !loadError"
      class="btn btn-outline export-btn"
      @click="exportTreeToPdf"
      :disabled="exporting"
    >
      {{ exporting ? "Đang xuất..." : "In gia phả (PDF)" }}
    </button>

  </div>
</template>

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

/* search box giờ nằm trong .filters, không còn absolute nữa */
.search-box {
  position: relative;
  width: 220px;
}
.search-row {
  display: flex;
  gap: 6px;
}
.search-input {
  flex: 1;
  box-sizing: border-box;
}
.reset-btn {
  flex-shrink: 0;
  padding: 6px 10px;
  line-height: 1;
}
.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  overflow-y: auto;
  max-height: 300px;
  background-color: #000;
  color: #fff;
  z-index: 20;
}
.search-option {
  padding: 5px 8px;
  cursor: pointer;
  border-bottom: 0.5px solid currentColor;
}
.search-option:hover {
  background-color: #333;
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

/* ================== SEARCH STATE ================== */
const searchQuery = ref("");
const searchDropdownOpen = ref(false);

const allSearchOptions = computed(() => {
  const seen = new Set();
  const options = [];
  data.forEach((d) => {
    if (seen.has(d.id)) return;
    seen.add(d.id);
    options.push({ label: d.data?.fullName || "", value: d.id });
  });
  return options;
});

const filteredSearchOptions = computed(() => {
  const q = searchQuery.value.toLowerCase();
  return allSearchOptions.value.filter((o) =>
    o.label.toLowerCase().includes(q),
  );
});

function selectSearchPerson(personId) {
  if (!f3Chart) return;
  f3Chart.updateMainId(personId);
  f3Chart.updateTree({ initial: true });
  searchDropdownOpen.value = false;
  searchQuery.value = "";
}

function resetToRoot() {
  if (!f3Chart) return;
  f3Chart.updateMainId(MAIN_PERSON_ID);
  f3Chart.updateTree({ initial: true });
  searchDropdownOpen.value = false;
  searchQuery.value = "";
}

function handleSearchFocusOut() {
  // đợi 1 chút để click vào option kịp xử lý trước khi đóng dropdown
  setTimeout(() => {
    searchDropdownOpen.value = false;
  }, 200);
}

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


/* ================== STATE PANEL ================== */
const panel = reactive({
  open: false,
  mode: "edit",
  targetId: null,
  gender: "M",
  relativeOfId: null,
  submitting: false,
  error: "",
});


function attachYears(personData) {
  personData.years = buildYearsLabel(
    personData.birthday,
    personData.death_date,
  );
  return personData;
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
</script>