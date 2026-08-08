<template>
  <main>
    <section class="hero">
      <div class="container hero-inner">
        <span class="seal" aria-hidden="true">
          <svg viewBox="0 0 40 40">
            <circle
              cx="20"
              cy="20"
              r="18.5"
              fill="none"
              stroke="currentColor"
              stroke-width="1.6"
            />
            <path
              d="M20 29 V15 M20 15 L13.5 8.5 M20 15 L26.5 8.5 M14.5 21 L20 15 L25.5 21"
              stroke="currentColor"
              stroke-width="1.6"
              fill="none"
              stroke-linecap="round"
            />
          </svg>
        </span>
        <span class="eyebrow">Từ đường trực tuyến</span>
        <h1>Gìn giữ cội nguồn,<br />nối tiếp truyền thống.</h1>
        <p class="lede">
          Nơi lưu giữ gia phả, hình ảnh và sự kiện của Họ Nguyễn Hữu qua các đời
          — để con cháu dù ở đâu cũng tìm về được gốc rễ của mình.
        </p>
        <div class="hero-actions">
          <RouterLink to="/gia-pha" class="btn btn-primary"
            >Xem cây gia phả</RouterLink
          >
        </div>
      </div>
    </section>

    <section>
      <div class="container">
        <div class="story-grid is-stacked">
          <div class="story-plate framed">
            <span class="corner tl"></span><span class="corner tr"></span>
            <span class="corner bl"></span><span class="corner br"></span>
            <img
              src="../assets/nha-tho-to.jpg"
              alt="Nhà thờ tổ Họ Nguyễn"
              class="story-plate-img"
            />
          </div>
          <div>
            <span class="eyebrow">Lịch sử dòng họ</span>
            <h2>Nguồn gốc từ xã Mỹ Thành</h2>
            <p>{{ familyInfo.description }}</p>
            <a href="#dieu-huong" class="btn btn-gold btn-sm">Khám phá thêm</a>
          </div>
        </div>
      </div>
    </section>

    <section>
      <div class="container">
        <div class="gen-strip">
          <div class="gen-item">
            <span class="num">{{ familyInfo.max_generation }}</span
            ><span class="label">Đời đã ghi nhận</span>
          </div>
          <div class="gen-item">
            <span class="num">{{ familyInfo.count_person }}</span
            ><span class="label">Con cháu</span>
          </div>
          <div class="gen-item">
            <span class="num">{{ familyInfo.branch_number }}</span
            ><span class="label">Chi lớn</span>
          </div>
          <div class="gen-item">
            <span class="num">{{ familyInfo.start_year }}</span
            ><span class="label">Năm lập tổ</span>
          </div>
        </div>
      </div>
    </section>
    <section>
      <div class="container">
        <span class="eyebrow">Giới thiệu</span>
        <h2>Video giới thiệu dòng họ</h2>
        <p class="lede" style="max-width: 60ch">
          Vài nét về lịch sử và truyền thống của dòng họ qua video giới thiệu.
        </p>

        <div class="video-wrap paper">
          <iframe
            :src="`https://www.youtube.com/embed/rf-zO7gcZUY`"
            title="Video giới thiệu dòng họ"
            frameborder="0"
            allow="
              accelerometer;
              autoplay;
              clipboard-write;
              encrypted-media;
              gyroscope;
              picture-in-picture;
              web-share;
            "
            referrerpolicy="strict-origin-when-cross-origin"
            allowfullscreen
          ></iframe>
        </div>
      </div>
    </section>
    <section id="dieu-huong">
      <div class="container">
        <div class="section-head">
          <span class="eyebrow">Điều hướng nhanh</span>
          <h2>Bắt đầu từ đâu</h2>
        </div>
        <div class="nav-grid">
          <RouterLink class="nav-card" to="/gia-pha">
            <span class="idx">01 — Xem gia phả</span>
            <h3>Cây phả hệ</h3>
            <p>
              Duyệt sơ đồ các thế hệ, mở rộng theo từng chi nhánh và xem chi
              tiết từng thành viên.
            </p>
          </RouterLink>
          <RouterLink class="nav-card" to="/gia-pha">
            <span class="idx">02 — Cập nhật</span>
            <h3>Thêm thành viên</h3>
            <p>
              Nhập thông tin thành viên mới và gán quan hệ cha mẹ – con vào cây
              gia phả.
            </p>
          </RouterLink>
          <RouterLink class="nav-card" to="/events">
            <span class="idx">03 — Sự kiện</span>
            <h3>Giỗ &amp; họp mặt</h3>
            <p>
              Theo dõi ngày giỗ, họp mặt dòng họ và nhận thông báo khi có sự
              kiện mới.
            </p>
          </RouterLink>
          <RouterLink class="nav-card" to="/albums">
            <span class="idx">04 — Album ảnh</span>
            <h3>Ảnh</h3>
            <p>Theo dõi hình ảnh của tất cả các sự kiện</p>
          </RouterLink>
        </div>
      </div>
    </section>
  </main>
</template>

<script>
import { getFamilyInfo } from "../api/familyApi";
export default {
  data() {
    return {
      familyInfo: {},
    };
  },

  mounted() {
    this.getFamilyInfo();
  },

  methods: {
    async getFamilyInfo() {
      try {
        const res = await getFamilyInfo("8b6c4f0e-7f3a-4d8e-9a61-2e7b5c9d1f20");
        this.familyInfo = res.data;
      } catch (error) {
        console.error("Load family tree error:", error);
      }
    },
  },
};
</script>

<style scoped>
.story-grid.is-stacked {
  grid-template-columns: 1fr;
}

.story-plate {
  aspect-ratio: 16/9;
  overflow: hidden;
  padding: 0;
}

.story-plate-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.video-wrap {
  position: relative;
  width: 100%;
  max-width: 860px;
  margin-top: 24px;
  padding: 0;
  overflow: hidden;
  border-radius: 12px;
  /* tỉ lệ 16:9 */
  aspect-ratio: 16 / 9;
}
.video-wrap iframe {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
}
</style>
