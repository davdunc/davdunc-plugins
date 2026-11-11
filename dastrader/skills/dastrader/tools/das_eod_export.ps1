# DAS end-of-day report export, driven through Windows COM / Win32 from WSL (daslaptop).
# Sequence (operator spec 2026-09-29): Account Report SIM -> LIVE -> ALL, then Trade > Reports
# (Orders/Executions/Tickets/Liquidity, CSV, training trades shown, path = today's folder),
# Export, click OK on the completion box, Quit, close the report windows.
# Usage: powershell.exe -NoProfile -ExecutionPolicy Bypass -File das_eod_export.ps1 [-Date yyyy-MM-dd]
param([string]$Date = (Get-Date -Format "yyyy-MM-dd"), [string]$Root = "{{WINDOWS_HOME_WIN}}\OneDrive\Desktop\Trade_Review",
      [string]$DasHost = "127.0.0.1", [int]$DasPort = 3192, [string]$DasUser, [string]$DasPass,
      [string[]]$Accounts = @("{{SIM_ACCOUNT}}","{{LIVE_ACCOUNT}}"), [string]$MainTitle = "Powered by DASTrader.com")
$ErrorActionPreference = "Continue"
$src=@"
using System; using System.Text; using System.Runtime.InteropServices; using System.Collections.Generic;
public class DX { public delegate bool EnumProc(IntPtr h, IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc p, IntPtr l);
 [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr h, EnumProc p, IntPtr l);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
 [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
 [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
 [DllImport("user32.dll", CharSet=CharSet.Unicode, EntryPoint="SendMessageW")] public static extern IntPtr SendMessageS(IntPtr h, uint m, IntPtr w, string l);
 [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l);
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
 [DllImport("user32.dll")] public static extern void mouse_event(uint f, uint dx, uint dy, uint d, UIntPtr e);
 [DllImport("user32.dll")] public static extern IntPtr GetParent(IntPtr h);
 [DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr h);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r); [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L,T,R,B; }
 public static List<string> Tops(uint want){ var o=new List<string>(); EnumWindows((h,l)=>{ uint pid; GetWindowThreadProcessId(h,out pid); if(pid==want && IsWindowVisible(h)){ var t=new StringBuilder(256); GetWindowText(h,t,256); var c=new StringBuilder(256); GetClassName(h,c,256); o.Add(h.ToString()+"|"+c+"|"+t);} return true; }, IntPtr.Zero); return o; }
 public static IntPtr FindTop(uint want, string cls, string title){ IntPtr r=IntPtr.Zero; EnumWindows((h,l)=>{ uint pid; GetWindowThreadProcessId(h,out pid); if(pid==want && IsWindowVisible(h)){ var t=new StringBuilder(256); GetWindowText(h,t,256); var c=new StringBuilder(256); GetClassName(h,c,256); if((cls=="" || c.ToString()==cls) && t.ToString().Contains(title)){ r=h; return false; } } return true; }, IntPtr.Zero); return r; }
 public static IntPtr FindChild(IntPtr h, string cls, string text){ IntPtr r=IntPtr.Zero; EnumChildWindows(h,(c,l)=>{ var cl=new StringBuilder(128); GetClassName(c,cl,128); var t=new StringBuilder(256); GetWindowText(c,t,256); if((cls=="" || cl.ToString()==cls) && (text=="" || t.ToString()==text)){ r=c; return false; } return true; }, IntPtr.Zero); return r; }
 public static string Text(IntPtr h){ var t=new StringBuilder(512); GetWindowText(h,t,512); return t.ToString(); }
}
"@
Add-Type -TypeDefinition $src
function Log($m){ Write-Host ("[{0}] {1}" -f (Get-Date -Format "HH:mm:ss"), $m) }
function Fail($m){ Log "FAIL: $m"; exit 2 }
$ws = New-Object -ComObject WScript.Shell
$dir = Join-Path $Root ("{0}\{1}" -f $Date.Substring(0,7), $Date)
New-Item -ItemType Directory -Force -Path $dir | Out-Null
$proc = Get-Process DasTrader64 -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $proc) { Fail "DasTrader64.exe is not running" }
$pid_ = [uint32]$proc.Id
$main = [DX]::FindTop($pid_, "", $MainTitle)
if ($main -eq [IntPtr]::Zero) { Fail "DAS main window not found" }
Log "DAS pid=$pid_ main=$main dir=$dir"

