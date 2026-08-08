<script setup>
import { ref, computed, watch, onBeforeUnmount } from "vue";
import FamilyChart from "./FamilyChart.vue";
import { tree } from "d3";
import {
  getPersonLineageStats,
  getRelationship
} from "../api/search.js";

const chartRef = ref(null);

/* ================== SEARCH BOX Ở CẤP TRANG ================== */
const searchQuery = ref("");
const searchDropdownOpen = ref(false);
const selectedPersonId = ref(null); // id của người đang xem (dùng làm person1 khi so quan hệ)

const filteredSearchOptions = computed(() => {
  if (!chartRef.value) return [];
  const q = searchQuery.value.trim().toLowerCase();
  const options = chartRef.value.getSearchOptions();
  if (!q) return options;
  return options.filter((o) => o.label.toLowerCase().includes(q));
});

function handleSearchFocusOut() {
  setTimeout(() => {
    searchDropdownOpen.value = false;
  }, 200);
}

function selectPerson(personId, label) {
  chartRef.value?.focusPerson(personId);
  searchDropdownOpen.value = false;
  searchQuery.value = "";
  selectedPersonId.value = personId;
  resetRelationState();
  fetchPersonStats(personId, label);
}

function resetSearch() {
  chartRef.value?.resetToRoot();
  searchQuery.value = "";
  searchDropdownOpen.value = false;
  personStats.value = null;
  statsError.value = "";
  selectedPersonId.value = null;
  findRelationshipMode.value = false;
  resetRelationState();
}

// Bấm trực tiếp vào 1 thẻ trong cây cũng cập nhật thẻ thống kê tương tự
function onPersonClick(personData) {
  selectedPersonId.value = personData.id;
  resetRelationState();
  fetchPersonStats(personData.id, personData.fullName);
}

/* ================== SỐ ĐỜI + CON CHÁU (NAM/NỮ) ================== */


const personStats = ref(null);
const statsLoading = ref(false);
const statsError = ref("");

const totalDescendants = computed(() => {
  if (!personStats.value) return 0;
  return (
    (personStats.value.maleDescendants ?? 0) +
    (personStats.value.femaleDescendants ?? 0)
  );
});

async function fetchPersonStats(personId, fallbackName) {
  statsError.value = "";
  statsLoading.value = true;
  personStats.value = null;
  try {
    const { data } = await getPersonLineageStats(personId)
    personStats.value = data
  } catch (err) {
    console.error("Không tải được thông tin con cháu:", err);
    statsError.value = `Không tải được thông tin: ${err.response?.data?.error || err.message}`;
  } finally {
    statsLoading.value = false;
  }
}
/* ================== TÌM QUAN HỆ VỚI NGƯỜI KHÁC ================== */
const findRelationshipMode = ref(false);

const relationQuery = ref("");
const relationDropdownOpen = ref(false);
const relationResult = ref(null);
const relationLoading = ref(false);
const relationError = ref("");

const filteredRelationOptions = computed(() => {
  if (!chartRef.value) return [];
  const q = relationQuery.value.trim().toLowerCase();
  const options = chartRef.value.getSearchOptions();
  const filtered = q ? options.filter((o) => o.label.toLowerCase().includes(q)) : options;
  // loại chính người đang xem (person1) ra khỏi danh sách chọn người thứ 2
  return filtered.filter((o) => o.value !== selectedPersonId.value);
});

function handleRelationFocusOut() {
  setTimeout(() => {
    relationDropdownOpen.value = false;
  }, 200);
}

function resetRelationState() {
  relationQuery.value = "";
  relationDropdownOpen.value = false;
  relationResult.value = null;
  relationError.value = "";
}

// Tắt checkbox thì dọn luôn kết quả đang hiện
watch(findRelationshipMode, (enabled) => {
  if (!enabled) resetRelationState();
});

async function selectRelationPerson(personId) {
  relationDropdownOpen.value = false;
  relationQuery.value = "";
  relationError.value = "";
  relationResult.value = null;

  if (!selectedPersonId.value) {
    relationError.value = "Vui lòng chọn 1 người ở ô tìm kiếm phía trên trước.";
    return;
  }

  relationLoading.value = true;
  try {
    const { data } = await getRelationship(selectedPersonId.value, personId);
    relationResult.value = data;
  } catch (err) {
    console.error("Không xác định được quan hệ:", err);
    relationError.value = `Không xác định được quan hệ: ${err.response?.data?.error || err.message}`;
  } finally {
    relationLoading.value = false;
  }
}
</script>

