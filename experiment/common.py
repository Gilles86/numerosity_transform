import numpy as np
import tempfile
import yaml
from pathlib import Path
from exptools2.core import Session, Trial
from exptools2.core.session import _merge_settings
from psychopy import event
from psychopy.visual import Circle, Line, Rect, TextStim

HERE = Path(__file__).parent
GREEN, RED, WHITE, YELLOW = (-1, 1, -1), (1, -1, -1), (1, 1, 1), (1, 1, -1)


def get_log_root(stimulus):
    """Numerals log to their own tree, so the dot-cloud analyses (which glob logs/sub-*) never pick them up."""
    return HERE / 'logs' / 'numerals' if stimulus == 'numeral' else HERE / 'logs'


def load_settings(name='default'):
    """settings/default.yml with settings/<name>.yml merged on top (exptools2 itself only merges onto its own defaults)."""
    settings = yaml.safe_load((HERE / 'settings' / 'default.yml').read_text())
    if name != 'default':
        _merge_settings(settings, yaml.safe_load((HERE / 'settings' / f'{name}.yml').read_text()))
    return settings


def mapping_curve(x, mapping, k):
    """[0, 1] -> [0, 1]. Linear; concave (1 - exp(-kx)) / (1 - exp(-k)); convex is concave mirrored in both axes."""
    concave = lambda x: (1 - np.exp(-k * x)) / (1 - np.exp(-k))
    return {'linear': x, 'concave': concave(x), 'convex': 1 - concave(1 - x)}[mapping]


def get_value(numerosity, mapping, settings):
    """Value of a number of dots, rounded to numerosity.value_precision (0.5 CHF). 1 dot is worth 1 CHF, 50 dots 50 CHF."""
    n = settings['numerosity']
    (lo, hi), step = n['range'], n['value_precision']
    v = lo + (hi - lo) * mapping_curve((numerosity - lo) / (hi - lo), mapping, settings['numeral']['curvature'])
    return float(round(v / step) * step)


def get_numeral_value(number, mapping, settings):
    """Value of a numeral: the same curve as the numerosities, unrounded apart from numeral.decimals."""
    n = settings['numeral']
    lo, hi = n['range']
    return round(float(lo + (hi - lo) * mapping_curve((number - lo) / (hi - lo), mapping, n['curvature'])), n['decimals'])


def sample_dot_positions(n, aperture_radius, dot_radius, min_ecc=0., max_tries=10000):
    """Rejection-sample n dots, uniform over the annulus min_ecc-aperture_radius (keeps the fixation cross free),
    no two closer than 2.2 dot radii."""
    xys = []
    r0, r1 = min_ecc + dot_radius, aperture_radius - dot_radius
    for _ in range(max_tries):
        r = np.sqrt(r0 ** 2 + np.random.rand() * (r1 ** 2 - r0 ** 2))
        xy = r * np.array([np.cos(a := np.random.rand() * 2 * np.pi), np.sin(a)])
        if all(np.hypot(*(xy - p)) > 2.2 * dot_radius for p in xys):
            xys.append(xy)
        if len(xys) == n:
            return np.array(xys)
    raise RuntimeError(f'Could not fit {n} dots in aperture')


class DotCloud:
    def __init__(self, win, n, aperture_radius, dot_radius, min_ecc=0.):
        self.dot = Circle(win, radius=dot_radius, edges=64, fillColor=WHITE, lineColor=None)
        self.xys = sample_dot_positions(n, aperture_radius, dot_radius, min_ecc)  # fresh on every presentation

    def draw(self):
        for xy in self.xys:
            self.dot.pos = xy
            self.dot.draw()


class NumeralStim:
    """An Arabic numeral with a fixed number of decimals, at the centre of the screen (same interface as DotCloud)."""

    def __init__(self, win, number, decimals, text_height):
        self.text = TextStim(win, f'{number:.{decimals}f}', height=text_height, color=WHITE)

    def draw(self):
        self.text.draw()


