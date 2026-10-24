import sys
import os
import json
import time

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.dirname(__file__))

from api_client import DoanVienClient, BASE_URL
import config

def get_admin():
    admin = DoanVienClient(config.SUPER_ACCOUNT["username"], config.SUPER_ACCOUNT["password"])
    if not admin.login():
        print("❌ Không thể đăng nhập tài khoản Admin yfie.hcmute!")
        return None
    return admin

def normalize_name(name):
    return (name or "").lower().replace("chi đoàn", "").replace("chi doan", "").replace(" ", "").strip()

# =============================================================================
# 1. DOUBLE CHECK RÈN LUYỆN ĐOÀN VIÊN
# =============================================================================
def check_ren_luyen(admin_client=None, silent=False):
    if not silent:
        print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
        print("║           🔍 DOUBLE CHECK [GIAI ĐOẠN 1]: CHƯƠNG TRÌNH RÈN LUYỆN ĐOÀN VIÊN            ║")
        print("╚══════════════════════════════════════════════════════════════════════════════════════╝")

    if not admin_client:
        admin_client = get_admin()
        if not admin_client:
            return None

    # Lấy cấu hình năm và id_chuongtrinh
    res_ch = admin_client.call("ndv05.dangky.ctrl_cauhinh", {"ten": "NAM"}, {"ten": "NAM_DANGKY"}, {"ten": "SL_TOITHIEU"})
    nam = "2026"
    id_chuongtrinh = "aGIZlolp"
    if isinstance(res_ch, list) and len(res_ch) > 3:
        if res_ch[1] and isinstance(res_ch[1], list) and res_ch[1][0].get("ten"):
            nam = res_ch[1][0]["ten"]
        if isinstance(res_ch[3], dict) and res_ch[3].get("id_chuongtrinh"):
            id_chuongtrinh = res_ch[3]["id_chuongtrinh"]

    # Lấy bảng thống kê rèn luyện
    rl_list = admin_client.call("ndv05.thongke", {"id_chuongtrinh": id_chuongtrinh, "nam": nam, "idtochuc": ""})
    rl_items = rl_list if isinstance(rl_list, list) else []

    tong_dv = 0
    tong_dk = 0
    tong_cham = 0
    tong_dcs_duyet = 0
    discrepancies_rl = []

    for it in rl_items:
        ten = it.get("tentochuc", "").strip()
        if ten == "Tổng":
            continue
        sldv = it.get("sldv", 0)
        sldk = it.get("sldk", 0)
        sl_cham = it.get("sldk_da_cham_diem", 0)
        sl_dcs = it.get("sldk_dcs_xacnhan", 0)

        tong_dv += sldv
        tong_dk += sldk
        tong_cham += sl_cham
        tong_dcs_duyet += sl_dcs

        if sldv != sldk or sldk != sl_cham or sl_cham != sl_dcs:
            discrepancies_rl.append({
                "ten": ten,
                "tong": sldv,
                "dk": sldk,
                "cham": sl_cham,
                "dcs": sl_dcs
            })

    if not silent:
        print(f" • Tổng số đoàn viên trong CSDL rèn luyện : {tong_dv} ĐV")
        print(f" • Đã đăng ký tiêu chí (Tab 1)          : {tong_dk}/{tong_dv} ({tong_dk/tong_dv*100:.1f}%)" if tong_dv else "")
        print(f" • Đã chấm điểm 100/100 (Tab 2)          : {tong_cham}/{tong_dv} ({tong_cham/tong_dv*100:.1f}%)" if tong_dv else "")
        print(f" • Đoàn cơ sở (Admin) đã duyệt xác nhận  : {tong_dcs_duyet}/{tong_dv} ({tong_dcs_duyet/tong_dv*100:.1f}%)" if tong_dv else "")

        if not discrepancies_rl:
            print(" ✅ KẾT QUẢ DOUBLE CHECK: 100% đoàn viên đã hoàn tất Đăng ký + Chấm điểm + Đoàn cơ sở duyệt!")
        else:
            print(f" ⚠️ Cảnh báo: Có {len(discrepancies_rl)} chi đoàn còn số liệu chưa đồng bộ 100%:")
            for d in discrepancies_rl[:5]:
                print(f"   - {d['ten']}: Tổng {d['tong']} | ĐK: {d['dk']} | Chấm: {d['cham']} | Duyệt: {d['dcs']}")

        print("-" * 88 + "\n")

    return {
        "tong_dv": tong_dv,
        "tong_dk": tong_dk,
        "tong_cham": tong_cham,
        "tong_dcs_duyet": tong_dcs_duyet,
        "discrepancies": discrepancies_rl,
        "is_perfect": len(discrepancies_rl) == 0
    }

