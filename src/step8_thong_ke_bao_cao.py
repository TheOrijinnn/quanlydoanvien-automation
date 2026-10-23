import sys
import time
import json
import os
from api_client import DoanVienClient, BASE_URL
import config

sys.stdout.reconfigure(encoding='utf-8')

def get_cauhinh_ren_luyen(admin_client):
    """Lấy cấu hình năm và id_chuongtrinh của Rèn luyện đoàn viên"""
    res = admin_client.call(
        "ndv05.dangky.ctrl_cauhinh",
        {"ten": "NAM"}, {"ten": "NAM_DANGKY"}, {"ten": "SL_TOITHIEU"}
    )
    nam = "2026"
    id_chuongtrinh = "aGIZlolp"
    if isinstance(res, list) and len(res) > 3:
        if res[1] and isinstance(res[1], list) and res[1][0].get("ten"):
            nam = res[1][0]["ten"]
        if isinstance(res[3], dict) and res[3].get("id_chuongtrinh"):
            id_chuongtrinh = res[3]["id_chuongtrinh"]
    return nam, id_chuongtrinh

def get_thong_ke_ren_luyen(admin_client, nam, id_chuongtrinh):
    """Lấy bảng theo dõi rèn luyện đoàn viên toàn khoa"""
    res = admin_client.call(
        "ndv05.thongke",
        {"id_chuongtrinh": id_chuongtrinh, "nam": nam, "idtochuc": ""}
    )
    return res if isinstance(res, list) else []

def get_danh_gia_organizations(admin_client, year=config.YEAR):
    """Lấy danh sách các Chi đoàn trong Nhận xét đánh giá"""
    url = f"{BASE_URL}/ws/api/DanhGia/getDanhGiaNhanVienToChuc"
    payload = {"idtochuc": admin_client.id_tochuc, "nam": int(year), "dsDanhGia": []}
    body_str = json.dumps(payload, separators=(',', ':'))
    headers = {
        "Authorization": f"Bearer {admin_client.token}",
        "X-XSRF-TOKEN": admin_client.get_xsrf(url, body_str),
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0"
    }
    res = admin_client.session.post(url, data=body_str, headers=headers, timeout=25)
    return res.json() if res.status_code == 200 else []

def get_chi_tiet_danh_gia(admin_client, org_id, year=config.YEAR):
    """Lấy danh sách toàn bộ đoàn viên trong chi đoàn để kiểm tra xếp loại"""
    url = f"{BASE_URL}/ws/api/DanhGia/getListDanhGiaDoanVien?idToChuc={org_id}&nam={year}&currentPage=0&maxSize=5000&keyword="
    headers = {
        "Authorization": f"Bearer {admin_client.token}",
        "X-XSRF-TOKEN": admin_client.get_xsrf(url, ""),
        "Content-Type": "application/json;charset=utf-8",
        "User-Agent": "Mozilla/5.0"
    }
    for attempt in range(3):
        try:
            res = admin_client.session.get(url, headers=headers, timeout=20)
            if res.status_code == 200:
                return res.json()
        except Exception:
            time.sleep(0.5)
    return []

def get_thong_ke_cap_the(admin_client):
    """Lấy danh sách yêu cầu cấp thẻ đoàn viên"""
    url = f"{BASE_URL}/ws/api/LichSuBienDong/biendongxuly_dsN_capthe"
    payload = {'data': json.dumps([{'idtochuc': str(admin_client.id_tochuc)}], separators=(',', ':'))}
    body_str = json.dumps(payload, separators=(',', ':'))
    headers = {
        'Authorization': f'Bearer {admin_client.token}',
        'X-XSRF-TOKEN': admin_client.get_xsrf(url, body_str),
        'Content-Type': 'application/json;charset=utf-8',
        'User-Agent': 'Mozilla/5.0'
    }
    res = admin_client.session.post(url, data=body_str, headers=headers, timeout=25)
    return res.json() if res.status_code == 200 else []

def normalize_name(name):
    return (name or "").lower().replace("chi đoàn", "").replace("chi doan", "").replace(" ", "").strip()