<template>
  <main>
    <section style="padding-bottom: 0">
      <div class="container">
        <span class="eyebrow">Sơ đồ phả hệ</span>
        <h1>Tra cứu gia phả</h1>
        <p class="lede" style="max-width: 60ch">
          Nhập tên một người để xem vị trí trên cây, và thông tin liên quan. Bấm vào một thành viên trên cây cũng cho kết quả tương tự.
        </p>
      </div>
    </section>

    <section>
      <div class="container">
        <!-- ================= SEARCH BOX (kích thước theo container) ================= -->
        <div class="search-panel paper" @focusout="handleSearchFocusOut">
          <div class="search-row">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Nhập tên người cần tra cứu…"
              class="search-input"
              autocomplete="off"
              @focus="searchDropdownOpen = true"
              @input="searchDropdownOpen = true"
            />
            <button
              type="button"
              class="btn btn-outline reset-btn"
              title="Về thuỷ tổ"
              @click="resetSearch"
            >
              ⟲ Về thuỷ tổ
            </button>
          </div>

          <div
            v-if="searchDropdownOpen && searchQuery.trim() && filteredSearchOptions.length"
            class="search-dropdown"
          >
            <div
              v-for="opt in filteredSearchOptions"
              :key="opt.value"
              class="search-option"
              style="color:black"
              @click="selectPerson(opt.value, opt.label)"
            >
              {{ opt.label }}
            </div>
          </div>

          <!-- ================= KẾT QUẢ: SỐ ĐỜI + CON CHÁU ================= -->
          <div v-if="statsLoading" class="stats-loading">
            Đang tải thông tin con cháu…
          </div>
          <p v-else-if="statsError" class="alert-error stats-error">
            {{ statsError }}
          </p>
          <div v-else-if="personStats" class="stats-result">
            <div class="stats-head">
              <span class="stats-name">{{ personStats.full_name }}</span>
              <span class="stats-gen-badge">Đời thứ {{ personStats.generation ?? "—" }}</span>
            </div>
            <div
            v-if="personStats?.father || personStats.mother || personStats.spouses?.length"
            class="family-relations"
          >
            <div v-if="personStats.father" class="relation-chip">
              <span class="relation-label">Bố:</span>
              <span class="relation-value">{{ personStats.father.full_name }}</span>
            </div>
            <div v-if="personStats.mother" class="relation-chip">
              <span class="relation-label">Mẹ:</span>
              <span class="relation-value">{{ personStats.mother.full_name }}</span>
            </div>
            <div
              v-for="(spouse, idx) in personStats.spouses"
              :key="spouse.id"
              class="relation-chip"
            >
              <span class="relation-label">
                {{ personStats.spouses.length > 1 ? `Vợ/chồng ${idx + 1}` : "Vợ/chồng:" }}
              </span>
              <span class="relation-value">{{ spouse.full_name }}</span>
            </div>
          </div>
            <div class="stats-row">
              <div class="stats-item">
                <span class="stats-number">{{ personStats.children_count ?? 0 }}</span>
                <span class="stats-label">Con</span>
              </div>
              <div class="stats-item">
                <span class="stats-number">{{ personStats.grandchildren_count ?? 0 }}</span>
                <span class="stats-label">Cháu</span>
              </div>
              <div class="stats-item">
                <span class="stats-number">{{ personStats.great_grandchildren_count }}</span>
                <span class="stats-label">Chắt</span>
              </div>
            </div>
          </div>
        </div>
        <!-- ================= CHECKBOX + DROPDOWN TÌM QUAN HỆ ================= -->
<label class="relation-toggle">
  <input type="checkbox" v-model="findRelationshipMode" />
  Tìm quan hệ với người khác
</label>

<div
  v-if="findRelationshipMode"
  class="relation-search-wrap"
  @focusout="handleRelationFocusOut"
