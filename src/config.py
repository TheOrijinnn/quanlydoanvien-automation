# Danh sách cấu hình tài khoản và thông số hệ thống
# Hệ thống: https://quanlydoanvien.doanthanhnien.vn

YEAR = "2026"
DEFAULT_PASSWORD = "Abc@123"

# Tài khoản Đoàn cơ sở (Cấp trên duyệt kết quả)
SUPER_ACCOUNT = {
    "name": "Đoàn cơ sở FIE",
    "username": "yfie.hcmute",
    "password": DEFAULT_PASSWORD
}

# Barem điểm chia đều 20 điểm/phần (Tổng 100 điểm)
SCORE_MAP = {
    # Phần 1: 7 tiêu chí (Tổng 20 điểm)
    "1.1": 2, "1.2": 2, "1.3": 2, "1.4": 2, "1.5": 4, "1.6": 4, "1.7": 4,
    # Phần 2: 6 tiêu chí (Tổng 20 điểm)
    "2.1": 3, "2.2": 3, "2.3": 3, "2.4": 3, "2.5": 4, "2.6": 4,
    # Phần 3: 5 tiêu chí (Tổng 20 điểm)
    "3.1": 4, "3.2": 4, "3.3": 4, "3.4": 4, "3.5": 4,
    # Phần 4: 4 tiêu chí (Tổng 20 điểm)
    "4.1": 5, "4.2": 5, "4.3": 5, "4.4": 5,
    # Phần 5: 4 tiêu chí (Tổng 20 điểm)
    "5.1": 5, "5.2": 5, "5.3": 5, "5.4": 5,
}

COMMENT_6M = "Hoàn thành tốt nhiệm vụ"
COMMENT_YEAR = "Hoàn thành tốt nhiệm vụ"

# Danh sách 73 Chi đoàn
CHIDOAN_ACCOUNTS = [
    # Khóa 23
    ("Chi đoàn 23110FIE", "23110fie"),
    ("Chi đoàn 23116FIE", "23116fie"),
    ("Chi đoàn 23119FIE", "23119fie"),
    ("Chi đoàn 23124FIE", "23124fie"),
    ("Chi đoàn 23142FIE", "23142fie"),
    ("Chi đoàn 23143FIE", "23143fie"),
    ("Chi đoàn 23145FIE", "23145fie"),
    ("Chi đoàn 23146FIE", "23146fie"),
    ("Chi đoàn 23149FIE", "23149fie"),
    ("Chi đoàn 23151FIE", "23151fie"),
    ("Chi đoàn 23161FIE", "23161fie"),
    ("Chi đoàn 23144FIE", "23144fie"),
    # Khóa 22 (Đầy đủ 13 Chi đoàn)
    ("Chi đoàn 22110FIE", "22110fie"),
    ("Chi đoàn 22116FIE", "22116fie"),
    ("Chi đoàn 22119FIE", "22119fie"),
    ("Chi đoàn 22124FIE", "22124fie"),
    ("Chi đoàn 22142FIE", "22142fie"),
    ("Chi đoàn 22143FIE", "22143fie"),
    ("Chi đoàn 22144FIE", "22144fie"),
    ("Chi đoàn 22145FIE", "22145fie"),
    ("Chi đoàn 22146FIE", "22146fie"),
    ("Chi đoàn 22147FIE", "22147fie"),
    ("Chi đoàn 22149FIE", "22149fie"),
    ("Chi đoàn 22151FIE", "22151fie"),
    ("Chi đoàn 22161FIE", "22161fie"),
    # Khóa 24
    ("Chi đoàn 24143FIE", "24143fie"),
    ("Chi đoàn 24146FIE", "24146fie"),
    ("Chi đoàn 24144FIE", "24144fie"),
    ("Chi đoàn 24149FIE", "24149fie"),
    ("Chi đoàn 24161FIE", "24161fie"),
    ("Chi đoàn 24142FIE", "24142fie"),
    ("Chi đoàn 24151FIE", "24151fie"),
    ("Chi đoàn 24119FIE", "24119fie"),
    ("Chi đoàn 24147FIE", "24147fie"),
    ("Chi đoàn 24145FIE", "24145fie"),
    ("Chi đoàn 24110FIE", "24110fie"),
    ("Chi đoàn 24116FIE", "24116fie"),
    ("Chi đoàn 24124FIE", "24124fie"),
    # Khóa 25
    ("25110FIE", "25110fie"),
    ("25116FIE", "25116fie"),
    ("25119FIE", "25119fie"),
    ("25124FIE", "25124fie"),
    ("25129FIE", "25129fie"),
    ("25142FIE", "25142fie"),
    ("25143FIE", "25143fie"),
    ("25144FIE", "25144fie"),
    ("25144FIEMA", "25144fiema"),
    ("25145FIE", "25145fie"),
    ("25146FIE", "25146fie"),
    ("25147FIE", "25147fie"),
    ("25149FIE", "25149fie"),
    ("25151FIE", "25151fie"),
    ("25161FIE", "25161fie"),
    # Khóa 26
    ("26110FIE1234", "26110fie1234"),
    ("26110FIE5678", "26110fie5678"),
    ("26116FIE123", "26116fie123"),
    ("26116FIE456", "26116fie456"),
    ("26119FIE", "26119fie"),
    ("26124FIE", "26124fie"),
    ("26126FIE", "26126fie"),
    ("26128FIE", "26128fie"),
    ("26129FIE", "26129fie"),
    ("26130FIE", "26130fie"),
    ("26133FIE", "26133fie"),
    ("26136FIE", "26136fie"),
    ("26142FIE123", "26142fie123"),
    ("26142FIE456", "26142fie456"),
    ("26143FIE123", "26143fie123"),
    ("26143FIE456", "26143fie456"),
    ("26144FIE123", "26144fie123"),
    ("26144FIE456", "26144fie456"),
    ("26144FIEMA", "26144fiema"),
    ("26145FIE123", "26145fie123"),
    ("26145FIE456", "26145fie456"),
    ("26146FIE123", "26146fie123"),
    ("26146FIE456", "26146fie456"),
    ("26147FIE", "26147fie"),
    ("26149FIE", "26149fie"),
    ("26151FIE123", "26151fie123"),
    ("26151FIE456", "26151fie456"),
    ("26161FIE", "26161fie"),
]
