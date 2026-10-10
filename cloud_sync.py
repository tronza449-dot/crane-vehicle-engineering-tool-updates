from __future__ import annotations

import base64
import ctypes
import hashlib
import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
import uuid
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

GITHUB_API = "https://api.github.com"
DEFAULT_REPO = "tronza449-dot/crane-vehicle-engineering-tool-updates"
DEFAULT_BRANCH = "main"
DEFAULT_PATH = "cloud_data/project_state.json"
FORMAT = "CVETCloudProject"
SCHEMA_VERSION = 1


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_repo(repo: str) -> str:
    value = str(repo or "").strip().strip("/")
    if value.startswith("https://github.com/"):
        value = value.split("https://github.com/", 1)[1].strip("/")
    parts = [x for x in value.split("/") if x]
    if len(parts) != 2:
        raise ValueError("GitHub repository ต้องเป็น owner/repository")
    return "/".join(parts)


def normalize_path(path: str) -> str:
    value = str(path or "").replace("\\", "/").strip().strip("/")
    if not value or value.startswith(".") or ".." in value.split("/"):
        raise ValueError("Cloud file path ไม่ถูกต้อง")
    return value


def canonical_state_hash(state: Dict[str, Any]) -> str:
    raw = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def default_device_id() -> str:
    host = "".join(ch for ch in socket.gethostname() if ch.isalnum() or ch in "-_")[:24] or "pc"
    return f"{host}-{uuid.uuid4().hex[:8]}"


def make_cloud_payload(state: Dict[str, Any], device_id: str, app_version: str) -> Dict[str, Any]:
    return {
        "format": FORMAT,
        "schema_version": SCHEMA_VERSION,
        "updated_at": utc_now_iso(),
        "device_id": str(device_id),
        "app_version": str(app_version),
        "state_hash": canonical_state_hash(state),
        "state": state,
    }


def validate_cloud_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("format") != FORMAT:
        raise ValueError("ไฟล์ Cloud ไม่ใช่ CVET Cloud Project")
    state = payload.get("state")
    if not isinstance(state, dict) or state.get("format") != "CraneVehicleEngineeringToolProject":
        raise ValueError("Cloud Project ไม่มี Desktop project state ที่ถูกต้อง")
    expected = str(payload.get("state_hash", ""))
    actual = canonical_state_hash(state)
    if expected and expected != actual:
        raise ValueError("Cloud Project hash ไม่ตรง — ยกเลิกเพื่อป้องกันข้อมูลเสีย")
    payload["state_hash"] = actual
    return payload


def _request(url: str, token: str = "", method: str = "GET", body: Optional[Dict[str, Any]] = None, timeout: int = 20):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "CraneVehicleEngineeringTool-CloudSync",
    }
    if token:
        headers["Authorization"] = f"Bearer {token.strip()}"
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            return response.status, json.loads(raw.decode("utf-8")) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw else {}
        except Exception:
            payload = {"message": raw}
        message = payload.get("message") or f"HTTP {exc.code}"
        err = RuntimeError(f"GitHub HTTP {exc.code}: {message}")
        setattr(err, "status_code", exc.code)
        raise err from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"เชื่อม GitHub ไม่สำเร็จ: {exc.reason}") from exc


def github_repo_info(repo: str, token: str = "") -> Dict[str, Any]:
    repo = normalize_repo(repo)
    _status, data = _request(f"{GITHUB_API}/repos/{repo}", token=token)
    return {
        "full_name": data.get("full_name", repo),
        "private": bool(data.get("private", False)),
        "default_branch": data.get("default_branch", "main"),
        "permissions": data.get("permissions", {}),
    }


def github_get_file(repo: str, branch: str, path: str, token: str = "") -> Optional[Dict[str, Any]]:
    repo = normalize_repo(repo)
    path = normalize_path(path)
    encoded = urllib.parse.quote(path, safe="/")
    ref = urllib.parse.quote(str(branch or "main"), safe="")
    url = f"{GITHUB_API}/repos/{repo}/contents/{encoded}?ref={ref}"
    try:
        _status, data = _request(url, token=token)
    except RuntimeError as exc:
        if getattr(exc, "status_code", None) == 404:
            return None
        raise
    if data.get("type") != "file":
        raise ValueError("Cloud path ไม่ใช่ไฟล์")
    encoded_content = str(data.get("content", "")).replace("\n", "")
    text = base64.b64decode(encoded_content).decode("utf-8") if encoded_content else ""
    return {
        "sha": data.get("sha", ""),
        "content": text,
        "html_url": data.get("html_url", ""),
        "size": data.get("size", 0),
    }


