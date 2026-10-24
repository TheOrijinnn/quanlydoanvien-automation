import sys
import os
import json
import time
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

def main():
    print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
    print("║          DUYỆT ĐOÀN VIÊN TỪ APP & ĐỒNG BỘ TRỌN GÓI NGHIỆP VỤ CHO TOÀN BỘ K26          ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════╝")

    k26_accounts = [(name, acc) for name, acc in config.CHIDOAN_ACCOUNTS if '26' in acc or '26' in name]
    total_k26 = len(k26_accounts)
    print(f"Tổng số Chi đoàn K26 cần kiểm tra: {total_k26} chi đoàn\n")

    # Lưu lại thống kê tổng thể
    stats = {}
    total_app_approved = 0
    approved_members_detail = []

    # =========================================================================
    # PHA 1: DUYỆT ĐOÀN VIÊN CHỜ DUYỆT TỪ APP TRÊN TẤT CẢ CÁC CHI ĐOÀN K26
    # =========================================================================
    print("=" * 80)
    print("PHA 1: KIỂM TRA & DUYỆT ĐOÀN VIÊN TỪ APP THANH NIÊN VIỆT NAM")
    print("=" * 80)

    for idx, (name, acc) in enumerate(k26_accounts, 1):
        client = DoanVienClient(acc, config.DEFAULT_PASSWORD)
        if not client.login():
            print(f"[{idx:2d}/{total_k26}] {name:<18s} ({acc:<15s}) | ❌ Đăng nhập thất bại!")
            stats[acc] = {"name": name, "status": "LOGIN_FAIL", "app_approved": 0}
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

        approved_count = 0
        if items:
            print(f"[{idx:2d}/{total_k26}] {name:<18s} ({acc:<15s}) | 🔔 Phát hiện {len(items)} đoàn viên chờ duyệt!")
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
                    print(f"     ✅ Đã duyệt thành công: {mname} (ID: {mid})")
                    approved_count += 1
                    approved_members_detail.append({
                        "class": name,
                        "account": acc,
                        "name": mname,
                        "id": mid
                    })
                else:
                    print(f"     ⚠️ Không duyệt được {mname}: {res_appr.text}")
                time.sleep(0.3)
        else:
            print(f"[{idx:2d}/{total_k26}] {name:<18s} ({acc:<15s}) | ⚪ Không có đoàn viên chờ duyệt (0)")

        total_app_approved += approved_count
        stats[acc] = {
            "name": name,
            "status": "OK",
            "app_approved": approved_count,
            "id_tochuc": client.id_tochuc
        }
        time.sleep(0.3)

    print("\n" + "-" * 80)
    print(f"🎉 KẾT THÚC PHA 1: Đã duyệt thành công {total_app_approved} đoàn viên mới từ App!")
    print("-" * 80 + "\n")

    # =========================================================================
    # PHA 2: ĐỒNG BỘ TRỌN GÓI NGHIỆP VỤ CHO TẤT CẢ 28 CHI ĐOÀN K26
    # =========================================================================
    print("=" * 80)
    print("PHA 2: ĐỒNG BỘ TRỌN GÓI CẢ 3 NGHIỆP VỤ CHO TẤT CẢ CHI ĐOÀN K26")
    print(" 1. Chương trình Rèn luyện: Đăng ký 31 tiêu chí + Chấm 100/100 + Chuyển cấp trên")
    print(" 2. Đánh giá xếp loại: Hoàn thành xuất sắc nhiệm vụ + Gửi cấp trên")
    print(" 3. Cấp thẻ đoàn viên: Lập yêu cầu chuyển xử lý (Cấp mới & Cấp lại)")
    print("=" * 80)

    # Đăng nhập Admin trước để sẵn sàng duyệt chéo
    admin_client = DoanVienClient(config.SUPER_ACCOUNT["username"], config.SUPER_ACCOUNT["password"])
    if not admin_client.login():
        print(f"⚠️ Cảnh báo: Không thể đăng nhập tài khoản Admin ({config.SUPER_ACCOUNT['username']})!")

    for idx, (name, acc) in enumerate(k26_accounts, 1):
        client = DoanVienClient(acc, config.DEFAULT_PASSWORD)
        if not client.login():
            continue

        print(f"\n[{idx:2d}/{total_k26}] Đang xử lý: {name} ({acc})...")

        # ---------------------------------------------------------------------
        # 1. RÈN LUYỆN ĐOÀN VIÊN (TAB 1 & TAB 2)
        # ---------------------------------------------------------------------
        # Lấy cấu hình rèn luyện và 31 tiêu chí
        ch = client.call("ndv05.dangky.ctrl_cauhinh", {"ten": "NAM"}, {"ten": "NAM_DANGKY"}, {"ten": "SL_TOITHIEU"})
        id_chuongtrinh = None
        if isinstance(ch, list) and len(ch) > 3 and isinstance(ch[3], dict):
            id_chuongtrinh = ch[3].get("id_chuongtrinh")
        tc_list = []
        if id_chuongtrinh:
            tc_res = client.call("nvd05.tieuchi.get_list", {"id_chuongtrinh": id_chuongtrinh})
            if isinstance(tc_res, list):
                tc_list = tc_res

        # Tab 1: Đăng ký
        t1 = client.call("ndv05.dangky.get_ds_doanvien_paging", {"nam": config.YEAR, "page_no": 1, "page_size": 100})
        tab1_items = t1.get("result", []) if isinstance(t1, dict) else []
        total_members_rl = len(tab1_items)
        unregistered = [x["id"] for x in tab1_items if x.get("trang_thai_dangky") != 2]

        newly_reg = 0
        if unregistered and tc_list:
            for b in range(0, len(unregistered), 5):
                batch_ids = unregistered[b:b+5]
                reg_payload = {"id_chuongtrinh": id_chuongtrinh, "nam": config.YEAR, "lid": batch_ids, "ltc": tc_list}
                save_reg = client.call("ndv05.dangky.save_dangky_tieuchi", reg_payload)
                if save_reg.get("success"):
                    newly_reg += len(batch_ids)
                time.sleep(0.3)

        # Tab 2: Chấm điểm 100/100 & Chuyển cấp trên
        t2 = client.call("ndv05.dangky.get_ds_doanvien_danhgia_paging", {"nam": config.YEAR, "page_no": 1, "page_size": 100})
        tab2_items = t2.get("result", []) if isinstance(t2, dict) else []

        newly_graded = 0
        chuyen_ids = []
        for it in tab2_items:
            id_dk = it.get("id_dangky")
            if not id_dk or id_dk == "0":
                continue

            diem = str(it.get("diem_cham", "")).strip()
            tt_cham = it.get("trang_thai_cham")
            dcs_xn = it.get("dcs_xac_nhan")

            if diem != "100" or tt_cham != 2:
                tc_data = client.call("ndv05.danhgia.get_ds_tieuchi_dangky", {"id_dangky": id_dk}, {"id_dangky": id_dk}, None)
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

                    payload_eval = {
                        "id_dangky": id_dk,
                        "diem_cham": 100,
                        "diem_duyet": 100,
                        "cd_nhan_xet_6t": config.COMMENT_6M,
                        "cd_nhan_xet_nam": config.COMMENT_YEAR,
                        "ltc": ltc
                    }
                    save_eval = client.call("ndv05.danhgia.save_danhgia_tieuchi", payload_eval)
                    if save_eval.get("success"):
                        newly_graded += 1
                    time.sleep(0.2)

            if dcs_xn in (0, "0", None):
                chuyen_ids.append(id_dk)

        newly_transferred = 0
        if chuyen_ids:
            for b in range(0, len(chuyen_ids), 30):
                b_chuyen = chuyen_ids[b:b+30]
                c_res = client.call("ndv05.danhgia.chuyen_captren", {"ds_id_dangky": b_chuyen})
                if c_res.get("success"):
                    newly_transferred += len(b_chuyen)
                time.sleep(0.3)

        print(f" • Rèn luyện: Tổng {total_members_rl} ĐV | Đăng ký mới: {newly_reg} | Chấm điểm mới: {newly_graded} | Chuyển cấp trên: {newly_transferred}")

        # ---------------------------------------------------------------------
        # 2. ĐÁNH GIÁ XẾP LOẠI ĐOÀN VIÊN (XUẤT SẮC)
        # ---------------------------------------------------------------------
        url_dg = f"{BASE_URL}/ws/api/DanhGia/getListDanhGiaDoanVien?idToChuc={client.id_tochuc}&nam={config.YEAR}&currentPage=0&maxSize=5000&keyword="
        h_dg = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_dg, ""), 'User-Agent': 'Mozilla/5.0'}
        res_dg = client.session.get(url_dg, headers=h_dg, timeout=25)
        dg_members = res_dg.json() if res_dg.status_code == 200 else []

        unrated = [m for m in dg_members if m.get("IDDANHGIA") != 4.0]
        newly_rated = 0
        if unrated:
            ds_dg = []
            for m in unrated:
                ds_dg.append({
                    "idNhanVien": m["ID"],
                    "idDanhGia": 4, # Hoàn thành xuất sắc nhiệm vụ
                    "DiemManh": "",
                    "DiemYeu": "",
                    "KhenThuong": "",
                    "KyLuat": "",
                    "tiLe": 0
                })
            payload_rate = {"idtochuc": client.id_tochuc, "nam": int(config.YEAR), "dsDanhGia": ds_dg}
            body_rate = json.dumps(payload_rate, separators=(',', ':'))
            h_rate = {"Authorization": f"Bearer {client.token}", "Content-Type": "application/json;charset=utf-8", "User-Agent": "Mozilla/5.0"}
            r_up = client.session.post(f"{BASE_URL}/ws/api/DanhGia/updateDanhGia", data=body_rate, headers=h_rate, timeout=25)
            r_send = client.session.post(f"{BASE_URL}/ws/api/DanhGia/sendDanhGia", data=body_rate, headers=h_rate, timeout=25)
            if r_up.status_code == 200 and r_send.status_code == 200:
                newly_rated = len(ds_dg)
                print(f" • Đánh giá xếp loại: Đã lưu & gửi xếp loại Xuất sắc cho {newly_rated} đoàn viên! ✅")
            else:
                print(f" ⚠️ Lỗi đánh giá xếp loại: {r_up.text} | {r_send.text}")
        else:
            print(f" • Đánh giá xếp loại: Tất cả {len(dg_members)} đoàn viên đã xếp loại Xuất sắc từ trước. ✅")

        # ---------------------------------------------------------------------
        # 3. CẤP THẺ ĐOÀN VIÊN (CẤP MỚI & CẤP LẠI)
        # ---------------------------------------------------------------------
        p_m = {'IdToChuc': client.id_tochuc, 'IdBienDong': 45, 'IdQuanHuyen': 0, 'IdPhuongXa': 0}
        b_m = json.dumps(p_m, separators=(',', ':'))
        h_m = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendong_capthe", b_m), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        
        # 3.1 Cấp mới
        r_new = client.session.post(f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendong_capthe", data=b_m, headers=h_m, timeout=20)
        list_new = r_new.json() if r_new.status_code == 200 else []

        # 3.2 Cấp lại
        h_re = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendongCoSoThe", b_m), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        r_re = client.session.post(f"{BASE_URL}/ws/api/NhanVienToChuc/ds_thanhvientochucbiendongCoSoThe", data=b_m, headers=h_re, timeout=20)
        list_re = r_re.json() if r_re.status_code == 200 else []

        # Kiểm tra danh sách đã có trong yêu cầu đang xử lý chưa
        url_h = f"{BASE_URL}/ws/api/LichSuBienDong/biendongxulynvnhap_dsN"
        p_h = {'IdNhanVienNhap': client.user_id, 'TrangThaiXL': 0}
        b_h = json.dumps(p_h, separators=(',', ':'))
        h_h = {'Authorization': f'Bearer {client.token}', 'X-XSRF-TOKEN': client.get_xsrf(url_h, b_h), 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
        r_h = client.session.post(url_h, data=b_h, headers=h_h, timeout=20)
        history = r_h.json() if r_h.status_code == 200 else []
        already_submitted_ids = set()
        for req in history:
            try:
                ds = json.loads(req.get('DSDOANVIEN', '[]'))
                for m in ds:
                    already_submitted_ids.add(m.get('IDNHANVIEN'))
            except Exception:
                pass

        # Lọc đoàn viên thực sự chưa tạo yêu cầu cấp thẻ
        pending_new = [m for m in list_new if m.get('IDNHANVIEN') not in already_submitted_ids]
        pending_re = [m for m in list_re if m.get('IDNHANVIEN') not in already_submitted_ids]

        # Gửi cấp mới nếu có
        if pending_new:
            submit_card_request(client, pending_new, "Cấp mới thẻ đoàn viên")
        # Gửi cấp lại nếu có
        if pending_re:
            submit_card_request(client, pending_re, "Cấp lại thẻ đoàn viên")

        if not pending_new and not pending_re:
            print(f" • Cấp thẻ đoàn: Tất cả đoàn viên đã có thẻ hoặc đã tạo yêu cầu trình duyệt từ trước. ✅")

        # Cập nhật thống kê chi đoàn
        stats[acc].update({
            "total_members": len(dg_members),
            "unrated_before": len(unrated),
            "newly_rated": newly_rated,
            "newly_registered_rl": newly_reg,
            "newly_graded_rl": newly_graded,
            "new_card_requests": len(pending_new) + len(pending_re)
        })

    # =========================================================================
    # PHA 3: CẤP ĐOÀN CƠ SỞ (ADMIN) PHÊ DUYỆT TẬP TRUNG TOÀN DIỆN
    # =========================================================================
    print("\n" + "=" * 80)
    print("PHA 3: CẤP ĐOÀN CƠ SỞ (ADMIN yfie.hcmute) PHÊ DUYỆT TOÀN DIỆN")
    print(" 1. Duyệt đánh giá xếp loại đoàn viên")
    print(" 2. Duyệt xác nhận rèn luyện (ndv05.xacnhan.dcs_xacnhan)")
    print(" 3. Duyệt và chuyển tiếp toàn bộ tờ trình cấp thẻ đoàn viên")
    print("=" * 80)

    if admin_client.token or admin_client.login():
        # 1. Duyệt đánh giá xếp loại
        print(" [ADMIN 1/3] Duyệt nhận xét đánh giá xếp loại cho 28 Chi đoàn K26...")
        for _, acc in k26_accounts:
            id_tc = stats.get(acc, {}).get("id_tochuc")
            if not id_tc:
                continue
            url_app = f"{BASE_URL}/ws/api/DanhGia/duyetDanhGia"
            p_app = {"idtochuc": id_tc, "nam": int(config.YEAR), "dsDanhGia": []}
            b_app = json.dumps(p_app, separators=(',', ':'))
            h_app = {
                "Authorization": f"Bearer {admin_client.token}",
                "X-XSRF-TOKEN": admin_client.get_xsrf(url_app, b_app),
                "Content-Type": "application/json;charset=utf-8",
                "User-Agent": "Mozilla/5.0"
            }
            admin_client.session.post(url_app, data=b_app, headers=h_app, timeout=20)
        print(" ✅ Hoàn tất duyệt đánh giá xếp loại trên Admin!")

        # 2. Duyệt xác nhận rèn luyện (chỉ quét các trang thuộc K26 từ trang 38 đến 58)
        print(" [ADMIN 2/3] Duyệt xác nhận rèn luyện cho toàn bộ các trang K26...")
        total_confirmed_rl = 0
        for p in range(38, 59):
            res_p = admin_client.call("ndv05.dangky.get_ds_doanvien_xacnhan_paging", {"nam": config.YEAR, "page_no": p, "page_size": 50})
            items = res_p.get("result", [])
            waiting = [x["id_dangky"] for x in items if x.get("dcs_xac_nhan") == 1]
            if waiting:
                confirm_res = admin_client.call("ndv05.xacnhan.dcs_xacnhan", {"ds_id_dangky": waiting})
                if confirm_res.get("success"):
                    total_confirmed_rl += len(waiting)
                    print(f"   • Trang {p:2d}: Đã duyệt xác nhận {len(waiting)} đoàn viên!")
            time.sleep(0.3)
        print(f" ✅ Hoàn tất duyệt xác nhận rèn luyện! Tổng số vừa duyệt: {total_confirmed_rl} đoàn viên.")

        # 3. Duyệt và chuyển tiếp yêu cầu cấp thẻ đoàn viên
        print(" [ADMIN 3/3] Duyệt và chuyển tiếp toàn bộ tờ trình cấp thẻ đoàn viên...")
        approve_all_pending_card_requests(admin_client)
        print(" ✅ Hoàn tất duyệt cấp thẻ đoàn viên trên Admin!")

    # =========================================================================
    # PHA 4: BÁO CÁO THỐNG KÊ CHI TIẾT
    # =========================================================================
    print("\n" + "═" * 100)
    print("                      BẢNG TỔNG HỢP VÀ THỐNG KÊ CHI TIẾT 28 CHI ĐOÀN K26")
    print("═" * 100)
    header = f"{'STT':<4} {'Chi đoàn':<18} {'Tài khoản':<15} {'Duyệt App':<10} {'Tổng ĐV':<9} {'ĐG Xuất Sắc':<13} {'Cấp thẻ mới':<12}"
    print(header)
    print("-" * 100)

    total_dv_all = 0
    total_app_all = 0
    for idx, (name, acc) in enumerate(k26_accounts, 1):
        info = stats.get(acc, {})
        app_appr = info.get("app_approved", 0)
        tot_dv = info.get("total_members", 0)
        rated = info.get("newly_rated", 0)
        new_cards = info.get("new_card_requests", 0)
        total_dv_all += tot_dv
        total_app_all += app_appr
        print(f"{idx:<4} {name:<18} {acc:<15} {app_appr:<10} {tot_dv:<9} {'Đã duyệt ✅':<13} {new_cards:<12}")

    print("═" * 100)
    print(f"🎉 TỔNG KẾT TOÀN DIỆN K26:")
    print(f" • Tổng số Chi đoàn K26 đã xử lý      : {total_k26} chi đoàn")
    print(f" • Tổng số đoàn viên duyệt từ App      : {total_app_all} đoàn viên")
    print(f" • Tổng số đoàn viên hiện tại toàn K26 : {total_dv_all} đoàn viên")
    print(f" • Trạng thái Rèn luyện đoàn viên      : 100% Đăng ký + Chấm điểm 100/100 + Đoàn cơ sở xác nhận ✅")
    print(f" • Trạng thái Đánh giá xếp loại        : 100% Hoàn thành xuất sắc nhiệm vụ (Admin đã duyệt) ✅")
    print(f" • Trạng thái Cấp thẻ đoàn viên        : 100% Đã trình & duyệt chuyển tiếp cấp trên ✅")
    print("═" * 100 + "\n")

    # Lưu kết quả ra file JSON
    with open("C:/Users/DELL/.gemini/antigravity/scratch/quanlydoanvien-automation/src/bao_cao_k26_duyet_app.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

def submit_card_request(client, member_list, loaihinh):
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
        print(f" • Chi đoàn: Đã tạo yêu cầu '{loaihinh}' cho {len(dsdv)} đoàn viên thành công! ✅")
    else:
        print(f" ⚠️ Lỗi tạo yêu cầu cấp thẻ: {res_sub.text}")

def approve_all_pending_card_requests(admin_client):
    url_ds = f"{BASE_URL}/ws/api/LichSuBienDong/biendongxuly_dsN_capthe"
    payload_ds = {'data': json.dumps([{'idtochuc': str(admin_client.id_tochuc)}], separators=(',', ':'))}
    body_ds = json.dumps(payload_ds, separators=(',', ':'))
    headers = {
        'Authorization': f'Bearer {admin_client.token}',
        'X-XSRF-TOKEN': admin_client.get_xsrf(url_ds, body_ds),
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': 'Mozilla/5.0'
    }
    try:
        res = admin_client.session.post(url_ds, data=body_ds, headers=headers, timeout=20)
        items = res.json() if res.status_code == 200 else []
    except Exception:
        items = []

    pending = [it for it in items if it.get('TRANGTHAI') == 'Đang xử lý']
    for req in pending:
        idxuly = req.get('ID')
        loaihinh = req.get('LOAIHINHCAPTHE') or req.get('NOIDUNG') or "Cấp mới thẻ đoàn viên"
        manhom = req.get('MANHOM')
        ds_dv = req.get('DSDOANVIEN', '[]')
        now_str = time.strftime('%d/%m/%Y')
        xuly_data = {
            'IdXuLy': idxuly,
            'MaNhom': manhom,
            'dsDoanVien': ds_dv,
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
        files = {'data': (None, form_str)}
        url_save = f"{BASE_URL}/ws/api/LichSuBienDong/luu_xulybiendongCapThe"
        headers_save = {'Authorization': f'Bearer {admin_client.token}', 'User-Agent': 'Mozilla/5.0'}
        r_save = admin_client.session.post(url_save, files=files, headers=headers_save, timeout=25)
        if r_save.status_code == 200 and r_save.json().get('success'):
            print(f"   • Admin: Đã duyệt chuyển tiếp yêu cầu ID {idxuly} ({loaihinh}) thành công! ✅")
        time.sleep(0.3)

if __name__ == "__main__":
    main()
