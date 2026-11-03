"""Timings per request from today's LM Studio server logs, since an hour given as HH:MM:SS."""
import re, sys, glob, os
since = sys.argv[1] if len(sys.argv) > 1 else "00:00:00"
day = sys.argv[2] if len(sys.argv) > 2 else "2026-11-03"
rows, cur = [], None
for f in sorted(glob.glob(os.path.expanduser(f"~/.lmstudio/server-logs/{day[:7]}/{day}*.log")), key=os.path.getmtime):
    for l in open(f, encoding="utf-8", errors="replace"):
        m = re.match(r"\[(\S+) (\S+)\]\[INFO\]\[([^\]]+)\].*with (\d+) messages", l)
        if m:
            cur = {"t": m[2], "m": m[3]}
            rows.append(cur)
            continue
        m = re.search(r"prompt eval time =\s*([\d.]+) ms /\s*(\d+) tokens.*?([\d.]+) tokens per second", l)
        if m and cur:
            cur.update(pe=float(m[1]) / 1000, pt=int(m[2]), pr=float(m[3]))
            continue
        m = re.search(r"\beval time =\s*([\d.]+) ms /\s*(\d+) tokens.*?([\d.]+) tokens per second", l)
        if m and cur and "pe" in cur and "ev" not in cur:
            cur.update(ev=float(m[1]) / 1000, et=int(m[2]), er=float(m[3]))
            continue
        m = re.search(r"draft acceptance = ([\d.]+)", l)
        if m and cur:
            cur["dr"] = float(m[1])
rows = [r for r in rows if r["t"] >= since]
print("hora      leidos  lect_s   t/s  escritos  esc_s   t/s  draft")
tp = te = 0.0
for r in rows:
    if "pe" in r:
        tp += r["pe"]; te += r.get("ev", 0)
        print(f'{r["t"]} {r["pt"]:6d} {r["pe"]:7.1f} {r["pr"]:5.0f} {r.get("et",0):8d} {r.get("ev",0):6.1f} {r.get("er",0):5.0f}  {r.get("dr",0):.2f}')
    else:
        print(r["t"], "en curso")
print(f"peticiones={len(rows)} lectura={tp:.1f}s escritura={te:.1f}s modelo={rows[-1]['m'] if rows else '-'}")
