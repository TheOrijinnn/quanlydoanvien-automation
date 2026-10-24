# 🚀 BỘ TOOL TỰ ĐỘNG HÓA QUẢN LÝ ĐOÀN VIÊN

Bộ công cụ tự động hóa toàn diện 3 nghiệp vụ lớn trên cổng thông tin:  
🔗 [https://quanlydoanvien.doanthanhnien.vn](https://quanlydoanvien.doanthanhnien.vn)

1. **Chương trình rèn luyện đoàn viên:** Đăng ký rèn luyện $\rightarrow$ Tự chấm điểm tối đa (100/100) $\rightarrow$ Chuyển cấp trên $\rightarrow$ Đoàn cơ sở duyệt 56 trang $\rightarrow$ Đối soát báo cáo.
2. **Nghiệp vụ Đánh giá đoàn viên:** Tự động phân trang $\rightarrow$ Xếp loại "Hoàn thành xuất sắc nhiệm vụ" (100%) $\rightarrow$ Lưu & Gửi từng trang $\rightarrow$ **Auto Double-Check kiểm tra 100% đoàn viên** $\rightarrow$ Đoàn cơ sở duyệt nhận xét đánh giá.
3. **Nghiệp vụ Cấp thẻ đoàn viên:** Tự động chọn tất cả đoàn viên chưa có thẻ $\rightarrow$ Trình "Cấp mới thẻ đoàn viên" $\rightarrow$ **Auto Double-Check xác nhận lịch sử** $\rightarrow$ Đoàn cơ sở duyệt xử lý cấp thẻ lên cấp trên.
4. **Hệ thống Double-Check & Thống kê toàn diện:** Tính năng tự động đối soát chéo số liệu giữa Rèn luyện và Đánh giá (báo cáo ngay lập tức nếu lệch cột tổng số đoàn viên) + Tùy chọn xuất dashboard & file JSON thống kê tổng thể toàn khoa.

---

## 📂 CẤU TRÚC THƯ MỤC GỌN GÀNG

```text
quanlydoanvien-automation/
│
├── CHAY_TU_DONG.bat      # File chạy tự động toàn bộ 1-click (tự check Python, tự cài thư viện)
├── MENU_LUA_CHON.bat     # Menu tương tác chọn chạy từng nghiệp vụ riêng biệt
├── run.md                # Hướng dẫn chi tiết dành riêng cho người không rành kỹ thuật (low-tech)
├── README.md             # Tài liệu kỹ thuật chi tiết
│
└── src/                  # Toàn bộ mã nguồn & file kỹ thuật được gom gọn vào đây
    ├── config.py         # File cấu hình: 73 tài khoản, tài khoản admin yfie.hcmute, mật khẩu, năm
    ├── api_client.py     # Module kết nối API hệ thống (XSRF generator AES-PBKDF2, auto-retry, token manager)
    │
    │   --- Nghiệp vụ 1: Rèn luyện đoàn viên ---
    ├── step1_chidoan.py  # Bước 1: 73 Chi đoàn đăng ký, chấm 100đ, chuyển cấp trên
    ├── step2_co_so.py    # Bước 2: Đoàn cơ sở (yfie.hcmute) duyệt toàn bộ 56 trang xác nhận
    ├── step3_audit.py    # Bước 3: Đối soát đa luồng kiểm tra 100% hoàn thành & xuất audit_report.json
    │
    │   --- Nghiệp vụ 2: Đánh giá đoàn viên ---
    ├── step4_danh_gia_doan_vien.py # Bước 4: Đánh giá xếp loại xuất sắc (ID=4), lưu & gửi từng trang
    ├── step5_duyet_danh_gia.py     # Bước 5: Đoàn cơ sở duyệt nhận xét đánh giá (chỉ duyệt hàng gửi, không đánh giá lại)
    │
    │   --- Nghiệp vụ 3: Cấp thẻ đoàn viên ---
    ├── step6_trinh_cap_the.py      # Bước 6: Chi đoàn trình cấp mới thẻ (chọn toàn bộ đoàn viên chưa cấp thẻ)
    ├── step7_duyet_cap_the.py      # Bước 7: Đoàn cơ sở duyệt xử lý cấp thẻ chuyển tiếp cấp trên
    │
    │   --- Bổ sung: Thống kê & Double-Check toàn diện ---
    ├── step8_thong_ke_bao_cao.py   # Bước 8: Tùy chọn xuất thống kê Dashboard & Auto Double-Check đối soát chéo
    │
    │   --- Tính năng nhanh cho 1 đoàn viên mới thêm ---
    ├── xu_ly_mot_nguoi.py          # Xử lý đơn lẻ 1 người: Điền Tên + MSSV + Lớp (Tự động Đánh giá & Cấp thẻ)
    │
    ├── run_all.py        # Script chạy chuỗi toàn bộ tất cả nghiệp vụ tự động (kèm Auto Double-Check)
    ├── requirements.txt  # Thư viện phụ thuộc (`requests`, `cryptography`)
    ├── audit_report.json # File báo cáo kết quả đối soát chi tiết
    └── bao_cao_thong_ke_toan_khoa.json # File JSON xuất số liệu thống kê toàn khoa
```

---

## 🛠️ YÊU CẦU & CÀI ĐẶT

### Chạy bằng file `.bat` (Khuyên dùng)
- Máy tính cần có Python 3.8+ (khi cài nhớ tích chọn `Add python.exe to PATH`).
- Click đúp vào **`MENU_LUA_CHON.bat`** để mở Menu điều khiển trực quan:
  * `[1]` Bước 1: Chi đoàn đăng ký & chấm điểm rèn luyện
  * `[2]` Bước 2: Đoàn cơ sở xác nhận duyệt rèn luyện
  * `[3]` Bước 3: Đối soát tiến độ rèn luyện
  * `[4]` Bước 4: Chi đoàn đánh giá đoàn viên xuất sắc 100% (Auto Double-Check)
  * `[5]` Bước 5: Đoàn cơ sở duyệt đánh giá đoàn viên (Auto Double-Check)
  * `[6]` Bước 6: Chi đoàn trình cấp mới thẻ đoàn viên (Auto Double-Check)
  * `[7]` Bước 7: Đoàn cơ sở duyệt cấp thẻ đoàn viên (Auto Double-Check)
  * `[8]` Tùy chọn: Thống kê & Xuất báo cáo tổng hợp toàn khoa
  * `[9]` Tùy chọn: Chạy kiểm tra & Đối soát chéo số liệu (Double-Check Audit)
  * `[10]` CHẠY TẤT CẢ CÁC BƯỚC TỰ ĐỘNG (Bao gồm Auto Double-Check toàn diện)
  * `[11]` Xử lý đơn lẻ 1 người: Điền Tên + MSSV + Lớp (Tự động Đánh giá & Cấp thẻ)
  * `[0]` Thoát
- Hoặc click đúp vào **`CHAY_TU_DONG.bat`** để chạy từ đầu đến cuối một mạch.

---

## 💡 CÁC ĐẶC BIỆT LƯU Ý ĐÃ ĐƯỢC XỬ LÝ SẴN TRONG CODE (Gotchas)

1. **Bảo mật XSRF Token nâng cao:**  
   Các API REST `/ws/api/...` của cổng thông tin yêu cầu header `X-XSRF-TOKEN` được mã hóa lồng nhau qua AES-CBC với khóa PBKDF2 HMAC-SHA1 dựa trên JWT token, URL và nội dung Body/FormData. `api_client.py` đã giải mã và tích hợp bộ sinh token chuẩn 100%.
2. **Cơ chế phân trang & Lưu trạng thái Đánh giá đoàn viên:**  
   Khi chuyển trang trên giao diện web, dữ liệu trang trước sẽ bị mất nếu chưa bấm Lưu. Tool tự động lặp qua từng trang (50 đoàn viên/trang), gọi `updateDanhGia` (Lưu) rồi gọi `sendDanhGia` (Gửi) cho từng trang độc lập.
3. **An toàn dữ liệu khi Duyệt nhận xét đánh giá:**  
   Code cam kết **chỉ bấm Duyệt** cho các Chi đoàn có trạng thái `TRANGTHAI = 1` ("Đã gửi danh sách đánh giá"), **tuyệt đối bỏ qua** và không bấm "Đánh giá lại" với các hàng đã duyệt (`TRANGTHAI = 2`).
4. **Loại trừ các Chi đoàn đã cấp thẻ:**  
   Khi trình cấp thẻ (`step6_trinh_cap_the.py`), hệ thống tự động kiểm tra lịch sử và danh sách ngoại lệ các Chi đoàn đã xử lý từ trước để tránh tạo trùng lặp yêu cầu.
5. **Tự động chia cụm & Gia hạn Token:**  
   Tự động chia cụm 5 đoàn viên/lần gửi để tránh lỗi tràn bộ nhớ Oracle (ORA-01403) và tự động đăng nhập lại khi token hết hạn.
