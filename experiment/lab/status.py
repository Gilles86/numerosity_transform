"""What every lab PC is doing: computer, participant, session, version, phase, time of the last change.
Run on the ExpMaster during a session (status.bat), and check the participant/session column before people start.
    status.bat            refresh every 10 s (Ctrl+C to stop)
    status.bat --once"""
import argparse
import os
import time
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--once', action='store_true')
p.add_argument('--test', action='store_true', help='Show the *_test results folder')
a = p.parse_args()
results = os.path.expandvars(yaml.safe_load((HERE / 'lab_config.yml').read_text())['results_dir'])
status_dir = Path(results.rstrip('/\\') + ('_test' if a.test else ''), 'status')

while True:
    rows = sorted(f.read_text().strip().split('\t') for f in status_dir.glob('*.tsv'))
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f'{status_dir}   ({time.strftime("%H:%M:%S")})\n')
    print(f'{"PC":<14}{"Particip.":>9}{"Session":>8}  {"Version":<17}{"Phase":<26}{"Since":>8}')
    for pc, sub, ses, stim, mapping, phase, t in rows:
        print(f'{pc:<14}{sub:>9}{ses:>8}  {stim + " " + mapping:<17}{phase:<26}{t:>8}')
    sessions = {r[2] for r in rows if not r[5].startswith('finished')}
    if len(sessions) > 1:
        print(f'\n!! Different sessions running: {", ".join(sorted(sessions))}')
    if a.once:
        break
    time.sleep(10)
