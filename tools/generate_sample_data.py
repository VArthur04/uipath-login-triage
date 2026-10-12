# Generates fake login_attempts.csv for the Login Triage Bot (reproducible, seed 42).
# Usage: python tools/generate_sample_data.py  -> writes login_attempts.csv in the current folder
import csv, random
from datetime import datetime, timedelta
random.seed(42)
base = datetime(2026,10,9,6,0,0)
rows = []
def ts(): return base + timedelta(seconds=random.randint(0, 12*3600))
users = ["arthur","maria","andrei","elena","tibor","ioana","bogdan","kata"]
internal = {u: f"10.0.0.{10+i}" for i,u in enumerate(users)}
# normal traffic
for _ in range(330):
    u = random.choice(users)
    rows.append((ts(), u, internal[u], "SUCCESS"))
# occasional typos from normal users (1-3 failures)
for u in users:
    for _ in range(random.randint(1,3)):
        rows.append((ts(), u, internal[u], "FAILED"))
# decoy: just under threshold
for _ in range(4):
    rows.append((ts(), "bogdan", "10.0.0.45", "FAILED"))
# attacker 1: brute force on admin, then success
t0 = base + timedelta(hours=2, minutes=13)
for i in range(47):
    rows.append((t0 + timedelta(seconds=i*2), random.choice(["admin","root"]), "203.0.113.5", "FAILED"))
rows.append((t0 + timedelta(seconds=47*2+5), "admin", "203.0.113.5", "SUCCESS"))
# attacker 2: password spraying across usernames
t1 = base + timedelta(hours=7, minutes=40)
for i in range(12):
    rows.append((t1 + timedelta(seconds=i*20), random.choice(users+["guest","test","svc_backup"]), "198.51.100.23", "FAILED"))
# attacker 3: borderline, just over threshold
t2 = base + timedelta(hours=10, minutes=5)
for i in range(6):
    rows.append((t2 + timedelta(seconds=i*45), "tibor", "192.0.2.77", "FAILED"))
rows.sort(key=lambda r: r[0])
with open("login_attempts.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["timestamp","username","source_ip","result"])
    for r in rows:
        w.writerow([r[0].strftime("%Y-%m-%d %H:%M:%S"), r[1], r[2], r[3]])
