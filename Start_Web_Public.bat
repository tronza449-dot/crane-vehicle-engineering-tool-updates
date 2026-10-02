@echo off
title Crane Vehicle Engineering Tool - PUBLIC WEB
if exist CraneVehicleWebServer.exe (
  CraneVehicleWebServer.exe --public
) else (
  python web_launcher.py --public
)
pause
