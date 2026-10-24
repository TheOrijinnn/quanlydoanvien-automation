# 🚀 BỘ TOOL TỰ ĐỘNG HÓA QUẢN LÝ ĐOÀN VIÊN

Bộ công cụ tự động hóa toàn diện các nghiệp vụ trên cổng thông tin:  
🔗 [https://quanlydoanvien.doanthanhnien.vn](https://quanlydoanvien.doanthanhnien.vn)

---

## 🌟 CÁC GIAI ĐOẠN NGHIỆP VỤ TỰ ĐỘNG HÓA

1. **[Giai đoạn 1] Duyệt App & Rèn luyện đoàn viên:**  
   Quét & Duyệt đoàn viên từ App TNVN $\rightarrow$ Đăng ký rèn luyện (31 tiêu chí) $\rightarrow$ Chấm điểm tối đa (100/100) $\rightarrow$ Chuyển cấp trên $\rightarrow$ Đoàn cơ sở duyệt xác nhận $\rightarrow$ **🔍 Auto Double-Check CSDL rèn luyện**.
2. **[Giai đoạn 2] Nghiệp vụ Cấp thẻ đoàn viên:**  
   Tự động quét cả diện Cấp mới & Cấp lại thẻ (cho đoàn viên đã có thẻ từ cấp 3) $\rightarrow$ Lập tờ trình chuyển xử lý $\rightarrow$ Đoàn cơ sở duyệt và chuyển tiếp lên Đoàn trường $\rightarrow$ **🔍 Auto Double-Check số lượng thẻ**.
3. **[Giai đoạn 3] Đánh giá xếp loại đoàn viên:**  
   Tự động phân trang $\rightarrow$ Xếp loại "Hoàn thành xuất sắc nhiệm vụ" (100%) $\rightarrow$ Lưu & Gửi từng trang $\rightarrow$ Đoàn cơ sở duyệt nhận xét đánh giá $\rightarrow$ **🔍 Auto Double-Check tỷ lệ xuất sắc**.
4. **[Tùy chọn nhanh] Xử lý đơn lẻ cho 1 người (Chỉ cần Tên + Lớp):**  
   Tự động chạy trọn gói: Duyệt App (nếu đang chờ) $\rightarrow$ Rèn luyện 100đ $\rightarrow$ Cấp thẻ đoàn $\rightarrow$ Đánh giá xuất sắc.

---

## 📂 CẤU TRÚC THƯ MỤC GỌN GÀNG

```text
quanlydoanvien-automation/
│
├── SETUP_MOI_TRUONG.bat  # File 1-click tự động kiểm tra Python & cài đặt môi trường
├── MENU_LUA_CHON.bat     # Menu tương tác phân chia theo 4 giai đoạn logic
├── run.md                # Hướng dẫn chi tiết dành cho người dùng (low-tech)
├── README.md             # Tài liệu kỹ thuật chi tiết
│
└── src/                  # Toàn bộ mã nguồn & file kỹ thuật
    ├── config.py         # Cấu hình danh sách tài khoản, mật khẩu, năm, trọng số điểm
    ├── api_client.py     # Module kết nối API hệ thống (XSRF generator AES-PBKDF2, auto-retry)
    │
    ├── step0_duyet_app.py          # Bước 0: Quét & Duyệt đoàn viên từ App TNVN
    ├── step1_chidoan.py            # Bước 1: Chi đoàn đăng ký 31 TC & chấm 100đ rèn luyện
    ├── step2_co_so.py              # Bước 2: Đoàn cơ sở (yfie.hcmute) duyệt xác nhận rèn luyện
    │
    ├── step6_trinh_cap_the.py      # Bước 6: Chi đoàn trình Cấp mới & Cấp lại thẻ đoàn
    ├── step7_duyet_cap_the.py      # Bước 7: Đoàn cơ sở duyệt chuyển tiếp cấp thẻ lên Đoàn trường
    │
    ├── step4_danh_gia_doan_vien.py # Bước 4: Chi đoàn đánh giá xếp loại xuất sắc (ID=4)
    ├── step5_duyet_danh_gia.py     # Bước 5: Đoàn cơ sở duyệt nhận xét xếp loại đoàn viên
    │
    ├── double_check.py             # Module kiểm tra đối soát chéo số liệu từng bước (Double-Check)
    ├── step8_thong_ke_bao_cao.py   # Xuất báo cáo Dashboard & file JSON thống kê toàn diện
    │
    ├── xu_ly_mot_nguoi.py          # Xử lý đơn lẻ 1 người: Điền Tên + Lớp (Tự động All-in-One)
    ├── run_all.py                  # Chạy chuỗi toàn bộ tất cả nghiệp vụ tự động kèm Double-Check
    └── requirements.txt            # Thư viện phụ thuộc (`requests`, `cryptography`)
```

---

## 🛠️ HƯỚNG DẪN KHỞI CHẠY NHANH

1. Click đúp vào **`SETUP_MOI_TRUONG.bat`** để tự động chuẩn bị môi trường thư viện.
2. Click đúp vào **`MENU_LUA_CHON.bat`** để mở Menu điều khiển và chọn nghiệp vụ mong muốn.
