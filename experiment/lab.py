"""Lab launcher: one participant per computer, no terminal needed. LabControl starts this script on every client.

1. A dialog asks for the participant number (from the seating card) and the session; the session is filled in from
   the results already on the network share. Stimulus and mapping come from lab/participants.tsv.
2. All phases run in a row: examples, training, auction runs 1-4. After a crash, start again: the dialog proposes to
   continue with the first phase that has no log yet.
3. Logs are written to a local folder outside C:\\ExpFiles (LabControl's mirroring would delete them there) and copied
   to the results folder on the network after every phase.
4. At the end a dialog shows what the participant earned this session; the amount is also saved for the payment list
   (lab/payment_list.py).

Fully automatic (no dialogs; every participant keeps the same seat in all sessions):
    lab.bat --auto              participant = computer number (group on computers 1-30 -> participants 1-30)
    lab.bat --auto --offset 30  participant = computer number + 30 (group on computers 1-5 -> participants 31-35)
The session is the participant's first session without all auction runs, and an interrupted session continues at the
first phase without a log. If the computer number does not give a known participant, the dialogs are shown instead.

Where things go is set in lab/lab_config.yml. Test outside the lab with:  uv run python lab.py
"""
import csv
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
CONFIG = yaml.safe_load((HERE / 'lab' / 'lab_config.yml').read_text())
SETTINGS = yaml.safe_load((HERE / 'settings' / 'default.yml').read_text())
M = SETTINGS['main_task']
PHASES = ['examples', 'training'] + [f'run{r}' for r in range(1, M['n_runs'] + 1)]
COMPUTER = platform.node()


def local_root():
    return Path(os.path.expandvars(CONFIG['local_log_dir'])).expanduser()


def results_root():
    """Network results folder, or None if it is not set or not reachable (then only the local copy exists)."""
    path = CONFIG.get('results_dir')
    if not path:
        return None
    path = Path(os.path.expandvars(path))
    if not path.is_absolute():  # e.g. an N:\ path on a Mac
        return None
    try:
        path.mkdir(parents=True, exist_ok=True)
        return path
    except OSError:
        return None


def sub_dir(root, subject, session, stimulus):
    return root / ('numerals' if stimulus == 'numeral' else '') / f'sub-{subject:02d}' / f'ses-{session}'


def read_plan():
    with open(HERE / 'lab' / 'participants.tsv', newline='') as f:
        return {(int(r['subject']), int(r['session'])): (r['stimulus'], r['mapping']) for r in csv.DictReader(f, delimiter='\t')}


def completed_sessions(subject):
    """Sessions with all auction runs logged, locally or on the network."""
    done = set()
    for root in filter(None, [local_root(), results_root()]):
        for d in root.glob(f'**/sub-{subject:02d}/ses-*'):
            if len(list(d.glob('reward_*.txt'))) >= M['n_runs']:
                done.add(int(d.name.removeprefix('ses-')))
    return done


def first_missing_phase(subject, session, stimulus, mapping):
    """First phase without a log, locally or on the network (the participant may have moved to another computer)."""
    dirs = [sub_dir(root, subject, session, stimulus) for root in filter(None, [local_root(), results_root()])]
    for phase in PHASES:
        task = 'auction_run-%02d' % int(phase[3:]) if phase.startswith('run') else phase
        if not any(next(d.glob(f'*_task-{task}.{mapping}_events.tsv'), None) for d in dirs):
            return phase
    return PHASES[0]


def commands(subject, session, stimulus, mapping):
    opts = ['--mapping', mapping, '--stimulus', stimulus, '--settings', CONFIG['settings']]
    resp = ['--response', SETTINGS['response']]
    cmds = {'examples': ['examples.py', str(subject), str(session), *opts],
            'training': ['training.py', str(subject), str(session), *opts, *resp]}
    for r in range(1, M['n_runs'] + 1):
        cmds[f'run{r}'] = ['task.py', str(subject), str(session), str(r), *opts, *resp]
    return cmds


def copy_to_network(subject, session, stimulus):
    dest = results_root()
    if dest is None:
        return False
    src = sub_dir(local_root(), subject, session, stimulus)
    try:
        shutil.copytree(src, sub_dir(dest, subject, session, stimulus), dirs_exist_ok=True)
        return True
    except OSError:
        return False


def session_earnings(subject, session, stimulus, mapping):
    d = sub_dir(local_root(), subject, session, stimulus)
    bonus = sum(float(f.read_text()) for f in d.glob(f'reward_*.{mapping}.txt'))
    completion = M['completion_bonus'] if session == M['n_sessions'] else 0.
    return bonus, M['show_up_fee'], completion


def save_earnings(subject, session, stimulus, mapping, bonus, fee, completion):
    """One small file per participant and session (no two computers ever write the same file)."""
    row = dict(subject=subject, session=session, computer=COMPUTER, stimulus=stimulus, mapping=mapping,
               auction_bonus=f'{bonus:.2f}', show_up_fee=f'{fee:.2f}', completion_bonus=f'{completion:.2f}',
               total=f'{bonus + fee + completion:.2f}', time=datetime.now().isoformat(timespec='seconds'))
    for root in filter(None, [local_root(), results_root()]):
        f = root / 'earnings' / f'earnings_sub-{subject:02d}_ses-{session}.tsv'
        f.parent.mkdir(parents=True, exist_ok=True)
        with open(f, 'w', newline='') as fh:
            w = csv.DictWriter(fh, row.keys(), delimiter='\t')
            w.writeheader()
            w.writerow(row)


