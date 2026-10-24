import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

import step0_duyet_app
import step1_chidoan
import step2_co_so
import step6_trinh_cap_the
import step7_duyet_cap_the
import step4_danh_gia_doan_vien
import step5_duyet_danh_gia
import double_check
import step8_thong_ke_bao_cao

def main(filter_prefix=None):
    print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
    print("║               HỆ THỐNG TỰ ĐỘNG HÓA TỔNG THỂ QUẢN LÝ ĐOÀN VIÊN                        ║")
    print("║  LUỒNG CHUẨN:                                                                        ║")
    print("║    1. DUYỆT APP + RÈN LUYỆN -> ADMIN DUYỆT -> 🔍 DOUBLE CHECK SỐ LƯỢNG               ║")
    print("║    2. CẤP THẺ ĐOÀN -> ADMIN DUYỆT -> 🔍 DOUBLE CHECK SỐ LƯỢNG                        ║")
    print("║    3. ĐÁNH GIÁ XẾP LOẠI -> ADMIN DUYỆT -> 🔍 DOUBLE CHECK SỐ LƯỢNG                   ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════╝\n")

    start_all = time.time()
    admin_client = double_check.get_admin()

    # =========================================================================
    # GIAI ĐOẠN 1: DUYỆT APP + CHƯƠNG TRÌNH RÈN LUYỆN ĐOÀN VIÊN + DOUBLE CHECK
    # =========================================================================
    print("\n" + "█" * 88)
    print("  GIAI ĐOẠN 1: DUYỆT APP + RÈN LUYỆN (ĐĂNG KÝ 31 TC, CHẤM 100Đ) -> ADMIN DUYỆT")
    print("█" * 88 + "\n")

    # 1.1 Quét & Duyệt đoàn viên từ App TNVN
    step0_duyet_app.main(filter_prefix)
    print("\n" + "-" * 88 + "\n")

    # 1.2 Chi đoàn: Đăng ký 31 tiêu chí + Chấm 100/100 + Chuyển cấp trên
    step1_chidoan.main()
    print("\n" + "-" * 88 + "\n")

    # 1.3 Cấp Đoàn cơ sở (Admin): Duyệt xác nhận toàn bộ rèn luyện
    step2_co_so.main()
    print("\n" + "-" * 88 + "\n")

    # 1.4 DOUBLE CHECK & THỐNG KÊ SỐ LƯỢNG RÈN LUYỆN
    print(">> TIẾN HÀNH AUTO DOUBLE CHECK GIAI ĐOẠN 1 (RÈN LUYỆN ĐOÀN VIÊN)...")
    double_check.check_ren_luyen(admin_client)

    # =========================================================================
    # GIAI ĐOẠN 2: CẤP THẺ ĐOÀN VIÊN (CẤP MỚI & CẤP LẠI) -> ADMIN DUYỆT + DOUBLE CHECK
    # =========================================================================
    print("\n" + "█" * 88)
    print("  GIAI ĐOẠN 2: NGHIỆP VỤ CẤP THẺ ĐOÀN VIÊN (TRÌNH CẤP MỚI & CẤP LẠI) -> ADMIN DUYỆT")
    print("█" * 88 + "\n")

    # 2.1 Chi đoàn: Kiểm tra và lập tờ trình chuyển xử lý (cả Cấp mới và Cấp lại)
    step6_trinh_cap_the.main(filter_prefix)
    print("\n" + "-" * 88 + "\n")

    # 2.2 Cấp Đoàn cơ sở (Admin): Phê duyệt và chuyển tiếp tờ trình lên Đoàn trường
    step7_duyet_cap_the.main()
    print("\n" + "-" * 88 + "\n")

    # 2.3 DOUBLE CHECK & THỐNG KÊ SỐ LƯỢNG CẤP THẺ
    print(">> TIẾN HÀNH AUTO DOUBLE CHECK GIAI ĐOẠN 2 (CẤP THẺ ĐOÀN VIÊN)...")
    double_check.check_cap_the(admin_client)

    # =========================================================================
    # GIAI ĐOẠN 3: ĐÁNH GIÁ XẾP LOẠI ĐOÀN VIÊN -> ADMIN DUYỆT + DOUBLE CHECK
    # =========================================================================
    print("\n" + "█" * 88)
    print("  GIAI ĐOẠN 3: ĐÁNH GIÁ XẾP LOẠI ĐOÀN VIÊN (XUẤT SẮC 100%) -> ADMIN DUYỆT")
    print("█" * 88 + "\n")

    # 3.1 Chi đoàn: Đánh giá xếp loại Xuất sắc, lưu & gửi danh sách
    step4_danh_gia_doan_vien.main(filter_prefix or "26")
    print("\n" + "-" * 88 + "\n")

    # 3.2 Cấp Đoàn cơ sở (Admin): Duyệt nhận xét đánh giá xếp loại
    step5_duyet_danh_gia.main()
    print("\n" + "-" * 88 + "\n")

    # 3.3 DOUBLE CHECK & THỐNG KÊ SỐ LƯỢNG ĐÁNH GIÁ
    print(">> TIẾN HÀNH AUTO DOUBLE CHECK GIAI ĐOẠN 3 (ĐÁNH GIÁ XẾP LOẠI)...")
    double_check.check_danh_gia(admin_client, filter_prefix)

    # =========================================================================
    # GIAI ĐOẠN 4: THỐNG KÊ TỔNG HỢP VÀ BÁO CÁO TOÀN DIỆN
    # =========================================================================
    print("\n" + "█" * 88)
    print("  GIAI ĐOẠN 4: XUẤT BÁO CÁO THỐNG KÊ TỔNG HỢP TOÀN KHOA")
    print("█" * 88 + "\n")
    step8_thong_ke_bao_cao.main(quick_mode=False)

    total_time = time.time() - start_all
    print("\n" + "═" * 88)
    print(f"🎉 HOÀN TẤT TRỌN VẸN TOÀN BỘ QUY TRÌNH TỰ ĐỘNG HÓA VÀ DOUBLE CHECK TRONG {total_time/60:.2f} PHÚT!")
    print("═" * 88)

if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else None
    main(prefix)
