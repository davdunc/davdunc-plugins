# DAS Trader Pro — CMD API Reference

## Architecture

The DAS CMD API is a **plain-text TCP socket protocol**.

- **Connection**: `127.0.0.1:<port>` — the port is whatever DAS is configured with (`CMDAPI:PORT` in `Config.cfg`, Setup → Other Configuration); 9910 is only the factory default. Never assume it.
- **Requirement**: DAS Trader Pro must be running on the **same machine** as your client
- **Security**: No TLS — plain text only, local connections only
- **Concurrency**: **One connection at a time** — either your bot OR the DAS GUI has API access, not both simultaneously

### API Tiers

| Tier | Connection | Use Case | Notes |
|---|---|---|---|
| CMD API | TCP 127.0.0.1:<configured port> | Automation on same machine | Most common; plain text; from WSL use mirrored networking so the source IP is loopback (DAS enforces an allow-IP mask) |
| .NET API | Remote to DAS servers | Remote/cloud automation | More expensive |
| FIX API | Remote, institutional | Order entry only, no data | Requires institutional arrangement |

---

## Connection Sequence

```
1. Connect TCP socket to 127.0.0.1:<configured port>
2. Send: LOGIN <username> <password> <account> <mode>   (mode 0 = trading, 1 = watch/read-only)
3. Receive: #LOGIN SUCCESSED, then the current %POS / %ORDER / %TRADE lines
4. Begin sending commands / receiving responses
```

---

## Command Reference

| Command | Syntax | Description |
|---|---|---|
| `LOGIN` | `LOGIN user pass account [0|1]` | Authenticate and select account; 1 = watch mode |
| `NEWORDER` | See parameters below | Place a new order |
| `CANCEL` | `CANCEL <order_id>` | Cancel specific order |
| `CANCEL ALL` | `CANCEL ALL` | Cancel all open orders |
| `SB` / `UNSB` | `SB <symbol> Lv1|Lv2|tms|MINCHART|DAYCHART` | Subscribe / unsubscribe quote, depth, T&S, bars |
| `POSREFRESH` | `POSREFRESH` | Re-send all positions as `%POS` lines |
| `GET BP` | `GET BP` | Buying power |
| `GET SHORTINFO` | `GET SHORTINFO <symbol>` | Shortable / marginable info |
| `SCRIPT` | `SCRIPT <WindowName> <script>` | Run a hotkey script in a DAS window (`GLOBALSCRIPT` for window-independent commands such as `ShowAccount <acct>`) |

---

## NEWORDER Syntax (positional — verified against the manual and a live instance)

```
NEWORDER <token> <B|S|SS> <symbol> <route> <shares> <price|MKT> [TIF=DAY|DAY+|IOC|GTC|...]
```

- `<token>` is your own correlation id; it comes back in the `%ORDER` line.
- A bare `S` on smart routes opens a **short**; to close a long use `S` on `REB25L` (or the platform's close
  route). `B` covers a short. Verify the side in `%POS` before and after.
- `DAY+` = regular plus extended hours. Stop types (`STOPMKT`, `STOPLMT`, `STOPTRAILING`, `STOPRANGE`) and pegs
  follow the manual's positional forms.

**Example — buy-to-cover 11 shares at a limit, extended hours allowed:**
```
NEWORDER SCH040000 B CAPR REB25L 11 9.08 DAY+
```

The `NEWORDER SYMBOL=... SIDE=...` key/value form and the `GETPOSITION` / `GETBUYINGPOWER` commands that
earlier revisions of this file listed are **rejected by DAS**; do not use them.

## Response Formats

### Order / trade / position lines
```
%ORDER <id> <token> <symbol> <B/S> <type> <qty> <lvqty> <cxlqty> <price> <route> <status> <time> ... <account>
%TRADE <id> <symbol> <B/S> <qty> <price> <route> <time> <orderid> ...
%POS   <symbol> <type> <qty> <avgcost> <initqty> <initprice> <realized> <created> <unrealized>
```
Status values seen: `Sending`, `Accepted`, `Executed`, `Canceled`, `Rejected`.
**`%POS` qty is unsigned**: a short shows the same positive qty as a long. Read the side from the trade
history or the account object, never from the sign of the position. (A close script that used the sign
doubled a short on 2026-09-25.)

### Quote Response (`$Quote`)
```
$Quote <SYMBOL> T:<HHMMSS> B:<bid> A:<ask> L:<last> V:<volume>
```

---

## Constraints

| Constraint | Detail |
|---|---|
| Local only | Must connect from same machine running DAS |
| One connection | Bot OR GUI — not both simultaneously |
| No Level 2 | Depth of book not available via any API |
| No RTH stop orders | Stop orders blocked outside regular trading hours |
| Spec is proprietary | Full protocol spec requires DAS certification form |

### Getting the Full Specification

The complete CMD API spec is behind DAS's certification process:
- URL: `agreements.dastrader.mobi/APIRequest/login.aspx`
- Fill in the form and DAS will provide the PDF manual

---

## Open-Source Libraries

### das-bridge (Python, MIT)
- **Repo**: `github.com/jefrnc/das-bridge`
- **Notes**: Most complete public Python implementation; the repo also contains a copy of the CMD API Manual PDF
- **Install**: `pip install das-bridge`

### DAS.Trader.IntegrationClient (.NET, MIT)
- **Package**: `nuget.org/packages/DAS.Trader.IntegrationClient`
- **Notes**: Built on the 2021/11/10 revision of the official spec; C# client
- **Install**: `dotnet add package DAS.Trader.IntegrationClient`

---

## Integration Pattern with Falcon

The Falcon platform (`falcon-trader` + `falcon-messenger`) generates signals. To execute those signals automatically via DAS:

1. `falcon-trader` produces signals via REST API at `/api/orders`
2. A bridge script polls `falcon-trader` and translates signals to `NEWORDER` commands
3. Bridge connects via TCP to `localhost:9910` and sends commands
4. DAS Trader Pro on TRADER-DESK executes the orders

**Important**: The bridge must run on TRADER-DESK (same machine as DAS). Only one API connection at a time — the bridge will occupy the CMD API connection while active.

```python
# Minimal pattern using das-bridge
from das_bridge import DASClient

client = DASClient(host='localhost', port=9910)
client.login(user='davdunc', password='...', account='...')

# Send order from Falcon signal
client.new_order(symbol='AAPL', side='B', price=182.50, 
                 shares=100, route='ARCAL', tif='DAY')
```
