@echo off
chcp 65001 >nul
title HỆ THỐNG TỰ ĐỘNG HÓA QUẢN LÝ ĐOÀN VIÊN
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

:: Tự cài / cập nhật thư viện nếu cần
python -m pip install -r requirements.txt --quiet >nul 2>&1

:MENU
cls
echo ===============================================================================
echo            HỆ THỐNG TỰ ĐỘNG HÓA QUẢN LÝ ĐOÀN VIÊN - MENU ĐIỀU KHIỂN
echo ===============================================================================
echo.
echo   --- [GIAI ĐOẠN 1]: DUYỆT APP + CHƯƠNG TRÌNH RÈN LUYỆN ĐOÀN VIÊN ---
echo   [1] Bước 0: Quét ^& Duyệt đoàn viên từ App Thanh niên Việt Nam (Chờ duyệt)
echo   [2] Bước 1: Chi đoàn Đăng ký (31 tiêu chí), Chấm 100 điểm ^& Chuyển cấp trên
echo   [3] Bước 2: Đoàn cơ sở (yfie.hcmute) duyệt xác nhận rèn luyện
echo   [4] 🔍 Double Check Giai đoạn 1: Đối soát số liệu Rèn luyện đoàn viên
echo.
echo   --- [GIAI ĐOẠN 2]: NGHIỆP VỤ CẤP THẺ ĐOÀN VIÊN ---
echo   [5] Bước 6: Chi đoàn lập tờ trình cấp thẻ (Cả Cấp mới ^& Cấp lại)
echo   [6] Bước 7: Đoàn cơ sở (yfie.hcmute) duyệt chuyển tiếp cấp thẻ lên Đoàn trường
echo   [7] 🔍 Double Check Giai đoạn 2: Đối soát số liệu Cấp thẻ đoàn viên
echo.
echo   --- [GIAI ĐOẠN 3]: ĐÁNH GIÁ XẾP LOẠI ĐOÀN VIÊN ---
echo   [8] Bước 4: Chi đoàn đánh giá xếp loại "Hoàn thành xuất sắc nhiệm vụ"
echo   [9] Bước 5: Đoàn cơ sở (yfie.hcmute) duyệt nhận xét xếp loại đoàn viên
echo   [10] 🔍 Double Check Giai đoạn 3: Đối soát số liệu Đánh giá xếp loại
echo.
echo   --- [TÙY CHỌN ĐƠN LẺ CHO 1 NGƯỜI (CHỈ CẦN TÊN + LỚP)] ---
echo   [11] Xử lý trọn gói 1 người: Duyệt App -^> Rèn luyện -^> Cấp thẻ -^> Đánh giá
echo.
echo   --- [CHẠY TỰ ĐỘNG HOÀN TOÀN TOÀN BỘ CÁC GIAI ĐOẠN] ---
echo   [12] CHẠY TẤT CẢ TỰ ĐỘNG (Duyệt App -^> Rèn luyện -^> Cấp thẻ -^> Đánh giá -^> Auto Double Check)
echo   [13] Xuất báo cáo thống kê tổng hợp toàn khoa (Full Audit)
echo   [0] Thoát
echo.
echo ===============================================================================
set /p choice="Nhập lựa chọn của bạn (0-13) rồi bấm Enter: "

if "%choice%"=="1" goto DUYET_APP
if "%choice%"=="2" goto B1
if "%choice%"=="3" goto B2
if "%choice%"=="4" goto CHECK_RL
if "%choice%"=="5" goto B6
if "%choice%"=="6" goto B7
if "%choice%"=="7" goto CHECK_THE
if "%choice%"=="8" goto B4
if "%choice%"=="9" goto B5
if "%choice%"=="10" goto CHECK_DG
if "%choice%"=="11" goto XU_LY_DON_LE
if "%choice%"=="12" goto CHAY_HET
if "%choice%"=="13" goto THONG_KE
if "%choice%"=="0" exit /b

echo Lựa chọn không hợp lệ, vui lòng chọn lại!
pause
goto MENU

:DUYET_APP
cls
echo [1] Duyệt App cho Chi đoàn K26 (Khuyên dùng)
echo [2] Duyệt App cho toàn bộ 73 Chi đoàn (K22 - K26)
set /p opt="Chọn đối tượng (1 hoặc 2): "
if "%opt%"=="1" python step0_duyet_app.py 26
if "%opt%"=="2" python step0_duyet_app.py
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

:CHECK_RL
cls
python -c "import double_check; double_check.check_ren_luyen()"
echo.
pause
goto MENU

:B6
cls
echo [1] Trình cấp thẻ cho Chi đoàn K26 (Khuyên dùng)
echo [2] Trình cấp thẻ cho toàn bộ 73 Chi đoàn (K22 - K26)
set /p opt="Chọn đối tượng (1 hoặc 2): "
if "%opt%"=="1" python step6_trinh_cap_the.py 26
if "%opt%"=="2" python step6_trinh_cap_the.py
echo.
pause
goto MENU

:B7
cls
python step7_duyet_cap_the.py
echo.
pause
goto MENU

:CHECK_THE
cls
python -c "import double_check; double_check.check_cap_the()"
echo.
pause
goto MENU

:B4
cls
echo [1] Đánh giá xếp loại cho Chi đoàn K26 (Khuyên dùng)
echo [2] Đánh giá xếp loại cho toàn bộ 73 Chi đoàn (K22 - K26)
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

:CHECK_DG
cls
python -c "import double_check; double_check.check_danh_gia()"
echo.
pause
goto MENU

:XU_LY_DON_LE
cls
python xu_ly_mot_nguoi.py
echo.
pause
goto MENU

:CHAY_HET
cls
echo [1] Chạy toàn diện cho Chi đoàn K26
echo [2] Chạy toàn diện cho toàn bộ 73 Chi đoàn (K22 - K26)
set /p opt="Chọn chế độ (1 hoặc 2): "
if "%opt%"=="1" python run_all.py 26
if "%opt%"=="2" python run_all.py
echo.
pause
goto MENU

:THONG_KE
cls
python step8_thong_ke_bao_cao.py
echo.
pause
goto MENU
