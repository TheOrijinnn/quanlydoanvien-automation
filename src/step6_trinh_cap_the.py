import sys
import time
import json
from api_client import DoanVienClient, BASE_URL
import config

sys.stdout.reconfigure(encoding='utf-8')

def submit_card_batch(client, id_tochuc_captren, id_quytrinh, member_list, loaihinh):
    timestamp = int(time.time() * 1000)
    manhom = f"{client.user_id}{timestamp}"
    now_iso = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())

    dsdv = []
    for m in member_list:
        dsdv.append({
            'IDNHANVIEN': m['IDNHANVIEN'],
            'HOTEN': m['HOTEN'],
            'NGAYSINH': m.get('NGAYSINH', ''),
            'NGAYVAODOAN': m.get('NGAYVAODOAN', ''),
            'IDTINHTHANH': m.get('IDTINHTHANH') or m.get('QUEQUANTINHTHANH') or 0,
            'SOTHEDOAN': m.get('SOTHEDOAN', ''),
            'DUYET': 1
        })

    en = {
        'idbiendong': 45,
        'quyetdinh': "",
        'ngay': now_iso,
        'idloaihtc': client.id_loaihtc,
        'idtochuc': id_tochuc_captren,
        'noidung': loaihinh,
        'trangthaixl': 2, # Chuyển xử lý
        'idnhanviennhap': client.user_id,
        'idtochucnhap': client.id_tochuc,
        'idquytrinhchitiet': id_quytrinh,
        'manhom': manhom,
        'dsfile': "[]",
        'dsdoanvien': json.dumps(dsdv, separators=(',', ':')),
        'loaihinhcapthe': loaihinh
    }

    data_str = json.dumps(en, separators=(',', ':'))
    url_submit = f"{BASE_URL}/ws/api/LichSuBienDong/biendongxuly_nhap"
    form_dict = {'data': data_str}
    xe = "[FORMDATA]" + json.dumps(form_dict, separators=(',', ':'))

    submit_headers = {
        'Authorization': f'Bearer {client.token}',
        'X-XSRF-TOKEN': client.get_xsrf(url_submit, xe),
        'User-Agent': 'Mozilla/5.0'
    }
    files = {'data': (None, data_str)}

    res_sub = client.session.post(url_submit, files=files, headers=submit_headers, timeout=25)
    if res_sub.status_code == 200 and res_sub.json().get('success'):
        idxuly = res_sub.json().get('idxuly')
        return True, idxuly, len(dsdv)
    return False, res_sub.text, len(dsdv)

