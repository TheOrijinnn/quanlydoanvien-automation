import sys
import time
import json
from api_client import DoanVienClient, BASE_URL
import config

sys.stdout.reconfigure(encoding='utf-8')

def get_organizations(client, id_tochuc, year=config.YEAR):
    url = f"{BASE_URL}/ws/api/DanhGia/getDanhGiaNhanVienToChuc"
    payload = {
        "idtochuc": id_tochuc,
        "nam": int(year),
        "dsDanhGia": []
    }
    body_str = json.dumps(payload, separators=(',', ':'))
    xsrf = client.get_xsrf(url, body_str)
    headers = {
        "Authorization": f"Bearer {client.token}",
        "X-XSRF-TOKEN": xsrf,
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0"
    }
    res = client.session.post(url, data=body_str, headers=headers, timeout=25)
    if res.status_code != 200:
        raise Exception(f"Lỗi lấy danh sách tổ chức ({res.status_code}): {res.text}")
    return res.json()

def duyet_tochuc(client, org_id, year=config.YEAR):
    url = f"{BASE_URL}/ws/api/DanhGia/duyetDanhGia"
    payload = {
        "idtochuc": org_id,
        "nam": int(year),
        "dsDanhGia": []
    }
    body_str = json.dumps(payload, separators=(',', ':'))
    xsrf = client.get_xsrf(url, body_str)
    headers = {
        "Authorization": f"Bearer {client.token}",
        "X-XSRF-TOKEN": xsrf,
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0"
    }
    res = client.session.post(url, data=body_str, headers=headers, timeout=25)
    if res.status_code != 200:
        raise Exception(f"Lỗi duyệt tổ chức {org_id} ({res.status_code}): {res.text}")
    res_data = res.json()
    if not res_data.get("success", False):
        raise Exception(f"Duyệt không thành công: {res.text}")
    return True

def main():
    print("=" * 80)
    print(f"BƯỚC 5: DUYỆT NHẬN XÉT ĐÁNH GIÁ ĐOÀN VIÊN NĂM {config.YEAR}")
    print(f"Tài khoản Admin: {config.SUPER_ACCOUNT['username']}")
    print("Quy tắc: CHỈ DUYỆT các hàng có trạng thái 'Đã gửi danh sách đánh giá' (TRANGTHAI = 1)")
    print("         TUYỆT ĐỐI KHÔNG nhấn đánh giá lại các hàng đã duyệt (TRANGTHAI = 2)")
    print("=" * 80)

    admin_client = DoanVienClient(config.SUPER_ACCOUNT["username"], config.SUPER_ACCOUNT["password"])
    if not admin_client.login():
        print("❌ Đăng nhập Admin thất bại!")
        return

    id_tochuc = admin_client.id_tochuc
    print(f"Đăng nhập thành công! Tổ chức admin ID: {id_tochuc}")

    orgs = get_organizations(admin_client, id_tochuc, config.YEAR)
    pending_orgs = [o for o in orgs if o.get("TRANGTHAI") == 1]
    already_approved = [o for o in orgs if o.get("TRANGTHAI") == 2]

    print(f"Tổng số tổ chức trực thuộc: {len(orgs)}")
    print(f" - Số tổ chức ĐÃ DUYỆT từ trước (bỏ qua): {len(already_approved)}")
    print(f" - Số tổ chức ĐANG CHỜ DUYỆT (cần xử lý): {len(pending_orgs)}")
    print("-" * 80)

    if not pending_orgs:
        print("🎉 Không còn tổ chức nào cần duyệt! Toàn bộ đã được duyệt hoàn tất.")
        return

    success_count = 0
    for idx, org in enumerate(pending_orgs, 1):
        org_id = int(org["ID"])
        org_name = org.get("TENTOCHUC", f"ID {org_id}")
        print(f"[{idx}/{len(pending_orgs)}] Đang duyệt: {org_name} (ID: {org_id})...", end=" ", flush=True)
        try:
            duyet_tochuc(admin_client, org_id, config.YEAR)
            print("=> [DUYỆT THÀNH CÔNG ✅]")
            success_count += 1
            time.sleep(0.4)
        except Exception as e:
            print(f"=> [LỖI ❌]: {str(e)}")

    print("\n" + "=" * 80)
    print("ĐỐI SOÁT TRẠNG THÁI CUỐI CÙNG TRÊN HỆ THỐNG")
    print("=" * 80)
    time.sleep(1)
    recheck_orgs = get_organizations(admin_client, id_tochuc, config.YEAR)
    recheck_pending = [o for o in recheck_orgs if o.get("TRANGTHAI") == 1]
    recheck_approved = [o for o in recheck_orgs if o.get("TRANGTHAI") == 2]

    print(f"Tổng số tổ chức: {len(recheck_orgs)}")
    print(f"Số tổ chức ĐÃ DUYỆT (TRANGTHAI = 2): {len(recheck_approved)} / {len(recheck_orgs)}")
    print(f"Số tổ chức CHƯA DUYỆT (TRANGTHAI = 1): {len(recheck_pending)}")

    # --- TỰ ĐỘNG DOUBLE CHECK LẠI SỐ LIỆU ---
    print("\n" + "-" * 80)
    if len(recheck_approved) == len(recheck_orgs):
        print("🔍 [AUTO DOUBLE-CHECK HOÀN TẤT ✅]: 100% Chi đoàn trực thuộc đã được phê duyệt thành công!")
    else:
        print(f"⚠️ [AUTO DOUBLE-CHECK CẢNH BÁO]: Còn {len(recheck_pending)} chi đoàn chưa được duyệt:")
        for po in recheck_pending:
            print(f"   • {po.get('TENTOCHUC')} (ID: {po.get('ID')})")

if __name__ == "__main__":
    main()
