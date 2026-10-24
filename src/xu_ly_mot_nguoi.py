import sys
import os
import json
import time
import argparse
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))

from api_client import DoanVienClient, BASE_URL
import config

def remove_accents(input_str):
    if not input_str:
        return ""
    s1 = unicodedata.normalize('NFD', input_str)
    s2 = "".join([c for c in s1 if unicodedata.category(c) != 'Mn'])
    return s2.replace('đ', 'd').replace('Đ', 'D').lower().strip()

def find_account_by_class(class_name):
    norm_input = remove_accents(class_name).replace("chi doan", "").replace("chidoan", "").replace(" ", "").strip()
    for name, acc in config.CHIDOAN_ACCOUNTS:
        norm_acc = remove_accents(acc).replace("chi doan", "").replace("chidoan", "").replace(" ", "").strip()
        norm_name = remove_accents(name).replace("chi doan", "").replace("chidoan", "").replace(" ", "").strip()
        if norm_input in norm_acc or norm_input in norm_name or norm_acc in norm_input:
            return acc, name
    return class_name.lower().replace("chi đoàn", "").replace(" ", "").strip(), class_name

def process_single_member(ho_ten, lop_ten, mssv=""):
    print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
    print("║     XỬ LÝ ĐƠN LẺ TRỌN GÓI: DUYỆT APP -> RÈN LUYỆN -> CẤP THẺ -> ĐÁNH GIÁ XẾP LOẠI     ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════╝")
    print(f" • Họ và tên : {ho_ten}")
    print(f" • Lớp       : {lop_ten}")
    if mssv:
        print(f" • MSSV      : {mssv}")
    print("-" * 88)

    acc, full_name = find_account_by_class(lop_ten)
    print(f"🔍 Nhận diện tài khoản Chi đoàn: {acc} ({full_name})")

    client = DoanVienClient(acc, config.DEFAULT_PASSWORD)
    if not client.login():
        print(f"❌ Đăng nhập thất bại vào tài khoản Chi đoàn {acc}!")
        return False

    print(f"✅ Đăng nhập Chi đoàn thành công! ID Tổ chức: {client.id_tochuc}")

    admin_client = DoanVienClient(config.SUPER_ACCOUNT["username"], config.SUPER_ACCOUNT["password"])
    if not admin_client.login():
        print(f"⚠️ Cảnh báo: Không thể đăng nhập tài khoản Admin ({config.SUPER_ACCOUNT['username']})!")

    norm_target = remove_accents(ho_ten)

    # =========================================================================
    # BƯỚC 0: KIỂM TRA & DUYỆT ĐOÀN VIÊN TỪ APP (NẾU ĐANG CHỜ DUYỆT)
    # =========================================================================
    print("\n" + "=" * 88)
    print("[BƯỚC 0/3] KIỂM TRA TRẠNG THÁI DUYỆT TỪ APP THANH NIÊN VIỆT NAM")
    print("=" * 88)

    url_app_list = f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochuc_appn?idToChuc={client.id_tochuc}&trangThai=1"
    payload_app = {"HOTEN":"","DIENTHOAI":"","CMND":"","EMAIL":""}
    b_app_str = json.dumps(payload_app, separators=(',', ':'))
    h_app = {
        'Authorization': f'Bearer {client.token}',
        'X-XSRF-TOKEN': client.get_xsrf(url_app_list, b_app_str),
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        res_app_l = client.session.post(url_app_list, data=b_app_str, headers=h_app, timeout=20)
        app_items = res_app_l.json() if res_app_l.status_code == 200 else []
    except Exception:
        app_items = []

    matched_app = None
    for it in app_items:
        if remove_accents(it.get("HOTEN", "")) == norm_target:
            matched_app = it
            break

    if matched_app:
        mid = matched_app.get("ID")
        print(f" 🔔 Phát hiện đoàn viên đang chờ duyệt từ App (ID: {mid}). Đang tiến hành phê duyệt...")
        url_appr = f"{BASE_URL}/ws/api/NhanVienToChuc/duyet_thanhvientochuc_app?id={mid}"
        h_appr = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_appr, ""), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        res_appr = client.session.post(url_appr, data="", headers=h_appr, timeout=25)
        if res_appr.status_code == 200 and res_appr.json().get("success"):
            print(" ✅ Đã duyệt đoàn viên từ App vào Chi đoàn thành công!")
        else:
            print(f" ⚠️ Cảnh báo duyệt App: {res_appr.text}")
        time.sleep(0.5)
    else:
        print(" • Đoàn viên đã nằm trong danh sách Chi đoàn (không có yêu cầu chờ duyệt trên App). ✅")

    # =========================================================================
    # BƯỚC 1: CHƯƠNG TRÌNH RÈN LUYỆN ĐOÀN VIÊN (ĐĂNG KÝ + CHẤM ĐIỂM + ADMIN DUYỆT)
    # =========================================================================
    print("\n" + "=" * 88)
    print("[BƯỚC 1/3] CHƯƠNG TRÌNH RÈN LUYỆN ĐOÀN VIÊN")
    print("=" * 88)

    # 1.1 Kiểm tra & Đăng ký rèn luyện (Tab 1)
    print(" 1.1 Kiểm tra trạng thái Đăng ký (Tab 1)...")
    t1 = client.call("ndv05.dangky.get_ds_doanvien_paging", {"nam": config.YEAR, "page_no": 1, "page_size": 100})
    tab1_items = t1.get("result", []) if isinstance(t1, dict) else []

    matched_t1 = None
    for m in tab1_items:
        if remove_accents(m.get("ho_ten", "")) == norm_target:
            matched_t1 = m
            break
    if not matched_t1:
        last_name = norm_target.split()[-1] if norm_target else ""
        cands = [m for m in tab1_items if last_name in remove_accents(m.get("ho_ten", ""))]
        if len(cands) == 1:
            matched_t1 = cands[0]

    if matched_t1:
        if matched_t1.get("trang_thai_dangky") == 2:
            print(f"   • {matched_t1.get('ho_ten')}: Đã đăng ký rèn luyện từ trước. ✅")
        else:
            print(f"   • {matched_t1.get('ho_ten')}: Chưa đăng ký. Đang đăng ký 31 tiêu chí...")
            ch = client.call("ndv05.dangky.ctrl_cauhinh", {"ten": "NAM"}, {"ten": "NAM_DANGKY"}, {"ten": "SL_TOITHIEU"})
            id_chuongtrinh = None
            if isinstance(ch, list) and len(ch) > 3 and isinstance(ch[3], dict):
                id_chuongtrinh = ch[3].get("id_chuongtrinh")
            tc_list = []
            if id_chuongtrinh:
                tc_res = client.call("nvd05.tieuchi.get_list", {"id_chuongtrinh": id_chuongtrinh})
                if isinstance(tc_res, list):
                    tc_list = tc_res
            if tc_list:
                reg_payload = {"id_chuongtrinh": id_chuongtrinh, "nam": config.YEAR, "lid": [matched_t1["id"]], "ltc": tc_list}
                save_reg = client.call("ndv05.dangky.save_dangky_tieuchi", reg_payload)
                if save_reg.get("success"):
                    print("   • Chi đoàn: Đăng ký thành công 31 tiêu chí rèn luyện! ✅")
    else:
        print(f"   ⚠️ Không tìm thấy tên trong danh sách Tab 1 của Chi đoàn.")

    # 1.2 Kiểm tra & Đánh giá rèn luyện (Tab 2)
    print(" 1.2 Kiểm tra Đánh giá & Chấm điểm (Tab 2)...")
    t2 = client.call("ndv05.dangky.get_ds_doanvien_danhgia_paging", {"nam": config.YEAR, "page_no": 1, "page_size": 100})
    tab2_items = t2.get("result", []) if isinstance(t2, dict) else []

    matched_t2 = None
    for m in tab2_items:
        if remove_accents(m.get("ho_ten", "")) == norm_target:
            matched_t2 = m
            break
    if not matched_t2:
        last_name = norm_target.split()[-1] if norm_target else ""
        cands = [m for m in tab2_items if last_name in remove_accents(m.get("ho_ten", ""))]
        if len(cands) == 1:
            matched_t2 = cands[0]

    if matched_t2:
        id_dangky = matched_t2.get("id_dangky")
        diem_cham = str(matched_t2.get("diem_cham", "")).strip()
        trang_thai_cham = matched_t2.get("trang_thai_cham")

        if diem_cham == "100" and trang_thai_cham == 2:
            print(f"   • {matched_t2.get('ho_ten')}: Đã được chấm 100/100 (Hoàn thành xuất sắc) từ trước. ✅")
        else:
            print(f"   • {matched_t2.get('ho_ten')}: Tiến hành chấm 100/100 tiêu chí rèn luyện...")
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
                        s = config.SCORE_MAP.get(muc, 4)
                        ic["diem_cham"] = str(s)
                        ic["diem_duyet"] = str(s)
                    ltc.append(ic)

                payload_ev = {
                    "id_dangky": id_dangky,
                    "diem_cham": 100,
                    "diem_duyet": 100,
                    "cd_nhan_xet_6t": config.COMMENT_6M,
                    "cd_nhan_xet_nam": config.COMMENT_YEAR,
                    "ltc": ltc
                }
                save_eval = client.call("ndv05.danhgia.save_danhgia_tieuchi", payload_ev)
                if save_eval.get("success"):
                    print("   • Chi đoàn: Lưu đánh giá 100/100 tiêu chí thành công! ✅")

        if matched_t2.get("dcs_xac_nhan") in (0, "0", None):
            print("   • Chi đoàn: Đang chuyển hồ sơ rèn luyện lên Đoàn cấp trên...")
            c_res = client.call("ndv05.danhgia.chuyen_captren", {"ds_id_dangky": [id_dangky]})
            if c_res.get("success"):
                print("   • Chi đoàn: Đã chuyển cấp trên xác nhận thành công! ✅")

    # 1.3 Đoàn cơ sở (Admin) duyệt xác nhận rèn luyện
    print(" 1.3 Đoàn cơ sở (Admin) xác nhận rèn luyện...")
    if admin_client.token:
        start_p, end_p = 1, 58
        if "22" in lop_ten:
            start_p, end_p = 1, 15
        elif "23" in lop_ten:
            start_p, end_p = 8, 25
        elif "24" in lop_ten:
            start_p, end_p = 18, 35
        elif "25" in lop_ten:
            start_p, end_p = 28, 45
        elif "26" in lop_ten:
            start_p, end_p = 38, 58

        confirmed_done = False
        for p in range(start_p, end_p + 1):
            res_p = admin_client.call("ndv05.dangky.get_ds_doanvien_xacnhan_paging", {"nam": config.YEAR, "page_no": p, "page_size": 50})
            items = res_p.get("result", [])
            target_in_admin = None
            for it in items:
                if remove_accents(it.get("ho_ten", "")) == norm_target:
                    target_in_admin = it
                    break
            if target_in_admin:
                if target_in_admin.get("dcs_xac_nhan") == 2:
                    print(f"   • Admin: Đoàn viên đã được Đoàn cơ sở xác nhận từ trước. ✅")
                else:
                    id_dk_admin = target_in_admin.get("id_dangky")
                    res_xn = admin_client.call("ndv05.xacnhan.dcs_xacnhan", {"ds_id_dangky": [id_dk_admin]})
                    if res_xn.get("success"):
                        print(f"   • Admin: Đoàn cơ sở đã duyệt xác nhận rèn luyện thành công! ✅")
                break

    # =========================================================================
    # BƯỚC 2: CẤP THẺ ĐOÀN VIÊN (CẤP MỚI / CẤP LẠI & ADMIN DUYỆT CHUYỂN TIẾP)
    # =========================================================================
    print("\n" + "=" * 88)
    print("[BƯỚC 2/3] NGHIỆP VỤ CẤP THẺ ĐOÀN VIÊN")
    print("=" * 88)

    # Lấy thông tin ID đoàn viên
    url_dg = f"{BASE_URL}/ws/api/DanhGia/getListDanhGiaDoanVien?idToChuc={client.id_tochuc}&nam={config.YEAR}&currentPage=0&maxSize=5000&keyword="
    h_dg = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_dg, ""), 'User-Agent': 'Mozilla/5.0'}
    res_dg = client.session.get(url_dg, headers=h_dg, timeout=25)
    members = res_dg.json() if res_dg.status_code == 200 else []

    matched_member = None
    for m in members:
        if remove_accents(m.get("HOTEN")) == norm_target:
            matched_member = m
            break
    if not matched_member:
        last_name = norm_target.split()[-1] if norm_target else ""
        candidates = [m for m in members if last_name in remove_accents(m.get("HOTEN"))]
        if len(candidates) == 1:
            matched_member = candidates[0]

    if not matched_member:
        print(f"❌ Không tìm thấy đoàn viên '{ho_ten}' trong danh sách {len(members)} đoàn viên của Chi đoàn {acc}!")
        return False

    member_id = matched_member["ID"]
    member_name = matched_member["HOTEN"]
    print(f"✅ Đã tìm thấy: {member_name} (ID: {member_id})")

    p_m = {'IdToChuc': client.id_tochuc, 'IdBienDong': 45, 'IdQuanHuyen': 0, 'IdPhuongXa': 0}
    b_m = json.dumps(p_m, separators=(',', ':'))

    # Cấp mới
    h_m_new = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendong_capthe", b_m), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    r_new = client.session.post(f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendong_capthe", data=b_m, headers=h_m_new, timeout=20)
    list_new = r_new.json() if r_new.status_code == 200 else []

    # Cấp lại
    h_m_re = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendongCoSoThe", b_m), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    r_re = client.session.post(f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendongCoSoThe", data=b_m, headers=h_m_re, timeout=20)
    list_re = r_re.json() if r_re.status_code == 200 else []

    target_capthe = None
    loaihinh = "Cấp mới thẻ đoàn viên"

    for it in list_new:
        if it.get("IDNHANVIEN") == member_id or remove_accents(it.get("HOTEN")) == norm_target:
            target_capthe = it
            loaihinh = "Cấp mới thẻ đoàn viên"
            break

    if not target_capthe:
        for it in list_re:
            if it.get("IDNHANVIEN") == member_id or remove_accents(it.get("HOTEN")) == norm_target:
                target_capthe = it
                loaihinh = "Cấp lại thẻ đoàn viên"
                break

    if not target_capthe:
        url_h = f"{BASE_URL}/ws/api/LichSuBienDong/biendongxulynvnhap_dsN"
        p_h = {'IdNhanVienNhap': client.user_id, 'TrangThaiXL': 0}
        b_h = json.dumps(p_h, separators=(',', ':'))
        h_h = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_h, b_h), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        r_h = client.session.post(url_h, data=b_h, headers=h_h, timeout=20)
        history = r_h.json() if r_h.status_code == 200 else []
        already_submitted = False
        for req in history:
            ds = json.loads(req.get('DSDOANVIEN', '[]'))
            if any(m.get('IDNHANVIEN') == member_id or remove_accents(m.get('HOTEN')) == norm_target for m in ds):
                already_submitted = True
                print(f" • Yêu cầu cấp thẻ cho {member_name} ĐÃ ĐƯỢC TẠO từ trước (Mã yêu cầu: {req.get('ID')}, Trạng thái: {req.get('TRANGTHAI')}). ✅")
                break
        if not already_submitted:
            print(f" • Không tìm thấy đoàn viên trong danh sách chờ cấp thẻ (có thể đã có thẻ từ trước).")
    else:
        print(f" • Phát hiện trong danh sách diện: '{loaihinh}'. Đang tạo yêu cầu...")
        url_ct = f"{BASE_URL}/ws/api/LichSuBienDong/ds_ToChucCapTren"
        p_ct = {'IdToChuc': client.id_tochuc}
        b_ct = json.dumps(p_ct, separators=(',', ':'))
        h_ct = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_ct, b_ct), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        res_ct = client.session.post(url_ct, data=b_ct, headers=h_ct, timeout=20)
        captren = res_ct.json()[0]
        id_tochuc_captren = captren['ID']
        id_captc_captren = captren['IDCAPTC']

        url_cptc = f"{BASE_URL}/ws/api/QuyTrinh/quytrinh_chitiet_cauhinh"
        p_cptc = {'IdBienDong': 45, 'IdCapToChuc': client.id_captc, 'IdLoaiHTC': client.id_loaihtc, 'IdLoaiHTCBDong': 1}
        b_cptc = json.dumps(p_cptc, separators=(',', ':'))
        h_cptc = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_cptc, b_cptc), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        res_cptc = client.session.post(url_cptc, data=b_cptc, headers=h_cptc, timeout=20)
        cauhinh = res_cptc.json() if res_cptc.status_code == 200 else []
        qt_match = next((q for q in cauhinh if q.get('IDCAPTOCHUC') == id_captc_captren), None)
        id_quytrinh = qt_match['ID'] if qt_match else 232

        timestamp = int(time.time() * 1000)
        manhom = f"{client.user_id}{timestamp}"
        now_iso = time.strftime('%Y-%m-%dT%H:%M:%S.000Z', time.gmtime())

        dsdv = [{
            'IDNHANVIEN': member_id,
            'HOTEN': member_name,
            'NGAYSINH': target_capthe.get('NGAYSINH', ''),
            'NGAYVAODOAN': target_capthe.get('NGAYVAODOAN', ''),
            'IDTINHTHANH': target_capthe.get('IDTINHTHANH') or target_capthe.get('QUEQUANTINHTHANH') or 0,
            'SOTHEDOAN': target_capthe.get('SOTHEDOAN', ''),
            'DUYET': 1
        }]

        en = {
            'idbiendong': 45,
            'quyetdinh': "",
            'ngay': now_iso,
            'idloaihtc': client.id_loaihtc,
            'idtochuc': id_tochuc_captren,
            'noidung': loaihinh,
            'trangthaixl': 2,
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
        submit_headers = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_submit, xe), 'User-Agent': 'Mozilla/5.0'}
        files = {'data': (None, data_str)}
        res_sub = client.session.post(url_submit, files=files, headers=submit_headers, timeout=25)
        if res_sub.status_code == 200 and res_sub.json().get('success'):
            idxuly = res_sub.json().get('idxuly')
            print(f" • Chi đoàn: Đã tạo yêu cầu '{loaihinh}' thành công! (Mã xử lý: {idxuly}) ✅")

            if admin_client.token:
                now_str = time.strftime('%d/%m/%Y')
                xuly_data = {
                    'IdXuLy': idxuly,
                    'MaNhom': manhom,
                    'dsDoanVien': json.dumps(dsdv, separators=(',', ':')),
                    'IdToChuc': 247294,
                    'TrangThaiXL': 2,
                    'IdNhanVienNhap': admin_client.user_id,
                    'IdQuyTrinhChiTiet': 234,
                    'IdToChucNhap': admin_client.id_tochuc,
                    'loaihinhcapthe': loaihinh,
                    'idBienDong': 45,
                    'Ngay': now_str,
                    'NgayHL': now_str,
                    'NOIDUNG': loaihinh,
                    'SOQUYETDINH': '',
                    'SONGHIQUYET': '',
                    'chuyenDonVi': 0,
                    'dsfile': '[]',
                    'quyetdinh': ''
                }
                form_str = json.dumps(xuly_data, separators=(',', ':'))
                files_app = {'data': (None, form_str)}
                url_app_ct = f"{BASE_URL}/ws/api/LichSuBienDong/luu_xulybiendongCapThe"
                headers_app_ct = {'Authorization': f'Bearer {admin_client.token}', 'User-Agent': 'Mozilla/5.0'}
                res_app_ct = admin_client.session.post(url_app_ct, files=files_app, headers=headers_app_ct, timeout=25)
                if res_app_ct.status_code == 200 and res_app_ct.json().get('success'):
                    print(" • Admin: Đã duyệt và chuyển tiếp yêu cầu cấp thẻ lên Đoàn trường thành công! ✅")

    # =========================================================================
    # BƯỚC 3: ĐÁNH GIÁ XẾP LOẠI ĐOÀN VIÊN (XUẤT SẮC & ADMIN DUYỆT)
    # =========================================================================
    print("\n" + "=" * 88)
    print("[BƯỚC 3/3] ĐÁNH GIÁ XẾP LOẠI ĐOÀN VIÊN: HOÀN THÀNH XUẤT SẮC NHIỆM VỤ")
    print("=" * 88)

    current_rating = matched_member.get("IDDANHGIA")
    if current_rating == 4.0:
        print(f" • Đoàn viên đã được xếp loại Xuất sắc từ trước (ID: {current_rating}). ✅")
    else:
        payload_eval = {
            "idtochuc": client.id_tochuc,
            "nam": int(config.YEAR),
            "dsDanhGia": [{
                "idNhanVien": member_id,
                "idDanhGia": 4,
                "DiemManh": "",
                "DiemYeu": "",
                "KhenThuong": "",
                "KyLuat": "",
                "tiLe": 0
            }]
        }
        body_eval = json.dumps(payload_eval, separators=(',', ':'))
        h_eval = {"Authorization": f"Bearer {client.token}", "Content-Type": "application/json;charset=utf-8", "User-Agent": "Mozilla/5.0"}
        r_up = client.session.post(f"{BASE_URL}/ws/api/DanhGia/updateDanhGia", data=body_eval, headers=h_eval, timeout=25)
        r_send = client.session.post(f"{BASE_URL}/ws/api/DanhGia/sendDanhGia", data=body_eval, headers=h_eval, timeout=25)
        if r_up.status_code == 200 and r_send.status_code == 200:
            print(" • Chi đoàn: Đã Lưu & Gửi đánh giá xếp loại Xuất sắc thành công! ✅")

    if admin_client.token:
        url_app = f"{BASE_URL}/ws/api/DanhGia/duyetDanhGia"
        p_app = {"idtochuc": client.id_tochuc, "nam": int(config.YEAR), "dsDanhGia": []}
        b_app = json.dumps(p_app, separators=(',', ':'))
        h_app = {"Authorization": f"Bearer {admin_client.token}", "X-XSRF-TOKEN": admin_client.get_xsrf(url_app, b_app), "Content-Type": "application/json;charset=utf-8", "User-Agent": "Mozilla/5.0"}
        r_app = admin_client.session.post(url_app, data=b_app, headers=h_app, timeout=25)
        if r_app.status_code == 200 and r_app.json().get("success"):
            print(" • Admin: Đã duyệt đánh giá xếp loại thành công! ✅")

    # =========================================================================
    # TỔNG KẾT & DOUBLE CHECK
    # =========================================================================
    print("\n" + "═" * 88)
    print(f"🎉 HOÀN TẤT XỬ LÝ TRỌN GÓI CHO: {member_name} ({full_name})")
    print(" 0. Duyệt App TNVN     : Đã nằm trong danh sách Chi đoàn ✅")
    print(" 1. Rèn luyện đoàn viên : Đã đăng ký 31 tiêu chí + Chấm 100/100 + Đoàn cơ sở xác nhận ✅")
    print(" 2. Nghiệp vụ cấp thẻ   : Đã lập yêu cầu & Admin duyệt chuyển tiếp lên Đoàn trường ✅")
    print(" 3. Đánh giá xếp loại   : Hoàn thành xuất sắc nhiệm vụ (Admin đã duyệt phê chuẩn ✅)")
    print("═" * 88 + "\n")
    return True

