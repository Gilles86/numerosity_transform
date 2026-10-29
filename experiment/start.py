"""Interactive launcher: asks for subject, session, mapping, screen and response mode, then runs all phases.
python start.py  (any python: installs uv if needed and re-launches itself inside the project's uv environment)"""
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if Path(sys.prefix).resolve() != HERE / '.venv':
    find_uv = lambda: shutil.which('uv') or shutil.which('uv', path=str(Path.home() / '.local' / 'bin'))
    if not find_uv():
        print('uv not found; installing it (https://docs.astral.sh/uv/) ...')
        subprocess.run(['powershell', '-ExecutionPolicy', 'ByPass', '-c', 'irm https://astral.sh/uv/install.ps1 | iex']
                       if sys.platform == 'win32' else ['sh', '-c', 'curl -LsSf https://astral.sh/uv/install.sh | sh'], check=True)
    sys.exit(subprocess.run([find_uv(), 'run', '--project', str(HERE), 'python', str(HERE / 'start.py')]).returncode)
import yaml


def ask(question, options=None, default=None):
    """Free-text question, or a numbered multiple choice (answer with the number or the name; Enter = default)."""
    if options:
        print(f'\n{question}:')
        for i, option in enumerate(options, 1):
            print(f'  {i}) {option}' + ('  (default)' if option == default else ''))
    while True:
        answer = input('> ' if options else f'{question}' + (f' (default: {default})' if default else '') + ': ').strip() or default
        if answer and options and answer.isdigit() and 1 <= int(answer) <= len(options):
            return options[int(answer) - 1]
        if answer and (options is None or answer in options):
            return answer
        print(f'  Please answer 1-{len(options)}.' if options else '  Please answer.')


subject = ask('Subject (number or name, letters/digits only)')
session = ask('Session', default='1')
mapping = ask('Mapping', ['linear', 'concave', 'convex'])
settings = ask('Screen settings', sorted(f.stem for f in (HERE / 'settings').glob('*.yml')), default='dell_p2725qe')
response = ask('Response', ['typing', 'slider'], default='typing')

n_runs = yaml.safe_load((HERE / 'settings' / 'default.yml').read_text())['main_task']['n_runs']
phases = ['examples', 'training'] + [f'run{r}' for r in range(1, n_runs + 1)]
start = ask('Start at phase (to resume after a crash)', phases, default='examples')

log_dir = HERE / 'logs' / f'sub-{subject.zfill(2)}' / f'ses-{session}'
if any(log_dir.glob(f'*.{mapping}*')) and ask(f'{log_dir} already has {mapping} files; they may be overwritten. Continue?',
                                               ['y', 'n'], 'n') != 'y':
    sys.exit()

opts = [subject, session, '--mapping', mapping, '--settings', settings]
commands = {'examples': ['examples.py', *opts], 'training': ['training.py', *opts, '--response', response]}
commands.update({f'run{r}': ['task.py', subject, session, str(r), *opts[2:], '--response', response] for r in range(1, n_runs + 1)})
for phase in phases[phases.index(start):]:
    print(f'\n=== {phase} ===')
    subprocess.run([sys.executable, str(HERE / commands[phase][0]), *commands[phase][1:]], check=True)
print(f'\nDone. Earnings: uv run python earnings.py {subject}')
