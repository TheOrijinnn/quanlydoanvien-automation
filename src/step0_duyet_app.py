import sys
import json
import time
from api_client import DoanVienClient, BASE_URL
import config

sys.stdout.reconfigure(encoding='utf-8')

def process_duyet_app(accounts=config.CHIDOAN_ACCOUNTS, filter_prefix=None):
    if filter_prefix:
        accounts = [(name, acc) for name, acc in accounts if filter_prefix in acc or filter_prefix in name]

    print("=" * 80)
    print(f"BƯỚC 0: DUYỆT THÔNG TIN ĐOÀN VIÊN TỪ APP THANH NIÊN VIỆT NAM")
    print(f"Tổng số Chi đoàn cần kiểm tra: {len(accounts)} chi đoàn")
    print("=" * 80)

    total_approved = 0
    approved_details = []

    for idx, (name, acc) in enumerate(accounts, 1):
        client = DoanVienClient(acc, config.DEFAULT_PASSWORD)
        if not client.login():
            print(f"[{idx:2d}/{len(accounts)}] {name:<22s} ({acc:<15s}) | ❌ Đăng nhập thất bại!")
            continue

        url_list = f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochuc_appn?idToChuc={client.id_tochuc}&trangThai=1"
        payload = {"HOTEN":"","DIENTHOAI":"","CMND":"","EMAIL":""}
        b_str = json.dumps(payload, separators=(',', ':'))
        headers = {
            'Authorization': f'Bearer {client.token}',
            'X-XSRF-TOKEN': client.get_xsrf(url_list, b_str),
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        }

        try:
            res = client.session.post(url_list, data=b_str, headers=headers, timeout=20)
            items = res.json() if res.status_code == 200 else []
        except Exception:
            items = []

        if items:
            print(f"[{idx:2d}/{len(accounts)}] {name:<22s} ({acc:<15s}) | 🔔 Có {len(items)} đoàn viên chờ duyệt!")
            for it in items:
                mid = it.get("ID")
                mname = it.get("HOTEN")
                url_appr = f"{BASE_URL}/ws/api/NhanVienToChuc/duyet_thanhvientochuc_app?id={mid}"
                h_appr = {
                    'Authorization': f'Bearer {client.token}',
                    'X-XSRF-TOKEN': client.get_xsrf(url_appr, ""),
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0'
                }
                res_appr = client.session.post(url_appr, data="", headers=h_appr, timeout=25)
                if res_appr.status_code == 200 and res_appr.json().get("success"):
                    print(f"     ✅ Đã duyệt: {mname} (ID: {mid})")
                    total_approved += 1
                    approved_details.append({"class": name, "account": acc, "name": mname, "id": mid})
                else:
                    print(f"     ⚠️ Lỗi duyệt {mname}: {res_appr.text}")
                time.sleep(0.3)
        else:
            print(f"[{idx:2d}/{len(accounts)}] {name:<22s} ({acc:<15s}) | ⚪ Không có ai chờ duyệt (0)")
        time.sleep(0.2)

    print("\n" + "=" * 80)
    print(f"🎉 TỔNG KẾT DUYỆT TỪ APP:")
    print(f" • Tổng số đoàn viên đã duyệt mới: {total_approved} đoàn viên")
    print("=" * 80 + "\n")
    return {"total_approved": total_approved, "details": approved_details}

def main(filter_prefix=None):
    process_duyet_app(filter_prefix=filter_prefix)

if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else None
    main(prefix)
