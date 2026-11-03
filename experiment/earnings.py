"""Print a subject's earnings: variable reward summed over reward files, plus show-up fee per session."""
import argparse
import yaml
from pathlib import Path

HERE = Path(__file__).parent

p = argparse.ArgumentParser()
p.add_argument('subject')
a = p.parse_args()
fee = yaml.safe_load((HERE / 'settings' / 'default.yml').read_text())['main_task']['show_up_fee']

total, n_sessions = 0., 0
sub = f'sub-{a.subject.zfill(2)}'
for ses in sorted([*(HERE / 'logs' / sub).glob('ses-*'), *(HERE / 'logs' / 'numerals' / sub).glob('ses-*')]):  # dots, numerals
    rewards = {f.stem: float(f.read_text()) for f in sorted(ses.glob('reward_*.txt'))}
    print(f'{"numerals " * (ses.parent.parent.name == "numerals")}{ses.name}: {len(rewards)} runs, {sum(rewards.values()):.2f} CHF')
    for name, reward in rewards.items():
        print(f'  {name}: {reward:.2f}')
    total += sum(rewards.values())
    n_sessions += 1
print(f'Variable reward {total:.2f} + show-up fee {fee * n_sessions:.2f} = {total + fee * n_sessions:.2f} CHF')
