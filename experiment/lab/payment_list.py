"""Payment list for one lab session, from the earnings files that lab.py writes to the results folder.
Run on the ExpMaster PC (or anywhere the results folder is reachable):
    uv run python lab/payment_list.py 1                 # session 1, results_dir from lab/lab_config.yml
    uv run python lab/payment_list.py 1 --results-dir <folder>
With --all, the total over all sessions per participant (for paying everything after the last session)."""
import argparse
import csv
import os
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('session', type=int, nargs='?')
p.add_argument('--results-dir', default=yaml.safe_load((HERE / 'lab_config.yml').read_text())['results_dir'])
p.add_argument('--all', action='store_true', help='Sum over all sessions per participant')
a = p.parse_args()

rows = []
for f in sorted(Path(os.path.expandvars(a.results_dir), 'earnings').glob('earnings_sub-*_ses-*.tsv')):
    with open(f, newline='') as fh:
        rows += list(csv.DictReader(fh, delimiter='\t'))
if a.session and not a.all:
    rows = [r for r in rows if int(r['session']) == a.session]
if not rows:
    raise SystemExit('No earnings files found.')

if a.all:
    totals = {}
    for r in rows:
        t = totals.setdefault(int(r['subject']), {'sessions': [], 'total': 0.})
        t['sessions'].append(int(r['session']))
        t['total'] += float(r['total'])
    print(f'{"Participant":>11}  {"Sessions":<10} {"Total CHF":>9}')
    for sub, t in sorted(totals.items()):
        print(f'{sub:>11}  {",".join(map(str, sorted(t["sessions"]))):<10} {t["total"]:>9.2f}')
    print(f'{"":>11}  {"":<10} {sum(t["total"] for t in totals.values()):>9.2f}  (sum)')
else:
    print(f'{"Participant":>11}  {"Computer":<12} {"Bonus":>6} {"Fee":>6} {"Compl.":>6} {"Total CHF":>9}')
    for r in sorted(rows, key=lambda r: int(r['subject'])):
        print(f'{r["subject"]:>11}  {r["computer"]:<12} {float(r["auction_bonus"]):>6.2f} {float(r["show_up_fee"]):>6.2f} '
              f'{float(r["completion_bonus"]):>6.2f} {float(r["total"]):>9.2f}')
    print(f'{len(rows)} participants, total {sum(float(r["total"]) for r in rows):.2f} CHF')