>
  <p v-if="!selectedPersonId" class="relation-hint">
    Hãy chọn 1 người ở ô tìm kiếm phía trên trước.
  </p>

  <template v-else>
    <input
      v-model="relationQuery"
      type="text"
      placeholder="Nhập tên người thứ 2 để so sánh quan hệ…"
      class="search-input"
      autocomplete="off"
      @focus="relationDropdownOpen = true"
      @input="relationDropdownOpen = true"
    />
    <div
      v-if="relationDropdownOpen && filteredRelationOptions.length"
      class="search-dropdown"
    >
      <div
        v-for="opt in filteredRelationOptions"
        :key="opt.value"
        class="search-option"
        style="color:black"
        @click="selectRelationPerson(opt.value)"
      >
        {{ opt.label }}
      </div>
    </div>
  </template>

  <div v-if="relationLoading" class="stats-loading">Đang xác định quan hệ…</div>
  <p v-else-if="relationError" class="alert-error stats-error">{{ relationError }}</p>

  <div v-else-if="relationResult" class="relation-result">
    <template v-if="relationResult.type === 'SPOUSE'">
      <p class="relation-result-line">Hai người là <strong>vợ chồng</strong>.</p>
    </template>

    <template v-else-if="relationResult.type === 'UNRELATED'">
      <p class="relation-result-line">
        {{ relationResult.note || "Không tìm thấy quan hệ huyết thống giữa 2 người." }}
      </p>
    </template>

    <template v-else>
      <div class="relation-chip">
        <span class="relation-label">Quan hệ giữa {{ personStats?.full_name }} và {{relationResult.senior?.fullName || relationResult.elder?.fullName  }} là: </span>
        <span class="relation-value">{{ relationResult.person2CallsPerson1 }} - {{ relationResult.person1CallsPerson2 }}</span>
      </div>
      <p v-if="relationResult.commonAncestor?.fullName" class="relation-note">
        Tổ tiên chung: {{ relationResult.commonAncestor.fullName }}
      </p>
      <p v-if="relationResult.note" class="relation-note">{{ relationResult.note }}</p>
    </template>
  </div>
</div>
        <div class="tree-wrap">
          <div class="tree">
            <FamilyChart ref="chartRef" is-search @person-click="onPersonClick" />
          </div>
        </div>

        <div class="legend" v-show="false">
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
</template>

<style scoped>
.search-panel {
  padding: 24px;
  margin-bottom: 24px;
  position: relative;
  z-index: 20;
}

.search-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.search-input {
  flex: 1;
  min-width: 240px;
  font-family: var(--font-body);
  font-size: 15px;
  padding: 12px 16px;
  border: 1px solid var(--color-paper-line, #e2ddce);
  border-radius: 8px;
  background: var(--paper-card, #fff);
  color: var(--color-ink, #2c281f);
}
.reset-btn {
  white-space: nowrap;
  padding: 12px 18px;
  font-size: 14px;
}

.search-dropdown {
  margin-top: 10px;
  border: 1px solid var(--color-paper-line, #e2ddce);
  border-radius: 8px;
  background: var(--paper-card, #fff);
  max-height: 320px;
  overflow-y: auto;
}
.family-relations {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}
.relation-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(86, 73, 47, 0.06);
  border: 1px solid var(--color-paper-line, #e2ddce);
}
.search-option {
  padding: 12px 16px;
  font-size: 14.5px;
  cursor: pointer;
  border-bottom: 1px solid var(--color-paper-line, #e2ddce);
}
.search-option:last-child { border-bottom: none; }
.search-option:hover { background: rgba(197, 160, 60, 0.12); }

.stats-loading {
  margin-top: 18px;
  font-size: 14px;
  color: var(--color-ink-soft, #6b6455);
}
.stats-error { margin-top: 18px; }

.stats-result {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--color-paper-line, #e2ddce);
}
.stats-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.stats-name {
  font-weight: 700;
  font-size: 19px;
  color: var(--color-ink, #2c281f);
}
.stats-gen-badge {
  font-size: 13px;
  font-weight: 700;
  color: var(--color-seal, #a5312b);
  border: 1px solid var(--color-seal, #a5312b);
  border-radius: 999px;
  padding: 5px 14px;
  white-space: nowrap;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.stats-item {
  text-align: center;
  padding: 20px 14px;
  border-radius: 10px;
  background: rgba(86, 73, 47, 0.05);
}
.stats-item-total {
  background: rgba(14, 24, 19, 0.05);
}
.stats-number {
  display: block;
  font-size: 32px;
  font-weight: 700;
  color: var(--color-ink, #2c281f);
  line-height: 1.1;
}
.stats-label {
  display: block;
  font-size: 13px;
  color: var(--color-ink-soft, #6b6455);
  margin-top: 6px;
}

@media (max-width: 640px) {
  .stats-row { grid-template-columns: 1fr; }
  .search-row { flex-direction: column; }
}
.relation-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  font-size: 14px;
  color: var(--color-ink, #2c281f);
  cursor: pointer;
}

.relation-search-wrap {
  margin-top: 12px;
  position: relative;
}
.relation-hint {
  font-size: 13.5px;
  color: var(--color-ink-soft, #6b6455);
  margin: 0;
}

.relation-result {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
.relation-result-line {
  font-size: 14.5px;
  color: var(--color-ink, #2c281f);
  margin: 0;
}
.relation-note {
  width: 100%;
  font-size: 12.5px;
  color: var(--color-ink-soft, #6b6455);
  margin: 4px 0 0;
}
</style>