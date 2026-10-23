import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

import step1_chidoan
import step2_co_so
import step3_audit
import step4_danh_gia_doan_vien
import step5_duyet_danh_gia
import step6_trinh_cap_the
import step7_duyet_cap_the
import step8_thong_ke_bao_cao

def main():
    print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
    print("║               HỆ THỐNG TỰ ĐỘNG HÓA TỔNG THỂ QUẢN LÝ ĐOÀN VIÊN                        ║")
    print("║      (RÈN LUYỆN ĐOÀN VIÊN + ĐÁNH GIÁ ĐOÀN VIÊN + CẤP MỚI THẺ ĐOÀN VIÊN)              ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════╝\n")

    start_all = time.time()

    # PHẦN 1: CHƯƠNG TRÌNH RÈN LUYỆN ĐOÀN VIÊN
    print("\n" + "█" * 80)
    print("  PHẦN 1: CHƯƠNG TRÌNH RÈN LUYỆN ĐOÀN VIÊN")
    print("█" * 80 + "\n")
    step1_chidoan.main()
    print("\n" + "-" * 80 + "\n")
    step2_co_so.main()
    print("\n" + "-" * 80 + "\n")
    step3_audit.main()

    # PHẦN 2: ĐÁNH GIÁ ĐOÀN VIÊN
    print("\n" + "█" * 80)
    print("  PHẦN 2: NGHIỆP VỤ ĐÁNH GIÁ ĐOÀN VIÊN (XUẤT SẮC 100%)")
    print("█" * 80 + "\n")
    step4_danh_gia_doan_vien.main("26")
    print("\n" + "-" * 80 + "\n")
    step5_duyet_danh_gia.main()

    # PHẦN 3: CẤP THẺ ĐOÀN VIÊN
    print("\n" + "█" * 80)
    print("  PHẦN 3: NGHIỆP VỤ CẤP THẺ ĐOÀN VIÊN (TRÌNH CẤP MỚI + DUYỆT)")
    print("█" * 80 + "\n")
    step6_trinh_cap_the.main()
    print("\n" + "-" * 80 + "\n")
    step7_duyet_cap_the.main()

    # PHẦN 4: AUTO DOUBLE-CHECK VÀ THỐNG KÊ TỔNG THỂ
    print("\n" + "█" * 80)
    print("  PHẦN 4: TỰ ĐỘNG DOUBLE-CHECK ĐỐI SOÁT CHÉO & XUẤT BÁO CÁO TOÀN DIỆN")
    print("█" * 80 + "\n")
    step8_thong_ke_bao_cao.main(quick_mode=False)

    total_time = time.time() - start_all
    print("\n" + "=" * 80)
    print(f"🎉 TOÀN BỘ QUY TRÌNH TỰ ĐỘNG HÓA ĐÃ HOÀN TẤT XUẤT SẮC TRONG {total_time/60:.2f} PHÚT!")
    print("=" * 80)

if __name__ == "__main__":
    main()
