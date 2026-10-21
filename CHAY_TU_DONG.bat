@echo off
chcp 65001 >nul
title HỆ THỐNG TỰ ĐỘNG HÓA CHƯƠNG TRÌNH RÈN LUYỆN ĐOÀN VIÊN
color 0B

echo ===============================================================================
echo     CHƯƠNG TRÌNH TỰ ĐỘNG HÓA RÈN LUYỆN ĐOÀN VIÊN (ĐĂNG KÝ + CHẤM ĐIỂM + DUYỆT)
echo ===============================================================================
echo.

:: 1. Kiểm tra Python
echo [1/3] Đang kiểm tra Python trên máy tính...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [LỖI] Máy tính của bạn chưa cài đặt Python!
    echo Vui lòng xem hướng dẫn chi tiết trong file "run.md".
    echo Tải Python tại: https://www.python.org/downloads/
    echo (LƯU Ý: Nhớ tích chọn ô "Add python.exe to PATH" khi cài).
    echo.
    pause
    exit /b
)
python --version

:: Chuyển vào thư mục mã nguồn src
cd /d "%~dp0src"

:: 2. Tự động kiểm tra và cài đặt thư viện cần thiết
echo.
echo [2/3] Đang kiểm tra và tự động cài đặt thư viện cần thiết...
python -m pip install -r requirements.txt --quiet >nul 2>&1
if %errorlevel% neq 0 (
    pip install requests --quiet >nul 2>&1
)
echo -> Đã sẵn sàng môi trường!

:: 3. Chạy chương trình
echo.
echo [3/3] BẮT ĐẦU CHẠY TỰ ĐỘNG TOÀN BỘ QUY TRÌNH...
echo (Quá trình chạy sẽ hiển thị tiến trình [1/73]... Vui lòng không tắt cửa sổ này)
echo ===============================================================================
echo.

python run_all.py

echo.
echo ===============================================================================
echo     ĐÃ HOÀN TẤT TẤT CẢ CÁC BƯỚC! BẠN CÓ THỂ ĐÓNG CỬA SỔ NÀY.
echo ===============================================================================
pause
