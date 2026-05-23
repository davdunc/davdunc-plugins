# DAS Trader Pro — Hotkey Scripting Reference

## Script Styles

### Classic Style
- Single-line, semicolon-delimited parameters
- No variables, no conditionals
- Best for simple, fast hotkeys
```
Route=ARCAL;Price=Ask+0.05;Share=100;TIF=DAY+;BUY=Send
```

### Advanced Style
- Multi-line, object-oriented
- Supports variables, conditionals, loops
- Requires: Setup → Other Configuration → Hotkey Advanced Script ✓
```
$MONTAGE = GetWindowObj("MONTAGE1");
$PRICE = $MONTAGE.Ask + 0.05;
$MONTAGE.Price = $PRICE;
$MONTAGE.Share = 100;
$MONTAGE.Route = "ARCAL";
$MONTAGE.TIF = "DAY+";
$MONTAGE.BUY();
```

---

## Core Keywords

| Keyword | Values / Notes |
|---|---|
| `Route` | ARCAL, ARCAM, EDGXL, EDGXM, INETS, INETL, SMRTL, SMRTM, NSDQL, NSDQM, NYSE, BATS, etc. |
| `Price` | Numeric, or expression using variables (Ask, Bid, etc.) |
| `Share` / `QTY` | Integer share count, or expression |
| `TIF` | DAY, DAY+, GTC, GTC+, IOC, FOK, At Open, At Close, NIGHT, 1Min, 2Min, 3Min, 5Min, 10Min |
| `StopPrice` | Numeric or expression; sets stop trigger price |
| `StopType` | STOPMARKET, STOPLIMIT, STOPTRAILING, STOPRANGE |
| `TriggerOrder` | Bracket / OCO order attached to a new position |
| `BUY=Send` | Execute buy order |
| `SELL=Send` | Execute sell order |
| `Send=Reverse` | Flip position (long→short or short→long) |
| `CXL ALLSYMB` | Cancel all open orders in the current symbol |

---

## Dynamic Variables

| Variable | Description |
|---|---|
| `Ask` | Current ask price |
| `Bid` | Current bid price |
| `Last` | Last trade price |
| `Pos` | Current position size (shares held) |
| `AvgCost` | Average cost of current position |
| `BP` | Available buying power |
| `Price` | Price clicked on chart (used in chart-click scripts) |
| `GetAccountObj($MONTAGE.Account).Equity` | Current account equity (for risk-based sizing) |

---

## ⚠️ Arithmetic: Left-to-Right, No Operator Precedence

DAS evaluates math strictly left-to-right. There is **no PEMDAS/BODMAS**.

```
2 + 3 * 4 = 20   ← DAS evaluates as (2+3)*4
```

**Workaround**: chain carefully or use variables:
```
# WRONG — intends Ask + (0.01 * 100):
Price=Ask+0.01*100    # gives (Ask+0.01)*100

# CORRECT — use a variable for the offset:
$OFFSET = 0.01 * 100;  # = 1.00
Price = Ask + $OFFSET;  # = Ask + 1.00
```

---

## Flow Control (Advanced Style Only)

### If / Else
```
if ($MONTAGE.Pos > 0) {
  $MONTAGE.SELL();
} else {
  $MONTAGE.BUY();
}
```

### While Loop (max 199 iterations)
```
$COUNT = 0;
while ($COUNT < 5) {
  $COUNT = $COUNT + 1;
}
```

---

## TriggerOrder (OCO Bracket) Syntax

TriggerOrder attaches a protective bracket to an order at the time of entry. Parameters:

| Parameter | Description |
|---|---|
| `RT:` | Route for the trigger order (usually STOP) |
| `STOPTYPE:` | MARKET, RANGEMKT, RANGELMT, LimitP (ext hours) |
| `StopPrice:` | Stop loss price |
| `LowPrice:` | Lower bound (for RANGEMKT/RANGELMT) |
| `HighPrice:` | Upper bound / profit target |
| `ACT:` | Action on trigger: S (sell), B (buy), SS (short sell), BC (buy to cover) |
| `QTY:` | Share quantity; use `Pos` to match full position |
| `TIF:` | Time in force for trigger order |

**Example — Buy with RANGEMKT bracket (stop + target):**
```
Route=ARCAL;Price=Ask+0.05;Share=100;TIF=DAY+;
TriggerOrder=RT:STOP STOPTYPE:RANGEMKT LowPrice:49.00 HighPrice:51.50 ACT:S QTY:Pos TIF:DAY+;
BUY=Send
```

**Extended hours — LimitP type:**
```
TriggerOrder=RT:STOP STOPTYPE:LimitP StopPrice:49.00 LimitPrice:48.90 ACT:S QTY:Pos TIF:DAY+
```

---

## 16 Ready-to-Use Script Examples

### Entry Scripts

**1. Simple Market Buy (Classic)**
```
Route=ARCAM;Share=100;TIF=DAY;BUY=Send
```

**2. Limit Buy at Ask + offset (Classic)**
```
Route=ARCAL;Price=Ask+0.05;Share=100;TIF=DAY+;BUY=Send
```