class FixationCross:
    def __init__(self, win, size=0.5, color=WHITE, line_width=5):
        self.lines = [Line(win, start=s, end=e, lineWidth=line_width, lineColor=color)
                      for s, e in [((0, -size / 2), (0, size / 2)), ((-size / 2, 0), (size / 2, 0))]]

    def set_color(self, color):
        for line in self.lines:
            line.lineColor = color

    def draw(self):
        for line in self.lines:
            line.draw()


class ResponseSlider:
    """Horizontal bar; the marker follows the mouse x position (snapped to `precision`)."""

    def __init__(self, win, pos, length, height, range, precision, text_height):
        self.range, self.precision, self.length, self.x0 = range, precision, length, pos[0]
        self.decimals = max(1, -int(np.floor(np.log10(precision))))
        self.bar = Rect(win, width=length, height=height, pos=pos, lineColor=(-1, -1, -1), fillColor=(.5, .5, .5))
        self.marker = Rect(win, width=height * .5, height=height * 1.5, pos=pos, lineColor=(-1, -1, -1), fillColor=(.25, .25, .25))
        self.number = TextStim(win, pos=(pos[0], pos[1] - height * 1.5), height=text_height)
        self.show_marker, self.value = False, None

    def reset(self, mouse):
        self.show_marker, self.mouse_x0 = False, mouse.getPos()[0]

    def update(self, events, mouse):
        """Marker follows the mouse once it has moved; a click confirms. Returns the confirmed value (or None)."""
        if mouse.getPos()[0] != self.mouse_x0:
            self.set_from_mouse(mouse.getPos()[0])
        if self.show_marker and mouse.getPressed()[0]:
            return self.value

    def set_from_mouse(self, x):
        frac = np.clip((x - self.x0) / self.length + .5, 0, 1)
        self.value = round(round((self.range[0] + frac * (self.range[1] - self.range[0])) / self.precision) * self.precision, self.decimals)
        self.marker.pos = (self.x0 + ((self.value - self.range[0]) / (self.range[1] - self.range[0]) - .5) * self.length, self.bar.pos[1])
        self.number.text = f'{self.value:.{self.decimals}f}'
        self.show_marker = True

    def draw(self, color=(.25, .25, .25)):
        self.bar.draw()
        if self.show_marker:
            self.marker.fillColor = color
            self.marker.draw()
            self.number.draw()


class TypedResponse:
    """Box in which a number is typed; ENTER confirms (only values within `range`)."""

    def __init__(self, win, pos, range, text_height, precision=.5, **kwargs):
        self.range = range
        self.decimals = max(1, -int(np.floor(np.log10(precision))))  # .5 -> 1 (type 23.5), .01 -> 2 (type 23.45)
        self.box = Rect(win, width=text_height * 6, height=text_height * 2.5, pos=pos, lineColor=WHITE, fillColor=None)
        self.text = TextStim(win, pos=pos, height=text_height * 1.5)
        self.hint = TextStim(win, f'Type a value ({range[0]}-{range[1]}) and press ENTER', pos=(pos[0], pos[1] - text_height * 2.5),
                             height=text_height * .8)
        self.typed, self.value = '', None

    def reset(self, mouse):
        self.typed = ''

    def update(self, events, mouse):
        for key, t in events:
            key = key.removeprefix('num_')
            whole, point, decimals = self.typed.partition('.')
            if key.isdigit() and (len(decimals) < self.decimals if point else len(whole) < 3):
                self.typed += key
            elif key in ('period', 'comma', 'decimal') and '.' not in self.typed:
                self.typed += '.'
            elif key == 'backspace':
                self.typed = self.typed[:-1]
            elif key in ('return', 'enter') and self.typed.strip('.'):
                if self.range[0] <= float(self.typed) <= self.range[1]:
                    self.value = float(self.typed)
                    return self.value

    def draw(self, color=WHITE):
        self.box.draw()
        self.text.text, self.text.color = self.typed, color
        self.text.draw()
        if color == WHITE:
            self.hint.draw()


