"""Render the vendor/community subagent prompts for one backfill week.
usage: python gen_prompts.py LABEL END  -> prompts/<LABEL>/{vendors_A,vendors_B,community}.txt"""
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
here = Path(__file__).resolve().parent
s, e = date.fromisoformat(sys.argv[1]), date.fromisoformat(sys.argv[2])
e1 = e + timedelta(days=1)
epoch = lambda d: int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())
months = sorted({(s.year, s.month), (e.year, e.month)})
tok = {
    "{S}": s.isoformat(), "{E}": e.isoformat(), "{E1}": e1.isoformat(),
    "{SS}": f"{s:%m-%d}", "{EE1X}": f"{e:%m-%d}", "{EE1}": f"{e1:%m-%d}",
    "{ES}": str(epoch(s)), "{EE}": str(epoch(e1)),
    "{EY}": str(e.year), "{EM}": str(e.month), "{ED}": str(e.day),
    "{YM}": f"{s.year}/{s.month:02d}", "{YM_HW}": f"{s.year}/{s.month}",
    "{MONTHS_ARCHIVE}": " 与 ".join(f"`/{y}/{m:02d}/`" for y, m in months),
}
note = ""
if len(months) > 1:
    note = (f"\n\n**注意：本窗口跨月（{s:%m-%d}~{e:%m-%d}），所有按月归档/按 URL 年月 grep 的入口，"
            f"{' 和 '.join(f'{y}/{m:02d}' for y, m in months)} 两个月都要查。**")
out = here / "prompts" / s.isoformat()
out.mkdir(parents=True, exist_ok=True)
for name in ("vendors_A", "vendors_B", "community"):
    t = (here / "prompts" / f"{name}.txt").read_text(encoding="utf-8")
    for k, v in tok.items():
        t = t.replace(k, v)
    (out / f"{name}.txt").write_text(t + note, encoding="utf-8")
print(out)
