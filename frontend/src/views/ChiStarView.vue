<template>
  <main class="section container" style="max-width: 1000px">
    <div class="tree-toolbar">
      <div>
        <span class="eyebrow">Tra cứu dòng họ</span>
        <h1 style="font-size: 28px">Lọc thành viên theo chi</h1>
      </div>
    </div>

    <p
      style="
        color: var(--color-cream-dim);
        font-size: 13.5px;
        margin-bottom: 24px;
      "
    >
      Dùng để lấy danh sách người thoả điều kiện, phục vụ tính đóng góp hoặc lập
      danh sách tổ chức sự kiện. Chỉ lọc trong số người
      <strong>còn sống</strong>.
    </p>

    <p v-if="loadError" class="alert-error">{{ loadError }}</p>
    <p v-if="usingMockData" class="alert-info">
      ⚠️ Đang dùng dữ liệu mẫu (demo) — backend GET /api/persons/ chưa sẵn sàng
      hoặc chưa kết nối.
    </p>
    <p v-if="loading" style="color: var(--color-cream-dim)">
      Đang tải dữ liệu…
    </p>

    <template v-else>
      <!-- ================= BỘ LỌC ================= -->
      <div class="paper filter-panel">
        <div class="filter-grid">
          <div class="field">
            <label>Chi</label>
            <select v-model="filters.chi">
              <option value="all">Tất cả các chi</option>
              <option
                v-for="(item, index) in availableChis"
                :key="index"
                :value="item"
              >
                {{ index }}
              </option>
            </select>
          </div>

          <div class="field">
            <label>Loại</label>
            <select v-model="filters.metric">
              <option value="dinh">Số đinh (nam giới)</option>
              <option value="ho">Số hộ (nam đã có vợ)</option>
              <option value="all">Tất cả (không phân biệt)</option>
            </select>
          </div>

          <div class="field">
            <label>Từ tuổi</label>
            <input
              v-model.number="filters.ageFrom"
              type="number"
              min="0"
              placeholder="VD: 18"
            />
          </div>

          <div class="field">
            <label>Đến tuổi</label>
            <input
              v-model.number="filters.ageTo"
              type="number"
              min="0"
              placeholder="VD: 70"
            />
          </div>
        </div>

        <div class="filter-actions">
          <button type="button" class="btn btn-outline" @click="resetFilters">
            Đặt lại
          </button>
          <button type="button" class="btn btn-primary" @click="runSearch">
            Tìm kiếm
          </button>
        </div>
      </div>

      <!-- ================= KẾT QUẢ ================= -->
      <div v-if="hasSearched" style="margin-top: 28px">
        <div class="result-header">
          <p class="result-count">
            Tìm thấy <strong>{{ results.length }}</strong> người thoả điều kiện.
          </p>
          <button
            type="button"
            class=""
            :disabled="!results.length || exporting"
            @click="exportToExcel"
          >
            {{ exporting ? "Đang xuất..." : "⬇ Xuất Excel" }}
          </button>
        </div>

        <div class="paper" style="overflow-x: auto">
          <table class="user-table">
            <thead>
              <tr>
                <th>Họ tên</th>
                <th>Tên bố</th>
                <th>Giới tính</th>
                <th>Năm sinh</th>
                <th>Tuổi</th>
                <th>Đã có vợ/chồng</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="p in paginatedResults" :key="p.id">
                <td>{{ p.fullName }}</td>
                <td>{{ p.parent }}</td>
                <td>{{ p.gender === "M" ? "Nam" : "Nữ" }}</td>
                <td>{{ p.birthYear || "—" }}</td>
                <td>{{ p.birthYear ? CURRENT_YEAR - p.birthYear : "—" }}</td>
                <td>{{ p.hasSpouse ? "Có" : "Chưa" }}</td>
              </tr>
            </tbody>
          </table>
          <p
            v-if="!results.length"
            style="color: var(--color-ink-soft); padding: 16px"
          >
            Không có ai thoả điều kiện đang chọn.
          </p>

          <!-- ================= PHÂN TRANG (20 người/trang) ================= -->
          <div v-if="results.length" class="pagination-bar">
            <span class="pagination-info">
              Trang {{ currentPage }} / {{ totalPages }} ({{
                (currentPage - 1) * PAGE_SIZE + 1
              }}–{{ Math.min(currentPage * PAGE_SIZE, results.length) }} trong
              {{ results.length }})
            </span>
            <div class="pagination-controls">
              <button
                class="btn btn-outline"
                :disabled="currentPage === 1"
                @click="currentPage--"
              >
                ‹ Trước
              </button>
              <button
                class="btn btn-outline"
                :disabled="currentPage === totalPages"
                @click="currentPage++"
              >
                Sau ›
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </main>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from "vue";
import * as XLSX from "xlsx";
import { getAllPerson, searchPersons } from "../api/person.js";

const CURRENT_YEAR = new Date().getFullYear();

const loading = ref(false);
const loadError = ref("");
const usingMockData = ref(false);

const filters = reactive({
  chi: "all",
  metric: "dinh", // 'dinh' | 'ho' | 'all'
  ageFrom: null,
  ageTo: null,
});

