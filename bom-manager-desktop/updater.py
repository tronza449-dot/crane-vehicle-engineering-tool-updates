"""GitHub Release updater for the Windows BOM Manager desktop application.

Only releases tagged bom-vMAJOR.MINOR.PATCH are considered, so Crane Vehicle
Engineering Tool releases cannot accidentally update this separate app.
"""
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

OWNER = "tronza449-dot"
REPO = "crane-vehicle-engineering-tool-updates"
ASSET_NAME = "CraneVehicleBOMManager_Setup.exe"
CHECKSUM_NAME = ASSET_NAME + ".sha256"
RELEASES_API = f"https://api.github.com/repos/{OWNER}/{REPO}/releases"
VERSION_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
TAG_RE = re.compile(r"^bom-v(\d+\.\d+\.\d+)$")
MAX_DOWNLOAD = 350 * 1024 * 1024  # Reject unexpectedly large installers.


class UpdateError(Exception):
    """An update could not be safely checked or downloaded."""


class DownloadCanceled(UpdateError):
    """Download canceled by the user."""


def current_version():
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    try:
        version = (root / "VERSION").read_text(encoding="utf-8").strip()
        version_tuple(version)
        return version
    except (OSError, ValueError) as exc:
        raise UpdateError("ไม่พบข้อมูลเวอร์ชันของโปรแกรม (VERSION)") from exc


def version_tuple(value):
    match = VERSION_RE.fullmatch(str(value))
    if not match:
        raise ValueError("Version must be MAJOR.MINOR.PATCH")
    return tuple(int(piece) for piece in match.groups())


def _read_url(url, max_bytes=128 * 1024):
    req = Request(url, headers={"User-Agent": "CraneVehicleBOMManager-Updater/1.0",
                                "Accept": "application/vnd.github+json"})
    with urlopen(req, timeout=25) as response:
        data = response.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise UpdateError("ข้อมูลจากเซิร์ฟเวอร์มีขนาดผิดปกติ")
    return data


def _asset_for(release, name):
    return next((a for a in release.get("assets", []) if a.get("name") == name
                 and a.get("state") == "uploaded"), None)


def _trusted_asset_url(url, tag, name):
    """Only download the named asset from the configured repository and tag."""
    parts = urlsplit(url)
    return (parts.scheme == "https"
            and parts.netloc == "github.com"
            and parts.path == f"/{OWNER}/{REPO}/releases/download/{tag}/{name}"
            and not parts.username and not parts.password and not parts.query
            and not parts.fragment)


def find_update(installed_version):
    """Return newer BOM Release metadata, None if latest; error if no BOM Release."""
    installed = version_tuple(installed_version)
    found = []
    for page in range(1, 6):  # Other apps publish releases in this same repository.
        url = f"{RELEASES_API}?per_page=100&page={page}"
        try:
            releases = json.loads(_read_url(url, max_bytes=2 * 1024 * 1024))
        except (OSError, ValueError, TypeError) as exc:
            raise UpdateError(f"ตรวจสอบ GitHub Releases ไม่สำเร็จ: {exc}") from exc
        if not isinstance(releases, list):
            raise UpdateError("GitHub Releases ส่งข้อมูลไม่ถูกต้องหรือเกินโควตา API")
        for release in releases:
            tag = str(release.get("tag_name", ""))
            match = TAG_RE.fullmatch(tag)
            if not match or release.get("draft") or release.get("prerelease"):
                continue
            exe = _asset_for(release, ASSET_NAME)
            sha = _asset_for(release, CHECKSUM_NAME)
            if not exe or not sha:
                continue  # Skip half-published/broken releases.
            if not (_trusted_asset_url(exe.get("browser_download_url", ""), tag, ASSET_NAME)
                    and _trusted_asset_url(sha.get("browser_download_url", ""), tag, CHECKSUM_NAME)):
                continue
            size = exe.get("size", 0)
            if not isinstance(size, int) or not (0 < size <= MAX_DOWNLOAD):
                continue
            found.append({"version": match.group(1), "tag": tag, "url": exe["browser_download_url"],
                          "sha_url": sha["browser_download_url"], "size": size,
                          "release_url": release.get("html_url", "")})
        if found or len(releases) < 100:
            break
    if not found:
        raise UpdateError("ยังไม่พบ BOM Manager Release พร้อมไฟล์ติดตั้งและ SHA256 บน GitHub")
    latest = max(found, key=lambda x: version_tuple(x["version"]))
    return latest if version_tuple(latest["version"]) > installed else None


def download_update(release, progress=None, cancelled=None):
    """Download and checksum-verify an installer; returns local Path.

    The caller must invoke it in a worker thread. Never execute a .part file.
    """
    tag = release["tag"]
    url, sha_url = release["url"], release["sha_url"]
    if not (_trusted_asset_url(url, tag, ASSET_NAME)
            and _trusted_asset_url(sha_url, tag, CHECKSUM_NAME)
            and TAG_RE.fullmatch(tag)):
        raise UpdateError("ลิงก์ไฟล์อัปเดตไม่ปลอดภัยหรือไม่ใช่ BOM Manager")
    try:
        checksum_text = _read_url(sha_url, max_bytes=1024).decode("utf-8-sig").strip()
    except (OSError, UnicodeError) as exc:
        raise UpdateError(f"อ่าน SHA256 ไม่สำเร็จ: {exc}") from exc
    match = re.fullmatch(r"([a-fA-F0-9]{64})\s+\*?" + re.escape(ASSET_NAME), checksum_text)
    if not match:
        raise UpdateError("รูปแบบไฟล์ SHA256 ไม่ถูกต้อง")
    expected_hash = match.group(1).lower()
    expected_size = release["size"]
    if not (0 < expected_size <= MAX_DOWNLOAD):
        raise UpdateError("ขนาดไฟล์ติดตั้งผิดปกติ")

    directory = Path(tempfile.mkdtemp(prefix="CVBOM_Update_"))
    pending = directory / (ASSET_NAME + ".part")
    installer = directory / ASSET_NAME
    digest = hashlib.sha256()
    received = 0
    try:
        request = Request(url, headers={"User-Agent": "CraneVehicleBOMManager-Updater/1.0"})
        with urlopen(request, timeout=40) as response, open(pending, "wb") as file:
            while True:
                if cancelled is not None and cancelled.is_set():
                    raise DownloadCanceled("ยกเลิกการดาวน์โหลดแล้ว")
                chunk = response.read(256 * 1024)
                if not chunk:
                    break
                received += len(chunk)
                if received > MAX_DOWNLOAD or received > expected_size:
                    raise UpdateError("ไฟล์ที่ดาวน์โหลดมีขนาดผิดปกติ")
                digest.update(chunk)
                file.write(chunk)
                if progress is not None:
                    progress(received, expected_size)
        if received != expected_size:
            raise UpdateError(f"ดาวน์โหลดไม่ครบ ({received}/{expected_size} ไบต์)")
        if digest.hexdigest() != expected_hash:
            raise UpdateError("ตรวจสอบ SHA256 ไม่ผ่าน: ไม่เปิดไฟล์อัปเดตที่อาจเสียหาย")
        if cancelled is not None and cancelled.is_set():
            raise DownloadCanceled("ยกเลิกการดาวน์โหลดแล้ว")
        os.replace(pending, installer)
        return installer
    except Exception:
        shutil.rmtree(directory, ignore_errors=True)
        raise
