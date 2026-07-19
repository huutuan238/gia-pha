<template>
  <div class="tree-wrap">
    <div id="FamilyChart" ref="chartEl" class="f3"></div>

    <!-- ================= MODAL TUỲ CHỈNH ================= -->
    <Teleport to="body">
      <div v-if="modal.open" class="modal-overlay" @click.self="closeModal">
        <div class="paper modal-card">
          <button class="modal-close" @click="closeModal" aria-label="Đóng">
            ✕
          </button>

          <!-- ---- Chế độ: Sửa / Thêm thành viên ---- -->
          <template v-if="modal.mode !== 'confirm-delete'">
            <div class="seal-badge" style="margin-bottom: 16px">
              {{ modal.mode === "edit" ? "SỬA" : "THÊM" }}
            </div>
            <h2 style="font-size: 20px; margin-bottom: 4px">
              {{ modalTitle }}
            </h2>
            <p
              style="
                font-size: 13px;
                color: var(--color-ink-soft);
                margin-bottom: 24px;
              "
            >
              {{ modalSubtitle }}
            </p>

            <form @submit.prevent="saveModal">
              <div class="form-grid">
                <div class="field full">
                  <label>Họ</label>
                  <input
                    v-model="form.lastName"
                    type="text"
                    placeholder="Nguyễn"
                  />
                </div>
                <div class="field full">
                  <label>Tên</label>
                  <input
                    v-model="form.firstName"
                    type="text"
                    placeholder="Văn An"
                  />
                </div>

                <div class="field">
                  <label>Giới tính</label>
                  <select v-model="form.gender">
                    <option value="M">Nam</option>
                    <option value="F">Nữ</option>
                  </select>
                </div>
                <div class="field">
                  <label>Tình trạng hôn nhân</label>
                  <select v-model="form.maritalStatus">
                    <option>Độc thân</option>
                    <option>Đã kết hôn</option>
                    <option>Ly hôn</option>
                    <option>Góa</option>
                  </select>
                </div>

                <div class="field">
                  <label>Ngày sinh</label>
                  <input v-model="form.birthday" type="date" />
                </div>
                <div class="field">
                  <label>Ngày mất <span class="hint">(nếu đã mất)</span></label>
                  <input v-model="form.deathday" type="date" />
                </div>

                <div class="field">
                  <label>Học vấn</label>
                  <input
                    v-model="form.education"
                    type="text"
                    placeholder="Đại học Bách Khoa"
                  />
                </div>
                <div class="field">
                  <label>Quê quán</label>
                  <input
                    v-model="form.hometown"
                    type="text"
                    placeholder="Đông Bàn, Hải Dương"
                  />
                </div>

                <div class="field full">
                  <label>Ghi chú / tiểu sử</label>
                  <textarea
                    v-model="form.notes"
                    rows="2"
                    placeholder="Vài dòng ghi chú…"
                  ></textarea>
                </div>
              </div>

              <div class="form-actions" style="justify-content: space-between">
                <button
                  v-if="modal.mode === 'edit'"
                  type="button"
                  class="btn btn-outline"
                  style="
                    color: var(--color-seal);
                    border-color: var(--color-seal);
                  "
                  @click="askDelete"
                >
                  Xoá thành viên
                </button>
                <div v-else></div>

                <div style="display: flex; gap: 12px">
                  <button
                    type="button"
                    class="btn btn-outline"
                    @click="closeModal"
                  >
                    Hủy
                  </button>
                  <button type="submit" class="btn btn-primary">Lưu</button>
                </div>
              </div>
            </form>

            <!-- Thêm quan hệ (chỉ hiện khi đang sửa 1 người đã tồn tại) -->
            <div v-if="modal.mode === 'edit'" class="relation-actions">
              <span class="hint" style="display: block; margin-bottom: 10px"
                >Thêm quan hệ cho người này:</span
              >
              <div style="display: flex; gap: 10px; flex-wrap: wrap">
                <button
                  class="btn btn-paper"
                  style="font-size: 13px; padding: 8px 14px"
                  @click="openAddModal('child')"
                >
                  + Thêm con
                </button>
                <button
                  class="btn btn-paper"
                  style="font-size: 13px; padding: 8px 14px"
                  @click="openAddModal('spouse')"
                >
                  + Thêm vợ/chồng
                </button>
              </div>
            </div>
          </template>

          <!-- ---- Chế độ: Xác nhận xoá ---- -->
          <template v-else>
            <h2 style="font-size: 19px; margin-bottom: 12px">
              Xoá thành viên này?
            </h2>
            <p
              style="
                font-size: 14px;
                color: var(--color-ink-soft);
                margin-bottom: 24px;
              "
            >
              Bạn có chắc muốn xoá
              <strong>{{ form.firstName }} {{ form.lastName }}</strong
              >? Thao tác này cũng sẽ gỡ liên kết cha/mẹ/con/vợ chồng liên quan.
            </p>
            <div class="form-actions" style="justify-content: flex-end">
              <button
                type="button"
                class="btn btn-outline"
                @click="modal.mode = 'edit'"
              >
                Hủy
              </button>
              <button
                type="button"
                class="btn btn-primary"
                style="background: var(--color-seal)"
                @click="confirmDelete"
              >
                Xác nhận xoá
              </button>
            </div>
          </template>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import * as f3 from "family-chart";