def message(title, text):
    from psychopy import gui
    dlg = gui.Dlg(title=title)
    for line in text.split('\n'):
        dlg.addText(line)
    dlg.show()


def computer_number():
    """Trailing number of the computer name (e.g. 23 for a client called ...23), or None."""
    m = re.search(r'(\d+)\D*$', COMPUTER)
    return int(m.group(1)) if m else None


def suggested_participant():
    """If participants keep the same seat in every session: participant = computer number + subject_offset."""
    nr = computer_number()
    if CONFIG.get('subject_from_computer') and nr is not None:
        return str(nr + int(CONFIG.get('subject_offset', 0)))
    return ''


def ask_participant(plan):
    from psychopy import gui
    while True:
        info = {'Participant number': suggested_participant()}
        dlg = gui.DlgFromDict(info, title=f'Numerosity study - {COMPUTER}', alwaysOnTop=True)
        if not dlg.OK:
            sys.exit()
        try:
            subject = int(info['Participant number'])
        except ValueError:
            message('Error', 'Please type a number.')
            continue
        done = completed_sessions(subject)
        session = max(done, default=0) + 1
        sessions = [s for (sub, s) in plan if sub == subject]
        if not sessions:
            message('Unknown participant', f'Participant {subject} is not in lab/participants.tsv.\n'
                                           'Check the number, or call the experimenter.')
            continue
        info = {'Participant number': subject, 'Session': min(session, max(sessions))}
        dlg = gui.DlgFromDict(info, title='Please check', fixed=['Participant number'], sortKeys=False, alwaysOnTop=True)
        if not dlg.OK:
            continue
        session = int(info['Session'])
        if (subject, session) not in plan:
            message('Unknown session', f'There is no session {session} for participant {subject}.')
            continue
        if session in done and not ask_yes(f'Session {session} of participant {subject} is already complete.\n'
                                           'Run it again anyway?'):
            continue
        return subject, session


def ask_yes(text):
    from psychopy import gui
    dlg = gui.Dlg(title='Please confirm')
    for line in text.split('\n'):
        dlg.addText(line)
    dlg.show()
    return dlg.OK


def automatic(plan, offset):
    """No dialogs: participant = computer number + offset, session = first session not yet completed.
    Returns None (and the dialogs are used instead) if that does not give a known participant and session."""
    nr = computer_number()
    if nr is None:
        return None
    subject = nr + offset
    done = completed_sessions(subject)
    session = max(done, default=0) + 1
    return (subject, session) if (subject, session) in plan else None


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--auto', action='store_true',
                   help='No dialogs: participant = computer number + offset, session and phase from the logs')
    p.add_argument('--offset', type=int, default=int(CONFIG.get('subject_offset', 0)),
                   help='Added to the computer number (e.g. 30 for a second group on computers 1-5)')
    a = p.parse_args()
    if a.offset:
        CONFIG.update(subject_from_computer=True, subject_offset=a.offset)

    plan = read_plan()
    auto = automatic(plan, a.offset) if a.auto else None
    subject, session = auto or ask_participant(plan)
    stimulus, mapping = plan[(subject, session)]
    print(f'{COMPUTER}: participant {subject}, session {session}, {stimulus} {mapping}')

    from psychopy import gui
    start = first_missing_phase(subject, session, stimulus, mapping)
    if start != PHASES[0] and not auto:  # only after a crash: let the experimenter confirm where to continue
        info = {'Continue at phase': [start] + [p for p in PHASES if p != start]}
        dlg = gui.DlgFromDict(info, title=f'EXPERIMENTER: participant {subject}, session {session} was interrupted',
                              alwaysOnTop=True)
        if not dlg.OK:
            sys.exit()
        start = info['Continue at phase']

    env = dict(os.environ, NUMEROSITY_LOG_ROOT=str(local_root()))
    cmds = commands(subject, session, stimulus, mapping)
    for phase in PHASES[PHASES.index(start):]:
        result = subprocess.run([sys.executable, str(HERE / cmds[phase][0]), *cmds[phase][1:]], cwd=HERE, env=env)
        copy_to_network(subject, session, stimulus)
        if result.returncode != 0:
            message('Problem', f'The experiment stopped during "{phase}".\nPlease raise your hand.')
            sys.exit(1)

    bonus, fee, completion = session_earnings(subject, session, stimulus, mapping)
    save_earnings(subject, session, stimulus, mapping, bonus, fee, completion)
    saved = copy_to_network(subject, session, stimulus)
    lines = [f'This session is finished. Thank you!', '',
             f'Auction bonus: {bonus:.2f} CHF', f'Show-up fee: {fee:.2f} CHF']
    if completion:
        lines.append(f'Completion bonus: {completion:.2f} CHF')
    lines += [f'Total: {bonus + fee + completion:.2f} CHF', '', 'Please stay seated and raise your hand.']
    if not saved:
        lines += ['', '(Experimenter: results were NOT copied to the network; they are in ' + str(local_root()) + ')']
    message('Finished', '\n'.join(lines))


if __name__ == '__main__':
    main()
