import sys
import time
import json
from config import SUPER_ACCOUNT, YEAR
from api_client import DoanVienClient

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=" * 80)
    print("BƯỚC 2: CẤP ĐOÀN CƠ SỞ DUYỆT XÁC NHẬN TOÀN BỘ CÁC TRANG")
    print(f"Tài khoản Đoàn cơ sở: {SUPER_ACCOUNT['username']}")
    print(f"Năm rèn luyện: {YEAR}")
    print("=" * 80)

    client = DoanVienClient(SUPER_ACCOUNT["username"], SUPER_ACCOUNT["password"])
    if not client.login():
        print("❌ Đăng nhập thất bại vào tài khoản Đoàn cơ sở!")
        sys.exit(1)

    # Lấy tổng số bản ghi và số trang
    init_res = client.call("ndv05.dangky.get_ds_doanvien_xacnhan_paging", {"nam": YEAR, "page_no": 1, "page_size": 50})
    total_records = init_res.get("total", 0)
    page_size = 50
    total_pages = (total_records + page_size - 1) // page_size

    print(f"Tổng số đoàn viên trên toàn cơ sở: {total_records}")
    print(f"Số lượng hiển thị: {page_size}/trang => Tổng số trang: {total_pages} trang\n")

    confirmed_in_this_run = 0
    already_confirmed = 0

    for page in range(1, total_pages + 1):
        res = client.call("ndv05.dangky.get_ds_doanvien_xacnhan_paging", {"nam": YEAR, "page_no": page, "page_size": page_size})
        items = res.get("result", [])
        if not items:
            print(f"[Trang {page:2d}/{total_pages:2d}] Không có dữ liệu.")
            continue

        waiting = [x["id_dangky"] for x in items if x.get("dcs_xac_nhan") == 1]
        done = sum(1 for x in items if x.get("dcs_xac_nhan") == 2)
        already_confirmed += done

        if waiting:
            # Tích chọn và bấm xác nhận
            confirm_res = client.call("ndv05.xacnhan.dcs_xacnhan", {"ds_id_dangky": waiting})
            if confirm_res.get("success"):
                confirmed_in_this_run += len(waiting)
                print(f"[Trang {page:2d}/{total_pages:2d}] ✅ Đã tích chọn & xác nhận {len(waiting):2d} đoàn viên! (Đã duyệt trước: {done:2d})")
            else:
                print(f"[Trang {page:2d}/{total_pages:2d}] ❌ Lỗi xác nhận: {confirm_res}")
        else:
            print(f"[Trang {page:2d}/{total_pages:2d}] ⚪ Đã xác nhận xong từ trước ({done:2d}/{len(items):2d} đoàn viên)")

        time.sleep(0.3)

    print("\n" + "-" * 50)
    print("TIẾN HÀNH KIỂM TRA LẠI (AUDIT) TOÀN BỘ...")
    final_confirmed = 0
    final_waiting = 0

    for page in range(1, total_pages + 1):
        res = client.call("ndv05.dangky.get_ds_doanvien_xacnhan_paging", {"nam": YEAR, "page_no": page, "page_size": page_size})
        items = res.get("result", [])
        for it in items:
            s = it.get("dcs_xac_nhan")
            if s == 2:
                final_confirmed += 1
            elif s == 1:
                final_waiting += 1

    print("=" * 80)
    print(f"🎉 HOÀN TẤT DUYỆT CẤP ĐOÀN CƠ SỞ!")
    print(f"Tổng số đoàn viên đã duyệt xác nhận: {final_confirmed}/{total_records} ({(final_confirmed/total_records*100):.1f}%)")
    print(f"Số lượng còn chờ xác nhận         : {final_waiting}")
    print("=" * 80)

if __name__ == "__main__":
    main()
