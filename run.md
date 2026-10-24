# 📖 HƯỚNG DẪN DÀNH CHO NGƯỜI DÙNG (LOW-TECH)

Tài liệu này được viết theo cách **đơn giản nhất**, ai cũng có thể làm được chỉ với **1 cú click chuột**, không cần biết lập trình hay gõ lệnh phức tạp.

---

## ⚡ CÁC BƯỚC THỰC HIỆN:

### BƯỚC 1: Cài đặt môi trường (Chỉ làm 1 lần đầu tiên)
👉 **Click đúp chuột vào:** **`SETUP_MOI_TRUONG.bat`**  
- Hệ thống sẽ tự động kiểm tra Python, nâng cấp `pip`, và tự cài đặt 100% các thư viện cần thiết.
- Khi cài xong, chương trình sẽ tự động mở luôn **`MENU_LUA_CHON.bat`** cho bạn.

---

### BƯỚC 2: Mở Menu điều khiển để chọn chức năng
👉 **Click đúp chuột vào:** **`MENU_LUA_CHON.bat`**  

Màn hình sẽ hiển thị Menu điều khiển gồm 4 giai đoạn chuẩn hóa:

#### --- [GIAI ĐOẠN 1]: DUYỆT APP + CHƯƠNG TRÌNH RÈN LUYỆN ĐOÀN VIÊN ---
* Nhập **`1`** rồi Enter: Bước 0 - Quét & Duyệt đoàn viên từ App Thanh niên Việt Nam (Chờ duyệt).
* Nhập **`2`** rồi Enter: Bước 1 - Chi đoàn Đăng ký (31 tiêu chí), Chấm 100 điểm & Chuyển cấp trên.
* Nhập **`3`** rồi Enter: Bước 2 - Đoàn cơ sở (`yfie.hcmute`) duyệt xác nhận rèn luyện.
* Nhập **`4`** rồi Enter: 🔍 **Double Check Giai đoạn 1** - Đối soát CSDL rèn luyện đoàn viên.

#### --- [GIAI ĐOẠN 2]: NGHIỆP VỤ CẤP THẺ ĐOÀN VIÊN ---
* Nhập **`5`** rồi Enter: Bước 6 - Chi đoàn lập tờ trình cấp thẻ (Cả Cấp mới & Cấp lại thẻ).
* Nhập **`6`** rồi Enter: Bước 7 - Đoàn cơ sở (`yfie.hcmute`) duyệt chuyển tiếp cấp thẻ lên Đoàn trường.
* Nhập **`7`** rồi Enter: 🔍 **Double Check Giai đoạn 2** - Đối soát số liệu cấp thẻ đoàn viên.

#### --- [GIAI ĐOẠN 3]: ĐÁNH GIÁ XẾP LOẠI ĐOÀN VIÊN ---
* Nhập **`8`** rồi Enter: Bước 4 - Chi đoàn đánh giá xếp loại "Hoàn thành xuất sắc nhiệm vụ".
* Nhập **`9`** rồi Enter: Bước 5 - Đoàn cơ sở (`yfie.hcmute`) duyệt nhận xét xếp loại đoàn viên.
* Nhập **`10`** rồi Enter: 🔍 **Double Check Giai đoạn 3** - Đối soát số liệu đánh giá xếp loại.

#### --- [TÙY CHỌN ĐƠN LẺ CHO 1 NGƯỜI (CHỈ CẦN TÊN + LỚP)] ---
* Nhập **`11`** rồi Enter: **Xử lý trọn gói 1 người** (Chỉ cần điền Tên + Lớp ➔ Hệ thống tự Duyệt App ➔ Rèn luyện 100đ ➔ Cấp thẻ đoàn ➔ Đánh giá xuất sắc).

#### --- [CHẠY TỰ ĐỘNG HOÀN TOÀN TẤT CẢ CÁC BƯỚC] ---
* Nhập **`12`** rồi Enter: **CHẠY TẤT CẢ TỰ ĐỘNG** theo đúng luồng chuẩn hóa kèm Auto Double-Check sau mỗi bước.
* Nhập **`13`** rồi Enter: Xuất báo cáo thống kê tổng hợp toàn khoa (Full Audit).
* Nhập **`0`** rồi Enter: Thoát chương trình.

---

## ❓ NẾU MÁY BÁO LỖI "CHƯA CÀI ĐẶT PYTHON"
1. **Bước 1:** Vào trang chính thức tải Python: [https://www.python.org/downloads/](https://www.python.org/downloads/)  
   Bấm nút vàng **"Download Python 3.x.x"**.
2. **Bước 2 (RẤT QUAN TRỌNG):**  
   Mở file vừa tải về lên. Ở màn hình đầu tiên, **TÍCH CHỌN VÀO Ô:**  
   ☑️ **"Add python.exe to PATH"** *(ở góc dưới cùng)*.
3. **Bước 3:** Bấm nút **"Install Now"** cho máy chạy xong thì bấm Close.
4. **Bước 4:** Bấm chạy lại file **`SETUP_MOI_TRUONG.bat`** là xong!

---

## 📝 NẾU MUỐN THAY ĐỔI CẤU HÌNH / MẬT KHẨU:
Mở thư mục **`src`** ➔ Mở file **`config.py`** bằng Notepad:
* Sửa `YEAR = "2026"` nếu cần đổi năm.
* Sửa `DEFAULT_PASSWORD = "..."` nếu có lớp đổi mật khẩu.
* Lưu lại (Ctrl + S) là xong.
