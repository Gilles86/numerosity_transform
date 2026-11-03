import argparse

# Parse arguments before importing psychopy, which would otherwise hijack --help
p = argparse.ArgumentParser()
p.add_argument('subject')
p.add_argument('session', type=int)
p.add_argument('--mapping', required=True, choices=['linear', 'concave', 'convex'])
p.add_argument('--stimulus', choices=['dots', 'numeral'], default='dots', help='Dot clouds, or Arabic numerals (0-100, two decimals)')
p.add_argument('--settings', default='default')
a = p.parse_args()
if a.stimulus == 'numeral' and a.mapping == 'linear':
    p.error('the numeral version exists for the concave and convex mappings only')
import numpy as np
from psychopy.visual import TextStim
from exptools2.core import Trial
from common import BaseSession, InstructionTrial, GREEN


class ExampleSession(BaseSession):
    """Self-paced browser over all numerosities (or evenly spaced numerals) and their values."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, task='examples', **kwargs)
        s = self.settings
        self.stimuli = self.levels
        self.idx, self.seen = 0, {0}
        self.cloud = self.new_cloud()
        self.value_text = TextStim(self.win, height=1, color=GREEN, pos=(0, 1.2 * s['cloud']['aperture_radius'] + .5))
        self.bottom = TextStim(self.win, height=.6, wrapWidth=30, pos=(0, -1.4 * s['cloud']['aperture_radius']))

    def new_cloud(self):
        return self.make_stimulus(self.stimuli[self.idx])

    def create_trials(self):
        self.trials = [InstructionTrial(self, 0, self.instructions['phase_1']), ExampleTrial(self, 1)]


class ExampleTrial(Trial):
    def __init__(self, session, trial_nr):
        super().__init__(session, trial_nr, [np.inf], ['examples'])

    def get_events(self):
        s = self.session
        for key, t in super().get_events():
            if key in ('left', 'right'):
                s.idx = int(np.clip(s.idx + (1 if key == 'right' else -1), 0, len(s.stimuli) - 1))
                s.seen.add(s.idx)
                s.cloud = s.new_cloud()
            elif key == 'space' and len(s.seen) == len(s.stimuli):
                self.stop_phase()

    def draw(self):
        s = self.session
        x, what = s.stimuli[s.idx], 'numbers' if s.is_numeral else 'numbers of dots'
        s.value_text.text = (f'Value: {s.get_value(x):.2f} CHF' if s.is_numeral else f'{x} dots = {s.get_value(x):.1f} CHF')
        s.bottom.text = f'Left/right arrow: change {"number" if s.is_numeral else "number of dots"}.' + (
            '\nSPACE BAR: continue.' if len(s.seen) == len(s.stimuli) else
            f'\nSeen {len(s.seen)} of {len(s.stimuli)} {what}.')
        s.cloud.draw()
        s.value_text.draw()
        s.bottom.draw()
        if not s.is_numeral:
            s.fixation.draw()


if __name__ == '__main__':
    s = ExampleSession(a.subject, a.session, a.mapping, settings=a.settings, stimulus=a.stimulus)
    s.create_trials()
    s.run()
