"""Screenshots of the real task screens for the booklets, drawn with the experiment's own stimulus classes and settings.
Opens a window for a few seconds. Run with the experiment environment:
    cd experiment && uv run python instructions/make_screenshots.py
Writes instructions/screens/<stimulus>_<mapping>_<screen>.png."""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from psychopy import monitors, visual

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from common import (GREEN, RED, WHITE, YELLOW, DotCloud, FixationCross, NumeralStim, TextStim, TypedResponse,
                    get_numeral_value, get_value, load_settings)

OUT = HERE / 'screens'
OUT.mkdir(exist_ok=True)
S = load_settings()
SIZE = S['window']['size']
mon = monitors.Monitor('booklet', width=S['monitor']['width'], distance=S['monitor']['distance'])
mon.setSizePix(SIZE)
win = visual.Window(SIZE, units='deg', monitor=mon, color=S['window']['color'], fullscr=False, allowGUI=False)
CROP_DEG = (9, 5.5, 6)  # half width, top, bottom (deg) kept around the screen centre

# Example stimuli: one number of dots / one numeral per booklet, and a wrong training answer
EXAMPLE = {'dots': 30, 'numeral': 18.18}
WRONG = {'dots': '3.5', 'numeral': '3.50'}
BID_OFFSET = -1.5  # the bid shown in the auction screenshot is a little below the true value


def deg2px(deg):
    return deg * SIZE[0] / (2 * np.degrees(np.arctan(S['monitor']['width'] / 2 / S['monitor']['distance'])))


def save(name, *stims):
    for s in stims:
        s.draw()
    win.getMovieFrame(buffer='back')
    img = win.movieFrames.pop()
    win.clearBuffer()
    scale = img.size[0] / SIZE[0]  # retina framebuffers are 2x
    cx, cy = img.size[0] / 2, img.size[1] / 2
    hw, top, bottom = (deg2px(d) * scale for d in CROP_DEG)
    img.crop((int(cx - hw), int(cy - top), int(cx + hw), int(cy + bottom))).save(OUT / f'{name}.png')


class Draw:
    """Wraps a few stimuli into one drawable."""

    def __init__(self, *stims):
        self.stims = stims

    def draw(self):
        for s in self.stims:
            s.draw()


def response_box(y, typed, color=WHITE, precision=.5):
    sl = S['slider']
    box = TypedResponse(win, (0, y), sl['range'], sl['text_height'], precision)
    box.typed = typed
    return Draw(type('B', (), {'draw': lambda self: box.draw(color)})())


def screens(stimulus, mapping):
    np.random.seed(1)
    numeral = stimulus == 'numeral'
    x = EXAMPLE[stimulus]
    precision = S['numeral']['response_precision'] if numeral else S['slider']['precision']
    value = get_numeral_value(x, mapping, S) if numeral else get_value(x, mapping, S)
    fmt = (lambda v: f'{v:.2f}') if numeral else (lambda v: f'{v:.1f}')
    stim = NumeralStim(win, x, S['numeral']['decimals'], S['numeral']['text_height']) if numeral else DotCloud(win, x, **S['cloud'])
    fix, fix_green = FixationCross(win, **S['fixation_cross']), FixationCross(win, **S['fixation_cross'])
    fix_green.set_color(GREEN)
    above = (0, 1.2 * S['cloud']['aperture_radius'] + .5)
    name = f'{stimulus}_{mapping}_'

    # Phase 1: examples browser
    label = f'Value: {value:.2f} CHF' if numeral else f'{x} dots = {value:.1f} CHF'
    what = 'number' if numeral else 'number of dots'
    bottom = TextStim(win, f'Left/right arrow: change {what}.\nSeen 12 of 25 {what.replace("number", "numbers")}.',
                      height=.6, wrapWidth=30, pos=(0, -1.4 * S['cloud']['aperture_radius']))
    save(name + 'examples', stim, TextStim(win, label, height=1, color=GREEN, pos=above), bottom, *([] if numeral else [fix]))

    # Trial building blocks (fixation, stimulus) are shared by phases 2 and 3
    save(name + 'fixation_green', fix_green)
    save(name + 'fixation_white', fix)
    save(name + 'stimulus', stim, *([] if numeral else [fix]))

    # Phase 2: training. The stimulus stays on screen, the box is below it; feedback shows the true value above it.
    y = -3.8
    save(name + 'training_response', stim, response_box(y, fmt(value + 2), precision=precision))
    save(name + 'training_feedback_wrong', stim, response_box(y, WRONG[stimulus], YELLOW, precision),
         TextStim(win, fmt(value), pos=above, height=.75, color=RED))
    save(name + 'training_feedback_right', stim, response_box(y, fmt(value), YELLOW, precision),
         TextStim(win, fmt(value), pos=above, height=.75, color=GREEN))

    # Phase 3: auction. The stimulus disappears; the box is at the centre; no feedback.
    save(name + 'auction_response', response_box(0, fmt(value + BID_OFFSET), precision=precision))
    save(name + 'auction_confirmed', response_box(0, fmt(value + BID_OFFSET), YELLOW, precision))
    save(name + 'too_late', TextStim(win, 'Too late!', height=.5, color=RED))
    v = S['various']
    save(name + 'run_summary', TextStim(win, 'This run: 11.84 CHF\n\nTotal so far (1/4 runs): 11.84 CHF', height=v['text_height'],
                                        wrapWidth=v['text_width']),
         TextStim(win, 'Press SPACE BAR to continue.', pos=(0, -4.5), height=v['text_height']))


for stimulus, mappings in [('dots', ['linear', 'concave', 'convex']), ('numeral', ['concave', 'convex'])]:
    for mapping in mappings:
        screens(stimulus, mapping)
win.close()
print(f'Wrote {len(list(OUT.glob("*.png")))} screenshots to {OUT}')
