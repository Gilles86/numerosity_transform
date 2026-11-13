"""Write lab/participants.tsv: which version (stimulus x mapping) each participant does in each session. lab.py only
looks it up, so the whole assignment is fixed in advance and can be checked before the first session.

Design: every participant does all four versions, one per session. The order follows a Williams Latin square: across
the four orders, each version comes once in each session and directly follows each other version exactly once, so
order and carry-over effects are balanced. Participants cycle through the orders (1 -> order 1, 2 -> order 2, ...),
so neighbouring seats get different versions and every 4 consecutive participants form a complete square.

    python lab/make_participants.py   # any python, no dependencies
"""
import csv
from pathlib import Path

N_SUBJECTS = 35
VERSIONS = {'A': ('dots', 'concave'), 'B': ('dots', 'convex'), 'C': ('numeral', 'concave'), 'D': ('numeral', 'convex')}
WILLIAMS = ['ABDC', 'BCAD', 'CDBA', 'DACB']  # rows = orders, columns = sessions

with open(Path(__file__).parent / 'participants.tsv', 'w', newline='') as f:
    w = csv.writer(f, delimiter='\t')
    w.writerow(['subject', 'session', 'stimulus', 'mapping', 'order'])
    for subject in range(1, N_SUBJECTS + 1):
        order = (subject - 1) % len(WILLIAMS)
        for session, version in enumerate(WILLIAMS[order], 1):
            w.writerow([subject, session, *VERSIONS[version], order + 1])
print(f'Wrote {N_SUBJECTS} participants x {len(WILLIAMS[0])} sessions')
