@echo off
chcp 65001 >nul
title MENU TÙY CHỌN - TỰ ĐỘNG HÓA RÈN LUYỆN ĐOÀN VIÊN
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

:: Tự cài thư viện
python -m pip install -r requirements.txt --quiet >nul 2>&1

:MENU
cls
echo ===============================================================================
echo            HỆ THỐNG TỰ ĐỘNG HÓA RÈN LUYỆN ĐOÀN VIÊN - MENU ĐIỀU KHIỂN
echo ===============================================================================
echo.
echo   [1] CHẠY TẤT CẢ (Khuyên dùng: Bước 1 + Bước 2 + Bước 3)
echo   [2] Chỉ chạy BƯỚC 1: Xử lý 73 Chi đoàn (Đăng ký, Chấm 100đ, Chuyển cấp trên)
echo   [3] Chỉ chạy BƯỚC 2: Cấp Đoàn cơ sở (yfie.hcmute) duyệt 56 trang
echo   [4] Chỉ chạy BƯỚC 3: Đối soát đa luồng & Xuất báo cáo (audit_report.json)
echo   [0] Thoát
echo.
echo ===============================================================================
set /p choice="Nhập lựa chọn của bạn (0-4) rồi bấm Enter: "

if "%choice%"=="1" goto CHAY_HET
if "%choice%"=="2" goto B1
if "%choice%"=="3" goto B2
if "%choice%"=="4" goto B3
if "%choice%"=="0" exit /b

echo Lựa chọn không hợp lệ, vui lòng chọn lại!
pause
goto MENU

:CHAY_HET
cls
python run_all.py
echo.
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