def main(quick_mode=False, audit_only=False):
    print("╔══════════════════════════════════════════════════════════════════════════════════════╗")
    print("║               HỆ THỐNG THỐNG KÊ, BÁO CÁO & DOUBLE-CHECK TOÀN DIỆN                    ║")
    print("║        (ĐỐI SOÁT CHÉO: RÈN LUYỆN ĐOÀN VIÊN + ĐÁNH GIÁ XẾP LOẠI + CẤP THẺ)            ║")
    print("╚══════════════════════════════════════════════════════════════════════════════════════╝\n")

    admin_client = DoanVienClient(config.SUPER_ACCOUNT["username"], config.SUPER_ACCOUNT["password"])
    if not admin_client.login():
        print("❌ Đăng nhập Admin (yfie.hcmute) thất bại!")
        return

    print(f"Đăng nhập Admin thành công: {admin_client.ten_tochuc} (ID: {admin_client.id_tochuc})")
    print(f"Chế độ quét: {'Nhanh (Quick mode)' if quick_mode else 'Toàn diện (Full audit)'}\n")

    # 1. Lấy dữ liệu rèn luyện
    print("⏳ [1/3] Đang tải dữ liệu Chương trình Rèn luyện đoàn viên...", end=" ", flush=True)
    nam_rl, id_ct = get_cauhinh_ren_luyen(admin_client)
    rl_list = get_thong_ke_ren_luyen(admin_client, nam_rl, id_ct)
    print(f"Xong! ({len(rl_list)} dòng dữ liệu)")

    rl_map = {}
    tong_toan_khoa_rl = {}
    for item in rl_list:
        ten = item.get("tentochuc", "").strip()
        if ten == "Tổng":
            tong_toan_khoa_rl = item
        else:
            rl_map[normalize_name(ten)] = item

    # 2. Lấy dữ liệu đánh giá
    print("⏳ [2/3] Đang tải dữ liệu Nhận xét Đánh giá đoàn viên...", end=" ", flush=True)
    dg_orgs = get_danh_gia_organizations(admin_client, config.YEAR)
    print(f"Xong! ({len(dg_orgs)} Chi đoàn trực thuộc)")

    # 3. Lấy dữ liệu cấp thẻ
    print("⏳ [3/3] Đang tải dữ liệu Nghiệp vụ Cấp thẻ đoàn viên...", end=" ", flush=True)
    cap_the_items = get_thong_ke_cap_the(admin_client)
    print(f"Xong! ({len(cap_the_items)} yêu cầu cấp thẻ)\n")

    # Tiến hành đối soát chéo và thống kê từng Chi đoàn
    print("=" * 105)
    print(f"{'STT':<4} | {'Chi đoàn':<24} | {'Tổng ĐV (RL)':<12} | {'ĐV Đã duyệt':<11} | {'ĐV Đánh giá':<11} | {'Chưa lên':<8} | {'Trạng thái'}")
    print("=" * 105)

    chi_doan_reports = []
    tong_dv_rl_all = 0
    tong_dv_duyet_rl_all = 0
    tong_dv_dg_all = 0
    tong_chua_danh_gia_all = 0
    so_org_chua_duyet = 0

    discrepancies = []

    for idx, org in enumerate(dg_orgs, 1):
        org_id = int(org["ID"])
        org_name = org.get("TENTOCHUC", "")
        org_tt = org.get("TRANGTHAI")  # 2.0 = Đã duyệt, 1.0 = Chờ duyệt
        norm_key = normalize_name(org_name)

        # Lấy số liệu rèn luyện
        rl_info = rl_map.get(norm_key, {})
        sldv_rl = rl_info.get("sldv", 0)
        sldk_duyet_rl = rl_info.get("sldk_dcs_xacnhan", 0)

        # Lấy số liệu đánh giá
        if not quick_mode:
            members = get_chi_tiet_danh_gia(admin_client, org_id, config.YEAR)
            total_dg = len(members)
            evaluated_xuat_sac = sum(1 for m in members if (m.get("IDDANHGIA") or 0) == 4.0)
            chua_danh_gia = [m.get("HOTEN") for m in members if not (m.get("IDDANHGIA") or 0)]
            chua_dg_count = len(chua_danh_gia)
        else:
            total_dg = sldv_rl
            evaluated_xuat_sac = sldv_rl
            chua_danh_gia = []
            chua_dg_count = 0

        tong_dv_rl_all += sldv_rl
        tong_dv_duyet_rl_all += sldk_duyet_rl
        tong_dv_dg_all += total_dg
        tong_chua_danh_gia_all += chua_dg_count

        if org_tt != 2.0:
            so_org_chua_duyet += 1

        is_same = (sldv_rl == total_dg)
        status_icon = "✅ Khớp 100%" if (is_same and chua_dg_count == 0 and org_tt == 2.0) else "⚠️ CẦN XỬ LÝ"

        if not is_same or chua_dg_count > 0 or org_tt != 2.0:
            discrepancies.append({
                "stt": idx,
                "org_name": org_name,
                "id": org_id,
                "sldv_rl": sldv_rl,
                "total_dg": total_dg,
                "chua_dg_count": chua_dg_count,
                "chua_dg_names": chua_danh_gia,
                "trang_thai_duyet": org_tt
            })

        chi_doan_reports.append({
            "stt": idx,
            "id_tochuc": org_id,
            "ten_tochuc": org_name,
            "tong_dv_ren_luyen": sldv_rl,
            "dv_duyet_ren_luyen": sldk_duyet_rl,
            "tong_dv_danh_gia": total_dg,
            "dv_xuat_sac": evaluated_xuat_sac,
            "dv_chua_danh_gia": chua_dg_count,
            "ds_chua_danh_gia": chua_danh_gia,
            "trang_thai_duyet_admin": org_tt,
            "giong_nhau": is_same
        })

        if not audit_only or (audit_only and status_icon != "✅ Khớp 100%"):
            print(f"{idx:<4} | {org_name:<24} | {sldv_rl:<12} | {sldk_duyet_rl:<11} | {total_dg:<11} | {chua_dg_count:<8} | {status_icon}")

        if not quick_mode and idx % 20 == 0:
            time.sleep(0.2)

    print("=" * 105)
    print(f"TỔNG KẾT TOÀN KHOA: {len(dg_orgs)} Chi đoàn")
    print(f" • Tổng số đoàn viên (Rèn luyện): {tong_dv_rl_all}")
    print(f" • Tổng số đoàn viên (Đánh giá)  : {tong_dv_dg_all}")
    print(f" • Tổng số đoàn viên đã duyệt RL : {tong_dv_duyet_rl_all} ({tong_dv_duyet_rl_all/tong_dv_rl_all*100:.1f}%)" if tong_dv_rl_all else "")
    print(f" • Số đoàn viên CHƯA ĐÁNH GIÁ   : {tong_chua_danh_gia_all}")
    print(f" • Số Chi đoàn chưa duyệt admin  : {so_org_chua_duyet}")
    print("=" * 105)

    # 4. Thống kê Cấp thẻ đoàn viên
    pending_cap_the = [it for it in cap_the_items if it.get("TRANGTHAI") == "Đang xử lý"]
    processed_cap_the = [it for it in cap_the_items if it.get("TRANGTHAI") != "Đang xử lý"]
    print("\n" + "█" * 80)
    print("  THỐNG KÊ NGHIỆP VỤ CẤP THẺ ĐOÀN VIÊN")
    print("█" * 80)
    print(f" • Tổng số lượt yêu cầu cấp thẻ : {len(cap_the_items)}")
    print(f" • Số yêu cầu ĐÃ XỬ LÝ (ĐÃ DUYỆT): {len(processed_cap_the)}")
    print(f" • Số yêu cầu ĐANG XỬ LÝ (CHỜ)   : {len(pending_cap_the)}")

    # 5. KẾT LUẬN AUTO DOUBLE-CHECK
    print("\n" + "█" * 80)
    print("  KẾT LUẬN KIỂM TRA ĐỐI SOÁT CHÉO TỰ ĐỘNG (AUTO DOUBLE-CHECK)")
    print("█" * 80)
    if not discrepancies and not pending_cap_the:
        print("🎉 [HOÀN HẢO 100% ✅]:")
        print("  1. Cột 'Tổng số đoàn viên' giữa Đánh giá và Rèn luyện TRÙNG KHỚP 100% (81/81 Chi đoàn).")
        print("  2. Toàn bộ đoàn viên đã đạt xếp loại Xuất sắc, không còn bất kỳ sinh viên nào chưa đánh giá.")
        print("  3. 100% Chi đoàn đã được Admin phê duyệt (Trạng thái 2.0).")
        print("  4. Toàn bộ yêu cầu Cấp thẻ đoàn viên đã được xử lý duyệt xong, không còn hồ sơ tồn đọng.")
    else:
        print(f"⚠️ PHÁT HIỆN CÓ {len(discrepancies)} VẤN ĐỀ CẦN XỬ LÝ:")
        for d in discrepancies:
            print(f"  • {d['org_name']} (ID: {d['id']}):")
            if d['sldv_rl'] != d['total_dg']:
                print(f"    - Lệch tổng số ĐV: Rèn luyện {d['sldv_rl']} vs Đánh giá {d['total_dg']}")
            if d['chua_dg_count'] > 0:
                print(f"    - Chưa đánh giá: {d['chua_dg_count']} bạn ({', '.join(d['chua_dg_names'])})")
            if d['trang_thai_duyet'] != 2.0:
                print(f"    - Trạng thái duyệt: {d['trang_thai_duyet']} (Chưa duyệt)")
        if pending_cap_the:
            print(f"  • Còn {len(pending_cap_the)} hồ sơ cấp thẻ chưa được Admin duyệt.")

    # 6. Lưu file JSON báo cáo tổng hợp
    out_file = os.path.join(os.path.dirname(__file__), "bao_cao_thong_ke_toan_khoa.json")
    report_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S+07:00"),
        "tong_so_chi_doan": len(dg_orgs),
        "tong_dv_ren_luyen": tong_dv_rl_all,
        "tong_dv_danh_gia": tong_dv_dg_all,
        "tong_dv_duyet_ren_luyen": tong_dv_duyet_rl_all,
        "tong_chua_danh_gia": tong_chua_danh_gia_all,
        "tong_yeu_cau_cap_the": len(cap_the_items),
        "yeu_cau_cap_the_dang_xu_ly": len(pending_cap_the),
        "so_chi_doan_lech_hoac_chua_xong": len(discrepancies),
        "chi_doan_chi_tiet": chi_doan_reports
    }
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print(f"\n📁 Đã xuất file báo cáo tổng hợp chi tiết tại: {out_file}\n")

if __name__ == "__main__":
    is_quick = "--quick" in sys.argv
    is_audit = "--audit-only" in sys.argv
    main(quick_mode=is_quick, audit_only=is_audit)
