<template>
    <main id="main" class="section container" style="max-width: 720px">
      <button class="btn btn-ghost btn-sm back-btn" @click="goBack">← Quay lại danh sách</button>
  
      <div v-if="loading" class="tree-status">Đang tải sự kiện...</div>
  
      <div v-else-if="loadError" class="tree-status tree-status-error">
        {{ loadError }}
        <button class="btn btn-outline" style="margin-left:12px;" @click="getEventDetail">Thử lại</button>
      </div>
  
      <div v-else-if="event" class="card framed event-detail">
        <span class="corner tl"></span>
        <span class="corner tr"></span>
        <span class="corner bl"></span>
        <span class="corner br"></span>
  
        <span class="eyebrow event-type-badge">{{ event.type }}</span>
        <h1 class="event-detail-title">{{ event.title }}</h1>
  
        <div class="event-detail-grid">
          <div class="detail-item">
            <span class="detail-label">Ngày diễn ra</span>
            <span class="detail-value">{{ event.datetime }}</span>
            <span class="detail-sub" v-if="event.lunerDateTime">{{ event.lunerDateTime }} (Âm lịch)</span>
          </div>
  
          <div class="detail-item" v-if="personName">
            <span class="detail-label">Liên quan tới</span>
            <span class="detail-value">{{ personName }}</span>
          </div>
  
          <div class="detail-item" v-if="event.location">
            <span class="detail-label">Địa điểm</span>
            <span class="detail-value">{{ event.location }}</span>
          </div>
        </div>
  
        <hr class="rule" v-if="event.description" />
  
        <div v-if="event.description" class="detail-note">
          <span class="detail-label">Ghi chú</span>
          <p>{{ event.description || event.note }}</p>
        </div>
  
        <div class="detail-actions">
          <button class="btn btn-outline" @click="goBack">Đóng</button>
          <button class="delete-btn" @click="onDelete" :disabled="deleting">
            {{ deleting ? "Đang xoá..." : "Xoá sự kiện" }}
          </button>
        </div>
  
        <p v-if="deleteError" class="modal-error">{{ deleteError }}</p>
      </div>
    </main>
  </template>
  
  <script>
  import { getEventById, deleteEvent } from "../api/event.js";
  import { getFamilyTree } from "../api/familyApi.js"; // TODO: chỉnh lại đúng đường dẫn nếu khác
  
  export default {
    data() {
      return {
        event: null,
        loading: false,
        loadError: "",
        familyMembers: [],
        deleting: false,
        deleteError: "",
      };
    },
  
    computed: {
      personName() {
        if (!this.event) return "";
        if (this.event.personName) return this.event.personName;
        const person = this.familyMembers.find((p) => p.id === this.event.personId);
        if (!person) return "";
        return `${person.data?.["first name"] || ""} ${person.data?.["last name"] || ""}`.trim();
      },
    },
  
    mounted() {
      this.getEventDetail();
    //   this.getFamilyMembers();
    },
  
    methods: {
      async getEventDetail() {
        this.loading = true;
        this.loadError = "";
        try {
          const res = await getEventById(this.$route.params.id);
          this.event = res.data;
        } catch (error) {
          console.error("Load event detail error:", error);
          this.loadError = "Không thể tải sự kiện. Vui lòng thử lại.";
        } finally {
          this.loading = false;
        }
      },
  
      async getFamilyMembers() {
        try {
          const res = await getFamilyTree();
          const payload = res.data;
          this.familyMembers = Array.isArray(payload) ? payload : (payload.items || payload.data || []);
        } catch (error) {
          console.error("Load family tree error:", error);
        }
      },
  
      async onDelete() {
        if (!confirm("Xoá sự kiện này?")) return;
        this.deleting = true;
        this.deleteError = "";
        try {
          await deleteEvent(this.$route.params.id);
          this.goBack();
        } catch (error) {
          console.error("Xoá sự kiện thất bại:", error);
          this.deleteError = error?.response?.data?.message || "Không thể xoá sự kiện. Vui lòng thử lại.";
          this.deleting = false;
        }
      },
  
      goBack() {
        this.$router.push("/events");
      },
    },
  };
  </script>
  
  <style scoped>
  .back-btn {
    margin-bottom: var(--space-3);
    padding-left: 0;
  }
  
  .event-detail {
    padding: var(--space-4);
    position: relative;
  }
  
  .event-type-badge {
    margin-bottom: var(--space-1);
  }
  
  .event-detail-title {
    margin-bottom: var(--space-3);
  }
  
  .event-detail-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--space-3);
    margin-bottom: var(--space-2);
  }
  
  .detail-item {
    display: flex;
    flex-direction: column;
  }
  .detail-label {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--ink-soft);
    margin-bottom: 0.3rem;
  }
  .detail-value {
    font-family: var(--font-display);
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--ink);
  }
  .detail-sub {
    font-size: 0.8rem;
    color: var(--ink-soft);
    margin-top: 0.2rem;
  }
  
  .detail-note p {
    margin-top: 0.4rem;
    color: var(--ink);
  }
  
  .detail-actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    margin-top: var(--space-3);
    padding-top: var(--space-3);
    border-top: 1px solid var(--line);
  }
  
  .delete-btn {
    padding: 0.75rem 1.4rem;
    background: transparent;
    border: 1px solid var(--lacquer);
    color: var(--lacquer);
    border-radius: var(--radius);
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s ease;
  }
  .delete-btn:hover { background: rgba(156, 43, 32, 0.08); }
  .delete-btn:disabled { opacity: 0.6; cursor: not-allowed; }
  
  .modal-error {
    margin-top: 12px;
    font-size: 13px;
    color: var(--lacquer);
    text-align: right;
  }
  
  @media (max-width: 600px) {
    .event-detail-grid {
      grid-template-columns: 1fr;
    }
  }
  </style>