#!/usr/bin/env python3
"""One-shot DAS CMD API order, meant for Task Scheduler. Operator-directed.
Usage: das_scheduled_order.py SIDE SYMBOL QTY PRICE [--account ACCT] [--route REB25L] [--tif DAY+] [--dry-run]
Logs to ~/.claude/MEMORY/LOGS/das-order-<date>.log and posts a share-count-free note to #falcon-cluster."""
import argparse, os, re, socket, subprocess, sys, time, datetime
ap = argparse.ArgumentParser()
ap.add_argument("side", choices=["B", "S", "SS"]); ap.add_argument("symbol"); ap.add_argument("qty", type=int); ap.add_argument("price")
ap.add_argument("--account", default=None); ap.add_argument("--route", default="REB25L"); ap.add_argument("--tif", default="DAY+"); ap.add_argument("--dry-run", action="store_true")
a = ap.parse_args()
env = {}
for l in open(os.path.expanduser("~/.claude/.env")):
    l = l.strip()
    if "=" in l and not l.startswith("#"):
        k, v = l.split("=", 1); env[k] = v.split("#")[0].strip().strip('"').strip("'")
host, port = env.get("DAS_HOST", "127.0.0.1"), int(env.get("DAS_PORT", "3192"))
user, pw, acct = env["DAS_USER"], env["DAS_PASSWORD"], a.account or env.get("DAS_ACCOUNT", "{{SIM_ACCOUNT}}")
logdir = os.path.expanduser("~/.claude/MEMORY/LOGS"); os.makedirs(logdir, exist_ok=True)
log = open(os.path.join(logdir, f"das-order-{datetime.date.today()}.log"), "a")
def L(m):
    line = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}] {m}"; print(line); log.write(line + "\n"); log.flush()
def note(m):
    h = os.path.expanduser("~/.claude/Tools/falcon-cluster-handoff.sh")
    if os.path.exists(h): subprocess.run([h, "state", m], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
L(f"start side={a.side} sym={a.symbol} qty={a.qty} px={a.price} route={a.route} tif={a.tif} acct={acct} dry={a.dry_run}")
try:
    s = socket.create_connection((host, port), timeout=15)
except Exception as e:
    L(f"FAIL connect {host}:{port}: {e}"); note(f"[daslaptop] scheduled {a.side} {a.symbol} order NOT sent: DAS CMD API unreachable ({e})"); sys.exit(2)
s.settimeout(2); buf = ""
def send(c): s.sendall((c + "\r\n").encode())
def read(secs):
    global buf; end = time.time() + secs; out = []
    while time.time() < end:
        try: d = s.recv(65536).decode(errors="replace")
        except socket.timeout: continue
        if not d: break
        buf += d
        while "\n" in buf:
            line, buf = buf.split("\n", 1); line = line.strip()
            if line: out.append(line)
    return out
send(f"LOGIN {user} {pw} {acct} {1 if a.dry_run else 0}")
lines = read(4)
if not any("LOGIN SUCCESSED" in l.upper() for l in lines):
    L(f"FAIL login: {[l for l in lines if l.startswith('#')][:3]}"); note(f"[daslaptop] scheduled {a.side} {a.symbol} order NOT sent: DAS login failed"); sys.exit(3)
L(f"login ok; positions: {[l for l in lines if l.startswith('%POS')]}")
if a.dry_run:
    L("dry run: no order sent"); s.close(); sys.exit(0)
tok = "SCH" + time.strftime("%H%M%S")
send(f"NEWORDER {tok} {a.side} {a.symbol} {a.route} {a.qty} {a.price} {a.tif}")
lines = read(8)
# DAS does not echo the client token in %ORDER (field 2 is its own ref); match on symbol/side/route/price
orders = [l for l in lines if l.startswith("%ORDER") and re.search(rf"%ORDER \S+ \S+ {re.escape(a.symbol)} {a.side[0]} \S+ .* {re.escape(a.route)} ", l) and str(float(a.price)) in [str(float(x)) for x in re.findall(r"\b\d+\.\d+\b", l)]]
trades = [l for l in lines if l.startswith("%TRADE") and a.symbol in l]
errs = [l for l in lines if l.startswith("#") and re.search(r"reject|error|fail|invalid", l, re.I)]
for l in orders + trades + errs: L(l)
status = "unknown"
for l in orders:
    for st in ("Executed", "Accepted", "Rejected", "Canceled", "Sending"): 
        if f" {st} " in l: status = st
L(f"result status={status}")
s.close()
note(f"[daslaptop] scheduled {a.side} {a.symbol} limit order ({a.tif}) at {a.price}: {status}" + (" (filled)" if trades else ""))
sys.exit(0 if status in ("Accepted", "Executed") else 4)
