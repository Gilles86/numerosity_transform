"""Write lab/participants.tsv: which stimulus and mapping each participant gets in each session. lab.py reads it.

DESIGN below is an assumption to be confirmed: every participant keeps one stimulus x mapping for all sessions, and the
five versions are balanced over participants (35 = 5 x 7). Change DESIGN (or edit the TSV by hand) if the plan differs,
e.g. a different mapping per session.

    python lab/make_participants.py   # any python, no dependencies
"""
import csv
import random
from pathlib import Path

N_SUBJECTS, N_SESSIONS, SEED = 35, 4, 2026
DESIGN = [('dots', 'linear'), ('dots', 'concave'), ('dots', 'convex'), ('numeral', 'concave'), ('numeral', 'convex')]

conditions = [DESIGN[i % len(DESIGN)] for i in range(N_SUBJECTS)]
random.Random(SEED).shuffle(conditions)
with open(Path(__file__).parent / 'participants.tsv', 'w', newline='') as f:
    w = csv.writer(f, delimiter='\t')
    w.writerow(['subject', 'session', 'stimulus', 'mapping'])
    for subject, (stimulus, mapping) in enumerate(conditions, 1):
        for session in range(1, N_SESSIONS + 1):
            w.writerow([subject, session, stimulus, mapping])
print(f'Wrote {N_SUBJECTS} participants x {N_SESSIONS} sessions')
