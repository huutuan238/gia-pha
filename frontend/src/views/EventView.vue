<template>
    <main id="main" class="section container" style="max-width:840px;">
      <div class="tree-toolbar">
        <div>
          <span class="eyebrow">Lịch giỗ · họp mặt · thông báo</span>
          <h1 style="font-size:28px;">Sự kiện dòng họ</h1>
        </div>
        <a href="#" class="btn btn-primary">+ Tạo sự kiện</a>
      </div>
  
      <div class="event-list">
        <div class="paper event-row" v-for="event in events" :key="event.id">
          <div class="event-date">
            <span class="d">{{ event.day }}</span>
            <span class="m">{{ event.month }}</span>
          </div>
          <div class="event-body">
            <h3>{{ event.title }}</h3>
            <p>{{ event.description }}</p>
          </div>
          <div class="event-meta">
            <span
              class="badge-notify"
              :style="event.notified ? '' : 'background:var(--color-gold); color:var(--color-ink);'"
            >
              {{ event.notified ? 'Đã gửi thông báo' : 'Sắp diễn ra' }}
            </span>
            <span>{{ event.notified ? `${event.recipients} người nhận` : 'Chưa gửi' }}</span>
          </div>
        </div>
      </div>
    </main>
  </template>
  
  <script setup>
  // Dữ liệu tĩnh khai báo ngay trong component.
  // Sau này sẽ thay bằng dữ liệu lấy từ API Flask (GET /api/events).
  import { reactive } from 'vue'
  
  const events = reactive([
    {
      id: 1,
      day: '12',
      month: 'Th.08',
      title: 'Giỗ tổ họ Nguyễn — đời thứ nhất',
      description: 'Tổ chức tại nhà thờ họ, làng Đông Bàn. Con cháu các chi tề tựu dâng hương.',
      notified: true,
      recipients: 128,
    },
    {
      id: 2,
      day: '03',
      month: 'Th.09',
      title: 'Họp mặt con cháu chi thứ 3',
      description: 'Gặp mặt thường niên, cập nhật gia phả và ảnh của các gia đình trong chi.',
      notified: true,
      recipients: 46,
    },
    {
      id: 3,
      day: '21',
      month: 'Th.10',
      title: 'Sinh nhật cụ Nguyễn Văn Khoa (đời 7)',
      description: 'Nhắc nhở gửi lời chúc mừng đến thành viên.',
      notified: false,
      recipients: 0,
    },
  ])
  </script>