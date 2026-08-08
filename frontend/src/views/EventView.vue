<template>
  <main id="main" class="section container" style="max-width: 1240px">
    <div class="tree-toolbar">
      <div>
        <span class="eyebrow">Lịch giỗ · họp mặt · thông báo</span>
        <h1 style="font-size: 28px">Sự kiện dòng họ</h1>
      </div>
      <button
        v-if="isAdmin"
        class="btn btn-primary"
        @click="showEventModal = true"
      >
        + Tạo sự kiện
      </button>
      <EventModal
        v-model:open="showEventModal"
        :persons="personOptions"
        @created="onEventCreated"
      />
    </div>

    <div v-if="loading" class="tree-status">Đang tải sự kiện...</div>
    <div v-else-if="loadError" class="tree-status tree-status-error">
      {{ loadError }}
      <button
        class="btn btn-outline"
        style="margin-left: 12px"
        @click="getEventInfos"
      >
        Thử lại
      </button>
    </div>

    <table v-else class="event-table paper">
      <thead>
        <tr>
          <th>Ngày tháng</th>
          <th>Loại</th>
          <th>Địa điểm</th>
          <th>Nội dung</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="eventInfos.length === 0">
          <td colspan="5" class="empty-cell">Chưa có sự kiện nào.</td>
        </tr>
        <tr
          v-for="event in eventInfos"
          :key="event.id"
          class="is-clickable"
          @click="goToDetail(event.id)"
        >
          <td>
            <div class="cell-date">{{ event.datetime }}</div>
            <div class="cell-date-lunar">{{ event.lunerDateTime }}(AL)</div>
          </td>
          <td>{{ event.type }}</td>
          <td>{{ event.location }}</td>
          <td>
            <div class="cell-title">{{ event.title }}</div>
            <div class="cell-desc">{{ event.description }}</div>
          </td>
        </tr>
      </tbody>
    </table>
  </main>
</template>

<script>
// Dữ liệu lấy từ API Flask (GET /api/events), danh sách thành viên lấy từ GET /family-tree
// để hiển thị dropdown "liên quan tới thành viên" trong EventModal.
import EventModal from "../components/EventModal.vue";
import { getAllEvent } from "../api/event.js";
import { getFamilyTree } from "../api/familyApi.js"; // TODO: chỉnh lại đúng đường dẫn/tên hàm nếu khác
import { authStore } from "../stores/auth.js";

export default {
  components: { EventModal },

  data() {
    return {
      eventInfos: [],
      loading: false,
      loadError: "",
      showEventModal: false,
      familyMembers: [], // [{ id, data, rels }, ...] lấy từ getFamilyTree()
      //   isAdmin: false,
    };
  },

  computed: {
    // Map sang { id, name } cho dropdown "Liên quan tới thành viên" trong EventModal
    personOptions() {
      return this.familyMembers.map((p) => ({
        id: p.id,
        name: `${p.data?.["first name"] || ""} ${p.data?.["last name"] || ""}`.trim(),
      }));
    },
    isAdmin() {
      return authStore.state.user?.role === "admin";
    },
  },

  mounted() {
    this.getEventInfos();
    this.getFamilyMembers();
  },

  methods: {
    async getEventInfos() {
      this.loading = true;
      this.loadError = "";
      try {
        const res = await getAllEvent();
        const payload = res.data;
        this.eventInfos = Array.isArray(payload)
          ? payload
          : payload.items || payload.data || [];
      } catch (error) {
        console.error("Load events error:", error);
        this.loadError = "Không thể tải danh sách sự kiện. Vui lòng thử lại.";
      } finally {
        this.loading = false;
      }
    },

    async getFamilyMembers() {
      try {
        const res = await getFamilyTree();
        const payload = res.data;
        this.familyMembers = Array.isArray(payload)
          ? payload
          : payload.items || payload.data || [];
      } catch (error) {
        console.error("Load family tree error:", error);
        // Không chặn trang sự kiện nếu lỗi phần này — chỉ dropdown "liên quan tới thành viên" sẽ trống
      }
    },

    // Được gọi khi EventModal tạo sự kiện thành công
    onEventCreated(event) {
      this.eventInfos.unshift(event);
    },

    // Tra tên thành viên theo personId, dùng khi backend không trả sẵn personName trong event
    getPersonName(personId) {
      if (!personId) return "";
      const person = this.familyMembers.find((p) => p.id === personId);
      if (!person) return "";
      return `${person.data?.["first name"] || ""} ${person.data?.["last name"] || ""}`.trim();
    },

    goToDetail(eventId) {
      this.$router.push(`/events/${eventId}`);
    },
  },
};
</script>
