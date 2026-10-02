from __future__ import annotations

import argparse
import json
import os
import queue
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path


CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
TAILSCALE_DOWNLOAD_URL = "https://tailscale.com/download/windows"
TUNNEL_RE = re.compile(r"https://[-a-z0-9]+\.trycloudflare\.com", re.I)
HTTPS_RE = re.compile(r"https://[^\s<>\"']+", re.I)


def app_data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    path = Path(base) / "CraneVehicleEngineeringTool" / "web"
    path.mkdir(parents=True, exist_ok=True)
    return path


def web_status_path() -> Path:
    return app_data_dir() / "web_status.json"


def write_web_status(mode: str, state: str, url: str = "", message: str = "") -> None:
    """Share Web Server state back to the desktop CVET UI."""
    path = web_status_path()
    tmp = path.with_suffix(".tmp")
    payload = {
        "mode": str(mode or ""),
        "state": str(state or ""),
        "url": str(url or ""),
        "message": str(message or ""),
        "updated_at": time.time(),
    }
    try:
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
    except Exception:
        try:
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass


def local_ip() -> str:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except Exception:
        return "127.0.0.1"


def wait_for_server(port: int, timeout: float = 20.0) -> bool:
    end = time.time() + timeout
    url = f"http://127.0.0.1:{port}/api/health"
    while time.time() < end:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                return resp.status == 200
        except Exception:
            time.sleep(0.25)
    return False


def ensure_cloudflared() -> Path:
    target = app_data_dir() / "cloudflared.exe"
    if target.exists() and target.stat().st_size > 1_000_000:
        return target

    print("\n[CVET] กำลังดาวน์โหลด Cloudflare Tunnel จาก GitHub ทางการ...")
    tmp = target.with_suffix(".download")
    try:
        req = urllib.request.Request(
            CLOUDFLARED_URL,
            headers={"User-Agent": "CraneVehicleEngineeringTool-WebLauncher"},
        )
        with urllib.request.urlopen(req, timeout=60) as response, open(tmp, "wb") as out:
            while True:
                block = response.read(1024 * 1024)
                if not block:
                    break
                out.write(block)
        tmp.replace(target)
    finally:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass

    if not target.exists():
        raise RuntimeError("ดาวน์โหลด cloudflared ไม่สำเร็จ")
    return target


def find_tailscale() -> Path | None:
    candidates = []
    w = shutil.which("tailscale")
    if w:
        candidates.append(Path(w))
    for env_name in ("ProgramFiles", "ProgramFiles(x86)", "LOCALAPPDATA"):
        base = os.environ.get(env_name)
        if base:
            candidates.extend([
                Path(base) / "Tailscale" / "tailscale.exe",
                Path(base) / "Programs" / "Tailscale" / "tailscale.exe",
            ])
    for p in candidates:
        try:
            if p.exists():
                return p
        except Exception:
            pass
    return None


def install_tailscale_windows() -> Path | None:
    print("\n[CVET] ยังไม่พบ Tailscale")
    print("[CVET] โหมด Permanent Free Link ต้องติดตั้ง Tailscale ฟรีเพียงครั้งแรก")
    print("[CVET] กำลังลองติดตั้งผ่าน Windows Package Manager (winget)...\n")
    winget = shutil.which("winget")
    if winget:
        try:
            code = subprocess.call([
                winget, "install",
                "--id", "Tailscale.Tailscale",
                "-e",
                "--accept-package-agreements",
                "--accept-source-agreements",
            ])
            if code == 0:
                time.sleep(2.0)
                found = find_tailscale()
                if found:
                    return found
        except Exception as exc:
            print(f"[CVET] winget install ไม่สำเร็จ: {exc}")

    print("\n[CVET] เปิดหน้าดาวน์โหลด Tailscale ทางการให้แล้ว")
    print("[CVET] ติดตั้งให้เสร็จ แล้วกลับมาหน้าต่างนี้")
    try:
        webbrowser.open(TAILSCALE_DOWNLOAD_URL)
    except Exception:
        pass
    input("กด Enter หลังติดตั้ง Tailscale เสร็จแล้ว: ")
    return find_tailscale()


