# DAS Trader Pro — Order Types, Routing & TIF Reference

## Route Naming Convention

Routes follow `[EXCHANGE][TYPE]` pattern:
- `L` = Limit
- `M` = Market
- `S` = Stop
- `P` = Pegged

Examples: `ARCAL` (ARCA Limit), `EDGXM` (EDGX Market), `INETS` (INET Stop), `SMRTL` (Smart Limit)

---

## Primary Routes

| Route Code | Exchange | Notes |
|---|---|---|
| `ARCAL` / `ARCAM` | NYSE Arca | Fast, co-located. Good all-around |
| `EDGXL` / `EDGXM` | CBOE EDGX | Sub-millisecond, excellent for momentum |
| `INETL` / `INETS` | Nasdaq INET | Primary Nasdaq venue |
| `NSDQL` / `NSDQM` | Nasdaq | Broad routing |
| `NYSE` | NYSE | NYSE-listed stocks |
| `BATS` / `BZX` | CBOE BZX | High-speed alternative |
| `BYX` | CBOE BYX | Maker-taker rebate venue (reduce fees) |
| `EDGA` | CBOE EDGA | Maker-taker rebate venue |
| `SMRTL` / `SMRTM` | DAS Smart | Smart routing; good for large orders |
| `LIMIT` / `MARKET` | DAS Network | Broker network routing (Cobra) |

**100+ total destinations** including dark pools available.

### Routing by Scenario

| Scenario | Recommended Route |
|---|---|
| Scalping / momentum | `ARCAL`, `EDGXM` |
| Large size, minimize impact | `SMRTL`, dark pools |
| Low-float / penny stocks | `ARCAL`, `INETL` — avoid smart routing |
| Reducing exchange fees | `BYX`, `EDGA` |
| General Nasdaq names | `NSDQL` / `INETL` |
| Pre/post market | `ARCAL` with `DAY+` TIF |

---

## Order Types

### Standard Orders

| Type | Route Suffix | Description |
|---|---|---|
| Limit | `L` | Execute at specified price or better |
| Market | `M` | Execute immediately at best available |

### Stop Orders

| Type | StopType= | Trigger Behavior |
|---|---|---|
| Stop Market | `STOPMARKET` | Triggers market order when stop price hit |
| Stop Limit | `STOPLIMIT` | Triggers limit order when stop price hit |
| Stop Trailing | `STOPTRAILING` | Trails price by TrailPrice= offset |
| Stop Range | `STOPRANGE` | Triggers between LowPrice and HighPrice |

### ⚠️ Stop Trigger Behavior

**Stops trigger on the LAST PRINT between the bid and ask — NOT on Time & Sales.**

A T&S print outside the spread (e.g., a crossing print) will NOT trigger your stop. This is critical for volatile names where the spread is wide.

### Pegged Orders

| Strategy | STOPTYPE= | Description |
|---|---|---|
| Aggressive | `AGG` | Peg to aggressive side of spread |
| Midpoint | `MID` | Peg to midpoint |
| Primary | `PRIM` | Peg to primary (passive) side |
| Last | `LAST` | Peg to last trade price |

---

## Time In Force (TIF)

| TIF | Description | Use Case |
|---|---|---|
| `DAY` | Active for the current trading session | Standard RTH orders |
| `DAY+` | Day + extended hours | Pre/post market access |
| `GTC` | Good-Till-Cancelled | Swing trade entries/exits |
| `GTC+` | GTC + extended hours | Swing with overnight/extended coverage |
| `IOC` | Immediate-Or-Cancel | Take only available liquidity, cancel rest |
| `FOK` | Fill-Or-Kill | Full fill only, or cancel entirely |
| `At Open` | MOO — executes at open | Gap plays, open momentum |
| `At Close` | MOC — executes at close | EOD positioning |
| `NIGHT` | Overnight session | After-hours trading |
| `1Min` | 1-minute duration | Very short-lived orders |
| `2Min` | 2-minute duration | |
| `3Min` | 3-minute duration | |
| `5Min` | 5-minute duration | Common for scalp entries |
| `10Min` | 10-minute duration | Wider window |

**Extended hours**: Always use `DAY+` or `GTC+`. Standard `DAY` orders are RTH only.

**Custom TIFs** and `GTD` (Good-Till-Date) are also available.

---

## Risk Management — Risk Control Window

| Field | Description |
|---|---|
| `MaxLoss` | Maximum daily loss before trading is halted |
| `Warning Loss` | Threshold to trigger a warning alert |
| `Total Loss` | Aggregate loss limit |
| `Curr EQ Lmt` | Current equity limit |
| `RemEQ%` | Remaining equity as percentage |
| `Position Total/Unrealized Loss` | Per-position loss limits |
| `Pos Mkt Val Loss%` | Position market value loss percentage |

### Auto-Liquidation Settings

| Setting | Description |
|---|---|
| `Enable Auto Stop` | Enables automatic position liquidation |
| `Downcount` | Number of trades before auto-stop triggers |
| `Stop Gain (drawdown)` | Locks in profits — stops if gains retrace by X% |
| Unwind scheduling | Schedule auto-liquidation at specific times |
| Long/Short caps | Separate max share and value caps for long vs. short (newer DAS versions) |

### PDT Protection
- **3-Roundtrip Control** — DAS tracks day trades and can block a 4th same-day roundtrip on accounts under $25K
- Enable in Risk Controls to avoid PDT violations

---

## Short Selling

### ETB vs. HTB

| Type | Description | Locate Required |
|---|---|---|
| ETB (Easy-To-Borrow) | Available at no locate cost | No |
| HTB (Hard-To-Borrow) | Must locate shares before shorting | Yes |

### HTB Locate Workflow

1. **Price Inquiry** — Get locate fee quote from your broker's inventory
2. **Locate Order** — Commit to the locate at the quoted fee
3. **Fee applies immediately** — Even if you never execute the short
4. **Validity**: Same trading day only; does not carry over
5. **Minimum**: 100 shares per locate
6. **CMD API**: Locate orders can be automated via `LOCATEORDER` command

### SSR (Short Sale Restriction)

When a stock is on SSR (down >10% from prior close), you may only short on an uptick. DAS enforces this automatically on affected symbols.

---

## Data Feeds Available in DAS

| Feed | Available |
|---|---|
| Nasdaq TotalView | ✅ |
| NYSE ArcaBook | ✅ |
| IEX DEEP | ✅ |
| NYSE OpenBook | ❌ Not available |
| BATS Book | ❌ Not available |

---

## DAS-Specific Features

| Feature | Description |
|---|---|
| **ChartEX** | Second-based charts (faster than standard minute charts) |
| **Market Data Replay** | Historical data for backtesting strategies |
| **Basket Orders** | Submit a list of orders simultaneously |
| **Equalized Equity Risk** | Built-in tool for position sizing by % risk |
| **Window Linking** | Link montage, chart, L2 by color for symbol sync |
| **Imbalance Data** | MOC/MOO order imbalances displayed |
