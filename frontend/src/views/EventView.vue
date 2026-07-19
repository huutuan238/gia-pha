<template>
  <main id="main" class="section container" style="max-width: 840px">
    <div class="tree-toolbar">
      <div>
        <span class="eyebrow">Lịch giỗ · họp mặt · thông báo</span>
        <h1 style="font-size: 28px">Sự kiện dòng họ</h1>
      </div>
      <button class="btn btn-primary" @click="showEventModal = true">+ Tạo sự kiện</button>
      <EventModal
        v-model:open="showEventModal"
        :persons="personOptions"
        @created="onEventCreated"
        />
    </div>

    <div class="event-list">
      <div class="paper event-row" v-for="event in events" :key="event.id">
        <div class="event-date">
            <h3>{{ event.datetime }}</h3>
            <p>{{ event.lunerDateTime }}(AL)</p>
        </div>
        <div class="event-body">
          <h3>{{ event.title }}</h3>
          <p>{{ event.description }}</p>
        </div>
        <div class="event-meta">
          <span
            class="badge-notify"
            :style="
              event.notified
                ? ''
                : 'background:var(--color-gold); color:var(--color-ink);'
            "
          >
            {{ event.notified ? "Đã gửi thông báo" : "Sắp diễn ra" }}
          </span>
          <span>{{
            event.notified ? `${event.recipients} người nhận` : "Chưa gửi"
          }}</span>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup>
// Dữ liệu tĩnh khai báo ngay trong component.
// Sau này sẽ thay bằng dữ liệu lấy từ API Flask (GET /api/events).
import { reactive } from "vue";
import { ref, computed } from 'vue'
import EventModal from '../components/EventModal.vue'

const showEventModal = ref(false)

const events = reactive([
  {
    id: 1,
    datetime: "2024-12-21 08:00",
    lunerDateTime: "2024-11-21",
    title: "Giỗ tổ và Khánh thành nhà thờ",
    description:
      "Tổ chức lễ khánh thành, văn nghệ,tế tổ và dâng hương",
    notified: true,
    recipients: 128
  },
  {
    id: 2,
    datetime: "2024-12-21 08:00",
    lunerDateTime: "2024-11-21",
    title: "Họ đông chí",
    description:
      "Gặp mặt thường niên, cập nhật gia phả và ảnh của các gia đình trong chi.",
    notified: true,
    recipients: 46,
  },
  {
    id: 3,
    datetime: "2024-12-21 08:00",
    lunerDateTime: "2024-11-21",
    title: "Đón giao thừa",
    description: "Nhắc nhở gửi lời chúc mừng đến thành viên.",
    notified: false,
    recipients: 0,
  },
  {
    id: 4,
    datetime: "2024-12-21 08:00",
    lunerDateTime: "2024-11-21",
    title: "Đón giao thừa",
    description: "Nhắc nhở gửi lời chúc mừng đến thành viên.",
    notified: false,
    recipients: 0,
  },
  {
    id: 4,
    datetime: "2024-12-21 08:00",
    lunerDateTime: "2024-11-21",
    title: "Đón giao thừa",
    description: "Nhắc nhở gửi lời chúc mừng đến thành viên.",
    notified: false,
    recipients: 0,
  },
]);
</script>
