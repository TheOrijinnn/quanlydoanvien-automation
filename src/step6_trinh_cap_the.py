import sys
import time
import json
from api_client import DoanVienClient, BASE_URL
import config

sys.stdout.reconfigure(encoding='utf-8')

def process_single_chidoan(idx, total, name, username):
    client = DoanVienClient(username, config.DEFAULT_PASSWORD)
    if not client.login():
        print(f"[{idx}/{total}] {name} ({username}): Lỗi đăng nhập -> [BỎ QUA]")
        return {"account": username, "status": "Lỗi đăng nhập", "members": 0}

    user_id = client.user_id
    id_tochuc = client.id_tochuc
    id_captc = client.id_captc
    id_loaihtc = client.id_loaihtc
    tai_khoan = client.tai_khoan

    headers = {
        'Authorization': f'Bearer {client.token}',
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': 'Mozilla/5.0'
    }

    # 1. Kiểm tra danh sách đoàn viên cần cấp thẻ trực tiếp từ hệ thống
    url_members = f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendong_capthe"
    payload_m = {'IdToChuc': id_tochuc, 'IdBienDong': 45, 'IdQuanHuyen': 0, 'IdPhuongXa': 0}
    body_m = json.dumps(payload_m, separators=(',', ':'))
    headers['X-XSRF-TOKEN'] = client.get_xsrf(url_members, body_m)
    res_m = client.session.post(url_members, data=body_m, headers=headers, timeout=20)
    members = res_m.json() if res_m.status_code == 200 else []

    if not members:
        print(f"[{idx}/{total}] {name} ({username}): ✅ Đã có thẻ đầy đủ (0 ĐV cần cấp mới) -> [BỎ QUA]")
        return {"account": username, "status": "Đã có thẻ đầy đủ", "members": 0}

    member_names = [m.get('HOTEN') for m in members]
    print(f"[{idx}/{total}] {name} ({username}): ⚠️ Phát hiện {len(members)} đoàn viên chưa có thẻ: {', '.join(member_names)}")

    # 2. Lấy thông tin tổ chức cấp trên
    url_captren = f"{BASE_URL}/ws/api/LichSuBienDong/ds_ToChucCapTren"
    payload_ct = {'IdToChuc': id_tochuc}
    body_ct = json.dumps(payload_ct, separators=(',', ':'))
    headers['X-XSRF-TOKEN'] = client.get_xsrf(url_captren, body_ct)
    res_ct = client.session.post(url_captren, data=body_ct, headers=headers, timeout=20)
    captren_list = res_ct.json() if res_ct.status_code == 200 else []
    if not captren_list:
        print(f"[{idx}/{total}] {name} ({username}): Không tìm thấy cấp trên -> [BỎ QUA]")
        return {"account": username, "status": "Không có cấp trên", "members": 0}
    captren = captren_list[0]
    id_tochuc_captren = captren['ID']
    id_captc_captren = captren['IDCAPTC']

    # 3. Lấy cấu hình quy trình chi tiết
    url_captochuc = f"{BASE_URL}/ws/api/QuyTrinh/quytrinh_chitiet_cauhinh"
    payload_cptc = {'IdBienDong': 45, 'IdCapToChuc': id_captc, 'IdLoaiHTC': id_loaihtc, 'IdLoaiHTCBDong': 1}
    body_cptc = json.dumps(payload_cptc, separators=(',', ':'))
    headers['X-XSRF-TOKEN'] = client.get_xsrf(url_captochuc, body_cptc)
    res_cptc = client.session.post(url_captochuc, data=body_cptc, headers=headers, timeout=20)
    cauhinh = res_cptc.json() if res_cptc.status_code == 200 else []
    qt_match = next((q for q in cauhinh if q.get('IDCAPTOCHUC') == id_captc_captren), None)
    id_quytrinh = qt_match['ID'] if qt_match else (cauhinh[0]['ID'] if cauhinh else 232)

    # Tự động chọn tất cả đoàn viên trong popup
    dsdv = []
    for m in members:
        dsdv.append({
            'IDNHANVIEN': m['IDNHANVIEN'],
            'HOTEN': m['HOTEN'],
            'NGAYSINH': m['NGAYSINH'],
            'NGAYVAODOAN': m['NGAYVAODOAN'],
            'IDTINHTHANH': m.get('IDTINHTHANH') or m.get('QUEQUANTINHTHANH') or 0,
            'DUYET': 1
        })

    # 5. Gửi yêu cầu chuyển xử lý (Cấp mới thẻ đoàn viên)
    timestamp = int(time.time() * 1000)
    manhom = f"{user_id}{timestamp}"
    now_iso = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())

    en = {
        'idbiendong': 45,
        'quyetdinh': "",
        'ngay': now_iso,
        'idloaihtc': id_loaihtc,
        'idtochuc': id_tochuc_captren,
        'noidung': "Cấp mới thẻ đoàn viên",
        'trangthaixl': 2, # Chuyển xử lý
        'idnhanviennhap': user_id,
        'idtochucnhap': id_tochuc,
        'idquytrinhchitiet': id_quytrinh,
        'manhom': manhom,
        'dsfile': "[]",
        'dsdoanvien': json.dumps(dsdv, separators=(',', ':')),
        'loaihinhcapthe': "Cấp mới thẻ đoàn viên"
    }

    data_str = json.dumps(en, separators=(',', ':'))
    url_submit = f"{BASE_URL}/ws/api/LichSuBienDong/biendongxuly_nhap"
    form_dict = {'data': data_str}
    xe = "[FORMDATA]" + json.dumps(form_dict, separators=(',', ':'))
    xsrf_submit = client.get_xsrf(url_submit, xe)

    submit_headers = {
        'Authorization': f'Bearer {client.token}',
        'X-XSRF-TOKEN': xsrf_submit,
        'User-Agent': 'Mozilla/5.0'
    }
    files = {'data': (None, data_str)}

    res_sub = client.session.post(url_submit, files=files, headers=submit_headers, timeout=25)
    if res_sub.status_code == 200 and res_sub.json().get('success'):
        idxuly = res_sub.json().get('idxuly')
        print(f"[{idx}/{total}] {name} ({username}): [THÀNH CÔNG ✅] Đã trình cấp mới thẻ cho {len(dsdv)} đoàn viên (ID: {idxuly})")

        # --- TỰ ĐỘNG DOUBLE CHECK LẠI SỐ LIỆU ---
        time.sleep(0.3)
        res_check = client.session.post(url_history, data=body_h, headers=headers, timeout=20)
        confirmed = False
        if res_check.status_code == 200:
            chk_history = res_check.json()
            confirmed = any(it.get('IDBIENDONG') == 45 for it in chk_history)
        if confirmed:
            print(f"      🔍 [AUTO DOUBLE-CHECK ✅]: Yêu cầu cấp thẻ đã được hệ thống ghi nhận thành công!")
        else:
            print(f"      ⚠️ [AUTO DOUBLE-CHECK CẢNH BÁO]: Chưa tìm thấy bản ghi lịch sử, vui lòng kiểm tra lại!")

        return {"account": username, "status": "Đã chuyển xử lý", "members": len(dsdv), "idxuly": idxuly}
    else:
        print(f"[{idx}/{total}] {name} ({username}): [LỖI ❌] {res_sub.text}")
        return {"account": username, "status": f"Lỗi gửi: {res_sub.text}", "members": len(dsdv)}

def main():
    print("=" * 80)
    print("BƯỚC 6: TRÌNH CẤP MỚI THẺ ĐOÀN VIÊN (CÁC CHI ĐOÀN)")
    print("Loại hình: 'Cấp mới thẻ đoàn viên' | Trạng thái: Chuyển xử lý")
    print("Tự động bỏ qua các lớp đã xử lý theo danh sách quy định")
    print("=" * 80)

    total = len(config.CHIDOAN_ACCOUNTS)
    results = []

    for idx, (name, username) in enumerate(config.CHIDOAN_ACCOUNTS, 1):
        res = process_single_chidoan(idx, total, name, username)
        results.append(res)
        time.sleep(0.3)

    print("\n" + "=" * 80)
    print("TỔNG KẾT BƯỚC TRÌNH CẤP THẺ ĐOÀN VIÊN")
    print("=" * 80)
    success = [r for r in results if r["status"] == "Đã chuyển xử lý"]
    total_members = sum(r["members"] for r in success)
    print(f"Số Chi đoàn tạo yêu cầu mới thành công: {len(success)}")
    print(f"Tổng số đoàn viên được trình cấp thẻ: {total_members}")

if __name__ == "__main__":
    main()
