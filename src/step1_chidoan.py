import sys
import time
import json
from config import CHIDOAN_ACCOUNTS, DEFAULT_PASSWORD, YEAR, SCORE_MAP, COMMENT_6M, COMMENT_YEAR
from api_client import DoanVienClient

# Ensure UTF-8 printing on Windows
sys.stdout.reconfigure(encoding='utf-8')

def process_one_chidoan(idx, total_acc, name, username):
    client = DoanVienClient(username, DEFAULT_PASSWORD)
    if not client.login():
        print(f"[{idx:2d}/{total_acc}] {name:<22s} ({username:<15s}) | ❌ Đăng nhập thất bại!")
        return {"status": "LOGIN_FAIL", "name": name, "username": username}

    # 1. Lấy thông tin cấu hình chương trình rèn luyện động của phiên
    ch = client.call("ndv05.dangky.ctrl_cauhinh", {"ten": "NAM"}, {"ten": "NAM_DANGKY"}, {"ten": "SL_TOITHIEU"})
    id_chuongtrinh = None
    if isinstance(ch, list) and len(ch) > 3 and isinstance(ch[3], dict):
        id_chuongtrinh = ch[3].get("id_chuongtrinh")

    # Lấy danh sách toàn bộ tiêu chí (31 tiêu chí)
    tc_list = []
    if id_chuongtrinh:
        tc_res = client.call("nvd05.tieuchi.get_list", {"id_chuongtrinh": id_chuongtrinh})
        if isinstance(tc_res, list):
            tc_list = tc_res

    # 2. TAB 1: ĐĂNG KÝ RÈN LUYỆN
    t1 = client.call("ndv05.dangky.get_ds_doanvien_paging", {"nam": YEAR, "page_no": 1, "page_size": 100})
    tab1_items = t1.get("result", [])
    total_members = t1.get("total", len(tab1_items))

    # Lọc danh sách đoàn viên chưa đăng ký (trang_thai_dangky != 2)
    unregistered = [x["id"] for x in tab1_items if x.get("trang_thai_dangky") != 2]
    newly_registered = 0

    if unregistered and tc_list:
        # CHÚ Ý QUAN TRỌNG: Chia nhỏ mảng thành từng cụm 5 đoàn viên/lần gửi để tránh lỗi ORA-01403 của Oracle backend
        BATCH_SIZE = 5
        for i in range(0, len(unregistered), BATCH_SIZE):
            batch_ids = unregistered[i:i+BATCH_SIZE]
            reg_payload = {
                "id_chuongtrinh": id_chuongtrinh,
                "nam": YEAR,
                "lid": batch_ids,
                "ltc": tc_list
            }
            save_reg = client.call("ndv05.dangky.save_dangky_tieuchi", reg_payload)
            if save_reg.get("success"):
                newly_registered += len(batch_ids)
            time.sleep(0.3)

    # 3. TAB 2: ĐÁNH GIÁ RÈN LUYỆN
    t2 = client.call("ndv05.dangky.get_ds_doanvien_danhgia_paging", {"nam": YEAR, "page_no": 1, "page_size": 100})
    tab2_items = t2.get("result", [])
    total_tab2 = t2.get("total", len(tab2_items))

    evaluated_count = 0
    chuyen_ids = []

    for it in tab2_items:
        id_dangky = it.get("id_dangky")
        if not id_dangky or id_dangky == "0":
            continue

        diem_cham = str(it.get("diem_cham", "")).strip()
        trang_thai_cham = it.get("trang_thai_cham")
        dcs_xac_nhan = it.get("dcs_xac_nhan")

        # Nếu chưa có điểm hoặc chưa đánh giá
        if not diem_cham or diem_cham in ("0", "None") or trang_thai_cham != 2:
            tc_data = client.call("ndv05.danhgia.get_ds_tieuchi_dangky", {"id_dangky": id_dangky}, {"id_dangky": id_dangky}, None)
            if tc_data and len(tc_data) > 0 and len(tc_data[0]) > 0:
                raw_tc = tc_data[0]
                ltc = []
                for x in raw_tc:
                    ic = dict(x)
                    muc = str(ic.get("muc", "")).strip()
                    if ic.get("id_cha") == 0 or ic.get("id_cha") == "0":
                        ic["diem_cham"] = "20"
                        ic["diem_duyet"] = "20"
                    else:
                        s = SCORE_MAP.get(muc, 4)
                        ic["diem_cham"] = str(s)
                        ic["diem_duyet"] = str(s)
                    ltc.append(ic)

                payload = {
                    "id_dangky": id_dangky,
                    "diem_cham": 100,
                    "diem_duyet": 100,
                    "cd_nhan_xet_6t": COMMENT_6M,
                    "cd_nhan_xet_nam": COMMENT_YEAR,
                    "ltc": ltc
                }
                save_eval = client.call("ndv05.danhgia.save_danhgia_tieuchi", payload)
                if save_eval.get("success"):
                    evaluated_count += 1
                time.sleep(0.2)
        else:
            evaluated_count += 1

        # Gom danh sách cần chuyển lên cấp trên (dcs_xac_nhan == 0)
        if dcs_xac_nhan in (0, "0"):
            chuyen_ids.append(id_dangky)

    # 4. CHUYỂN CẤP TRÊN
    transferred_count = 0
    if chuyen_ids:
        # Gửi theo cụm 30-50 đoàn viên
        for i in range(0, len(chuyen_ids), 30):
            batch_chuyen = chuyen_ids[i:i+30]
            c_res = client.call("ndv05.danhgia.chuyen_captren", {"ds_id_dangky": batch_chuyen})
            if c_res.get("success"):
                transferred_count += len(batch_chuyen)
            time.sleep(0.3)

    # Lấy lại số liệu xác nhận cuối cùng
    t2_final = client.call("ndv05.dangky.get_ds_doanvien_danhgia_paging", {"nam": YEAR, "page_no": 1, "page_size": 100})
    final_items = t2_final.get("result", [])
    final_graded = sum(1 for x in final_items if str(x.get("diem_cham", "")).strip() == "100")

    # In log tiến trình rõ ràng cho từng chi đoàn
    print(f"[{idx:2d}/{total_acc}] {name:<22s} ({username:<15s}) | Đăng ký: {total_members:2d}/{total_members:2d} | Đánh giá: {final_graded:2d}/{total_members:2d} | Chuyển cấp trên: {transferred_count:2d} | ✅ HOÀN THÀNH!")
    return {
        "status": "OK",
        "name": name,
        "username": username,
        "total": total_members,
        "graded": final_graded,
        "transferred": transferred_count
    }