function DasScript($acct, $cmd) {
  $c = New-Object System.Net.Sockets.TcpClient($DasHost, $DasPort); $s = $c.GetStream(); $s.ReadTimeout = 2000
  $w = New-Object System.IO.StreamWriter($s); $w.NewLine = "`r`n"; $w.AutoFlush = $true
  $w.WriteLine("LOGIN $DasUser $DasPass $acct 1"); Start-Sleep -Seconds 2
  $w.WriteLine($cmd); Start-Sleep -Seconds 2
  $buf = New-Object byte[] 65536; $out = ""
  try { while ($s.DataAvailable) { $n = $s.Read($buf, 0, $buf.Length); $out += [Text.Encoding]::ASCII.GetString($buf, 0, $n) } } catch {}
  $c.Close(); return $out
}
function SaveAsTo($path) {
  $dlg = [IntPtr]::Zero
  for ($i = 0; $i -lt 20 -and $dlg -eq [IntPtr]::Zero; $i++) { Start-Sleep -Milliseconds 300; $dlg = [DX]::FindTop($pid_, "#32770", "Save As") }
  if ($dlg -eq [IntPtr]::Zero) { Log "no Save As dialog appeared"; return $false }
  [DX]::ShowWindow($dlg, 5) | Out-Null; [DX]::SetForegroundWindow($dlg) | Out-Null; Start-Sleep -Milliseconds 700
  $null = $ws.AppActivate("Save As"); Start-Sleep -Milliseconds 500
  $ws.SendKeys("%n"); Start-Sleep -Milliseconds 400; $ws.SendKeys("^a"); Start-Sleep -Milliseconds 150
  $ws.SendKeys($path); Start-Sleep -Milliseconds 600; $ws.SendKeys("{ENTER}"); Start-Sleep -Seconds 2
  if ([DX]::IsWindow($dlg)) { # overwrite prompt?
    $ow = [DX]::FindTop($pid_, "#32770", "Confirm Save As"); if ($ow -ne [IntPtr]::Zero) { $null = $ws.AppActivate("Confirm Save As"); $ws.SendKeys("y"); Start-Sleep -Seconds 2 }
  }
  return (-not [DX]::IsWindow($dlg))
}
function ExportAccountReport($acct, $file, $selectAll) {
  $r = DasScript $acct "SCRIPT GLOBALSCRIPT ShowAccount $acct"
  if ($r -notmatch "run successful") { Log "ShowAccount ${acct}: $r" }
  $rep = [IntPtr]::Zero
  for ($i = 0; $i -lt 20 -and $rep -eq [IntPtr]::Zero; $i++) { Start-Sleep -Milliseconds 300; $rep = [DX]::FindTop($pid_, "WndFrm5678", "Account Report  --- $acct") }
  if ($rep -eq [IntPtr]::Zero) { Log "Account Report window for $acct not found"; return $false }
  if ($selectAll) {
    $cb = [DX]::FindChild($rep, "ComboBox", "")
    $idx = [DX]::SendMessageS($cb, 0x014D, [IntPtr](-1), "--All")   # CB_SELECTSTRING
    if ([int64]$idx -lt 0) { $idx = [DX]::SendMessage($cb, 0x014E, [IntPtr]0, [IntPtr]0) }  # CB_SETCURSEL 0 fallback
    $id = [DX]::GetDlgCtrlID($cb); $wp = [IntPtr](($id -band 0xFFFF) -bor (1 -shl 16))       # CBN_SELCHANGE
    [DX]::PostMessage([DX]::GetParent($cb), 0x0111, $wp, $cb) | Out-Null; Start-Sleep -Seconds 2
    Log "ALL selected (idx=$idx) on $rep"
  }
  $exp = [DX]::FindChild($rep, "Button", "&Export"); if ($exp -eq [IntPtr]::Zero) { Log "Export button not found"; return $false }
  [DX]::SetForegroundWindow($rep) | Out-Null; Start-Sleep -Milliseconds 300
  [DX]::PostMessage($exp, 0x00F5, [IntPtr]0, [IntPtr]0) | Out-Null
  $ok = SaveAsTo (Join-Path $dir $file)
  Start-Sleep -Seconds 1
  if (Test-Path (Join-Path $dir $file)) { Log "wrote $file ($((Get-Item (Join-Path $dir $file)).Length) bytes)"; return $true }
  Log "$file not written"; return $false
}

$results = @{}
foreach ($a in $Accounts) { $results["Accounts-$a.csv"] = ExportAccountReport $a "Accounts-$a.csv" $false }
$results["Accounts.csv"] = ExportAccountReport $Accounts[-1] "Accounts.csv" $true
foreach ($t in [DX]::Tops($pid_)) { if ($t -match "\|WndFrm5678\|Account Report") { [DX]::PostMessage([IntPtr]([int64]$t.Split("|")[0]), 0x0010, [IntPtr]0, [IntPtr]0) | Out-Null } }

