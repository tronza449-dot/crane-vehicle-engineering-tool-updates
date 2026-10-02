from __future__ import annotations

import argparse
import getpass
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path


CLOUDFLARED_URL = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
TUNNEL_RE = re.compile(r"https://[-a-z0-9]+\.trycloudflare\.com", re.I)
DEFAULT_PERMANENT_HOSTNAME = "cvet.caranimal.tech"


def app_data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    path = Path(base) / "CraneVehicleEngineeringTool" / "web"
    path.mkdir(parents=True, exist_ok=True)
    return path


def permanent_meta_path() -> Path:
    return app_data_dir() / "permanent_tunnel.json"


def permanent_token_path() -> Path:
    return app_data_dir() / "permanent_tunnel_token.txt"


def normalize_hostname(value: str) -> str:
    value = (value or DEFAULT_PERMANENT_HOSTNAME).strip()
    value = re.sub(r"^https?://", "", value, flags=re.I).strip().strip("/")
    return value or DEFAULT_PERMANENT_HOSTNAME


def load_permanent_meta() -> dict:
    try:
        data = json.loads(permanent_meta_path().read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def save_permanent_meta(hostname: str) -> None:
    permanent_meta_path().write_text(
        json.dumps({"hostname": normalize_hostname(hostname)}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_tunnel_token(token: str) -> Path:
    path = permanent_token_path()
    path.write_text(token.strip(), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass
    return path


def read_tunnel_token() -> str:
    env = os.environ.get("CVET_TUNNEL_TOKEN", "").strip() or os.environ.get("TUNNEL_TOKEN", "").strip()
    if env:
        return env
    try:
        return permanent_token_path().read_text(encoding="utf-8").strip()
    except Exception:
        return ""


def forget_permanent_config() -> None:
    for p in (permanent_token_path(), permanent_meta_path()):
        try:
            p.unlink(missing_ok=True)
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


def run_named_tunnel(port: int, hostname: str, no_browser: bool) -> int:
    hostname = normalize_hostname(hostname)
    url = f"https://{hostname}"
    token = read_tunnel_token()
    if not token:
        print("\n" + "=" * 68)
        print(" PERMANENT LINK — ตั้งค่าครั้งแรก")
        print("=" * 68)
        print(f" เป้าหมาย: {url}")
        print(" ต้องมี Cloudflare Named Tunnel ที่ Publish Hostname นี้")
        print(f" Service ต้องชี้มาที่: http://localhost:{port}")
        print("")
        print(" ไปที่ Cloudflare Dashboard > Networking > Tunnels")
        print(" สร้าง/เลือก Tunnel แล้ว Copy Tunnel Token (ขึ้นต้นประมาณ eyJ...)")
        print(" Token จะเก็บเฉพาะในเครื่องนี้ ไม่ถูกส่งเข้า GitHub")
        print("=" * 68)
        token = getpass.getpass("วาง Tunnel Token แล้วกด Enter: ").strip()
        if not token:
            print("[CVET] ยังไม่ได้ใส่ Tunnel Token — ยกเลิก Permanent Link")
            return 4
        save_tunnel_token(token)

    save_permanent_meta(hostname)
    cloudflared = ensure_cloudflared()

    server, thread = run_server_thread("127.0.0.1", port)
    if not wait_for_server(port):
        print("[CVET] Web server เริ่มทำงานไม่สำเร็จ")
        return 2

    print("\n" + "=" * 68)
    print(" CVET PERMANENT WEB")
    print(f" URL       : {url}")
    print(f" Local     : http://127.0.0.1:{port}")
    print(" Tunnel    : Cloudflare Named Tunnel")
    print(" Link type : FIXED / ไม่สุ่มทุกครั้ง")
    print("=" * 68)
    print("ถ้า URL ยังเปิดไม่ได้ ให้ตรวจ Published application ใน Cloudflare")
    print(f"Hostname = {hostname}")
    print(f"Service  = http://localhost:{port}")
    print("กด Ctrl+C เพื่อหยุด Server\n")

    env = os.environ.copy()
    env["TUNNEL_TOKEN"] = token
    cmd = [str(cloudflared), "tunnel", "--no-autoupdate", "run"]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1,
        env=env,
    )

    if not no_browser:
        threading.Timer(3.0, lambda: webbrowser.open(url)).start()

    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            upper = line.upper()
            if "ERR" in upper or "ERROR" in upper or "REGISTERED TUNNEL CONNECTION" in upper:
                print("[cloudflared]", line.strip())
        return proc.wait()
    except KeyboardInterrupt:
        print("\n[CVET] กำลังปิด Permanent Web...")
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
    parser.add_argument("--public", action="store_true", help="เปิดผ่าน Cloudflare Quick Tunnel")
    parser.add_argument("--permanent", action="store_true", help="เปิดผ่าน Cloudflare Named Tunnel / Custom Domain")
    parser.add_argument("--hostname", default="", help="Permanent hostname เช่น cvet.caranimal.tech")
    parser.add_argument("--tunnel-token", default="", help="Cloudflare Tunnel token (จะบันทึกไว้ในเครื่อง)")
    parser.add_argument("--forget-permanent", action="store_true", help="ล้าง Permanent Tunnel token/config ที่เก็บในเครื่อง")
    parser.add_argument("--lan", action="store_true", help="ให้เครื่องใน Wi-Fi/LAN เดียวกันเข้าได้")
    parser.add_argument("--pin", default="", help="PIN ที่ต้องกรอกบนเว็บก่อนคำนวณ")
    parser.add_argument("--allowed-mail", action="append", default=[],
                        help="อีเมลที่อนุญาตผ่าน Cloudflare Quick Tunnel (ใส่ซ้ำได้)")
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    if args.forget_permanent:
        forget_permanent_config()
        print("[CVET] ล้าง Permanent Tunnel token/config ในเครื่องแล้ว")
        return 0

    if args.tunnel_token.strip():
        save_tunnel_token(args.tunnel_token)

    meta = load_permanent_meta()
    if not args.hostname:
        args.hostname = str(meta.get("hostname") or DEFAULT_PERMANENT_HOSTNAME)

    # One-click EXE experience
    if len(sys.argv) == 1:
        print("เลือกโหมด Web Server")
        print(f"  1) PERMANENT LINK — https://{normalize_hostname(args.hostname)}")
        print("  2) PUBLIC QUICK LINK — trycloudflare.com (ลิงก์เปลี่ยนทุกครั้ง)")
        print("  3) LAN / Wi-Fi — ใช้เฉพาะเครือข่ายเดียวกัน")
        print("  4) LOCAL — ใช้เฉพาะเครื่องนี้")
        choice = input("เลือก [1/2/3/4] (ค่าเริ่มต้น 1): ").strip() or "1"
        if choice == "1":
            args.permanent = True
            pin = getpass.getpass("ตั้ง Web PIN (เว้นว่างได้): ").strip()
            if pin:
                args.pin = pin
        elif choice == "2":
            args.public = True
            pin = getpass.getpass("ตั้ง Web PIN (เว้นว่างได้): ").strip()
            if pin:
                args.pin = pin
        elif choice == "3":
            args.lan = True

    if args.pin:
        os.environ["CVET_WEB_PIN"] = args.pin.strip()

    port = max(1, min(65535, int(args.port)))

    if args.permanent:
        return run_named_tunnel(port, args.hostname, args.no_browser)

    host = "0.0.0.0" if args.lan and not args.public else "127.0.0.1"

    print("=" * 68)
    print(" Crane Vehicle Engineering Tool — Web Server")
    print("=" * 68)
    print(f" Local URL : http://127.0.0.1:{port}")
    if args.lan and not args.public:
        print(f" LAN URL   : http://{local_ip()}:{port}")
    if args.pin:
        print(" Web PIN   : เปิดใช้งานแล้ว")
    else:
        print(" Web PIN   : ไม่ได้ตั้ง (ผู้ที่มีลิงก์สามารถคำนวณได้)")
    print("=" * 68)

    if not args.public:
        import uvicorn
        from web_server import app
        if not args.no_browser:
            threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{port}")).start()
        uvicorn.run(app, host=host, port=port, log_level="info")
        return 0

    server, thread = run_server_thread("127.0.0.1", port)
    if not wait_for_server(port):
        print("[CVET] Web server เริ่มทำงานไม่สำเร็จ")
        return 2

    cloudflared = ensure_cloudflared()
    cmd = [
        str(cloudflared),
        "tunnel",
        "--url", f"http://127.0.0.1:{port}",
        "--no-autoupdate",
    ]
    for email in args.allowed_mail:
        if email.strip():
            cmd.extend(["--allowed-mail", email.strip()])

    print("\n[CVET] กำลังสร้างลิงก์ HTTPS สำหรับอินเทอร์เน็ตภายนอก...")
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
                print("\n" + "=" * 68)
                print(" PUBLIC WEB พร้อมใช้งาน")
                print(f" {public_url}")
                print("=" * 68)
                print("ส่งลิงก์นี้ให้คนอื่นเปิดจากมือถือหรือคอมได้เลย")
                print("เครื่อง Server เครื่องนี้ต้องเปิดโปรแกรมนี้ค้างไว้")
                if args.pin:
                    print("ผู้ใช้งานต้องกรอก PIN ที่ตั้งไว้ก่อนคำนวณ")
                print("กด Ctrl+C เพื่อหยุด Server และปิด Public URL\n")
                if not args.no_browser:
                    try:
                        webbrowser.open(public_url)
                    except Exception:
                        pass
            elif "ERR" in line.upper() or "ERROR" in line.upper():
                print("[cloudflared]", line.strip())

        return proc.wait()
    except KeyboardInterrupt:
        print("\n[CVET] กำลังปิด Public Web...")
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


if __name__ == "__main__":
    raise SystemExit(main())