def tailscale_json(ts: Path, *args: str) -> dict:
    try:
        cp = subprocess.run(
            [str(ts), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
        if cp.returncode != 0:
            return {}
        return json.loads(cp.stdout or "{}")
    except Exception:
        return {}


def tailscale_is_online(ts: Path) -> bool:
    data = tailscale_json(ts, "status", "--json")
    backend = str(data.get("BackendState", "")).lower()
    self_info = data.get("Self") or {}
    online = self_info.get("Online")
    return backend == "running" and online is not False


def ensure_tailscale_login(ts: Path) -> bool:
    if tailscale_is_online(ts):
        return True

    print("\n[CVET] Tailscale ยังไม่ได้ Login")
    print("[CVET] Browser อาจเปิดให้ Login ด้วย Google/Microsoft/GitHub")
    try:
        cp = subprocess.run(
            [str(ts), "up"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=45,
        )
        combined = (cp.stdout or "") + "\n" + (cp.stderr or "")
        for url in HTTPS_RE.findall(combined):
            if "tailscale" in url.lower():
                try:
                    webbrowser.open(url.rstrip(".,)"))
                except Exception:
                    pass
                break
        if combined.strip():
            print(combined.strip())
    except subprocess.TimeoutExpired:
        pass
    except Exception as exc:
        print(f"[CVET] เปิด Tailscale login ไม่สำเร็จ: {exc}")

    print("\n[CVET] รอการ Login Tailscale...")
    for _ in range(120):
        if tailscale_is_online(ts):
            print("[CVET] Login Tailscale สำเร็จ")
            return True
        time.sleep(1.0)
    return False


def set_tailscale_hostname(ts: Path, hostname: str) -> tuple[bool, str]:
    """Rename the Tailscale machine and verify the MagicDNS name really changed."""
    hostname = re.sub(r"[^a-z0-9-]+", "-", hostname.strip().lower()).strip("-") or "cvet"
    before = tailscale_dns_name(ts)
    try:
        cp = subprocess.run(
            [str(ts), "set", f"--hostname={hostname}"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
        )
        output = ((cp.stdout or "") + "\n" + (cp.stderr or "")).strip()
        if cp.returncode != 0:
            msg = output or f"tailscale set exited with code {cp.returncode}"
            print(f"[CVET] เปลี่ยนชื่อ Tailscale ไม่สำเร็จ: {msg}")
            return False, msg

        # The control plane can take a few seconds to return the new MagicDNS name.
        expected_prefix = hostname + "."
        for _ in range(20):
            dns = tailscale_dns_name(ts)
            if dns and (dns == hostname or dns.startswith(expected_prefix)):
                print(f"[CVET] Tailscale machine name = {dns}")
                return True, dns
            time.sleep(0.5)

        after = tailscale_dns_name(ts)
        if after and after != before:
            print(f"[CVET] Tailscale machine name = {after}")
            return True, after
        return False, after or output or "Tailscale ยังรายงานชื่อเครื่องเดิม"
    except Exception as exc:
        return False, str(exc)


def tailscale_dns_name(ts: Path) -> str:
    data = tailscale_json(ts, "status", "--json")
    self_info = data.get("Self") or {}
    name = str(self_info.get("DNSName") or "").strip().rstrip(".")
    return name


def funnel_status_text(ts: Path) -> str:
    try:
        cp = subprocess.run(
            [str(ts), "funnel", "status"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
        )
        return ((cp.stdout or "") + "\n" + (cp.stderr or "")).strip()
    except Exception:
        return ""


def funnel_looks_active(ts: Path, port: int) -> bool:
    status = funnel_status_text(ts).lower()
    if not status:
        return False
    target1 = f"127.0.0.1:{port}".lower()
    target2 = f"localhost:{port}".lower()
    return ("funnel on" in status or "available on the internet" in status) and (target1 in status or target2 in status or f":{port}" in status)


def _reader_to_queue(stream, q):
    try:
        for line in iter(stream.readline, ""):
            q.put(line)
    except Exception:
        pass
    finally:
        q.put(None)


def enable_tailscale_funnel(ts: Path, port: int) -> tuple[bool, str]:
    """Enable Funnel without hiding the first-time approval URL.

    Tailscale's first Funnel command can wait for browser approval.  Older CVET
    builds used subprocess.run(..., timeout=45), which hid the approval URL
    until timeout.  This version streams the output, opens the approval page as
    soon as Tailscale prints it, and patiently waits for the user to approve.
    """
    target = f"http://127.0.0.1:{port}"
    cmd = [str(ts), "funnel", "--bg", "--yes", target]
    deadline = time.time() + 300.0
    approval_url = ""
    combined_lines = []
    attempt = 0

    while time.time() < deadline and attempt < 6:
        attempt += 1
        print("\n[CVET] กำลังเปิด Tailscale Funnel...")
        if attempt == 1:
            print("[CVET] ถ้าเป็นครั้งแรก Browser จะเปิดหน้า Enable Funnel ให้อัตโนมัติ")

        write_web_status(
            "PERMANENT",
            "funnel_starting",
            message="กำลังสร้างลิงก์ HTTPS... ถ้าเป็นครั้งแรก Browser จะเปิดหน้า Enable Funnel ให้อัตโนมัติ",
        )

        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
            )
        except Exception as exc:
            return False, str(exc)

        q = queue.Queue()
        reader = threading.Thread(
            target=_reader_to_queue,
            args=(proc.stdout, q),
            name="CVET-Tailscale-Output",
            daemon=True,
        )
        reader.start()

        last_status_check = 0.0
        saw_eof = False

        while time.time() < deadline:
            try:
                item = q.get(timeout=0.35)
            except queue.Empty:
                item = ""

            if item is None:
                saw_eof = True
            elif item:
                line = item.rstrip()
                if line:
                    print(line)
                    combined_lines.append(line)
                    if len(combined_lines) > 80:
                        combined_lines = combined_lines[-80:]

                for raw_url in HTTPS_RE.findall(line):
                    url = raw_url.rstrip(".,)")
                    low = url.lower()
                    if "tailscale.com" in low and ("funnel" in low or "/f/" in low or "login." in low):
                        if url != approval_url:
                            approval_url = url
                            write_web_status(
                                "PERMANENT",
                                "approval_required",
                                url=url,
                                message="ต้องอนุญาต Funnel ครั้งแรก • เปิดหน้า Tailscale ให้แล้ว กรุณากด Enable Funnel",
                            )
                            print("\n[CVET] ต้องอนุญาต Funnel ครั้งแรก")
                            print(f"[CVET] เปิด Browser: {url}")
                            try:
                                webbrowser.open(url)
                            except Exception:
                                pass

            now = time.time()
            if now - last_status_check >= 2.0:
                last_status_check = now
                if funnel_looks_active(ts, port):
                    try:
                        if proc.poll() is None:
                            proc.terminate()
                    except Exception:
                        pass
                    dns = tailscale_dns_name(ts)
                    public_url = f"https://{dns}" if dns else ""
                    if public_url:
                        return True, public_url
                    return True, ""

            code = proc.poll()
            if code is not None and saw_eof:
                if code == 0:
                    dns = tailscale_dns_name(ts)
                    public_url = f"https://{dns}" if dns else ""
                    return True, public_url

                # First-time authorization can cause the command to end before
                # the browser approval is completed.  Keep waiting and retry.
                if approval_url:
                    write_web_status(
                        "PERMANENT",
                        "approval_required",
                        url=approval_url,
                        message="รอการกด Enable Funnel ใน Browser... โปรแกรมจะลองต่อให้อัตโนมัติ",
                    )
                    break

                text_out = "\n".join(combined_lines[-20:])
                return False, text_out or f"tailscale funnel exited with code {code}"

        try:
            if proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=3)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

        if approval_url and time.time() < deadline:
            # Give the admin console a moment to propagate the Funnel capability,
            # then retry the exact command automatically.
            for _ in range(10):
                if time.time() >= deadline:
                    break
                if funnel_looks_active(ts, port):
                    dns = tailscale_dns_name(ts)
                    return True, f"https://{dns}" if dns else ""
                time.sleep(1.0)
            continue

    if approval_url:
        return False, "หมดเวลารอการอนุญาต Funnel (5 นาที) • เปิดหน้า Tailscale ที่โปรแกรมเปิดไว้ กด Enable Funnel แล้วลองใหม่"
    return False, "\n".join(combined_lines[-20:]) or "เปิด Tailscale Funnel ไม่สำเร็จ"


def run_server_thread(host: str, port: int):
    import uvicorn
    from web_server import app

    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
        log_level="info",
        access_log=False,
    )
    server = uvicorn.Server(config)
    server.install_signal_handlers = lambda: None
    thread = threading.Thread(target=server.run, name="CVET-Web", daemon=True)
    thread.start()
    return server, thread


def run_tailscale_mode(port: int, hostname: str, no_browser: bool) -> int:
    write_web_status("PERMANENT", "starting", message="กำลังเตรียม Tailscale Permanent Link...")
    ts = find_tailscale()
    if ts is None and os.name == "nt":
        write_web_status("PERMANENT", "installing", message="ยังไม่พบ Tailscale • กำลังติดตั้ง/เปิดหน้าดาวน์โหลดครั้งแรก")
        ts = install_tailscale_windows()
    if ts is None:
        msg="ไม่พบ Tailscale • กรุณาติดตั้ง Tailscale แล้วลองใหม่"
        write_web_status("PERMANENT", "error", message=msg)
        print("\n[CVET] ไม่พบ Tailscale CLI")
        print("ติดตั้งฟรีจาก https://tailscale.com/download แล้วลองใหม่")
        return 3

    write_web_status("PERMANENT", "login", message="กำลังตรวจสอบ Tailscale Login • ถ้า Browser เปิดขึ้นมาให้ Login ให้เสร็จ")
    if not ensure_tailscale_login(ts):
        msg="ยัง Login Tailscale ไม่สำเร็จ • เปิด Tailscale จาก System Tray → Log in แล้วลองใหม่"
        write_web_status("PERMANENT", "error", message=msg)
        print("\n[CVET] ยัง Login Tailscale ไม่สำเร็จ")
        print("เปิด Tailscale จาก System Tray → Log in แล้วลองใหม่")
        return 4

    rename_ok, rename_info = set_tailscale_hostname(ts, hostname)
    if rename_ok:
        write_web_status(
            "PERMANENT",
            "renamed",
            message=f"ตั้งชื่อ Web Link เป็น {hostname} แล้ว • กำลังเปิด CVET Web Server...",
        )
    else:
        write_web_status(
            "PERMANENT",
            "rename_warning",
            message=("เปิดเว็บได้ แต่เปลี่ยนชื่อ Tailscale อัตโนมัติไม่สำเร็จ • "
                     "Browser จะเปิดหน้า Machines ให้แก้ชื่อเป็น '"+hostname+"' เองครั้งเดียว"),
        )
        print("\n[CVET] หมายเหตุ: เปลี่ยน machine name อัตโนมัติไม่สำเร็จ")
        if rename_info:
            print("[CVET]", rename_info)
        try:
            webbrowser.open("https://login.tailscale.com/admin/machines")
        except Exception:
            pass

    write_web_status("PERMANENT", "server_starting", message="Login สำเร็จ • กำลังเปิด CVET Web Server...")
    server, thread = run_server_thread("127.0.0.1", port)
    if not wait_for_server(port):
        msg="CVET Web Server เริ่มทำงานไม่สำเร็จ"
        write_web_status("PERMANENT", "error", message=msg)
        print("[CVET] Web server เริ่มทำงานไม่สำเร็จ")
        return 2

    write_web_status("PERMANENT", "funnel_starting", message="Web Server พร้อม • กำลังสร้างลิงก์ HTTPS แบบถาวร...")
    ok, public_url = enable_tailscale_funnel(ts, port)
    if not ok:
        msg="เปิด Tailscale Funnel ไม่สำเร็จ"
        if public_url:
            msg += " • " + str(public_url)[:300]
        write_web_status("PERMANENT", "error", message=msg)
        print("\n[CVET] เปิด Tailscale Funnel ไม่สำเร็จ")
        print(public_url)
        server.should_exit = True
        thread.join(timeout=5)
        return 5

    if public_url:
        write_web_status("PERMANENT", "ready", url=public_url, message="FREE PERMANENT LINK พร้อมใช้งาน")
    else:
        write_web_status("PERMANENT", "error", message="Funnel เปิดแล้ว แต่ยังอ่าน URL *.ts.net ไม่ได้ • ลองเปิดใหม่อีกครั้ง")

    print("\n" + "=" * 68)
    print(" FREE PERMANENT WEB พร้อมใช้งาน")
    if public_url:
        print(f" {public_url}")
    else:
        print(" ใช้คำสั่ง: tailscale funnel status เพื่อดู URL")
    print("=" * 68)
    print("ลิงก์ *.ts.net จะคงเดิมตราบใดที่ชื่อเครื่องและ Tailnet เดิมยังใช้ต่อ")
    print("ไม่ต้อง Port Forward และไม่ต้องซื้อ Domain")
    print("เครื่องนี้ต้องเปิด CVET Web Server และ Tailscale อยู่ขณะใช้งานเว็บ")
    print("กด Ctrl+C เพื่อหยุด CVET Web Server\n")

    if public_url and not no_browser:
        try:
            webbrowser.open(public_url)
        except Exception:
            pass

    try:
        while thread.is_alive():
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\n[CVET] กำลังปิด CVET Web Server...")
    finally:
        server.should_exit = True
        thread.join(timeout=5)
    return 0


def run_cloudflare_mode(port: int, no_browser: bool) -> int:
    write_web_status("QUICK", "starting", message="กำลังเปิด Cloudflare Quick Public Link...")
    server, thread = run_server_thread("127.0.0.1", port)
    if not wait_for_server(port):
        write_web_status("QUICK", "error", message="CVET Web Server เริ่มทำงานไม่สำเร็จ")
        print("[CVET] Web server เริ่มทำงานไม่สำเร็จ")
        return 2

    cloudflared = ensure_cloudflared()
    cmd = [
        str(cloudflared),
        "tunnel",
        "--url", f"http://127.0.0.1:{port}",
        "--no-autoupdate",
    ]

    print("\n[CVET] กำลังสร้าง Cloudflare Quick Link...")
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
    )

    public_url = None
    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            match = TUNNEL_RE.search(line)
            if match and public_url is None:
                public_url = match.group(0)
                write_web_status("QUICK", "ready", url=public_url, message="Quick Public Link พร้อมใช้งาน")
                print("\n" + "=" * 68)
                print(" QUICK PUBLIC WEB พร้อมใช้งาน")
                print(f" {public_url}")
                print("=" * 68)
                print("ลิงก์ Quick Tunnel จะเปลี่ยนเมื่อปิดแล้วเปิดใหม่")
                if not no_browser:
                    try:
                        webbrowser.open(public_url)
                    except Exception:
                        pass
            elif "ERR" in line.upper() or "ERROR" in line.upper():
                print("[cloudflared]", line.strip())
        return proc.wait()
    except KeyboardInterrupt:
        print("\n[CVET] กำลังปิด Quick Public Web...")
        return 0
    finally:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        server.should_exit = True
        thread.join(timeout=5)


def main() -> int:
    parser = argparse.ArgumentParser(description="Crane Vehicle Engineering Tool Web Server")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--public", action="store_true", help="Cloudflare Quick Tunnel")
    parser.add_argument("--tailscale", action="store_true", help="Tailscale Funnel permanent free link")
    parser.add_argument("--tailscale-hostname", default="cvet", help="Machine name used in the Tailscale URL")
    parser.add_argument("--lan", action="store_true", help="ให้เครื่องใน Wi-Fi/LAN เดียวกันเข้าได้")
    parser.add_argument("--pin", default="", help="PIN ที่ต้องกรอกบนเว็บก่อนคำนวณ")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        print("เลือกโหมด Web Server")
        print("  1) FREE PERMANENT LINK — Tailscale Funnel (*.ts.net) [แนะนำ]")
        print("  2) QUICK PUBLIC LINK — Cloudflare (ลิงก์สุ่ม)")
        print("  3) LAN / Wi-Fi — ใช้เฉพาะเครือข่ายเดียวกัน")
        print("  4) LOCAL — ใช้เฉพาะเครื่องนี้")
        choice = input("เลือก [1/2/3/4] (ค่าเริ่มต้น 1): ").strip() or "1"
        if choice == "1":
            args.tailscale = True
            pin = input("ตั้ง Web PIN (เว้นว่างได้): ").strip()
            if pin:
                args.pin = pin
        elif choice == "2":
            args.public = True
            pin = input("ตั้ง Web PIN (เว้นว่างได้): ").strip()
            if pin:
                args.pin = pin
        elif choice == "3":
            args.lan = True

    if args.pin:
        os.environ["CVET_WEB_PIN"] = args.pin.strip()

    port = max(1, min(65535, int(args.port)))

    print("=" * 68)
    print(" Crane Vehicle Engineering Tool — Web Server")
    print("=" * 68)
    print(f" Local URL : http://127.0.0.1:{port}")
    if args.lan and not args.public and not args.tailscale:
        print(f" LAN URL   : http://{local_ip()}:{port}")
    if args.pin:
        print(" Web PIN   : เปิดใช้งานแล้ว")
    else:
        print(" Web PIN   : ไม่ได้ตั้ง")
    print("=" * 68)

    if args.tailscale:
        return run_tailscale_mode(port, args.tailscale_hostname, args.no_browser)

    if args.public:
        return run_cloudflare_mode(port, args.no_browser)

    host = "0.0.0.0" if args.lan else "127.0.0.1"
    ready_url = f"http://{local_ip()}:{port}" if args.lan else f"http://127.0.0.1:{port}"
    write_web_status("LAN" if args.lan else "LOCAL", "ready", url=ready_url, message="Web Server พร้อมใช้งาน")
    import uvicorn
    from web_server import app
    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
    uvicorn.run(app, host=host, port=port, log_level="info")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
