import argparse

# Parse arguments before importing psychopy, which would otherwise hijack --help
p = argparse.ArgumentParser()
p.add_argument('subject')
p.add_argument('session', type=int)
p.add_argument('--mapping', required=True, choices=['linear', 'concave', 'convex'])
p.add_argument('--settings', default='default')
a = p.parse_args()
import numpy as np
from psychopy.visual import TextStim
from exptools2.core import Trial
from common import BaseSession, InstructionTrial, DotCloud, get_value, GREEN


class ExampleSession(BaseSession):
    """Self-paced browser over all numerosities and their values."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, task='examples', **kwargs)
        s = self.settings
        self.numerosities = s['mappings']['numerosities']
        self.idx, self.seen = 0, {0}
        self.cloud = self.new_cloud()
        self.value_text = TextStim(self.win, height=1, color=GREEN, pos=(0, 1.2 * s['cloud']['aperture_radius'] + .5))
        self.bottom = TextStim(self.win, height=.6, wrapWidth=30, pos=(0, -1.4 * s['cloud']['aperture_radius']))

    def new_cloud(self):
        return DotCloud(self.win, self.numerosities[self.idx], **self.settings['cloud'])

    def create_trials(self):
        self.trials = [InstructionTrial(self, 0, self.instructions['phase_1']), ExampleTrial(self, 1)]


class ExampleTrial(Trial):
    def __init__(self, session, trial_nr):
        super().__init__(session, trial_nr, [np.inf], ['examples'])

    def get_events(self):
        s = self.session
        for key, t in super().get_events():
            if key in ('left', 'right'):
                s.idx = int(np.clip(s.idx + (1 if key == 'right' else -1), 0, len(s.numerosities) - 1))
                s.seen.add(s.idx)
                s.cloud = s.new_cloud()
            elif key == 'space' and len(s.seen) == len(s.numerosities):
                self.stop_phase()

    def draw(self):
        s = self.session
        s.value_text.text = f'{s.numerosities[s.idx]} dots = {get_value(s.numerosities[s.idx], s.settings["mapping"]):.1f} CHF'
        s.bottom.text = 'Left/right arrow: change number of dots.' + (
            '\nSPACE BAR: continue.' if len(s.seen) == len(s.numerosities) else
            f'\nSeen {len(s.seen)} of {len(s.numerosities)} numbers of dots.')
        s.cloud.draw()
        s.value_text.draw()
        s.bottom.draw()
        s.fixation.draw()


if __name__ == '__main__':
    s = ExampleSession(a.subject, a.session, a.mapping, settings=a.settings)
    s.create_trials()
    s.run()
