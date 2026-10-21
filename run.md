# 📖 HƯỚNG DẪN DÀNH CHO NGƯỜI MỚI (LOW-TECH)

Tài liệu này được viết theo cách **đơn giản nhất**, ai cũng có thể làm được chỉ với **1 cú click chuột**, không cần biết lập trình hay gõ lệnh phức tạp.

---

## ⚡ CÁCH CHẠY (CHỌN 1 TRONG 3 CÁCH):

### Cách 1: Click file `.exe` (Nhanh nhất - Không cần cài gì cả)
👉 **Click đúp chuột vào:** **`CHAY_TU_DONG.exe`**  
*(Toàn bộ mã nguồn và thư viện đã được nén vào file này, máy tính không cần cài gì thêm vẫn chạy được).*

---

### Cách 2: Click file `.bat` tự động
👉 **Click đúp chuột vào:** **`CHAY_TU_DONG.bat`**  
Mọi thứ còn lại máy tính sẽ tự làm hoàn toàn:
1. Tự động kiểm tra máy tính đã có Python chưa.
2. Tự động tải thư viện cần thiết về máy.
3. Tự động đăng nhập lần lượt 73 chi đoàn: đăng ký, chấm 100 điểm, chuyển cấp trên.
4. Tự động đăng nhập tài khoản cấp trên duyệt tất cả các trang.
5. In kết quả hoàn thành `[1/73]...` trên màn hình và không tự tắt để bạn đọc kết quả.

---

### Cách 3: Chọn chạy từng bước riêng
👉 **Click đúp chuột vào:** **`MENU_LUA_CHON.bat`**  
Màn hình sẽ hiện menu số:
* Nhập số **`1`** rồi bấm Enter: Chạy tất cả từ đầu đến cuối.
* Nhập số **`2`** rồi bấm Enter: Chỉ chạy bước Chi đoàn (73 chi đoàn).
* Nhập số **`3`** rồi bấm Enter: Chỉ chạy bước Duyệt của Đoàn cơ sở.
* Nhập số **`4`** rồi bấm Enter: Chỉ chạy kiểm tra đối soát và in bảng thống kê.
* Nhập số **`0`** rồi bấm Enter: Thoát.

---

## ❓ NẾU MÁY BÁO LỖI "CHƯA CÀI ĐẶT PYTHON" (KHI DÙNG FILE .BAT)

1. **Bước 1:** Vào trang chính thức để tải: [https://www.python.org/downloads/](https://www.python.org/downloads/)  
   Bấm nút vàng **"Download Python 3.x.x"**.
2. **Bước 2 (RẤT QUAN TRỌNG):**  
   Mở file vừa tải về lên. Ở màn hình đầu tiên, **TÍCH CHỌN VÀO Ô:**  
   ☑️ **"Add python.exe to PATH"** *(ở dưới cùng)*.
3. **Bước 3:** Bấm nút **"Install Now"** cho máy chạy xong thì bấm Close.
4. **Bước 4:** Bấm chạy lại file **`CHAY_TU_DONG.bat`** là xong!

---

## 📝 NẾU MUỐN ĐỔI MẬT KHẨU HOẶC THAY ĐỔI CẤU HÌNH:
Mở thư mục **`src`** ➔ Mở file **`config.py`** bằng Notepad:
* Sửa dòng `YEAR = "2026"` nếu sang năm sau.
* Sửa `DEFAULT_PASSWORD = "..."` nếu có đổi mật khẩu.
* Lưu lại (Ctrl + S) là xong.
