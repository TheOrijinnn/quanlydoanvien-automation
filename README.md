# 🚀 BỘ TOOL TỰ ĐỘNG HÓA CHƯƠNG TRÌNH RÈN LUYỆN ĐOÀN VIÊN

Bộ công cụ tự động hóa toàn bộ quy trình **Đăng ký rèn luyện**, **Đánh giá rèn luyện (chấm 100/100 điểm)** và **Duyệt xác nhận cấp Đoàn cơ sở** trên cổng thông tin:  
🔗 [https://quanlydoanvien.doanthanhnien.vn](https://quanlydoanvien.doanthanhnien.vn)

---

## 📂 CẤU TRÚC THƯ MỤC GỌN GÀNG

```text
quanlydoanvien-automation/
│
├── CHAY_TU_DONG.exe      # File chạy độc lập 1-click (Zero install - Không cần cài Python)
├── CHAY_TU_DONG.bat      # File chạy tự động (Tự check Python, tự cài thư viện và chạy)
├── MENU_LUA_CHON.bat     # File menu điều khiển chọn chạy từng bước riêng
├── run.md                # Hướng dẫn chi tiết dành riêng cho người không rành kỹ thuật (low-tech)
├── README.md             # Tài liệu kỹ thuật
│
└── src/                  # Toàn bộ mã nguồn & file kỹ thuật được gom gọn vào đây
    ├── config.py         # File cấu hình: 73 tài khoản, tài khoản cơ sở, mật khẩu, năm, barem điểm
    ├── api_client.py     # Module kết nối API hệ thống (tự động lấy token, tự động retry)
    ├── step1_chidoan.py  # BƯỚC 1: Xử lý 73 Chi đoàn (Đăng ký, chấm 100đ, chuyển cấp trên)
    ├── step2_co_so.py    # BƯỚC 2: Cấp Đoàn cơ sở (yfie.hcmute) duyệt toàn bộ các trang
    ├── step3_audit.py    # BƯỚC 3: Đối soát đa luồng kiểm tra 100% hoàn thành & xuất báo cáo
    ├── run_all.py        # Script chạy tuần tự cả 3 bước
    ├── requirements.txt  # Thư viện phụ thuộc (`requests`)
    └── audit_report.json # File báo cáo kết quả đối soát chi tiết
```

---

## 🛠️ YÊU CẦU & CÀI ĐẶT

### Cách 1: Chạy trực tiếp `CHAY_TU_DONG.exe` (Khuyên dùng)
- Click đúp vào `CHAY_TU_DONG.exe`. Không cần cài thêm bất kỳ phần mềm nào khác!

### Cách 2: Chạy file `.bat`
- Máy tính cần có Python 3.8+ (tích chọn `Add python.exe to PATH`).
- Click đúp vào `CHAY_TU_DONG.bat` để chạy toàn bộ.
- Hoặc click đúp `MENU_LUA_CHON.bat` để chọn chạy từng bước.

---

## 💡 CÁC ĐẶC BIỆT LƯU Ý ĐÃ ĐƯỢC XỬ LÝ SẴN TRONG CODE (Gotchas)

1. **Giới hạn số lượng đăng ký 1 lần (Oracle ORA-01403):**  
   Hệ thống Quản lý đoàn viên sẽ báo lỗi nếu gửi đăng ký > 10 đoàn viên trong 1 request. Trong `step1_chidoan.py` đã cài đặt cơ chế **tự động chia cụm 5 đoàn viên/lần gửi**, đảm bảo 100% không bao giờ bị nghẽn hay lỗi backend.
2. **Mã hóa ID động theo phiên (Dynamic Encrypted IDs):**  
   Mỗi lần đăng nhập, mã chương trình và mã tiêu chí sẽ được hash ngẫu nhiên. Code đã tự động gọi `ndv05.dangky.ctrl_cauhinh` để bóc tách ID động cho từng phiên.
3. **Tự động gia hạn Token:**  
   Nếu token bị hết hạn giữa chừng (401 Unauthorized), `api_client.py` sẽ tự động đăng nhập lại và thực thi tiếp tục mà không làm gián đoạn tiến trình.
4. **Lọc bản ghi trùng lặp trong cơ sở dữ liệu:**  
   Bộ lọc thông minh theo mã sinh viên duy nhất (`id`) giúp loại bỏ các hồ sơ rác/trùng lặp do trường nạp dữ liệu.
