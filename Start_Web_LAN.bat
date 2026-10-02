@echo off
title Crane Vehicle Engineering Tool - LAN WEB
if exist CraneVehicleWebServer.exe (
  CraneVehicleWebServer.exe --lan
) else (
  python web_launcher.py --lan
)
pause
