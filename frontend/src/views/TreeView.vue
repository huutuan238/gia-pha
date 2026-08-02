<script setup>
import FamilyChart from "./FamilyChart.vue";
</script>
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
        <!-- <div class="tree-toolbar">
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
            <input
              class="search-field"
              type="text"
              placeholder="Tìm theo tên thành viên…"
            />
          </div>
          <a href="them-thanh-vien.html" class="btn btn-primary btn-sm"
            >+ Thêm thành viên</a
          >
        </div> -->

        <div class="tree-wrap">
          <div class="tree">
            <FamilyChart />
          </div>
        </div>

        <div class="legend">
          <span
          ><span class="dot" style="background: rgb(120, 159, 172)"></span>Nam</span
          >
          <span
            ><span class="dot" style="background: rgb(196, 138, 146)"></span>Nữ</span
          >
          <span
          ><span class="dot" style="background: darkgray"></span>Đã mất</span
        >
        </div>
      </div>
    </section>
  </main>
</template>
