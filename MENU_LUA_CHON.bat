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
echo   [1] Bước 1: Chi đoàn Đăng ký, Chấm 100 điểm ^& Chuyển cấp trên (73 Chi đoàn)
echo   [2] Bước 2: Đoàn cơ sở (yfie.hcmute) xác nhận duyệt rèn luyện (56 trang)
echo   [3] Bước 3: Đối soát đa luồng tiến độ rèn luyện ^& Xuất báo cáo
echo.
echo   --- NGHIỆP VỤ ĐÁNH GIÁ ĐOÀN VIÊN ---
echo   [4] Bước 4: Chi đoàn đánh giá xếp loại "Hoàn thành xuất sắc nhiệm vụ"
echo   [5] Bước 5: Đoàn cơ sở (yfie.hcmute) duyệt danh sách nhận xét đánh giá
echo.
echo   --- NGHIỆP VỤ CẤP THẺ ĐOÀN VIÊN ---
echo   [6] Bước 6: Chi đoàn trình "Cấp mới thẻ đoàn viên" cho tất cả đoàn viên
echo   [7] Bước 7: Đoàn cơ sở (yfie.hcmute) duyệt xử lý cấp thẻ đoàn viên
echo.
echo   --- CHẠY TỰ ĐỘNG HOÀN TOÀN ---
echo   [8] CHẠY TẤT CẢ CÁC BƯỚC TỰ ĐỘNG (Từ Bước 1 đến Bước 7)
echo   [0] Thoát
echo.
echo ===============================================================================
set /p choice="Nhập lựa chọn của bạn (0-8) rồi bấm Enter: "

if "%choice%"=="1" goto B1
if "%choice%"=="2" goto B2
if "%choice%"=="3" goto B3
if "%choice%"=="4" goto B4
if "%choice%"=="5" goto B5
if "%choice%"=="6" goto B6
if "%choice%"=="7" goto B7
if "%choice%"=="8" goto CHAY_HET
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

:CHAY_HET
cls
python run_all.py
echo.
pause
goto MENU
