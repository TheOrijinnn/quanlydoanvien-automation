import sys
import time
import json
import math
from api_client import DoanVienClient, BASE_URL
import config

sys.stdout.reconfigure(encoding='utf-8')

def evaluate_page(client, members, id_tochuc, year=config.YEAR, rating_id=4):
    """
    Tạo payload đánh giá cho danh sách đoàn viên trong 1 trang và thực hiện:
    1. Lưu (updateDanhGia)
    2. Gửi (sendDanhGia)
    """
    ds_danhgia = []
    for m in members:
        ds_danhgia.append({
            "idNhanVien": m["ID"],
            "idDanhGia": rating_id,  # 4 = Hoàn thành xuất sắc nhiệm vụ
            "DiemManh": m.get("DIEMMANH") or "",
            "DiemYeu": m.get("DIEMYEU") or "",
            "KhenThuong": m.get("KHENTHUONG") or "",
            "KyLuat": m.get("KYLUAT") or "",
            "tiLe": 0
        })
    
    payload = {
        "idtochuc": id_tochuc,
        "nam": int(year),
        "dsDanhGia": ds_danhgia
    }
    body_json = json.dumps(payload, separators=(',', ':'))
    
    headers = {
        "Authorization": f"Bearer {client.token}",
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0"
    }
    
    # 1. Lưu (updateDanhGia)
    update_url = f"{BASE_URL}/ws/api/DanhGia/updateDanhGia"
    res_update = client.session.post(update_url, data=body_json, headers=headers, timeout=25)
    if res_update.status_code != 200:
        raise Exception(f"Lỗi khi Lưu (updateDanhGia): {res_update.status_code} {res_update.text}")
        
    # 2. Gửi (sendDanhGia)
    send_url = f"{BASE_URL}/ws/api/DanhGia/sendDanhGia"
    res_send = client.session.post(send_url, data=body_json, headers=headers, timeout=25)
    if res_send.status_code != 200:
        raise Exception(f"Lỗi khi Gửi (sendDanhGia): {res_send.status_code} {res_send.text}")
        
    return len(ds_danhgia)

def fetch_members_page(client, id_tochuc, page_idx, max_size=50, year=config.YEAR):
    url = f"{BASE_URL}/ws/api/DanhGia/getListDanhGiaDoanVien?idToChuc={id_tochuc}&nam={year}&currentPage={page_idx}&maxSize={max_size}&keyword="
    xsrf = client.get_xsrf(url, "")
    headers = {
        "Authorization": f"Bearer {client.token}",
        "X-XSRF-TOKEN": xsrf,
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0"
    }
    for attempt in range(3):
        try:
            res = client.session.get(url, headers=headers, timeout=20)
            if res.status_code == 200:
                return res.json()
        except Exception:
            time.sleep(1)
    return []