const results = ref([]);
const hasSearched = ref(false);
const availableChis = ref([]);

/* ================== PHÂN TRANG ================== */
const PAGE_SIZE = 20;
const currentPage = ref(1);

const totalPages = computed(() =>
  Math.max(1, Math.ceil(results.value.length / PAGE_SIZE)),
);

const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE;
  return results.value.slice(start, start + PAGE_SIZE);
});

// Mỗi khi có kết quả tìm kiếm mới thì quay lại trang 1
watch(results, () => {
  currentPage.value = 1;
});

async function fetchPersons() {
  availableChis.value = {
    "Chi 1": "anc_huuthien",
    "Chi 2": "anc_huuduc",
    "Chi 3": "anc_huuthanh",
    "Chi 4": "u_nguyenhuuhuan_195",
  };
}

onMounted(fetchPersons);

function resetFilters() {
  filters.chi = "all";
  filters.metric = "dinh";
  filters.ageFrom = null;
  filters.ageTo = null;
  hasSearched.value = false;
  results.value = [];
  currentPage.value = 1;
}

async function runSearch() {
  try {
    const { data } = await searchPersons({
      chi: filters.chi,
      metric: filters.metric,
      age_from: filters.ageFrom,
      age_to: filters.ageTo,
    });

    results.value = data;
    hasSearched.value = true;
  } catch (err) {
    console.error(err);
  }
}

/* ================== XUẤT EXCEL ================== */
const exporting = ref(false);

function genderLabel(g) {
  return g === "M" ? "Nam" : "Nữ";
}

const METRIC_LABELS = {
  dinh: "Số đinh (nam giới)",
  ho: "Số hộ (nam đã có vợ)",
  all: "Tất cả",
};

function exportToExcel() {
  if (!results.value.length) return;

  exporting.value = true;
  try {
    // Xuất TOÀN BỘ kết quả đã lọc (không chỉ trang đang xem)
    const rows = results.value.map((p) => ({
      "Họ tên": p.fullName || "",
      "Tên bố": p.parent || "",
      "Giới tính": genderLabel(p.gender),
      "Năm sinh": p.birthYear || "",
      Tuổi: p.birthYear ? CURRENT_YEAR - p.birthYear : "",
      "Đã có vợ/chồng": p.hasSpouse ? "Có" : "Chưa",
    }));

    const worksheet = XLSX.utils.json_to_sheet(rows);

    // Auto-size cột cho dễ đọc thay vì mặc định quá hẹp
    worksheet["!cols"] = [
      { wch: 24 }, // Họ tên
      { wch: 24 }, // Tên bố
      { wch: 10 }, // Giới tính
      { wch: 10 }, // Năm sinh
      { wch: 8 }, // Tuổi
      { wch: 16 }, // Đã có vợ/chồng
    ];

    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Danh sách");

    const chiLabel =
      filters.chi === "all"
        ? "tat-ca-cac-chi"
        : Object.keys(availableChis.value).find(
            (k) => availableChis.value[k] === filters.chi,
          ) || "chi";
    const metricLabel = METRIC_LABELS[filters.metric] || filters.metric;
    const fileName = `danh-sach-${chiLabel}-${new Date()
      .toISOString()
      .slice(0, 10)}.xlsx`;

    XLSX.writeFile(workbook, fileName);
  } catch (err) {
    console.error("Xuất Excel thất bại:", err);
    loadError.value = "Không thể xuất file Excel. Vui lòng thử lại.";
  } finally {
    exporting.value = false;
  }
}
</script>

<style scoped>
.filter-panel {
  padding: 24px;
}
.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
.filter-grid .field label {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-ink-soft);
  display: block;
  margin-bottom: 6px;
}
.filter-grid .field select,
.filter-grid .field input {
  width: 100%;
  box-sizing: border-box;
  font-family: var(--font-body);
  font-size: 14px;
  padding: 10px 12px;
  border: 1px solid var(--color-paper-line);
  border-radius: 3px;
  background: #fbf6ea;
  color: var(--color-ink);
}
.filter-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
  padding-top: 18px;
  border-top: 1px solid var(--color-paper-line);
}
.filter-actions .btn-outline {
  color: var(--color-ink);
  border-color: var(--color-paper-line);
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.result-count {
  color: var(--color-cream-dim);
  font-size: 14px;
  margin: 0;
}
.export-btn {
  color: var(--color-ink);
  border-color: var(--color-paper-line);
  white-space: nowrap;
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

/* ---- Phân trang ---- */
.pagination-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  flex-wrap: wrap;
  gap: 10px;
}
.pagination-info {
  font-size: 13px;
  color: var(--color-ink-soft);
}
.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}
.pagination-controls .btn {
  padding: 6px 12px;
  font-size: 13px;
  color: var(--color-ink);
  border-color: var(--color-paper-line);
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
.alert-info {
  background: rgba(201, 162, 39, 0.12);
  color: var(--color-gold);
  border: 1px solid var(--color-gold-soft);
  border-radius: 4px;
  padding: 10px 14px;
  font-size: 13.5px;
  margin-bottom: 18px;
}

@media (max-width: 720px) {
  .filter-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
