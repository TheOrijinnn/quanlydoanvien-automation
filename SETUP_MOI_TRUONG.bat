@echo off
chcp 65001 >nul
title CÀI ĐẶT MÔI TRƯỜNG TỰ ĐỘNG - QUẢN LÝ ĐOÀN VIÊN
color 0B

echo ===============================================================================
echo            HỆ THỐNG THIẾT LẬP MÔI TRƯỜNG TỰ ĐỘNG (SETUP ENVIRONMENT)
echo ===============================================================================
echo.

:: 1. Kiểm tra Python
echo [1/4] Đang kiểm tra Python trên máy tính...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ❌ [LỖI] Chưa tìm thấy Python trên máy tính của bạn!
    echo.
    echo 📌 HƯỚNG DẪN CÀI ĐẶT:
    echo   1. Tải Python mới nhất tại: https://www.python.org/downloads/
    echo   2. Khi chạy bộ cài đặt, BẮT BUỘC TÍCH VÀO Ô:
    echo      [x] "Add Python to PATH" (hoặc "Add python.exe to PATH")
    echo   3. Cài đặt xong hãy mở lại file SETUP này.
    echo.
    pause
    exit /b
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo ✅ Đã phát hiện: %PYTHON_VER%

:: 2. Kiểm tra và nâng cấp pip
echo.
echo [2/4] Đang kiểm tra công cụ quản lý gói pip...
python -m ensurepip --default-pip >nul 2>&1
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Không tìm thấy pip! Vui lòng cài lại Python và tích chọn "pip".
    pause
    exit /b
)
echo ✅ Công cụ pip đã sẵn sàng!

:: 3. Cài đặt các thư viện cần thiết từ requirements.txt
echo.
echo [3/4] Đang tự động tải và cài đặt các thư viện cần thiết...
echo (Quá trình này chỉ mất vài giây, vui lòng đợi...)
echo.
python -m pip install --upgrade pip --quiet >nul 2>&1
python -m pip install -r "%~dp0src\requirements.txt"
if %errorlevel% neq 0 (
    color 0E
    echo ⚠️ Có cảnh báo khi cài đặt qua file requirements.txt, thử cài trực tiếp...
    python -m pip install requests cryptography
)

:: 4. Kiểm tra đối soát import thư viện
echo.
echo [4/4] Kiểm tra tính tương thích của môi trường...
python -c "import requests, cryptography; print('All modules imported successfully')" >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo ❌ Cài đặt thư viện thất bại! Vui lòng kiểm tra lại kết nối mạng Internet.
    pause
    exit /b
)

echo ✅ Môi trường đã sẵn sàng 100%!
echo.
echo ===============================================================================
echo        🎉 CHÚC MỪNG! BẠN ĐÃ CÀI ĐẶT MÔI TRƯỜNG THÀNH CÔNG!
echo ===============================================================================
echo.
echo Bấm phím bất kỳ để MỞ NGAY "MENU_LUA_CHON.bat"...
pause >nul

start "" "%~dp0MENU_LUA_CHON.bat"
exit /b