# =============================================================================
# 2. DOUBLE CHECK CẤP THẺ ĐOÀN VIÊN
# =============================================================================
def check_cap_the(admin_client=None, silent=False):
    if not silent:
        print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
        print("║              🔍 DOUBLE CHECK [GIAI ĐOẠN 2]: NGHIỆP VỤ CẤP THẺ ĐOÀN VIÊN               ║")
        print("╚══════════════════════════════════════════════════════════════════════════════════════╝")

    if not admin_client:
        admin_client = get_admin()
        if not admin_client:
            return None

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
        res = admin_client.session.post(url_ds, data=body_ds, headers=headers, timeout=25)
        items = res.json() if res.status_code == 200 else []
    except Exception:
        items = []

    pending = [it for it in items if it.get('TRANGTHAI') == 'Đang xử lý']
    processed = [it for it in items if it.get('TRANGTHAI') != 'Đang xử lý']

    tot_members_submitted = 0
    for it in items:
        try:
            ds = json.loads(it.get('DSDOANVIEN', '[]'))
            tot_members_submitted += len(ds)
        except Exception:
            pass

    if not silent:
        print(f" • Tổng số yêu cầu cấp thẻ đã lập        : {len(items)} lượt yêu cầu")
        print(f" • Tổng số lượt đoàn viên được trình thẻ : {tot_members_submitted} lượt đoàn viên")
        print(f" • Số yêu cầu ĐÃ DUYỆT (Chuyển Đoàn trường): {len(processed)} yêu cầu")
        print(f" • Số yêu cầu ĐANG XỬ LÝ (Chờ duyệt)      : {len(pending)} yêu cầu")

        if not pending:
            print(" ✅ KẾT QUẢ DOUBLE CHECK: 100% yêu cầu cấp thẻ đoàn đã được Admin phê duyệt chuyển tiếp!")
        else:
            print(f" ⚠️ Cảnh báo: Còn {len(pending)} yêu cầu đang chờ phê duyệt:")
            for p in pending[:5]:
                print(f"   - Mã {p.get('ID')}: {p.get('TOCHUCYEUCAU')} ({p.get('NOIDUNG')})")

        print("-" * 88 + "\n")

    return {
        "total_requests": len(items),
        "total_members": tot_members_submitted,
        "processed": len(processed),
        "pending": len(pending),
        "is_perfect": len(pending) == 0
    }

