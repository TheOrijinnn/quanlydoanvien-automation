import sys
import time
import json
from api_client import DoanVienClient, BASE_URL
import config

sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("=" * 80)
    print("BƯỚC 7: DUYỆT XỬ LÝ CẤP THẺ ĐOÀN VIÊN (TÀI KHOẢN ADMIN: yfie.hcmute)")
    print("=" * 80)

    admin_client = DoanVienClient(config.SUPER_ACCOUNT["username"], config.SUPER_ACCOUNT["password"])
    if not admin_client.login():
        print("❌ Đăng nhập Admin thất bại!")
        return

    user_id = admin_client.user_id
    id_tochuc = admin_client.id_tochuc
    print(f"Đăng nhập Admin thành công: {admin_client.ten_tochuc} (ID: {id_tochuc})")

    # Lấy danh sách yêu cầu cấp thẻ
    url_ds = f"{BASE_URL}/ws/api/LichSuBienDong/biendongxuly_dsN_capthe"
    payload_ds = {'data': json.dumps([{'idtochuc': str(id_tochuc)}], separators=(',', ':'))}
    body_ds = json.dumps(payload_ds, separators=(',', ':'))
    headers = {
        'Authorization': f'Bearer {admin_client.token}',
        'X-XSRF-TOKEN': admin_client.get_xsrf(url_ds, body_ds),
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': 'Mozilla/5.0'
    }
    r = admin_client.session.post(url_ds, data=body_ds, headers=headers, timeout=25)
    if r.status_code != 200:
        print(f"❌ Lỗi lấy danh sách yêu cầu ({r.status_code}): {r.text}")
        return

    items = r.json()
    pending_items = [it for it in items if it.get('TRANGTHAI') == 'Đang xử lý']
    print(f"Tổng số yêu cầu cấp thẻ: {len(items)}")
    print(f"Số yêu cầu đang ở trạng thái 'Đang xử lý': {len(pending_items)}")

    if not pending_items:
        print("🎉 Không có yêu cầu nào đang chờ xử lý! Toàn bộ đã được duyệt hoàn tất.")
        return

    url_approve = f"{BASE_URL}/api/LichSuBienDong/luu_xulybiendongCapThe"
    headers_approve = {
        'Authorization': f'Bearer {admin_client.token}',
        'User-Agent': 'Mozilla/5.0'
    }

    success_count = 0
    for idx, item in enumerate(pending_items, 1):
        req_id = item['ID']
        tochuc_yc = item.get('TOCHUCYEUCAU') or item.get('TENTOCHUC')
        print(f"[{idx}/{len(pending_items)}] Đang duyệt yêu cầu của {tochuc_yc} (ID: {req_id})...", end=" ", flush=True)

        xuly_data = {
            'IdXuLy': req_id,
            'MaNhom': item['MANHOM'],
            'dsDoanVien': item['DSDOANVIEN'],
            'IdToChuc': 247294, # Cấp trên Đoàn trường
            'TrangThaiXL': 2, # Chuyển tiếp yêu cầu
            'IdNhanVienNhap': user_id,
            'IdQuyTrinhChiTiet': 234,
            'IdToChucNhap': id_tochuc,
            'loaihinhcapthe': item.get('LOAIHINHCAPTHE') or 'Cấp mới thẻ đoàn viên',
            'idBienDong': 45,
            'Ngay': "22/10/2026",
            'NgayHL': "22/10/2026",
            'NOIDUNG': item.get('NOIDUNG') or 'Cấp mới thẻ đoàn viên',
            'SOQUYETDINH': '',
            'SONGHIQUYET': '',
            'chuyenDonVi': 0,
            'dsfile': '[]',
            'quyetdinh': ''
        }
        form_str = json.dumps(xuly_data, separators=(',', ':'))
        files = {'data': (None, form_str)}

        try:
            res_app = admin_client.session.post(url_approve, files=files, headers=headers_approve, timeout=25)
            if res_app.status_code == 200 and res_app.json().get('success'):
                print("=> [DUYỆT THÀNH CÔNG ✅]")
                success_count += 1
            else:
                print(f"=> [LỖI ❌]: {res_app.text}")
        except Exception as e:
            print(f"=> [LỖI NGOẠI LỆ ❌]: {str(e)}")

        time.sleep(0.4)

    print(f"\n=> Kết quả: Đã duyệt thành công {success_count}/{len(pending_items)} yêu cầu!")

if __name__ == "__main__":
    main()
