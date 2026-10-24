@echo off
chcp 65001 >nul
title MENU TÙY CHỌN - TỰ ĐỘNG HÓA QUẢN LÝ ĐOÀN VIÊN
color 0B

:: Kiểm tra Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [LỖI] Chưa cài đặt Python! Vui lòng cài Python và tích chọn "Add Python to PATH".
    pause
    exit /b
)

:: Chuyển vào thư mục src
cd /d "%~dp0src"

:: Tự cài / cập nhật thư viện
python -m pip install -r requirements.txt --quiet >nul 2>&1

:MENU
cls
echo ===============================================================================
echo            HỆ THỐNG TỰ ĐỘNG HÓA QUẢN LÝ ĐOÀN VIÊN - MENU ĐIỀU KHIỂN
echo ===============================================================================
echo.
echo   --- CHƯƠNG TRÌNH RÈN LUYỆN ĐOÀN VIÊN ---
echo   [1] Bước 1: Chi đoàn Đăng ký, Chấm 100 điểm ^& Chuyển cấp trên (Toàn bộ Chi đoàn)
echo   [2] Bước 2: Đoàn cơ sở (yfie.hcmute) xác nhận duyệt rèn luyện (56 trang)
echo   [3] Bước 3: Đối soát đa luồng tiến độ rèn luyện ^& Xuất báo cáo
echo.
echo   --- NGHIỆP VỤ ĐÁNH GIÁ ĐOÀN VIÊN ---
echo   [4] Bước 4: Chi đoàn đánh giá xếp loại "Hoàn thành xuất sắc" (Auto Double-Check)
echo   [5] Bước 5: Đoàn cơ sở (yfie.hcmute) duyệt nhận xét đánh giá (Auto Double-Check)
echo.
echo   --- NGHIỆP VỤ CẤP THẺ ĐOÀN VIÊN ---
echo   [6] Bước 6: Chi đoàn trình "Cấp mới thẻ đoàn viên" (Auto Double-Check)
echo   [7] Bước 7: Đoàn cơ sở (yfie.hcmute) duyệt xử lý cấp thẻ đoàn viên
echo.
echo   --- TÙY CHỌN BỔ SUNG: THỐNG KÊ ^& KIỂM TRA SỐ LIỆU ---
echo   [8] Tùy chọn: Thống kê ^& Xuất báo cáo tổng hợp toàn khoa (Rèn luyện + Đánh giá + Cấp thẻ)
echo   [9] Tùy chọn: Chạy kiểm tra ^& Đối soát chéo số liệu (Double-Check Audit)
echo.
echo   --- TÍNH NĂNG NHANH CHO 1 ĐOÀN VIÊN MỚI THÊM ---
echo   [11] Xử lý đơn lẻ 1 người: Điền Tên + MSSV + Lớp (Tự động Đánh giá ^& Cấp thẻ)
echo   [12] Quét ^& Duyệt đoàn viên từ App TNVN + Đồng bộ trọn gói nghiệp vụ toàn bộ K26
echo.
echo   --- CHẠY TỰ ĐỘNG HOÀN TOÀN ---
echo   [10] CHẠY TẤT CẢ CÁC BƯỚC TỰ ĐỘNG (Bao gồm Auto Double-Check toàn diện)
echo   [0] Thoát
echo.
echo ===============================================================================
set /p choice="Nhập lựa chọn của bạn (0-12) rồi bấm Enter: "

if "%choice%"=="1" goto B1
if "%choice%"=="2" goto B2
if "%choice%"=="3" goto B3
if "%choice%"=="4" goto B4
if "%choice%"=="5" goto B5
if "%choice%"=="6" goto B6
if "%choice%"=="7" goto B7
if "%choice%"=="8" goto THONG_KE
if "%choice%"=="9" goto DOUBLE_CHECK
if "%choice%"=="10" goto CHAY_HET
if "%choice%"=="11" goto XU_LY_DON_LE
if "%choice%"=="12" goto DUYET_APP_K26
if "%choice%"=="0" exit /b

echo Lựa chọn không hợp lệ, vui lòng chọn lại!
pause
goto MENU

:B1
cls
python step1_chidoan.py
echo.
pause
goto MENU

:B2
cls
python step2_co_so.py
echo.
pause
goto MENU

:B3
cls
python step3_audit.py
echo.
pause
goto MENU

:B4
cls
echo [1] Đánh giá toàn bộ Chi đoàn K26 (Khuyên dùng)
echo [2] Đánh giá toàn bộ 73 Chi đoàn (K22 - K26)
set /p opt="Chọn đối tượng (1 hoặc 2): "
if "%opt%"=="1" python step4_danh_gia_doan_vien.py 26
if "%opt%"=="2" python step4_danh_gia_doan_vien.py
echo.
pause
goto MENU

:B5
cls
python step5_duyet_danh_gia.py
echo.
pause
goto MENU

:B6
cls
python step6_trinh_cap_the.py
echo.
pause
goto MENU

:B7
cls
python step7_duyet_cap_the.py
echo.
pause
goto MENU

:THONG_KE
cls
echo [1] Báo cáo nhanh (Quick Mode)
echo [2] Báo cáo chi tiết toàn diện (Full Audit - Quét sâu từng đoàn viên)
set /p tk_opt="Chọn chế độ báo cáo (1 hoặc 2): "
if "%tk_opt%"=="1" python step8_thong_ke_bao_cao.py --quick
if "%tk_opt%"=="2" python step8_thong_ke_bao_cao.py
echo.
pause
goto MENU

:DOUBLE_CHECK
cls
python step8_thong_ke_bao_cao.py --audit-only
echo.
pause
goto MENU

:CHAY_HET
cls
python run_all.py
echo.
pause
goto MENU

:XU_LY_DON_LE
cls
python xu_ly_mot_nguoi.py
echo.
pause
goto MENU

:DUYET_APP_K26
cls
python duyet_app_va_dong_bo_k26.py
echo.
pause
goto MENU