class InstructionTrial(Trial):
    """Text screen; advances on space (or a mouse click)."""

    def __init__(self, session, trial_nr, txt, bottom_txt='Press SPACE BAR to continue.'):
        super().__init__(session, trial_nr, phase_durations=[.5, np.inf], phase_names=['instruction'] * 2)
        v = session.settings['various']
        self.text = TextStim(session.win, txt, height=v['text_height'], wrapWidth=v['text_width'], color=v['text_color'])
        self.bottom = TextStim(session.win, bottom_txt, pos=(0, -6), height=v['text_height'], color=v['text_color'])

    def get_events(self):
        if any(key == 'space' for key, t in super().get_events()) or (self.phase > 0 and self.session.mouse.getPressed()[0]):
            self.stop_phase()

    def draw(self):
        self.text.draw()
        self.bottom.draw()


class BaseSession(Session):
    """Session with the shared stimuli; subclasses add trials."""

    def __init__(self, subject, session, mapping, task, run=None, settings='default', response=None, response_y=0., stimulus='dots'):
        sub = f'sub-{subject.zfill(2)}'
        settings = load_settings(settings)
        if stimulus == 'numeral':
            settings['slider']['precision'] = settings['numeral']['response_precision']
        output_str = f'{sub}_ses-{session}_task-{task}' + (f'_run-{run:02d}' if run else '') + f'.{mapping}'
        settings_file = Path(tempfile.mkstemp(suffix='.yml')[1])
        settings_file.write_text(yaml.safe_dump(settings))
        super().__init__(output_str, output_dir=get_log_root(stimulus) / sub / f'ses-{session}', settings_file=settings_file)
        s = self.settings
        s.update(subject=subject, session=session, mapping=mapping, run=run, response=response or s['response'], stimulus=stimulus)
        self.mouse = event.Mouse(visible=False)
        self.fixation = FixationCross(self.win, **s['fixation_cross'])
        self.too_late = TextStim(self.win, 'Too late!', height=.5, color=RED)
        sl = s['slider']
        self.response = (TypedResponse(self.win, (0, response_y), **sl) if s['response'] == 'typing' else
                         ResponseSlider(self.win, (0, response_y), sl['length'], sl['height'], sl['range'], sl['precision'], sl['text_height']))
        self.instructions = yaml.safe_load((HERE / 'instructions.yml').read_text())
        if stimulus == 'numeral':
            self.instructions.update({k.removesuffix('_numeral'): v for k, v in self.instructions.items() if k.endswith('_numeral')})
        self.instructions['how'] = self.instructions[f'how_{s["response"]}']

    @property
    def is_numeral(self):
        return self.settings['stimulus'] == 'numeral'

    @property
    def levels(self):
        """The stimuli that can be browsed in the examples phase: n_examples evenly spaced numbers of dots or numerals."""
        n = self.settings['numeral' if self.is_numeral else 'numerosity']
        levels = np.linspace(*n['range'], n['n_examples'])
        return levels.round(n['decimals']).tolist() if self.is_numeral else sorted({int(x) for x in np.floor(levels + .5)})

    def sample_stimuli(self, n_repeats):
        """Shuffled stimuli for n_repeats passes over the range. Each pass draws one new stimulus per bin, so the range is
        covered evenly but no stimulus has to come back: numerals uniformly within 23 equal bins (two decimals), numbers
        of dots from 23 near-equal groups of the whole numbers 1-50."""
        if self.is_numeral:
            n = self.settings['numeral']
            edges = np.linspace(*n['range'], n['n_bins'] + 1)
            stimuli = np.random.uniform(np.tile(edges[:-1], n_repeats), np.tile(edges[1:], n_repeats)).round(n['decimals'])
        else:
            n = self.settings['numerosity']
            groups = np.array_split(np.arange(n['range'][0], n['range'][1] + 1), n['n_bins'])
            stimuli = np.array([np.random.choice(g) for _ in range(n_repeats) for g in groups])
        np.random.shuffle(stimuli)
        return stimuli

    def make_stimulus(self, x):
        s = self.settings
        if self.is_numeral:
            return NumeralStim(self.win, x, s['numeral']['decimals'], s['numeral']['text_height'])
        return DotCloud(self.win, x, **s['cloud'])

    def get_value(self, x):
        s = self.settings
        return get_numeral_value(x, s['mapping'], s) if self.is_numeral else get_value(x, s['mapping'], s)

    def run(self):
        self.start_experiment()
        for trial in self.trials:
            trial.run()
        self.close()