def github_put_file(
    repo: str,
    branch: str,
    path: str,
    text: str,
    token: str,
    message: str,
    sha: str = "",
) -> Dict[str, Any]:
    if not token.strip():
        raise ValueError("ต้องใส่ GitHub Fine-grained Token ก่อน Push")
    repo = normalize_repo(repo)
    path = normalize_path(path)
    encoded = urllib.parse.quote(path, safe="/")
    url = f"{GITHUB_API}/repos/{repo}/contents/{encoded}"
    body = {
        "message": str(message),
        "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
        "branch": str(branch or "main"),
    }
    if sha:
        body["sha"] = sha
    _status, data = _request(url, token=token, method="PUT", body=body, timeout=30)
    return {
        "commit_sha": (data.get("commit") or {}).get("sha", ""),
        "content_sha": (data.get("content") or {}).get("sha", ""),
        "html_url": (data.get("content") or {}).get("html_url", ""),
    }


# Windows DPAPI: the encrypted token can only be decrypted by the same Windows user.
class _DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _blob_from_bytes(data: bytes):
    buf = ctypes.create_string_buffer(data)
    blob = _DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))
    return blob, buf


def protect_secret(secret: str) -> str:
    if not secret:
        return ""
    if os.name != "nt":
        # Do not persist a plaintext secret on non-Windows systems.
        return ""
    raw = secret.encode("utf-8")
    in_blob, _buf = _blob_from_bytes(raw)
    out_blob = _DATA_BLOB()
    ok = ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(in_blob), "CVET GitHub Token", None, None, None, 0, ctypes.byref(out_blob)
    )
    if not ok:
        raise ctypes.WinError()
    try:
        encrypted = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        return base64.b64encode(encrypted).decode("ascii")
    finally:
        ctypes.windll.kernel32.LocalFree(out_blob.pbData)


def unprotect_secret(encoded: str) -> str:
    if not encoded or os.name != "nt":
        return ""
    raw = base64.b64decode(encoded)
    in_blob, _buf = _blob_from_bytes(raw)
    out_blob = _DATA_BLOB()
    ok = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(in_blob), None, None, None, None, 0, ctypes.byref(out_blob)
    )
    if not ok:
        raise ctypes.WinError()
    try:
        decrypted = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        return decrypted.decode("utf-8")
    finally:
        ctypes.windll.kernel32.LocalFree(out_blob.pbData)


def cloud_config_defaults() -> Dict[str, Any]:
    return {
        "enabled": False,
        "repo": DEFAULT_REPO,
        "branch": DEFAULT_BRANCH,
        "path": DEFAULT_PATH,
        "auto_pull": True,
        "auto_push": True,
        "poll_seconds": 120,
        "device_id": default_device_id(),
        "token_dpapi": "",
        "last_remote_sha": "",
        "last_synced_hash": "",
        "last_sync_at": "",
        "last_remote_device": "",
    }


def load_config(path: Path) -> Dict[str, Any]:
    defaults = cloud_config_defaults()
    try:
        if Path(path).exists():
            raw = json.loads(Path(path).read_text(encoding="utf-8-sig"))
            if isinstance(raw, dict):
                defaults.update(raw)
    except Exception:
        pass
    defaults["repo"] = normalize_repo(defaults.get("repo") or DEFAULT_REPO)
    defaults["path"] = normalize_path(defaults.get("path") or DEFAULT_PATH)
    defaults["branch"] = str(defaults.get("branch") or DEFAULT_BRANCH)
    defaults["poll_seconds"] = max(30, min(3600, int(defaults.get("poll_seconds", 120) or 120)))
    return defaults


def save_config(path: Path, config: Dict[str, Any]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    safe = dict(config)
    # Never allow accidental plaintext token persistence.
    safe.pop("token", None)
    tmp = p.with_suffix(p.suffix + ".tmp")
    tmp.write_text(json.dumps(safe, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)
