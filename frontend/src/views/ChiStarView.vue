<template>
    <main class="section container" style="max-width: 1000px;">
      <div class="tree-toolbar">
        <div>
          <span class="eyebrow">Tra cứu dòng họ</span>
          <h1 style="font-size: 28px;">Lọc thành viên theo chi</h1>
        </div>
      </div>
  
      <p style="color: var(--color-cream-dim); font-size: 13.5px; margin-bottom: 24px;">
        Dùng để lấy danh sách người thoả điều kiện, phục vụ tính đóng góp hoặc lập danh sách tổ chức sự kiện.
        Chỉ lọc trong số người <strong>còn sống</strong>.
      </p>
  
      <p v-if="loadError" class="alert-error">{{ loadError }}</p>
      <p v-if="usingMockData" class="alert-info">
        ⚠️ Đang dùng dữ liệu mẫu (demo) — backend GET /api/persons/ chưa sẵn sàng hoặc chưa kết nối.
      </p>
      <p v-if="loading" style="color: var(--color-cream-dim);">Đang tải dữ liệu…</p>
  
      <template v-else>
        <!-- ================= BỘ LỌC ================= -->
        <div class="paper filter-panel">
          <div class="filter-grid">
            <div class="field">
              <label>Chi</label>
              <select v-model="filters.chi">
                <option value="all">Tất cả các chi</option>
                <option v-for="(item, index) in availableChis" :key="index" :value="item">{{ index}}</option>
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
              <input v-model.number="filters.ageFrom" type="number" min="0" placeholder="VD: 18">
            </div>
  
            <div class="field">
              <label>Đến tuổi</label>
              <input v-model.number="filters.ageTo" type="number" min="0" placeholder="VD: 70">
            </div>
          </div>
  
          <div class="filter-actions">
            <button type="button" class="btn btn-outline" @click="resetFilters">Đặt lại</button>
            <button type="button" class="btn btn-primary" @click="runSearch">Tìm kiếm</button>
          </div>
        </div>
  
        <!-- ================= KẾT QUẢ ================= -->
        <div v-if="hasSearched" style="margin-top: 28px;">
          <p class="result-count">
            Tìm thấy <strong>{{ results.length }}</strong> người thoả điều kiện.
          </p>
  
          <div class="paper" style="overflow-x: auto;">
            <table class="user-table">
              <thead>
                <tr>
                  <th>Họ tên</th>
                  <th>Tên bố</th>
                  <th>Giới tính</th>
                  <th>Chi</th>
                  <th>Năm sinh</th>
                  <th>Tuổi</th>
                  <th>Đã có vợ/chồng</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in results" :key="p.id">
                  <td>{{ p.fullName }}</td>
                  <td>{{ p.parent }}</td>
                  <td>{{ p.gender === 'M' ? 'Nam' : 'Nữ' }}</td>
                  <td>{{ p.chi || '—' }}</td>
                  <td>{{ p.birthYear || '—' }}</td>
                  <td>{{ p.birthYear ? CURRENT_YEAR - p.birthYear : '—' }}</td>
                  <td>{{ p.hasSpouse ? 'Có' : 'Chưa' }}</td>
                </tr>
              </tbody>
            </table>
            <p v-if="!results.length" style="color: var(--color-ink-soft); padding: 16px;">
              Không có ai thoả điều kiện đang chọn.
            </p>
          </div>
        </div>
      </template>
    </main>
  </template>
  
  <script setup>
  import { ref, reactive, onMounted } from "vue";
  import { getAllPerson, searchPersons } from "../api/person.js";
  
  const CURRENT_YEAR = new Date().getFullYear();
  
  const persons = ref([]);
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
  }
  
  // ============================================================
  // ĐỊNH NGHĨA MẶC ĐỊNH (chỉnh lại nếu cách tính khác ý):
  // - "Số đinh"      -> chỉ nam giới, không xét đã có vợ hay chưa
  // - "Số hộ"        -> chỉ nam giới VÀ đã có vợ
  // - "Tất cả"       -> không lọc theo giới tính/hôn nhân
  // - Độ tuổi: tính theo năm hiện tại - birthYear. Người chưa rõ năm sinh
  //   sẽ BỊ LOẠI nếu bạn có nhập "Từ tuổi" hoặc "Đến tuổi" (vì không thể
  //   xác định có thoả điều kiện hay không); nếu để trống cả 2 ô tuổi thì
  //   vẫn hiển thị bình thường.
  // ============================================================
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
    // const alive = persons.value.filter((p) => !p.isDeceased);
  
    // const chiFiltered =
    //   filters.chi === "all" ? alive : alive.filter((p) => p.chi === filters.chi);
  
    // const metricFiltered = chiFiltered.filter((p) => {
    //   if (filters.metric === "dinh") return p.gender === "M";
    //   if (filters.metric === "ho") return p.gender === "M" && p.hasSpouse;
    //   return true; // 'all'
    // });
  
    // const hasAgeFilter = filters.ageFrom != null || filters.ageTo != null;
  
    // const ageFiltered = metricFiltered.filter((p) => {
    //   if (!hasAgeFilter) return true;
    //   if (!p.birthYear) return false; // không rõ năm sinh -> loại khi có lọc tuổi
  
    //   const age = CURRENT_YEAR - p.birthYear;
    //   if (filters.ageFrom != null && age < filters.ageFrom) return false;
    //   if (filters.ageTo != null && age > filters.ageTo) return false;
    //   return true;
    // });
  
    // results.value = ageFiltered;
    // hasSearched.value = true;
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
  
  .result-count {
    color: var(--color-cream-dim);
    font-size: 14px;
    margin-bottom: 16px;
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
    .filter-grid { grid-template-columns: repeat(2, 1fr); }
  }
  </style>