# Crane Vehicle Engineering Tool V53.8.50

## Debug Report / Support Diagnostics

This release adds a privacy-safe Debug Report to both Desktop and Web so calculation/UI/update problems can be diagnosed from a single report.

### Desktop Debug Report
Available from:
- **Project Tools → Debug Report**
- the new **🛠 Debug** button in the bottom status bar

The report includes:
- application version and session time,
- Python / PySide / Windows platform information,
- current design mode and key project inputs,
- important engineering outputs from Drive, Main Battery, Winch, Ramp and Stability,
- Input Source states (Manual / Auto / Linked / Component / Winch / Datasheet),
- a non-destructive Self-check,
- updater status and latest pending-version state,
- Web Server status without exposing the actual PIN,
- autosave/backup/update-config file existence,
- recent debug events,
- current-session exception information,
- the previous persisted exception after restarting the application.

Export options:
- **TXT**
- **JSON**
- **Copy Report**

### Privacy / redaction
Debug Reports intentionally:
- redact the local Windows/macOS/Linux user-home path,
- do not include the Web PIN,
- do not dump credentials or secrets,
- report only whether a public Web URL exists rather than including the URL itself in the Desktop report.

### Persistent exception capture
Uncaught exceptions and important button-action failures are recorded with time, error type, message and a redacted traceback.
The most recent exception is also stored in AppData so it remains available after reopening the program.

### Updater and Web diagnostics
The event log now records:
- updater check failures,
- updater download failures,
- successful update checks/downloads,
- Web Server launch failures,
- Web Server reported error state.

### Web Debug Report
Project Summary now includes a **Debug Report** card with:
- Refresh,
- Copy Report,
- Export JSON,
- Export TXT.

The Web report includes browser/viewport state, Web health/version, current forms, mass mode, Design Lock state, Input Source badges, Self-check results and recent browser/API errors. The Web PIN value is never included.

### Regression
The release audit verifies:
- Desktop Debug Report tab/UI and report schema,
- Self-check availability,
- home-path redaction,
- debug event capture/redaction,
- updater/Web error instrumentation,
- Web Debug Report controls/functions,
- browser error event capture,
- PIN privacy wording,
- all previous engineering calculation, Scenario Preset, Input Source, PDF, Save/Restore, updater and Desktop↔Web regression.