def process_single_chidoan(idx, total, name, username):
    client = DoanVienClient(username, config.DEFAULT_PASSWORD)
    if not client.login():
        print(f"[{idx:2d}/{total}] {name:<22s} ({username:<15s}) | ❌ Lỗi đăng nhập -> [BỎ QUA]")
        return {"account": username, "status": "Lỗi đăng nhập", "new": 0, "re": 0}

    # 1. Kiểm tra danh sách Cấp mới & Cấp lại
    p_m = {'IdToChuc': client.id_tochuc, 'IdBienDong': 45, 'IdQuanHuyen': 0, 'IdPhuongXa': 0}
    b_m = json.dumps(p_m, separators=(',', ':'))

    # Cấp mới
    h_new = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendong_capthe", b_m), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    res_new = client.session.post(f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendong_capthe", data=b_m, headers=h_new, timeout=20)
    list_new = res_new.json() if res_new.status_code == 200 else []

    # Cấp lại
    h_re = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendongCoSoThe", b_m), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    res_re = client.session.post(f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendongCoSoThe", data=b_m, headers=h_re, timeout=20)
    list_re = res_re.json() if res_re.status_code == 200 else []

    # Kiểm tra lịch sử để không gửi trùng lặp
    url_h = f"{BASE_URL}/ws/api/LichSuBienDong/biendongxulynvnhap_dsN"
    p_h = {'IdNhanVienNhap': client.user_id, 'TrangThaiXL': 0}
    b_h = json.dumps(p_h, separators=(',', ':'))
    h_h = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_h, b_h), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    res_h = client.session.post(url_h, data=b_h, headers=h_h, timeout=20)
    history = res_h.json() if res_h.status_code == 200 else []

    already_submitted_ids = set()
    for req in history:
        try:
            ds = json.loads(req.get('DSDOANVIEN', '[]'))
            for m in ds:
                already_submitted_ids.add(m.get('IDNHANVIEN'))
        except Exception:
            pass

    pending_new = [m for m in list_new if m.get('IDNHANVIEN') not in already_submitted_ids]
    pending_re = [m for m in list_re if m.get('IDNHANVIEN') not in already_submitted_ids]

    if not pending_new and not pending_re:
        print(f"[{idx:2d}/{total}] {name:<22s} ({username:<15s}) | ⚪ Đã có thẻ đầy đủ hoặc đã tạo yêu cầu từ trước (0 ĐV)")
        return {"account": username, "status": "Đã có thẻ đầy đủ", "new": 0, "re": 0}

    # Lấy thông tin tổ chức cấp trên
    url_captren = f"{BASE_URL}/ws/api/LichSuBienDong/ds_ToChucCapTren"
    p_ct = {'IdToChuc': client.id_tochuc}
    b_ct = json.dumps(p_ct, separators=(',', ':'))
    h_ct = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_captren, b_ct), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    res_ct = client.session.post(url_captren, data=b_ct, headers=h_ct, timeout=20)
    captren_list = res_ct.json() if res_ct.status_code == 200 else []
    if not captren_list:
        print(f"[{idx:2d}/{total}] {name:<22s} ({username:<15s}) | ❌ Không tìm thấy cấp trên")
        return {"account": username, "status": "Không có cấp trên", "new": 0, "re": 0}

    id_tochuc_captren = captren_list[0]['ID']
    id_captc_captren = captren_list[0]['IDCAPTC']

    # Lấy cấu hình quy trình chi tiết
    url_captochuc = f"{BASE_URL}/ws/api/QuyTrinh/quytrinh_chitiet_cauhinh"
    p_cptc = {'IdBienDong': 45, 'IdCapToChuc': client.id_captc, 'IdLoaiHTC': client.id_loaihtc, 'IdLoaiHTCBDong': 1}
    b_cptc = json.dumps(p_cptc, separators=(',', ':'))
    h_cptc = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_captochuc, b_cptc), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    res_cptc = client.session.post(url_captochuc, data=b_cptc, headers=h_cptc, timeout=20)
    cauhinh = res_cptc.json() if res_cptc.status_code == 200 else []
    qt_match = next((q for q in cauhinh if q.get('IDCAPTOCHUC') == id_captc_captren), None)
    id_quytrinh = qt_match['ID'] if qt_match else 232

    created_new = 0
    created_re = 0

    if pending_new:
        ok, res_id, count = submit_card_batch(client, id_tochuc_captren, id_quytrinh, pending_new, "Cấp mới thẻ đoàn viên")
        if ok:
            created_new = count
        time.sleep(0.3)

    if pending_re:
        ok, res_id, count = submit_card_batch(client, id_tochuc_captren, id_quytrinh, pending_re, "Cấp lại thẻ đoàn viên")
        if ok:
            created_re = count
        time.sleep(0.3)

    print(f"[{idx:2d}/{total}] {name:<22s} ({username:<15s}) | ✅ Trình cấp mới: {created_new:2d} ĐV | Trình cấp lại: {created_re:2d} ĐV")
    return {"account": username, "status": "Đã chuyển xử lý", "new": created_new, "re": created_re}

def main(filter_prefix=None):
    accounts = config.CHIDOAN_ACCOUNTS
    if filter_prefix:
        accounts = [(name, acc) for name, acc in accounts if filter_prefix in acc or filter_prefix in name]

    print("=" * 80)
    print("BƯỚC 6: TRÌNH CẤP THẺ ĐOÀN VIÊN (CẤP MỚI & CẤP LẠI)")
    print(f"Tổng số Chi đoàn xử lý: {len(accounts)} chi đoàn")
    print("=" * 80)

    total = len(accounts)
    results = []

    for idx, (name, username) in enumerate(accounts, 1):
        res = process_single_chidoan(idx, total, name, username)
        results.append(res)
        time.sleep(0.3)

    print("\n" + "=" * 80)
    print("TỔNG KẾT BƯỚC TRÌNH CẤP THẺ ĐOÀN VIÊN")
    print("=" * 80)
    tot_new = sum(r["new"] for r in results)
    tot_re = sum(r["re"] for r in results)
    print(f"Tổng đoàn viên trình Cấp mới : {tot_new} đoàn viên")
    print(f"Tổng đoàn viên trình Cấp lại : {tot_re} đoàn viên")
    print(f"Tổng cộng đã tạo tờ trình   : {tot_new + tot_re} đoàn viên")
    print("=" * 80 + "\n")
    return {"total_new": tot_new, "total_re": tot_re}

if __name__ == "__main__":
    prefix = sys.argv[1] if len(sys.argv) > 1 else None
    main(prefix)
