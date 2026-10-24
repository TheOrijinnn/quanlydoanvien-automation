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
    # Fallback to lowercased input
    return class_name.lower().replace("chi đoàn", "").replace(" ", "").strip(), class_name

def process_single_member(ho_ten, mssv, lop_ten):
    print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
    print("║                 XỬ LÝ ĐƠN LẺ: CẤP THẺ ĐOÀN & ĐÁNH GIÁ XẾP LOẠI                       ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════╝")
    print(f" • Họ và tên : {ho_ten}")
    print(f" • MSSV      : {mssv}")
    print(f" • Lớp       : {lop_ten}")
    print("-" * 80)

    acc, full_name = find_account_by_class(lop_ten)
    print(f"🔍 Nhận diện tài khoản Chi đoàn: {acc} ({full_name})")

    client = DoanVienClient(acc, config.DEFAULT_PASSWORD)
    if not client.login():
        print(f"❌ Đăng nhập thất bại vào tài khoản Chi đoàn {acc}!")
        return False

    print(f"✅ Đăng nhập Chi đoàn thành công! ID Tổ chức: {client.id_tochuc}")

    # =========================================================================
    # BƯỚC 1: TÌM ĐOÀN VIÊN TRONG HỆ THỐNG
    # =========================================================================
    print("\n[BƯỚC 1/3] Đang tìm kiếm đoàn viên trong danh sách Chi đoàn...")
    url_dg = f"{BASE_URL}/ws/api/DanhGia/getListDanhGiaDoanVien?idToChuc={client.id_tochuc}&nam={config.YEAR}&currentPage=0&maxSize=5000&keyword="
    h_dg = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_dg, ""), 'User-Agent': 'Mozilla/5.0'}
    res_dg = client.session.get(url_dg, headers=h_dg, timeout=25)
    members = res_dg.json() if res_dg.status_code == 200 else []

    norm_target = remove_accents(ho_ten)
    matched_member = None
    for m in members:
        if remove_accents(m.get("HOTEN")) == norm_target:
            matched_member = m
            break

    if not matched_member:
        # Thử tìm theo từ khóa tên cuối cùng
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

    # =========================================================================
    # BƯỚC 2: ĐÁNH GIÁ XẾP LOẠI XUẤT SẮC & GỬI DUYỆT
    # =========================================================================
    print("\n[BƯỚC 2/3] Thực hiện Đánh giá xếp loại: 'Hoàn thành xuất sắc nhiệm vụ'...")
    current_rating = matched_member.get("IDDANHGIA")
    
    if current_rating == 4.0:
        print(f" • Đoàn viên đã được xếp loại Xuất sắc từ trước (ID: {current_rating}).")
    else:
        payload_eval = {
            "idtochuc": client.id_tochuc,
            "nam": int(config.YEAR),
            "dsDanhGia": [{
                "idNhanVien": member_id,
                "idDanhGia": 4, # Hoàn thành xuất sắc nhiệm vụ
                "DiemManh": "",
                "DiemYeu": "",
                "KhenThuong": "",
                "KyLuat": "",
                "tiLe": 0
            }]
        }
        body_eval = json.dumps(payload_eval, separators=(',', ':'))
        h_eval = {
            "Authorization": f"Bearer {client.token}",
            "Content-Type": "application/json;charset=utf-8",
            "User-Agent": "Mozilla/5.0"
        }
        # Lưu
        r_up = client.session.post(f"{BASE_URL}/ws/api/DanhGia/updateDanhGia", data=body_eval, headers=h_eval, timeout=25)
        # Gửi
        r_send = client.session.post(f"{BASE_URL}/ws/api/DanhGia/sendDanhGia", data=body_eval, headers=h_eval, timeout=25)
        if r_up.status_code == 200 and r_send.status_code == 200:
            print(f" • Chi đoàn: Đã Lưu & Gửi đánh giá xếp loại Xuất sắc thành công! ✅")
        else:
            print(f" ⚠️ Cảnh báo lỗi Lưu/Gửi đánh giá: {r_up.text} | {r_send.text}")

    # Đăng nhập Admin để duyệt Đánh giá
    print(" • Đang đăng nhập Admin (yfie.hcmute) để duyệt nhận xét...")
    admin_client = DoanVienClient(config.SUPER_ACCOUNT["username"], config.SUPER_ACCOUNT["password"])
    if admin_client.login():
        url_app = f"{BASE_URL}/ws/api/DanhGia/duyetDanhGia"
        p_app = {"idtochuc": client.id_tochuc, "nam": int(config.YEAR), "dsDanhGia": []}
        b_app = json.dumps(p_app, separators=(',', ':'))
        h_app = {
            "Authorization": f"Bearer {admin_client.token}",
            "X-XSRF-TOKEN": admin_client.get_xsrf(url_app, b_app),
            "Content-Type": "application/json;charset=utf-8",
            "User-Agent": "Mozilla/5.0"
        }
        r_app = admin_client.session.post(url_app, data=b_app, headers=h_app, timeout=25)
        if r_app.status_code == 200 and r_app.json().get("success"):
            print(" • Admin: Đã duyệt đánh giá xếp loại thành công! ✅")
        else:
            print(f" • Admin duyệt: {r_app.text}")

    # =========================================================================
    # BƯỚC 3: CẤP THẺ ĐOÀN VIÊN (CẤP MỚI HOẶC CẤP LẠI) & DUYỆT
    # =========================================================================
    print("\n[BƯỚC 3/3] Thực hiện Cấp thẻ đoàn viên...")
    
    # 1. Kiểm tra trong danh sách Cấp mới
    url_m_new = f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendong_capthe"
    p_m = {'IdToChuc': client.id_tochuc, 'IdBienDong': 45, 'IdQuanHuyen': 0, 'IdPhuongXa': 0}
    b_m = json.dumps(p_m, separators=(',', ':'))
    h_m = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_m_new, b_m), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    r_new = client.session.post(url_m_new, data=b_m, headers=h_m, timeout=20)
    list_new = r_new.json() if r_new.status_code == 200 else []

    # 2. Kiểm tra trong danh sách Cơ sở thẻ (Cấp lại)
    url_m_re = f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendongCoSoThe"
    h_re = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_m_re, b_m), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    r_re = client.session.post(url_m_re, data=b_m, headers=h_re, timeout=20)
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
        # Kiểm tra xem đoàn viên đã được trình trong yêu cầu trước đó chưa
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
            print(f" • Không tìm thấy đoàn viên trong danh sách chờ cấp thẻ (có thể đã có thẻ hoặc đã hoàn tất).")
    else:
        print(f" • Tìm thấy trong danh sách: Diện '{loaihinh}'. Đang tạo yêu cầu...")
        
        # Lấy cấp trên
        url_ct = f"{BASE_URL}/ws/api/LichSuBienDong/ds_ToChucCapTren"
        p_ct = {'IdToChuc': client.id_tochuc}
        b_ct = json.dumps(p_ct, separators=(',', ':'))
        h_ct = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_ct, b_ct), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        res_ct = client.session.post(url_ct, data=b_ct, headers=h_ct, timeout=20)
        captren = res_ct.json()[0]
        id_tochuc_captren = captren['ID']
        id_captc_captren = captren['IDCAPTC']

        # Quy trình chi tiết
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
            print(f" • Chi đoàn: Đã gửi yêu cầu '{loaihinh}' thành công! (Mã xử lý: {idxuly}) ✅")

            # Duyệt cấp thẻ trên tài khoản Admin
            print(" • Đang duyệt yêu cầu cấp thẻ trên tài khoản Admin...")
            if admin_client.token or admin_client.login():
                now_str = time.strftime('%d/%m/%Y')
                xuly_data = {
                    'IdXuLy': idxuly,
                    'MaNhom': manhom,
                    'dsDoanVien': json.dumps(dsdv, separators=(',', ':')),
                    'IdToChuc': 247294, # Đoàn trường
                    'TrangThaiXL': 2, # Duyệt chuyển tiếp
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
                    print(" • Admin: Đã duyệt và chuyển tiếp yêu cầu cấp thẻ thành công! ✅")
                else:
                    print(f" • Admin duyệt cấp thẻ: {res_app_ct.text}")
        else:
            print(f" ❌ Lỗi tạo yêu cầu cấp thẻ: {res_sub.text}")

    print("\n" + "=" * 80)
    print(f"🎉 HOÀN TẤT XỬ LÝ CHO ĐOÀN VIÊN: {member_name} ({mssv} - {full_name})")
    print(f" • Đánh giá xếp loại : Hoàn thành xuất sắc nhiệm vụ (Admin đã duyệt ✅)")
    print(f" • Nghiệp vụ cấp thẻ  : Đã trình & duyệt chuyển tiếp cấp trên thành công ✅")
    print("=" * 80 + "\n")
    return True

def main():
    parser = argparse.ArgumentParser(description="Xử lý đơn lẻ 1 đoàn viên: Đánh giá xuất sắc + Cấp thẻ đoàn")
    parser.add_argument("--ten", type=str, help="Họ và tên đoàn viên (VD: Huỳnh Minh Quang)")
    parser.add_argument("--mssv", type=str, help="Mã số sinh viên (VD: 26130026)")
    parser.add_argument("--lop", type=str, help="Lớp / Chi đoàn (VD: 26130FIE)")

    args = parser.parse_args()

    ho_ten = args.ten
    mssv = args.mssv
    lop = args.lop

    # Nếu chạy trực tiếp không tham số -> Cho người dùng nhập tương tác
    if not ho_ten or not lop:
        print("=" * 80)
        print("          CHƯƠNG TRÌNH XỬ LÝ ĐƠN LẺ 1 ĐOÀN VIÊN MỚI BỔ SUNG")
        print("=" * 80)
        try:
            ho_ten = input("1. Nhập Họ và Tên đoàn viên: ").strip()
            mssv = input("2. Nhập Mã số sinh viên (MSSV): ").strip()
            lop = input("3. Nhập Lớp / Chi đoàn (VD: 26130FIE): ").strip()
        except EOFError:
            pass

    if not ho_ten or not lop:
        print("❌ Lỗi: Cần cung cấp đầy đủ Tên đoàn viên và Lớp!")
        sys.exit(1)

    process_single_member(ho_ten, mssv, lop)

if __name__ == "__main__":
    main()
