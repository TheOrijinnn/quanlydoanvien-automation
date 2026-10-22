import requests
import time
import json
import base64
import os
import math
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

BASE_URL = "https://quanlydoanvien.doanthanhnien.vn"

def encrypt_aes(plain_text, password):
    salt = os.urandom(16)
    iv = os.urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA1(), length=32, salt=salt, iterations=100)
    key = kdf.derive(password.encode('utf-8'))
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_text.encode('utf-8')) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return base64.b64encode(salt + iv + ciphertext).decode('utf-8')

def make_xsrf_token(full_url, username, token, body_str=""):
    Ne = full_url[full_url.index("/api"):].strip().lower()
    se = username
    ue = token[-32:] + token[:32]
    xe = body_str

    Re = ""
    while True:
        Re = encrypt_aes(";", se)
        if Re not in (se + Ne + xe):
            break

    Ae = Re + ";" + se + Re + Ne
    if xe:
        Ae += Re + xe

    return encrypt_aes(Ae, ue)

class DoanVienClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()
        
        # User & Organization attributes
        self.user_id = None
        self.tai_khoan = username
        self.id_tochuc = None
        self.id_captc = None
        self.id_loaihtc = None
        self.id_captccaptren = None
        self.ten_tochuc = username
        self.raw_user_info = None

    def login(self, max_retries=5):
        url = f"{BASE_URL}/ws/token"
        for i in range(max_retries):
            try:
                res = self.session.post(url, data={
                    "userName": self.username,
                    "password": self.password,
                    "grant_type": "password"
                }, headers={"Content-Type": "application/x-www-form-urlencoded"}, timeout=20)
                if res.status_code == 200:
                    token_data = res.json()
                    self.token = token_data.get("access_token")
                    
                    # Parse user info
                    try:
                        uinfo_raw = base64.b64decode(token_data.get("userInfo", "")).decode("utf-8")
                        uinfo = json.loads(uinfo_raw)
                        self.raw_user_info = uinfo
                        u_obj = uinfo.get("userInfo", {})
                        self.user_id = u_obj.get("Id")
                        self.tai_khoan = u_obj.get("TaiKhoan", self.username)
                        
                        jsontochuc_raw = u_obj.get("jsontochuc", "[]")
                        jsontochuc = json.loads(jsontochuc_raw)
                        tochuc = next((p for p in jsontochuc if str(p.get("idloaihtc")) == "1"), None)
                        if tochuc:
                            self.id_tochuc = tochuc.get("idtochuc")
                            self.id_captc = tochuc.get("idcaptc")
                            self.id_loaihtc = tochuc.get("idloaihtc")
                            self.id_captccaptren = tochuc.get("idcaptccaptren")
                            self.ten_tochuc = tochuc.get("tentochuc") or tochuc.get("tengon") or self.username
                    except Exception:
                        pass

                    return True
            except Exception:
                time.sleep(1.5)
        return False

    def call(self, endpoint, *params, max_retries=5):
        """Endpoint call for /ws/api/ep/call (used by step1, step2, step3)"""
        if not self.token:
            if not self.login():
                return {}

        url = f"{BASE_URL}/ws/api/ep/call"
        headers = {
            "Content-Type": "application/json;charset=utf-8",
            "Authorization": f"Bearer {self.token}",
            "User-Agent": "Mozilla/5.0"
        }
        for attempt in range(max_retries):
            try:
                res = self.session.post(url, json={"s": endpoint, "p": list(params)}, headers=headers, timeout=30)
                if res.status_code == 200:
                    return res.json()
                elif res.status_code == 401:
                    if self.login():
                        headers["Authorization"] = f"Bearer {self.token}"
                        continue
            except Exception:
                time.sleep(1)
        return {}

    def get_xsrf(self, full_url, body_str=""):
        return make_xsrf_token(full_url, self.tai_khoan, self.token, body_str)