import "family-chart/styles/family-chart.css";

const chartEl = ref(null);
let f3Chart = null;

/* ================== DỮ LIỆU MẪU ==================
     Sau này thay bằng dữ liệu thật lấy từ GET /api/tree.
     Mỗi field tự do trong `data` — ở đây dùng đúng các
     trường đã thiết kế: first name, last name, gender,
     birthday, deathday, marital_status, education,
     hometown, notes.
  */
const treeData = reactive([
  {
    id: "1",
    data: {
      "first name": "Văn Tổ",
      "last name": "Nguyễn",
      gender: "M",
      birthday: "1900",
      deathday: "1975",
      marital_status: "Đã kết hôn",
      education: "",
      hometown: "Đông Bàn, Hải Dương",
      notes: "Khởi tổ dòng họ.",
    },
    rels: { spouses: ["2"], children: ["3", "4"] },
  },
  {
    id: "2",
    data: {
      "first name": "Thị Muội",
      "last name": "Trần",
      gender: "F",
      birthday: "1903",
      deathday: "1980",
      marital_status: "Đã kết hôn",
      education: "",
      hometown: "Hải Dương",
      notes: "",
    },
    rels: { spouses: ["1"], children: ["3", "4"] },
  },
  {
    id: "3",
    data: {
      "first name": "Văn An",
      "last name": "Nguyễn",
      gender: "M",
      birthday: "1928",
      deathday: "2005",
      marital_status: "Đã kết hôn",
      education: "",
      hometown: "Đông Bàn, Hải Dương",
      notes: "",
    },
    rels: { parents: ["1", "2"], spouses: ["5"], children: ["6", "7"] },
  },
  {
    id: "4",
    data: {
      "first name": "Thị Bình",
      "last name": "Nguyễn",
      gender: "F",
      birthday: "1931",
      deathday: "2010",
      marital_status: "Đã kết hôn",
      education: "",
      hometown: "Đông Bàn, Hải Dương",
      notes: "",
    },
    rels: { parents: ["1", "2"] },
  },
  {
    id: "5",
    data: {
      "first name": "Thị Gấm",
      "last name": "Lê",
      gender: "F",
      birthday: "1930",
      deathday: "2008",
      marital_status: "Đã kết hôn",
      education: "",
      hometown: "",
      notes: "",
    },
    rels: { spouses: ["3"], children: ["6", "7"] },
  },
  {
    id: "6",
    data: {
      "first name": "Văn Khoa",
      "last name": "Nguyễn",
      gender: "M",
      birthday: "1998",
      deathday: "",
      marital_status: "Độc thân",
      education: "Đại học Bách Khoa",
      hometown: "Hà Nội",
      notes: "",
    },
    rels: { parents: ["3", "5"] },
  },
  {
    id: "7",
    data: {
      "first name": "Thị Lan",
      "last name": "Nguyễn",
      gender: "F",
      birthday: "2001",
      deathday: "",
      marital_status: "Độc thân",
      education: "Đại học Ngoại Thương",
      hometown: "Hà Nội",
      notes: "",
    },
    rels: { parents: ["3", "5"] },
  },
]);

