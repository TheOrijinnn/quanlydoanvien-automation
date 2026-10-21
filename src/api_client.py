import requests
import time
import json

BASE_URL = "https://quanlydoanvien.doanthanhnien.vn"

class DoanVienClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.token = None
        self.session = requests.Session()

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
                    self.token = res.json().get("access_token")
                    return True
            except Exception:
                time.sleep(1.5)
        return False

    def call(self, endpoint, *params, max_retries=5):
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
                    # Token expired, re-login
                    if self.login():
                        headers["Authorization"] = f"Bearer {self.token}"
                        continue
            except Exception:
                time.sleep(1)
        return {}