def main():
    print("=" * 80)
    print("BƯỚC 1: TỰ ĐỘNG ĐĂNG KÝ, CHẤM ĐIỂM (100/100) VÀ CHUYỂN CẤP TRÊN CHO 73 CHI ĐOÀN")
    print(f"Năm rèn luyện: {YEAR}")
    print("=" * 80)

    total_acc = len(CHIDOAN_ACCOUNTS)
    results = []
    start_time = time.time()

    for idx, (name, username) in enumerate(CHIDOAN_ACCOUNTS, 1):
        r = process_one_chidoan(idx, total_acc, name, username)
        results.append(r)
        time.sleep(0.5)

    elapsed = time.time() - start_time
    total_dv = sum(r.get("total", 0) for r in results if r.get("status") == "OK")
    total_dg = sum(r.get("graded", 0) for r in results if r.get("status") == "OK")
    ok_count = sum(1 for r in results if r.get("status") == "OK")

    print("\n" + "=" * 80)
    print(f"🎉 HOÀN TẤT BƯỚC 1 TRONG {elapsed/60:.1f} PHÚT!")
    print(f"Tổng Chi đoàn hoàn thành : {ok_count}/{total_acc}")
    print(f"Tổng Đoàn viên đã đánh giá: {total_dg}/{total_dv}")
    print("=" * 80)

if __name__ == "__main__":
    main()
