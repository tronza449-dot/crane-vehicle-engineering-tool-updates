# Crane Vehicle Engineering Tool V53.1.1

## ESP32 WiFi Live Telemetry + Non-Blocking Safety Hotfix

V53.1.1 includes all V53.1.0 WiFi telemetry features and changes the generated ESP32 WiFi sender so loss of WiFi cannot block the vehicle control loop.

### WiFi Telemetry
- Simulation / Demo
- ESP32 Serial JSON
- ESP32 WiFi UDP JSON
- PC IP selector
- UDP Port (default 4210)
- Device ID filter
- Remote ESP32 IP
- Packet rate
- Battery V / % / A
- Speed
- IMU tilt
- Left / Right RPM
- VESC current
- RC throttle / steering
- Limit switches
- E-stop / RC OK
- WiFi RSSI
- CSV logger
- Test WiFi Packet
- WiFi ESP32 .ino generator

### Safety hotfix
The generated ESP32 WiFi sketch now uses non-blocking WiFi reconnect:
- no while-loop waiting forever for WiFi
- control/safety loop can continue even when WiFi is lost
- reconnect attempt approximately every 5 seconds
- telemetry is sent only while WiFi is connected
- WiFi remains telemetry-only; no Drive / Crane / Winch commands are accepted

### Windows Regression Gate
Adds tests that verify:
- real UDP loopback receive
- Device ID filter
- WiFi metadata
- UDP cleanup
- generated WiFi sketch contains non-blocking reconnect
- generated sketch does not contain a blocking WL_CONNECTED wait loop
- all previous engineering/UI/PDF/update tests still pass

Note: UDP telemetry has no encryption/authentication by itself. Use it only on a trusted LAN/WiFi. RC failsafe and hardware E-stop remain independent safety paths.