/* ================== STATE CỦA MODAL ================== */
const modal = reactive({
  open: false,
  mode: "edit", // 'edit' | 'add-child' | 'add-spouse' | 'confirm-delete'
  targetId: null, // id người đang sửa
  relativeOfId: null, // id người đang thêm quan hệ (khi thêm con/vợ chồng)
});

const form = reactive({
  firstName: "",
  lastName: "",
  gender: "M",
  maritalStatus: "Độc thân",
  birthday: "",
  deathday: "",
  education: "",
  hometown: "",
  notes: "",
});

const modalTitle = ref("");
const modalSubtitle = ref("");

function resetForm() {
  form.firstName = "";
  form.lastName = "";
  form.gender = "M";
  form.maritalStatus = "Độc thân";
  form.birthday = "";
  form.deathday = "";
  form.education = "";
  form.hometown = "";
  form.notes = "";
}

function fillFormFromPerson(person) {
  const d = person.data;
  form.firstName = d["first name"] || "";
  form.lastName = d["last name"] || "";
  form.gender = d.gender || "M";
  form.maritalStatus = d.marital_status || "Độc thân";
  form.birthday = d.birthday || "";
  form.deathday = d.deathday || "";
  form.education = d.education || "";
  form.hometown = d.hometown || "";
  form.notes = d.notes || "";
}

/* ================== MỞ MODAL: SỬA (do click vào thẻ) ================== */
function openEditModal(person) {
  modal.mode = "edit";
  modal.targetId = person.id;
  modal.relativeOfId = null;
  fillFormFromPerson(person);
  modalTitle.value = "Sửa thông tin thành viên";
  modalSubtitle.value = "Cập nhật thông tin cá nhân cho người này.";
  modal.open = true;
}

/* ================== MỞ MODAL: THÊM CON / VỢ-CHỒNG ================== */
function openAddModal(kind) {
  modal.mode = kind === "child" ? "add-child" : "add-spouse";
  modal.relativeOfId = modal.targetId;
  resetForm();
  modalTitle.value = kind === "child" ? "Thêm con" : "Thêm vợ/chồng";
  modalSubtitle.value =
    kind === "child"
      ? "Người mới sẽ được gán làm con của thành viên đang xem."
      : "Người mới sẽ được gán làm vợ/chồng của thành viên đang xem.";
  modal.open = true;
}

function closeModal() {
  modal.open = false;
}

/* ================== LƯU (SỬA hoặc THÊM MỚI) ================== */
function buildDataFromForm() {
  return {
    "first name": form.firstName,
    "last name": form.lastName,
    gender: form.gender,
    marital_status: form.maritalStatus,
    birthday: form.birthday,
    deathday: form.deathday,
    education: form.education,
    hometown: form.hometown,
    notes: form.notes,
  };
}

function nextId() {
  const maxId = treeData.reduce(
    (max, p) => Math.max(max, parseInt(p.id, 10) || 0),
    0,
  );
  return String(maxId + 1);
}