class EstimationTrial(Trial):
    """Dot cloud or numeral -> slider or typed response. Training: stimulus stays up and the true value is shown as
    feedback. Task: BDM auction against a random price, no feedback."""

    def __init__(self, session, trial_nr, stimulus, training, isi=0.):
        s = session.settings
        d = s['durations_training' if training else 'durations']
        names = ['green_fixation', 'white_fixation', 'stimulus', 'isi', 'response', 'feedback', 'iti']
        super().__init__(session, trial_nr, [d['green_fixation'], d['white_fixation'], d['stimulus'], isi,
                                             d['response'], d['feedback'], d['iti']], names)
        self.training, self.response = training, session.response
        self.stimulus = session.make_stimulus(stimulus)
        self.parameters.update({'number' if session.is_numeral else 'numerosity': stimulus}, stimulus=s['stimulus'],
                               value=session.get_value(stimulus), mapping=s['mapping'],
                               response_mode=s['response'], response=np.nan, response_time=np.nan, reward=0.)
        self.feedback = TextStim(session.win, f'{self.parameters["value"]:.{session.response.decimals}f}', pos=(0, 1.2 * s['cloud']['aperture_radius'] + .5),
                                 height=.75, color=GREEN)
        self.responded = False

    def draw(self):
        phase, fix = self.phase_names[self.phase], self.session.fixation
        if phase == 'response' and not hasattr(self, 't0'):  # response phase just started: clear the previous
            self.t0 = self.session.clock.getTime()           # answer here, as exptools2 draws before get_events
            self.response.reset(self.session.mouse)
        show_stimulus = phase == 'stimulus' or (self.training and phase in ('response', 'feedback'))
        fix.set_color(GREEN if phase == 'green_fixation' else WHITE)
        if show_stimulus:
            self.stimulus.draw()
        if phase in ('response', 'feedback'):
            if phase == 'feedback' and not self.responded:
                self.session.too_late.draw()
            else:
                self.response.draw(YELLOW) if phase == 'feedback' else self.response.draw()
            if phase == 'feedback' and self.training:
                self.feedback.draw()
        if phase in ('green_fixation', 'white_fixation', 'isi') or (phase == 'stimulus' and not self.session.is_numeral):
            fix.draw()  # a numeral appears on the fixation cross and replaces it; dots leave it free

    def get_events(self):
        events = super().get_events()
        if self.phase_names[self.phase] != 'response' or self.responded:
            return
        value = self.response.update(events, self.session.mouse)
        if value is not None:
            self.responded = True
            self.parameters['response'] = value
            self.parameters['response_time'] = self.session.clock.getTime() - self.t0
            if self.training:
                # Numerals have 2-decimal values, so an exact hit would be luck: green within a tolerance
                tolerance = self.session.settings['numeral']['feedback_tolerance'] if self.session.is_numeral else 0.
                self.feedback.color = GREEN if abs(value - self.parameters['value']) <= tolerance else RED
            else:
                self.parameters['price'], self.parameters['reward'] = self.session.auction(value, self.parameters['value'])
            self.stop_phase()
