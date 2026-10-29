import numpy as np
import tempfile
import yaml
from functools import cache
from pathlib import Path
from exptools2.core import Session, Trial
from exptools2.core.session import _merge_settings
from psychopy import event
from psychopy.visual import Circle, Line, Rect, TextStim

HERE = Path(__file__).parent
GREEN, RED, WHITE, YELLOW = (-1, 1, -1), (1, -1, -1), (1, 1, 1), (1, 1, -1)


@cache
def get_mappings():
    return yaml.safe_load((HERE / 'settings' / 'default.yml').read_text())['mappings']


def load_settings(name='default'):
    """settings/default.yml with settings/<name>.yml merged on top (exptools2 itself only merges onto its own defaults)."""
    settings = yaml.safe_load((HERE / 'settings' / 'default.yml').read_text())
    if name != 'default':
        _merge_settings(settings, yaml.safe_load((HERE / 'settings' / f'{name}.yml').read_text()))
    return settings


def get_value(numerosity, mapping):
    m = get_mappings()
    return m[mapping][m['numerosities'].index(numerosity)]


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
        self.value = round((self.range[0] + frac * (self.range[1] - self.range[0])) / self.precision) * self.precision
        self.marker.pos = (self.x0 + ((self.value - self.range[0]) / (self.range[1] - self.range[0]) - .5) * self.length, self.bar.pos[1])
        self.number.text = f'{self.value:.1f}'
        self.show_marker = True

    def draw(self, color=(.25, .25, .25)):
        self.bar.draw()
        if self.show_marker:
            self.marker.fillColor = color
            self.marker.draw()
            self.number.draw()


class TypedResponse:
    """Box in which a number is typed; ENTER confirms (only values within `range`)."""

    def __init__(self, win, pos, range, text_height, **kwargs):
        self.range = range
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
            if key.isdigit() and len(self.typed) < 4:
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

    def __init__(self, subject, session, mapping, task, run=None, settings='default', response=None, response_y=0.):
        sub = f'sub-{subject.zfill(2)}'
        output_str = f'{sub}_ses-{session}_task-{task}' + (f'_run-{run:02d}' if run else '') + f'.{mapping}'
        settings_file = Path(tempfile.mkstemp(suffix='.yml')[1])
        settings_file.write_text(yaml.safe_dump(load_settings(settings)))
        super().__init__(output_str, output_dir=HERE / 'logs' / sub / f'ses-{session}', settings_file=settings_file)
        s = self.settings
        s.update(subject=subject, session=session, mapping=mapping, run=run, response=response or s['response'])
        self.mouse = event.Mouse(visible=False)
        self.fixation = FixationCross(self.win, **s['fixation_cross'])
        self.too_late = TextStim(self.win, 'Too late!', height=.5, color=RED)
        sl = s['slider']
        self.response = (TypedResponse(self.win, (0, response_y), **sl) if s['response'] == 'typing' else
                         ResponseSlider(self.win, (0, response_y), sl['length'], sl['height'], sl['range'], sl['precision'], sl['text_height']))
        self.instructions = yaml.safe_load((HERE / 'instructions.yml').read_text())
        self.instructions['how'] = self.instructions[f'how_{s["response"]}']

    def run(self):
        self.start_experiment()
        for trial in self.trials:
            trial.run()
        self.close()


class EstimationTrial(Trial):
    """Dot cloud -> slider or typed response. Training: cloud stays up and the true value is shown as feedback.
    Task: BDM auction against a random price, no feedback."""

    def __init__(self, session, trial_nr, numerosity, training, isi=0.):
        s = session.settings
        d = s['durations_training' if training else 'durations']
        names = ['green_fixation', 'white_fixation', 'stimulus', 'isi', 'response', 'feedback', 'iti']
        super().__init__(session, trial_nr, [d['green_fixation'], d['white_fixation'], d['stimulus'], isi,
                                             d['response'], d['feedback'], d['iti']], names)
        self.training, self.numerosity, self.response = training, numerosity, session.response
        self.cloud = DotCloud(session.win, numerosity, **s['cloud'])
        self.parameters.update(numerosity=numerosity, value=get_value(numerosity, s['mapping']), mapping=s['mapping'],
                               response_mode=s['response'], response=np.nan, response_time=np.nan, reward=0.)
        self.feedback = TextStim(session.win, f'{self.parameters["value"]:.1f}', pos=(0, 1.2 * s['cloud']['aperture_radius'] + .5),
                                 height=.75, color=GREEN)
        self.responded = False

    def draw(self):
        phase, fix = self.phase_names[self.phase], self.session.fixation
        show_cloud = phase == 'stimulus' or (self.training and phase in ('response', 'feedback'))
        fix.set_color(GREEN if phase == 'green_fixation' else WHITE)
        if show_cloud:
            self.cloud.draw()
        if phase in ('response', 'feedback'):
            if phase == 'feedback' and not self.responded:
                self.session.too_late.draw()
            else:
                self.response.draw(YELLOW) if phase == 'feedback' else self.response.draw()
            if phase == 'feedback' and self.training:
                self.feedback.draw()
        if phase in ('green_fixation', 'white_fixation', 'stimulus', 'isi'):
            fix.draw()

    def get_events(self):
        events = super().get_events()
        if self.phase_names[self.phase] != 'response' or self.responded:
            return
        if not hasattr(self, 't0'):  # response phase just started
            self.t0 = self.session.clock.getTime()
            self.response.reset(self.session.mouse)
        value = self.response.update(events, self.session.mouse)
        if value is not None:
            self.responded = True
            self.parameters['response'] = value
            self.parameters['response_time'] = self.session.clock.getTime() - self.t0
            if self.training:
                self.feedback.color = GREEN if value == self.parameters['value'] else RED
            else:
                self.parameters['price'], self.parameters['reward'] = self.session.auction(value, self.parameters['value'])
            self.stop_phase()
