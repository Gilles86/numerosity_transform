"""Seating plan for one session: which PC, participant, version and booklet. Print it and lay out the booklets.
    python lab/session_plan.py 1                # group on PCs 1-30 (participants 1-30)
    python lab/session_plan.py 1 --offset 30 --pcs 5   # group on PCs 1-5 (participants 31-35)"""
import argparse
import csv
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('session', type=int)
p.add_argument('--offset', type=int, default=0)
p.add_argument('--pcs', type=int, default=30, help='Number of PCs used (1..pcs)')
a = p.parse_args()

with open(Path(__file__).parent / 'participants.tsv', newline='') as f:
    plan = {(int(r['subject']), int(r['session'])): r for r in csv.DictReader(f, delimiter='\t')}
print(f'Session {a.session}\n{"PC":>3}  {"Participant":>11}  {"Version":<17} Booklet')
for pc in range(1, a.pcs + 1):
    r = plan.get((pc + a.offset, a.session))
    if r:
        version = f'{"numbers" if r["stimulus"] == "numeral" else "dots"} {r["mapping"]}'
        booklet = f'instructions_{"numeral_" if r["stimulus"] == "numeral" else ""}{r["mapping"]}.docx'
        print(f'{pc:>3}  {pc + a.offset:>11}  {version:<17} {booklet}')