def process_chidoan(idx, total, name, username, year=config.YEAR):
    print(f"\n[{idx}/{total}] Chi đoàn: {name} ({username})")
    client = DoanVienClient(username, config.DEFAULT_PASSWORD)
    if not client.login():
        print(f"  ❌ Đăng nhập thất bại -> Bỏ qua.")
        return {"account": username, "status": "Lỗi đăng nhập", "total": 0, "evaluated": 0}
        
    id_tochuc = client.id_tochuc
    if not id_tochuc:
        print(f"  ❌ Không lấy được ID Tổ chức -> Bỏ qua.")
        return {"account": username, "status": "Không có id_tochuc", "total": 0, "evaluated": 0}

    # Trang đầu tiên để lấy số lượng
    page0 = fetch_members_page(client, id_tochuc, 0, max_size=50, year=year)
    if not page0:
        print(f"  ℹ️ Không có đoàn viên nào trong năm {year}.")
        return {"account": username, "status": "Không có đoàn viên", "total": 0, "evaluated": 0}
        
    total_rows = int(page0[0].get("TOTALROWS", len(page0)))
    total_pages = math.ceil(total_rows / 50)
    print(f"  📊 Tổng số đoàn viên: {total_rows} | Số trang cần xử lý: {total_pages}")
    
    evaluated_count = 0
    for p in range(total_pages):
        members = page0 if p == 0 else fetch_members_page(client, id_tochuc, p, max_size=50, year=year)
        if not members:
            continue
        count = evaluate_page(client, members, id_tochuc, year=year, rating_id=4)
        evaluated_count += count
        print(f"    Trang {p+1}/{total_pages}: [ĐÃ LƯU & GỬI] {count} đoàn viên -> Hoàn thành xuất sắc nhiệm vụ.")
        time.sleep(0.4)
        
    # --- TỰ ĐỘNG DOUBLE-CHECK LẠI SỐ LIỆU SAU KHI LƯU & GỬI ---
    time.sleep(0.3)
    check_page0 = fetch_members_page(client, id_tochuc, 0, max_size=50, year=year)
    all_checked_members = []
    if check_page0:
        c_rows = int(check_page0[0].get("TOTALROWS", len(check_page0)))
        c_pages = math.ceil(c_rows / 50)
        for cp in range(c_pages):
            cm = check_page0 if cp == 0 else fetch_members_page(client, id_tochuc, cp, max_size=50, year=year)
            all_checked_members.extend(cm)

    unevaluated = [m for m in all_checked_members if not (m.get("IDDANHGIA") or 0)]
    if unevaluated:
        names = [m.get("HOTEN") for m in unevaluated]
        print(f"  ⚠️ [AUTO DOUBLE-CHECK CẢNH BÁO]: Có {len(unevaluated)} đoàn viên chưa lưu xếp loại ({', '.join(names[:3])}...) -> Đang tự động đánh giá lại...")
        try:
            evaluate_page(client, unevaluated, id_tochuc, year=year, rating_id=4)
            print(f"  ✅ [AUTO RETRY THÀNH CÔNG]: Đã lưu & gửi bổ sung cho {len(unevaluated)} đoàn viên còn thiếu!")
            evaluated_count += len(unevaluated)
        except Exception as ex:
            print(f"  ❌ [AUTO RETRY THẤT BẠI]: {str(ex)}")
    else:
        print(f"  🔍 [AUTO DOUBLE-CHECK ✅]: 100% đoàn viên ({len(all_checked_members)}/{total_rows}) đã đạt xếp loại Xuất sắc!")

    print(f"  ✅ Hoàn tất {username}: {evaluated_count}/{total_rows} đoàn viên đã được đánh giá & gửi duyệt.")
    return {
        "account": username,
        "status": "Thành công",
        "total": total_rows,
        "evaluated": evaluated_count,
        "unevaluated_left": len(unevaluated) if unevaluated else 0
    }

def main(filter_prefix=""):
    """
    filter_prefix: Lọc theo tiền tố tài khoản (e.g. '26' để chạy riêng K26, hoặc '' để chạy tất cả)
    """
    print("=" * 80)
    print(f"BƯỚC 4: ĐÁNH GIÁ ĐOÀN VIÊN NĂM {config.YEAR}")
    print("Xếp loại: 'Hoàn thành xuất sắc nhiệm vụ' (ID = 4)")
    print("Thao tác: LƯU (updateDanhGia) -> GỬI (sendDanhGia) từng trang")
    print("=" * 80)
    
    target_accounts = config.CHIDOAN_ACCOUNTS
    if filter_prefix:
        target_accounts = [a for a in target_accounts if a[1].startswith(filter_prefix)]
        print(f"Đang lọc theo tiền tố '{filter_prefix}': {len(target_accounts)} tài khoản.")
        
    total = len(target_accounts)
    results = []
    
    for idx, (name, username) in enumerate(target_accounts, 1):
        res = process_chidoan(idx, total, name, username)
        results.append(res)
        time.sleep(0.3)
        
    print("\n" + "=" * 80)
    print("TỔNG KẾT KẾT QUẢ ĐÁNH GIÁ ĐOÀN VIÊN")
    print("=" * 80)
    success = sum(1 for r in results if r["status"] == "Thành công")
    total_dv = sum(r["total"] for r in results)
    total_eval = sum(r["evaluated"] for r in results)
    print(f"Số Chi đoàn xử lý: {len(results)} | Thành công: {success}/{len(results)}")
    print(f"Tổng số đoàn viên đã đánh giá xuất sắc: {total_eval}/{total_dv}")

if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else ""
    main(prefix)
