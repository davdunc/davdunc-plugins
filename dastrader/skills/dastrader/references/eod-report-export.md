# DAS Trader Pro — Automating the End-of-Day Report Export (Windows/WSL)

The Trade Report and Account Report exports are GUI-only. `tools/das_eod_export.ps1` (driven by
`tools/das-eod-export.sh` from WSL) reproduces the operator's manual sequence and `tools/das_scheduled_order.py`
places a single order from a scheduler. Both need DAS running and logged in, an interactive Windows session,
and `DAS_USER`, `DAS_PASSWORD`, `DAS_PORT`, `TRADE_REVIEW_PATH` in `~/.claude/.env` (never committed, never copied).

## Sequence the export reproduces
1. Account Report per account, then the ALL view: `SCRIPT GLOBALSCRIPT ShowAccount <account>` over the CMD API
   opens window class `WndFrm5678` titled `Account Report  --- <account>`; its `&Export` button raises a Save As
   dialog; the ALL view is the window's ComboBox (`CB_SELECTSTRING "--All"` + post `WM_COMMAND`/`CBN_SELCHANGE`
   to the parent so the grid refreshes).
2. Trade → Reports (Orders, Executions, Tickets, Add/Rem Liquidity; CSV; "Show Training orders/trades" ON so the
   SIM account is included; Path = `Trade_Review\YYYY-MM\YYYY-MM-DD`), Export, OK on the completion box, Quit.

Output files: `Accounts-<acct>.csv` per account, `Accounts.csv` (ALL), `Orders.csv`, `Trades.csv`, `Tickets.csv`.

## What works and what does not
- **UI Automation sees nothing** inside DAS (MFC, owner-drawn control bars, `GetMenu` returns 0) and nothing
  inside the Save As dialog across the WSL boundary. Use `user32` P/Invoke via `Add-Type`: `EnumWindows` /
  `EnumChildWindows` filtered by the DAS process id give every window and control by class and caption.
- **Save As**: keystrokes through the Windows Script Host shell (`WScript.Shell`): `AppActivate("Save As")`,
  `%n`, `^a`, type the full path, `{ENTER}`. Setting the edit by message landed in the wrong control.
- **Trade → Reports has no script/hotkey command.** The Trade menu is a SkinMagic popup: keyboard selection does
  not fire. `Alt+T` then a mouse click at main-window offset (+90, +296) hits "Reports" (dialog class `#32770`,
  title `Report`). Verify the dialog appeared; do not click blind. The offset breaks if DAS moves the item.
- Report dialog controls are plain Win32: `BM_GETCHECK`/`BM_SETCHECK` for the checkboxes, `WM_SETTEXT` for the
  path (reads back empty but takes the value; the dialog remembers its last path, so always set it).
- **Export must be `PostMessage`, not `SendMessage`**: DAS blocks on a modal completion box (`#32770` titled with
  the platform name, an OK button) until it is dismissed. Poll for it, post OK, post Quit, `WM_CLOSE` the report
  windows you opened.
- PowerShell: function `Write-Output` becomes the function's return value (use `Write-Host` for logs); a P/Invoke
  alias for `SendMessageW` needs an explicit `EntryPoint`.

## Scheduling
Task Scheduler, weekdays after the after-hours close (20:05 ET), interactive-only, e.g.
`schtasks /Create /TN FalconDASExport /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 19:05 /TR "wsl.exe -d <distro> -u <user> -- ~/.claude/Tools/das-eod-export.sh"`.
Keep the CMD API capture job as the fallback; the export overwrites its marked files and the ingest cleans the rest.
Exported reports outrank API capture; the capture never overwrites a folder that already holds a report.