# =============================================================================
# 3. DOUBLE CHECK ĐÁNH GIÁ XẾP LOẠI ĐOÀN VIÊN
# =============================================================================
def check_danh_gia(admin_client=None, filter_prefix=None, silent=False):
    if not silent:
        print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
        print("║           🔍 DOUBLE CHECK [GIAI ĐOẠN 3]: ĐÁNH GIÁ XẾP LOẠI ĐOÀN VIÊN XUẤT SẮC         ║")
        print("╚══════════════════════════════════════════════════════════════════════════════════════╝")

    if not admin_client:
        admin_client = get_admin()
        if not admin_client:
            return None

    # Lấy danh sách tổ chức
    url_org = f"{BASE_URL}/ws/api/DanhGia/getDanhGiaNhanVienToChuc"
    payload = {"idtochuc": admin_client.id_tochuc, "nam": int(config.YEAR), "dsDanhGia": []}
    b_str = json.dumps(payload, separators=(',', ':'))
    headers = {
        "Authorization": f"Bearer {admin_client.token}",
        "X-XSRF-TOKEN": admin_client.get_xsrf(url_org, b_str),
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0"
    }
    res_org = admin_client.session.post(url_org, data=b_str, headers=headers, timeout=25)
    dg_orgs = res_org.json() if res_org.status_code == 200 else []

    if filter_prefix:
        dg_orgs = [o for o in dg_orgs if filter_prefix in o.get("TENTOCHUC", "")]

    total_orgs = len(dg_orgs)
    orgs_approved = sum(1 for o in dg_orgs if o.get("TRANGTHAI") == 2.0)
    orgs_waiting = total_orgs - orgs_approved

    tot_members_dg = 0
    tot_xuat_sac = 0
    chua_dg_all = 0
    discrepancies_dg = []

    for idx, org in enumerate(dg_orgs, 1):
        org_id = int(org["ID"])
        org_name = org.get("TENTOCHUC", "")
        org_tt = org.get("TRANGTHAI")

        url_mem = f"{BASE_URL}/ws/api/DanhGia/getListDanhGiaDoanVien?idToChuc={org_id}&nam={config.YEAR}&currentPage=0&maxSize=5000&keyword="
        h_mem = {"Authorization": f"Bearer {admin_client.token}", "X-XSRF-TOKEN": admin_client.get_xsrf(url_mem, ""), "User-Agent": "Mozilla/5.0"}
        try:
            r_mem = admin_client.session.get(url_mem, headers=h_mem, timeout=20)
            m_list = r_mem.json() if r_mem.status_code == 200 else []
        except Exception:
            m_list = []

        tot_members_dg += len(m_list)
        xs_count = sum(1 for m in m_list if m.get("IDDANHGIA") == 4.0)
        tot_xuat_sac += xs_count
        not_xs = [m.get("HOTEN") for m in m_list if m.get("IDDANHGIA") != 4.0]
        chua_dg_all += len(not_xs)

        if len(not_xs) > 0 or org_tt != 2.0:
            discrepancies_dg.append({
                "ten": org_name,
                "id": org_id,
                "total": len(m_list),
                "xs": xs_count,
                "not_xs_count": len(not_xs),
                "not_xs_names": not_xs,
                "status_admin": org_tt
            })

    if not silent:
        print(f" • Tổng số Chi đoàn kiểm tra             : {total_orgs} chi đoàn")
        print(f" • Chi đoàn Admin đã duyệt (Trạng thái 2) : {orgs_approved}/{total_orgs} chi đoàn")
        print(f" • Tổng số đoàn viên trong danh sách ĐG   : {tot_members_dg} ĐV")
        print(f" • Đoàn viên đạt Xuất sắc (ID: 4.0)       : {tot_xuat_sac}/{tot_members_dg} ({tot_xuat_sac/tot_members_dg*100:.1f}%)" if tot_members_dg else "")
        print(f" • Số đoàn viên chưa đạt Xuất sắc         : {chua_dg_all} ĐV")

        if not discrepancies_dg:
            print(" ✅ KẾT QUẢ DOUBLE CHECK: 100% đoàn viên đạt xếp loại Xuất sắc và 100% Chi đoàn đã được Admin phê duyệt!")
        else:
            print(f" ⚠️ Cảnh báo: Có {len(discrepancies_dg)} chi đoàn cần rà soát:")
            for d in discrepancies_dg[:5]:
                print(f"   - {d['ten']}: Tổng {d['total']} | Xuất sắc: {d['xs']} | Chưa XS: {d['not_xs_count']} | Duyệt: {d['status_admin']}")

        print("-" * 88 + "\n")

    return {
        "total_orgs": total_orgs,
        "orgs_approved": orgs_approved,
        "total_members": tot_members_dg,
        "total_xuat_sac": tot_xuat_sac,
        "chua_dg": chua_dg_all,
        "discrepancies": discrepancies_dg,
        "is_perfect": len(discrepancies_dg) == 0
    }

def main():
    print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
    print("║               HỆ THỐNG KIỂM TRA ĐỐI SOÁT CHÉO TỰ ĐỘNG (DOUBLE-CHECK)                 ║")
    print("║          ĐỐI SOÁT CHÉO TỪNG BƯỚC: RÈN LUYỆN + CẤP THẺ + ĐÁNH GIÁ XẾP LOẠI            ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════╝\n")

    admin = get_admin()
    if not admin:
        return

    r1 = check_ren_luyen(admin)
    r2 = check_cap_the(admin)
    r3 = check_danh_gia(admin)

    print("═" * 88)
    print("                      TỔNG KẾT ĐỐI SOÁT TOÀN DIỆN")
    print("═" * 88)
    print(f" 1. Rèn luyện đoàn viên : {'✅ Hoàn hảo 100%' if r1 and r1['is_perfect'] else '⚠️ Cần xử lý'}")
    print(f" 2. Nghiệp vụ cấp thẻ   : {'✅ Hoàn hảo 100%' if r2 and r2['is_perfect'] else '⚠️ Cần xử lý'}")
    print(f" 3. Đánh giá xếp loại   : {'✅ Hoàn hảo 100%' if r3 and r3['is_perfect'] else '⚠️ Cần xử lý'}")
    print("═" * 88 + "\n")

if __name__ == "__main__":
    main()
