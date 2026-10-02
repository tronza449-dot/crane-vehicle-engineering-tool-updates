@echo off
cd /d "%~dp0"
CraneVehicleWebServer.exe --tailscale --tailscale-hostname cvet
pause
