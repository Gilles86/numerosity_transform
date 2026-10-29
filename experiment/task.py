import argparse

# Parse arguments before importing psychopy, which would otherwise hijack --help
p = argparse.ArgumentParser()
p.add_argument('subject')
p.add_argument('session', type=int)
p.add_argument('run', type=int)
p.add_argument('--mapping', required=True, choices=['linear', 'concave', 'convex'])
p.add_argument('--settings', default='default')
p.add_argument('--response', choices=['slider', 'typing'], help='Overrides `response` in the settings')
p.add_argument('--n_trials', type=int, help='Run only this many trials (testing)')
a = p.parse_args()
import numpy as np
from common import BaseSession, InstructionTrial, EstimationTrial


class TaskSession(BaseSession):
    """BDM auction without feedback; one run per call."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, task='auction', **kwargs)
        self.reward_file = self.output_dir / f'reward_{self.settings["subject"]}_{self.settings["session"]}_{self.settings["run"]}.{self.settings["mapping"]}.txt'

    def auction(self, bid, value):
        """Random price from the slider range; if bid > price, pay the price and receive the value."""
        lo, hi = self.settings['slider']['range']
        precision = self.settings['slider']['precision']
        price = round(np.random.uniform(lo, hi) / precision) * precision
        return price, hi + value - price if bid > price else hi

    def create_trials(self, n_trials=None):
        m = self.settings['main_task']
        numerosities = np.tile(self.settings['mappings']['numerosities'], m['n_repeats'])
        np.random.shuffle(numerosities)
        numerosities = numerosities[:n_trials]
        isis = np.random.choice(self.settings['durations']['isis'], len(numerosities))

        self.trials = [InstructionTrial(self, 0, self.instructions['phase_3'].format(run=self.settings['run'], n_runs=m['n_runs'], how=self.instructions['how']))]
        self.trials += [EstimationTrial(self, i + 1, int(n), training=False, isi=isi)
                        for i, (n, isi) in enumerate(zip(numerosities, isis))]

    def run(self):
        self.start_experiment()
        for trial in self.trials:
            trial.run()

        s = self.settings
        reward = sum(t.parameters['reward'] for t in self.trials[1:]) / s['main_task']['reward_scaling']
        self.reward_file.write_text(f'{reward:.2f}\n')
        files = list(self.output_dir.glob(f'reward_{s["subject"]}_{s["session"]}_*.{s["mapping"]}.txt'))
        total = sum(float(f.read_text()) for f in files)
        summary = InstructionTrial(self, len(self.trials), f'This run: {reward:.2f} CHF\n\nTotal so far '
                                   f'({len(files)}/{s["main_task"]["n_runs"]} runs): {total:.2f} CHF')
        summary.run()
        self.close()


if __name__ == '__main__':
    s = TaskSession(a.subject, a.session, a.mapping, run=a.run, settings=a.settings, response=a.response)
    s.create_trials(a.n_trials)
    s.run()