**3. Buy with Hard Stop (Advanced)**
```
$MONTAGE = GetWindowObj("MONTAGE1");
$STOP = $MONTAGE.Bid - 0.30;
$MONTAGE.Price = $MONTAGE.Ask + 0.05;
$MONTAGE.Share = 100;
$MONTAGE.Route = "ARCAL";
$MONTAGE.TIF = "DAY+";
$MONTAGE.TRIGGERORDER = "RT:STOP STOPTYPE:STOPMARKET StopPrice:" + $STOP + " ACT:S QTY:Pos TIF:DAY+";
$MONTAGE.BUY();
```

**4. Buy with RANGEMKT OCO Bracket**
```
Route=ARCAL;Price=Ask+0.05;Share=100;TIF=DAY+;
TriggerOrder=RT:STOP STOPTYPE:RANGEMKT LowPrice:49.00 HighPrice:51.50 ACT:S QTY:Pos TIF:DAY+;
BUY=Send
```

**5. Equalized Risk Entry (Advanced — size by $ risk)**
```
$MONTAGE = GetWindowObj("MONTAGE1");
$EQ = GetAccountObj($MONTAGE.Account).Equity;
$RISK_PCT = 0.01;
$RISK_DOLLARS = $EQ * $RISK_PCT;
$STOP_DIST = $MONTAGE.Ask - ($MONTAGE.Bid - 0.25);
$SHARES = $RISK_DOLLARS / $STOP_DIST;
$MONTAGE.Share = $SHARES;
$MONTAGE.Price = $MONTAGE.Ask + 0.05;
$MONTAGE.Route = "ARCAL";
$MONTAGE.TIF = "DAY+";
$MONTAGE.BUY();
```
*Sizes position so that 1% of equity is risked to the stop.*

---

### Exit Scripts

**6. Sell Full Position at Market**
```
Route=ARCAM;Share=Pos;TIF=DAY;SELL=Send
```

**7. Sell Half Position (Classic)**
```
Route=ARCAL;Price=Bid-0.05;Share=Pos/2;TIF=DAY+;SELL=Send
```

**8. Sell One-Third Position**
```
Route=ARCAL;Price=Bid-0.05;Share=Pos/3;TIF=DAY+;SELL=Send
```

**9. Cancel All + Flatten at Market**
```
CXL ALLSYMB;Route=ARCAM;Share=Pos;TIF=DAY;SELL=Send
```

**10. Position Flip (Long → Short)**
```
Route=ARCAM;Share=Pos*2;TIF=DAY;Send=Reverse
```

---

### Stop / Risk Management Scripts

**11. Move Stop to Break-Even (Advanced)**
```
$MONTAGE = GetWindowObj("MONTAGE1");
$BE = $MONTAGE.AvgCost;
$MONTAGE.StopPrice = $BE;
$MONTAGE.UPDATESTOP();
```

**12. Trailing Stop at -0.20 from current (Classic)**
```
Route=STOP;StopType=STOPTRAILING;TrailPrice=0.20;Share=Pos;TIF=DAY;SELL=Send
```

---

### Short Selling Scripts

**13. Short Sell Limit at Bid (Classic)**
```
Route=ARCAL;Price=Bid-0.05;Share=100;TIF=DAY+;SELL=Send
```
*Note: SELL for short. Ensure you have a locate if HTB.*

**14. Short with Stop Buy-to-Cover Bracket**
```
Route=ARCAL;Price=Bid-0.05;Share=100;TIF=DAY+;
TriggerOrder=RT:STOP STOPTYPE:STOPMARKET StopPrice:51.00 ACT:BC QTY:Pos TIF:DAY+;
SELL=Send
```

---

### Advanced / Conditional

**15. Buy if No Position, Flatten if Long (Advanced)**
```
$MONTAGE = GetWindowObj("MONTAGE1");
if ($MONTAGE.Pos > 0) {
  $MONTAGE.Share = $MONTAGE.Pos;
  $MONTAGE.Route = "ARCAM";
  $MONTAGE.SELL();
} else {
  $MONTAGE.Price = $MONTAGE.Ask + 0.05;
  $MONTAGE.Share = 100;
  $MONTAGE.Route = "ARCAL";
  $MONTAGE.TIF = "DAY+";
  $MONTAGE.BUY();
}
```

**16. Extended Hours Buy with LimitP Protection**
```
Route=ARCAL;Price=Ask+0.05;Share=100;TIF=DAY+;
TriggerOrder=RT:STOP STOPTYPE:LimitP StopPrice:49.00 LimitPrice:48.90 ACT:S QTY:Pos TIF:DAY+;
BUY=Send
```
*LimitP is required for stop protection outside RTH — STOPMARKET is blocked in pre/post.*

---

## HTK File Format

DAS saves hotkeys in `.HTK` files. Each line:
```
Key=F1
Script=Route=ARCAL;Price=Ask+0.05;Share=100;TIF=DAY+;BUY=Send
```

Assign hotkeys via: **Setup → Hot Key** or the montage button editor.