# --- Trade > Reports (Orders / Executions / Tickets) ---
$rect = New-Object DX+RECT; [DX]::GetWindowRect($main, [ref]$rect) | Out-Null
$rdlg = [IntPtr]::Zero
for ($try = 0; $try -lt 3 -and $rdlg -eq [IntPtr]::Zero; $try++) {
  [DX]::SetForegroundWindow($main) | Out-Null; Start-Sleep -Milliseconds 400
  $null = $ws.AppActivate($MainTitle); Start-Sleep -Milliseconds 300
  $ws.SendKeys("%t"); Start-Sleep -Milliseconds 800
  [DX]::SetCursorPos($rect.L + 90, $rect.T + 296) | Out-Null; Start-Sleep -Milliseconds 300
  [DX]::mouse_event(2,0,0,0,[UIntPtr]::Zero); [DX]::mouse_event(4,0,0,0,[UIntPtr]::Zero)
  for ($i = 0; $i -lt 15 -and $rdlg -eq [IntPtr]::Zero; $i++) { Start-Sleep -Milliseconds 300; $rdlg = [DX]::FindTop($pid_, "#32770", "Report") }
  if ($rdlg -eq [IntPtr]::Zero) { $ws.SendKeys("{ESC}{ESC}") }
}
if ($rdlg -eq [IntPtr]::Zero) { Fail "Trade > Reports dialog did not open" }
Log "Report dialog $rdlg"
foreach ($name in "Orders","Executions","Tickets","Add/Rem Liquidity",".CSV Text File(Comma delimited)","Show Training orders/trades") {
  $b = [DX]::FindChild($rdlg, "Button", $name); if ($b -ne [IntPtr]::Zero -and [int64]([DX]::SendMessage($b, 0x00F0, [IntPtr]0, [IntPtr]0)) -ne 1) { [DX]::SendMessage($b, 0x00F1, [IntPtr]1, [IntPtr]0) | Out-Null; Log "checked $name" }
}
$b = [DX]::FindChild($rdlg, "Button", "Open reports after export"); if ($b -ne [IntPtr]::Zero -and [int64]([DX]::SendMessage($b, 0x00F0, [IntPtr]0, [IntPtr]0)) -eq 1) { [DX]::SendMessage($b, 0x00F1, [IntPtr]0, [IntPtr]0) | Out-Null }
$edit = [DX]::FindChild($rdlg, "Edit", ""); [DX]::SendMessageS($edit, 0x000C, [IntPtr]0, $dir) | Out-Null; Log "path set: $([DX]::Text($edit))"
$before = @{}; foreach ($f in "Trades.csv","Orders.csv","Tickets.csv") { $p = Join-Path $dir $f; $before[$f] = if (Test-Path $p) { (Get-Item $p).LastWriteTime } else { [datetime]0 } }
$exp = [DX]::FindChild($rdlg, "Button", "Export"); [DX]::PostMessage($exp, 0x00F5, [IntPtr]0, [IntPtr]0) | Out-Null; Log "Export posted"
$okbox = [IntPtr]::Zero
for ($i = 0; $i -lt 40 -and $okbox -eq [IntPtr]::Zero; $i++) { Start-Sleep -Milliseconds 500; foreach ($t in [DX]::Tops($pid_)) { if ($t -match "\|#32770\|Cobra Trading") { $okbox = [IntPtr]([int64]$t.Split("|")[0]) } } }
if ($okbox -ne [IntPtr]::Zero) { $okb = [DX]::FindChild($okbox, "Button", "OK"); [DX]::PostMessage($okb, 0x00F5, [IntPtr]0, [IntPtr]0) | Out-Null; Log "OK clicked on completion box" } else { Log "no completion box seen" }
Start-Sleep -Seconds 1
$q = [DX]::FindChild($rdlg, "Button", "Quit"); [DX]::PostMessage($q, 0x00F5, [IntPtr]0, [IntPtr]0) | Out-Null
Start-Sleep -Seconds 1
$fails = 0
foreach ($f in "Trades.csv","Orders.csv","Tickets.csv") { $p = Join-Path $dir $f; if ((Test-Path $p) -and (Get-Item $p).LastWriteTime -gt $before[$f]) { Log "refreshed $f ($((Get-Content $p).Count - 1) rows)" } else { Log "NOT refreshed: $f"; $fails++ } }
foreach ($k in $results.Keys) { if (-not $results[$k]) { $fails++ } }
foreach ($t in [DX]::Tops($pid_)) { if ($t -notmatch [regex]::Escape($MainTitle)) { Log "still open: $t" } }
Log "done, failures=$fails"
exit $fails
