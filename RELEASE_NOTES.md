# Crane Vehicle Engineering Tool V53.8.38

## Fix QtWidgets DLL File-Lock Crash During Update

### 1. Root cause addressed
The built-in updater previously launched Inno Setup with both:
- /RESTARTAPPLICATIONS
- an installer [Run] entry that launches the application after installation

That could cause the application to be restarted more than once around the same update window and could race with replacement/loading of PySide6 / Qt files.

Typical symptom:
- DLL load failed while importing QtWidgets
- The process cannot access the file because it is being used by another process

### 2. Safe updater sequence
The updater now uses:
- /CLOSEAPPLICATIONS
- /NORESTARTAPPLICATIONS
- /NORESTART

The intended sequence is now:
1. Save current project values
2. Close the running application
3. Replace all application / Qt / PySide6 files
4. Let the installer [Run] section start exactly one fresh application instance

### 3. Installer hardening
Inno Setup now explicitly uses:
- CloseApplications=yes
- RestartApplications=no
- RestartIfNeededByRun=no

This prevents Windows Restart Manager from launching an extra old application instance while the installer is still finishing.

### 4. Save protection before update
Before handing control to the installer, the Desktop app writes Save Values once more so an update-related forced close cannot lose the current project inputs.

### 5. Regression coverage
The release build now fails if:
- /RESTARTAPPLICATIONS returns to the updater
- /NORESTARTAPPLICATIONS is missing
- installer CloseApplications / RestartApplications safety directives are removed
- installer no longer has exactly the intended post-install application launch path

All previous Desktop/Web parity, PDF, Save/Restore, FBD, and Web Sync regressions remain enabled.
