import hashlib
import json
from datetime import datetime
from typing import List, Optional, Dict, Any

import requests


class FlomoAPI:
    def __init__(self, authorization: str, salt: str = "dbbc3dd73364b4084c3a69346e0ce2b2"):
        self.token = authorization
        self.salt = salt
        self.limit = 200
        self.url_updated = "https://flomoapp.com/api/v1/memo/updated/"
        self.success_code = 0

    def _get_params(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = params or {}
        params_sorted = {
            "limit": self.limit,
            "tz": "8:0",
            "timestamp": str(int(datetime.now().timestamp())),
            "api_key": "flomo_web",
            "app_version": "4.0",
            "webp": "1",
            "platform": "web"
        }
        latest_slug = params.get("latest_slug", "")
        latest_updated_at = params.get("latest_updated_at", 0)
        if latest_slug and latest_updated_at:
            params_sorted.update({
                "latest_slug": latest_slug,
                "latest_updated_at": latest_updated_at
            })
        # Sort parameters and generate signature
        param_str = "&".join([f"{k}={v}" for k, v in sorted(params_sorted.items())])
        sign = hashlib.md5((param_str + self.salt).encode("utf-8")).hexdigest()
        params_sorted["sign"] = sign
        return params_sorted

    def request(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        headers = {"authorization": self.token}
        resp = requests.get(self.url_updated, params=self._get_params(params), headers=headers)
        data = resp.json()
        if data["code"] != self.success_code:
            raise Exception(f"Flomo request error: {data}")
        return data.get("data", []) or []

    def get_all_memos(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        memos = self.request(params)
        if len(memos) >= self.limit:
            _updated_at = int(datetime.fromisoformat(memos[-1]["updated_at"]).timestamp())
            _params = {
                "latest_slug": memos[-1]["slug"],
                "latest_updated_at": _updated_at
            }
            return memos + self.get_all_memos(_params)
        else:
            return memos

    def get_all_memos2(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        path = '/Users/linq/Downloads/flomo.txt'
        with open(path, 'r') as file:
            data = json.load(file)
        return data.get("data")