import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

import step1_chidoan
import step2_co_so
import step3_audit

def main():
    print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
    print("║               HỆ THỐNG TỰ ĐỘNG HÓA CHƯƠNG TRÌNH RÈN LUYỆN ĐOÀN VIÊN                  ║")
    print("║                   (ĐĂNG KÝ -> ĐÁNH GIÁ -> DUYỆT CƠ SỞ -> ĐỐI SOÁT)                   ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════╝\n")

    start_all = time.time()

    # BƯỚC 1: Xử lý 73 chi đoàn
    step1_chidoan.main()
    print("\n" + "#" * 80 + "\n")

    # BƯỚC 2: Duyệt cấp cơ sở
    step2_co_so.main()
    print("\n" + "#" * 80 + "\n")

    # BƯỚC 3: Đối soát & Báo cáo
    step3_audit.main()

    total_time = time.time() - start_all
    print(f"\n🎉 TOÀN BỘ QUY TRÌNH ĐÃ HOÀN TẤT TRONG {total_time/60:.2f} PHÚT!")

if __name__ == "__main__":
    main()