function saveModal() {
  if (modal.mode === "edit") {
    const person = treeData.find((p) => p.id === modal.targetId);
    if (person) person.data = buildDataFromForm();
  } else if (modal.mode === "add-child") {
    const parent = treeData.find((p) => p.id === modal.relativeOfId);
    const newId = nextId();
    const newPerson = {
      id: newId,
      data: buildDataFromForm(),
      rels: { parents: [modal.relativeOfId] },
    };
    // nếu cha/mẹ đang xem có vợ/chồng, gán luôn người kia làm phụ huynh thứ 2
    const spouseId = parent?.rels?.spouses?.[0];
    if (spouseId) newPerson.rels.parents.push(spouseId);
    treeData.push(newPerson);
    parent.rels.children = [...(parent.rels.children || []), newId];
    if (spouseId) {
      const spouse = treeData.find((p) => p.id === spouseId);
      if (spouse)
        spouse.rels.children = [...(spouse.rels.children || []), newId];
    }
  } else if (modal.mode === "add-spouse") {
    const person = treeData.find((p) => p.id === modal.relativeOfId);
    const newId = nextId();
    const newPerson = {
      id: newId,
      data: buildDataFromForm(),
      rels: { spouses: [modal.relativeOfId] },
    };
    treeData.push(newPerson);
    person.rels.spouses = [...(person.rels.spouses || []), newId];
  }

  refreshChart();
  closeModal();
}

/* ================== XOÁ ================== */
function askDelete() {
  modal.mode = "confirm-delete";
}

function confirmDelete() {
  const id = modal.targetId;
  const idx = treeData.findIndex((p) => p.id === id);
  if (idx === -1) return;

  // Gỡ liên kết ở tất cả người khác đang tham chiếu tới id này
  treeData.forEach((p) => {
    if (p.rels?.children)
      p.rels.children = p.rels.children.filter((c) => c !== id);
    if (p.rels?.spouses)
      p.rels.spouses = p.rels.spouses.filter((s) => s !== id);
    if (p.rels?.parents)
      p.rels.parents = p.rels.parents.filter((pr) => pr !== id);
  });
  treeData.splice(idx, 1);

  refreshChart();
  closeModal();
}

/* ================== KHỞI TẠO CHART ================== */
function refreshChart() {
  if (!f3Chart) return;
  f3Chart.updateData(treeData);
  f3Chart.updateTree({ tree_position: "inherit" });
}

onMounted(() => {
  f3Chart = f3
    .createChart(chartEl.value, treeData)
    .setTransitionTime(600)
    .setCardXSpacing(220)
    .setCardYSpacing(150);

  const f3Card = f3Chart
    .setCardHtml()
    .setCardDisplay([["first name", "last name"], ["birthday"]])
    .setStyle("imageCircle")
    .setMiniTree(true)
    .setOnHoverPathToMain();

  // Ghi đè hoàn toàn hành vi click mặc định của thư viện —
  // không dùng f3EditTree / modal mặc định nữa.
  f3Card.setOnCardClick((e, d) => {
    openEditModal(d.data);
  });

  f3Chart.updateTree({ initial: true });
});
</script>

<style scoped>
.tree-wrap {
  width: 100%;
}
#FamilyChart {
  width: 100%;
  height: 78vh;
  background: var(--color-bg);
  border: 1px solid var(--color-gold-soft);
  border-radius: 6px;
}

/* Card mặc định của family-chart -> phối theo theme giấy cổ */
:deep(.card) {
  background: var(--color-paper) !important;
  border: 2px solid var(--color-gold) !important;
  color: var(--color-ink) !important;
  font-family: var(--font-body) !important;
  border-radius: 6px !important;
}
:deep(.card-female) {
  border-color: var(--color-seal) !important;
}
:deep(.card_dim) {
  cursor: pointer;
}

/* ---------- Modal ---------- */
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
  max-width: 560px;
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
  line-height: 1;
}
.modal-close:hover {
  color: var(--color-seal);
}

.relation-actions {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-paper-line);
}
</style>
