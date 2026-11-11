#!/usr/bin/env bash
# End-of-day DAS report export (operator reports = the authoritative record) + ingest.
# Drives the DAS GUI through Windows COM/Win32 from WSL via das_eod_export.ps1, then runs
# falcon-stats ingest on the exported folder. Scheduled by Windows Task Scheduler as
# "FalconDASExport" at 19:05 local (20:05 ET, after the after-hours close); FalconDASCapture (18:45) now runs BEFORE it, so the capture
# finds reports and stands down. Idempotent: re-running just rewrites the same files.
set -uo pipefail
LOG_DIR="$HOME/.claude/MEMORY/LOGS"; mkdir -p "$LOG_DIR"
DATE_STR="${1:-$(date +%Y-%m-%d)}"
LOG="$LOG_DIR/das-eod-export-$DATE_STR.log"
ENVF="$HOME/.claude/.env"
getenv(){ grep -E "^[[:space:]]*$1[[:space:]]*=" "$ENVF" | tail -1 | cut -d= -f2- | sed -e 's/#.*//' -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' -e 's/^"//' -e 's/"$//' -e "s/^'//" -e "s/'$//"; }
DAS_USER=$(getenv DAS_USER); DAS_PASS=$(getenv DAS_PASSWORD); DAS_PORT=$(getenv DAS_PORT); DAS_PORT=${DAS_PORT:-3192}
ROOT_WSL=$(getenv TRADE_REVIEW_PATH); ROOT_WSL=${ROOT_WSL:-{{WINDOWS_HOME}}/OneDrive/Desktop/Trade_Review}
ROOT_WIN=$(wslpath -w "$ROOT_WSL" 2>/dev/null || echo '{{WINDOWS_HOME_WIN}}\OneDrive\Desktop\Trade_Review')
{
  echo "=== das-eod-export $DATE_STR $(date '+%F %T %Z') on ${HOSTNAME:-node} ==="
  powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$(wslpath -w "$HOME/.claude/Tools/das_eod_export.ps1")" \
      -Date "$DATE_STR" -Root "$ROOT_WIN" -DasPort "$DAS_PORT" -DasUser "$DAS_USER" -DasPass "$DAS_PASS" 2>&1 | tr -d '\r'
  rc=${PIPESTATUS[0]}
  echo "powershell rc=$rc"
  DIR="$ROOT_WSL/${DATE_STR:0:7}/$DATE_STR"
  if [[ $rc -eq 0 && -s "$DIR/Trades.csv" ]]; then
    echo "--- ingest"
    "$HOME/.claude/Tools/falcon-stats" ingest "$DIR" 2>&1 | grep -E "Parsed|Identified|^  2026|Trades:|P&L:|Avg R|DynamoDB"
    echo "RESULT: ok"
  else
    echo "RESULT: export failed (rc=$rc); FalconDASCapture at 18:45 remains the fallback"
    [[ -x "$HOME/.claude/Tools/falcon-cluster-handoff.sh" ]] && "$HOME/.claude/Tools/falcon-cluster-handoff.sh" state "[daslaptop] das-eod-export FAILED for $DATE_STR (rc=$rc); capture fallback pending" >/dev/null 2>&1 || true
  fi
} 2>&1 | tee -a "$LOG"
