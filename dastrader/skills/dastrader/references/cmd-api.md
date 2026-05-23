# DAS Trader Pro — CMD API Reference

## Architecture

The DAS CMD API is a **plain-text TCP socket protocol**.

- **Connection**: `localhost:9910`
- **Requirement**: DAS Trader Pro must be running on the **same machine** as your client
- **Security**: No TLS — plain text only, local connections only
- **Concurrency**: **One connection at a time** — either your bot OR the DAS GUI has API access, not both simultaneously

### API Tiers

| Tier | Connection | Use Case | Notes |
|---|---|---|---|
| CMD API | TCP localhost:9910 | Automation on same machine | Most common; plain text |
| .NET API | Remote to DAS servers | Remote/cloud automation | More expensive |
| FIX API | Remote, institutional | Order entry only, no data | Requires institutional arrangement |

---

## Connection Sequence

```
1. Connect TCP socket to localhost:9910
2. Send: LOGIN <username> <password> <account>
3. Receive: LOGIN OK (or error)
4. Begin sending commands / receiving responses
```

---

## Command Reference

| Command | Syntax | Description |
|---|---|---|
| `LOGIN` | `LOGIN user pass account` | Authenticate and select account |
| `NEWORDER` | See parameters below | Place a new order |
| `CANCEL` | `CANCEL <order_id>` | Cancel specific order |
| `CANCEL ALL` | `CANCEL ALL` | Cancel all open orders |
| `SUBSCRIBE LEVEL1` | `SUBSCRIBE LEVEL1 <SYMBOL>` | Subscribe to Level 1 quote stream |
| `GETPOSITION` | `GETPOSITION` | Get all current positions |
| `GETBUYINGPOWER` | `GETBUYINGPOWER` | Get current buying power |
| `GETORDER` | `GETORDER` | Get all open orders |
| `LOCATEORDER` | `LOCATEORDER <params>` | Automate HTB share locate |

---

## NEWORDER Parameters

| Parameter | Values | Description |
|---|---|---|
| `SYMBOL` | e.g., `AAPL` | Ticker symbol |
| `SIDE` | `B`, `S`, `SS`, `BC` | Buy / Sell / Short Sell / Buy to Cover |
| `PRICE` | Numeric | Limit price (use 0 for market) |
| `SHARE` | Integer | Number of shares |
| `ROUTE` | e.g., `ARCAL`, `SMRTL` | Routing destination |
| `TIF` | `DAY`, `GTC`, `IOC`, etc. | Time in force |
| `StopType` | `STOPMARKET`, `STOPLIMIT`, `STOPTRAILING`, `STOPRANGE` | For stop orders |
| `StopPrice` | Numeric | Stop trigger price |
| `TrailPrice` | Numeric | Trail offset (for STOPTRAILING) |
| `LowPrice` | Numeric | Lower bound (for STOPRANGE) |
| `HighPrice` | Numeric | Upper bound / profit target (for STOPRANGE) |

**Example — Buy 100 AAPL at limit:**
```
NEWORDER SYMBOL=AAPL SIDE=B PRICE=182.50 SHARE=100 ROUTE=ARCAL TIF=DAY
```

**Example — Short sell with stop:**
```
NEWORDER SYMBOL=TSLA SIDE=SS PRICE=245.00 SHARE=50 ROUTE=ARCAL TIF=DAY StopType=STOPMARKET StopPrice=248.00
```

---

## Response Formats

### Order Response (`%ORDER`)
```
%ORDER <order_id> <symbol> <side> <price> <shares> <status> <filled> <avg_fill_price>
```

Status values: `PENDING`, `OPEN`, `FILLED`, `PARTIAL`, `CANCELED`, `REJECTED`

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
