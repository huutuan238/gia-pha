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
          Nơi lưu giữ gia phả, hình ảnh và sự kiện của Họ Nguyễn qua các đời —
          để con cháu dù ở đâu cũng tìm về được gốc rễ của mình.
        </p>
        <div class="hero-actions">
          <a href="gia-pha.html" class="btn btn-primary">Xem cây gia phả</a>
          <a href="them-thanh-vien.html" class="btn btn-ghost"
            >Thêm thành viên mới</a
          >
        </div>
      </div>
    </section>

    <section>
      <div class="container">
        <div class="story-grid">
          <div>
            <span class="eyebrow">Lịch sử dòng họ</span>
            <h2>Nguồn gốc từ làng Vân Cốc</h2>
            <p>
              Theo gia phả cổ còn lưu tại từ đường, thủy tổ Họ Nguyễn di cư từ
              vùng Sơn Nam đến định cư tại làng Vân Cốc vào khoảng đầu thế kỷ
              18. Trải qua hơn mười đời, con cháu dòng họ đã tỏa ra nhiều chi
              nhánh, từ Bắc chí Nam, nhưng vẫn giữ lệ về chầu tổ vào dịp giỗ họ
              hằng năm.
            </p>
            <p>
              Dòng họ có truyền thống hiếu học và nhiều đời làm nghề dạy chữ,
              bốc thuốc. Nhà thờ họ hiện đặt tại quê gốc, nơi lưu giữ sắc phong,
              bài vị và cuốn gia phả chép tay được xem là báu vật của dòng tộc.
            </p>
            <a href="#dieu-huong" class="btn btn-gold btn-sm">Khám phá thêm</a>
          </div>
          <div class="story-plate framed">
            <span class="corner tl"></span><span class="corner tr"></span>
            <span class="corner bl"></span><span class="corner br"></span>
            <span class="seal" aria-hidden="true">
              <svg viewBox="0 0 40 40">
                <circle
                  cx="20"
                  cy="20"
                  r="18.5"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="1.2"
                />
                <path
                  d="M20 29 V15 M20 15 L13.5 8.5 M20 15 L26.5 8.5 M14.5 21 L20 15 L25.5 21"
                  stroke="currentColor"
                  stroke-width="1.2"
                  fill="none"
                  stroke-linecap="round"
                />
              </svg>
            </span>
          </div>
        </div>
      </div>
    </section>

    <section>
      <div class="container">
        <div class="gen-strip">
          <div class="gen-item">
            <span class="num">12</span
            ><span class="label">Đời đã ghi nhận</span>
          </div>
          <div class="gen-item">
            <span class="num">238</span><span class="label">Thành viên</span>
          </div>
          <div class="gen-item">
            <span class="num">6</span><span class="label">Chi nhánh</span>
          </div>
          <div class="gen-item">
            <span class="num">1728</span><span class="label">Năm lập tổ</span>
          </div>
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
          <RouterLink class="nav-card" o="/gia-pha">
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
          <RouterLink class="nav-card" to="/event">
            <span class="idx">03 — Sự kiện</span>
            <h3>Giỗ &amp; họp mặt</h3>
            <p>
              Theo dõi ngày giỗ, họp mặt dòng họ và nhận thông báo khi có sự
              kiện mới.
            </p>
          </RouterLink>
          <RouterLink class="nav-card" to="/event">
            <span class="idx">04 — Album ảnh</span>
            <h3>Ảnh</h3>
            <p>Theo dõi hình ảnh của tất cả các sự kiện</p>
          </RouterLink>
        </div>
      </div>
    </section>
  </main>
</template>
