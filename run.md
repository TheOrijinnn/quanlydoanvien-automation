# 📖 HƯỚNG DẪN DÀNH CHO NGƯỜI MỚI (LOW-TECH)

Tài liệu này được viết theo cách **đơn giản nhất**, ai cũng có thể làm được chỉ với **1 cú click chuột**, không cần biết lập trình hay gõ lệnh phức tạp.

---

## ⚡ CÁCH CHẠY (CHỌN 1 TRONG 2 CÁCH):

### Cách 1: Dùng Menu điều khiển trực quan (Khuyên dùng)
👉 **Click đúp chuột vào:** **`MENU_LUA_CHON.bat`**  

Màn hình đen sẽ hiện ra Menu với các con số rất dễ chọn:
* Nhập **`1`** rồi Enter: Chạy tự động rèn luyện cho các Chi đoàn (đăng ký, chấm 100đ, chuyển cấp trên).
* Nhập **`2`** rồi Enter: Đoàn cơ sở (admin `yfie.hcmute`) duyệt 56 trang rèn luyện.
* Nhập **`3`** rồi Enter: Kiểm tra đối soát tiến độ rèn luyện (xem còn ai thiếu không).
* Nhập **`4`** rồi Enter: Đánh giá xếp loại đoàn viên xuất sắc 100% (tự động phân trang, lưu & gửi).
* Nhập **`5`** rồi Enter: Đoàn cơ sở duyệt nhận xét đánh giá đoàn viên.
* Nhập **`6`** rồi Enter: Các Chi đoàn trình cấp mới thẻ đoàn viên (chọn toàn bộ đoàn viên).
* Nhập **`7`** rồi Enter: Đoàn cơ sở duyệt cấp thẻ đoàn viên.
* Nhập **`8`** rồi Enter: **Thống kê & Báo cáo số liệu toàn diện** (xem tổng số đoàn viên, tỷ lệ hoàn thành, xuất file JSON).
* Nhập **`9`** rồi Enter: **Chạy Double-Check kiểm tra & đối soát chéo** (so sánh số liệu giữa các nghiệp vụ).
* Nhập **`10`** rồi Enter: **CHẠY TẤT CẢ** các bước từ đầu đến cuối hoàn toàn tự động (kèm Auto Double-Check).
* Nhập **`0`** rồi Enter: Thoát chương trình.

---

### Cách 2: Chạy 1 mạch toàn bộ
👉 **Click đúp chuột vào:** **`CHAY_TU_DONG.bat`**  
Mọi thứ còn lại máy tính sẽ tự làm từ đầu đến cuối và in tiến trình `[1/73]...` trên màn hình. Khi xong máy sẽ không tự tắt để bạn đọc kết quả.

---

## ❓ NẾU MÁY BÁO LỖI "CHƯA CÀI ĐẶT PYTHON"
1. **Bước 1:** Vào trang chính thức tải Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)  
   Bấm nút vàng **"Download Python 3.x.x"**.
2. **Bước 2 (RẤT QUAN TRỌNG):**  
   Mở file vừa tải về lên. Ở màn hình đầu tiên, **TÍCH CHỌN VÀO Ô:**  
   ☑️ **"Add python.exe to PATH"** *(ở góc dưới cùng)*.
3. **Bước 3:** Bấm nút **"Install Now"** cho máy chạy xong thì bấm Close.
4. **Bước 4:** Bấm chạy lại file **`MENU_LUA_CHON.bat`** là xong!

---

## 📝 NẾU MUỐN THAY ĐỔI CẤU HÌNH / MẬT KHẨU:
Mở thư mục **`src`** ➔ Mở file **`config.py`** bằng Notepad:
* Sửa `YEAR = "2026"` nếu cần đổi năm.
* Sửa `DEFAULT_PASSWORD = "..."` nếu có lớp đổi mật khẩu.
* Lưu lại (Ctrl + S) là xong.
