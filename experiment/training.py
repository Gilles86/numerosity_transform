import argparse

# Parse arguments before importing psychopy, which would otherwise hijack --help
p = argparse.ArgumentParser()
p.add_argument('subject')
p.add_argument('session', type=int)
p.add_argument('--mapping', required=True, choices=['linear', 'concave', 'convex'])
p.add_argument('--stimulus', choices=['dots', 'numeral'], default='dots', help='Dot clouds, or Arabic numerals (0-100, two decimals)')
p.add_argument('--settings', default='default')
p.add_argument('--response', choices=['slider', 'typing'], help='Overrides `response` in the settings')
p.add_argument('--n_trials', type=int, help='Run only this many trials (testing)')
a = p.parse_args()
if a.stimulus == 'numeral' and a.mapping == 'linear':
    p.error('the numeral version exists for the concave and convex mappings only')
import numpy as np
from common import BaseSession, InstructionTrial, EstimationTrial


class TrainingSession(BaseSession):
    """Estimation with feedback: every numerosity (or numeral bin) x n_repeats, in blocks."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, task='training', response_y=-3.8, **kwargs)

    def create_trials(self, n_trials=None):
        t = self.settings['training']
        stimuli = self.sample_stimuli(t['n_repeats'])
        n_blocks = 1 if n_trials else t['n_blocks']
        blocks = np.array_split(stimuli[:n_trials], n_blocks)

        self.trials = [InstructionTrial(self, 0, self.instructions['phase_2'].format(how=self.instructions['how']))]
        for i, block in enumerate(blocks):
            self.trials.append(InstructionTrial(self, len(self.trials), f'Block {i + 1} of {n_blocks}\n\n'
                                                'You will receive feedback on each trial.\nRespond as accurately as possible.',
                                                'Press SPACE BAR to start.'))
            self.trials += [EstimationTrial(self, len(self.trials) + j, n.item(), training=True) for j, n in enumerate(block)]


if __name__ == '__main__':
    s = TrainingSession(a.subject, a.session, a.mapping, settings=a.settings, response=a.response, stimulus=a.stimulus)
    s.create_trials(a.n_trials)
    s.run()