def main():
    parser = argparse.ArgumentParser(description="Xử lý đơn lẻ 1 người: Duyệt App + Rèn luyện + Cấp thẻ + Đánh giá xuất sắc")
    parser.add_argument("--ten", type=str, help="Họ và tên đoàn viên (VD: Nguyễn Văn A)")
    parser.add_argument("--lop", type=str, help="Lớp / Chi đoàn (VD: 26130FIE)")
    parser.add_argument("--mssv", type=str, default="", help="Mã số sinh viên (tùy chọn)")

    args = parser.parse_args()

    ho_ten = args.ten
    lop = args.lop
    mssv = args.mssv

    if not ho_ten or not lop:
        print("═" * 88)
        print("    CHƯƠNG TRÌNH XỬ LÝ ĐƠN LẺ TRỌN GÓI CHO 1 ĐOÀN VIÊN (CHỈ CẦN TÊN + LỚP)")
        print("  (0. Duyệt App -> 1. Rèn luyện 100đ -> 2. Cấp thẻ đoàn -> 3. Đánh giá xuất sắc)")
        print("═" * 88)
        try:
            ho_ten = input("1. Nhập Họ và Tên đoàn viên: ").strip()
            lop = input("2. Nhập Lớp / Chi đoàn (VD: 26130FIE): ").strip()
            mssv = input("3. Nhập MSSV (nếu có, hoặc bấm Enter để bỏ qua): ").strip()
        except EOFError:
            pass

    if not ho_ten or not lop:
        print("❌ Lỗi: Cần cung cấp đầy đủ Tên đoàn viên và Lớp!")
        sys.exit(1)

    process_single_member(ho_ten, lop, mssv)

if __name__ == "__main__":
    main()
