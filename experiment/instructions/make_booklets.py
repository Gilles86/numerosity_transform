"""Participant booklets (md, docx via pandoc) for all five versions: dot clouds (linear, concave, convex) and Arabic
numerals (concave, convex). Payment numbers come from settings/default.yml; the screenshots from make_screenshots.py.
Run with the experiment environment:
    cd experiment && uv run python instructions/make_screenshots.py && uv run python instructions/make_booklets.py"""
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from common import get_numeral_value, get_value, load_settings

S = load_settings()
M, N = S['main_task'], S['numeral']
LO, HI = S['slider']['range']
N_TRIALS = M['n_runs'] * M['n_repeats'] * 23
FRACTION = round(M['reward_scaling'] / N_TRIALS)  # bonus = mean trial outcome / FRACTION
assert FRACTION * N_TRIALS == M['reward_scaling']
SCREENS = HERE / 'screens'
D, DT = S['durations'], S['durations_training']
EXAMPLE = {'dots': 30, 'numeral': 18.18}

DOTS_SHAPE = {
    'linear': 'The relationship is linear: the value of a dot cloud (in CHF) is simply equal to its number of dots. Each '
              'additional dot adds the same amount of money, wherever you are on the scale. For example, a cloud with 21 '
              'dots is worth 21 CHF and a cloud with 41 dots is worth 41 CHF.',
    'concave': 'The relationship between the number of dots and the value is not linear: the value rises steeply for '
               'small numbers of dots and then flattens out for large numbers of dots. For example, going from 1 to 8 dots '
               'increases the value by 17 CHF (from 1 to 18 CHF), whereas going from 39 to 46 dots increases the value by '
               'only 2 CHF (from 47 to 49 CHF).',
    'convex': 'The relationship between the number of dots and the value is not linear: the value rises only slowly for '
              'small numbers of dots and then increases steeply for large numbers of dots. For example, going from 1 to 8 '
              'dots increases the value by only 1.5 CHF (from 1 to 2.5 CHF), whereas going from 39 to 46 dots increases '
              'the value by 14 CHF (from 25.5 to 39.5 CHF).'}


def value(stimulus, x, mapping):
    return get_numeral_value(x, mapping, S) if stimulus == 'numeral' else get_value(x, mapping, S)


def numeral_shape(mapping):
    a0, a1, b0, b1 = (value('numeral', x, mapping) for x in (1, 13, 30, 42))
    if mapping == 'concave':
        rise, first, second = 'rises steeply for small numbers and then flattens out for large numbers', '', 'only '
    else:
        rise, first, second = 'rises only slowly for small numbers and then increases steeply for large numbers', 'only ', ''
    return (f'The relationship between the number and its value is not linear: the value {rise}. For example, going '
            f'from 1 to 13 increases the value by {first}{a1 - a0:.2f} CHF (from {a0:.2f} to {a1:.2f} CHF), whereas going '
            f'from 30 to 42 increases the value by {second}{b1 - b0:.2f} CHF (from {b0:.2f} to {b1:.2f} CHF).')


def expected_bonus(stimulus, mapping):
    """Bonus per session for truthful bids: (budget + E[value - price | price < value] P(price < value)) / FRACTION,
    with the price uniform between LO and HI."""
    xs = np.linspace(*N['range'], 10001) if stimulus == 'numeral' else np.arange(LO, HI + 1)
    v = np.array([value(stimulus, x, mapping) for x in xs])
    return (HI + np.mean((v - LO) ** 2) / (2 * (HI - LO))) / FRACTION


def strip(path, panels):
    """A row of screenshots with arrows between them and a caption (what + how long) under each."""
    fig, axes = plt.subplots(2, 3, figsize=(6.5, 4.0))
    for i, (ax, (name, caption)) in enumerate(zip(axes.flat, panels)):
        img = Image.open(SCREENS / f'{name}.png')
        w, h = img.size
        ax.imshow(img.crop((int(.18 * w), 0, int(.82 * w), h)))  # the screens are mostly empty at the sides
        ax.set_xticks([]), ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color('black')
        ax.set_xlabel(f'{i + 1}. {caption}', fontsize=8.5, linespacing=1.3)
        if i % 3:
            ax.annotate('', xy=(-.01, .5), xytext=(-.13, .5), xycoords='axes fraction',
                        arrowprops=dict(arrowstyle='-|>', color='black', lw=1.2))
    fig.subplots_adjust(left=.01, right=.99, top=.99, bottom=.11, wspace=.18, hspace=.42)
    fig.savefig(path, dpi=200)
    plt.close(fig)


def single(path, name):
    Image.open(SCREENS / f'{name}.png').save(path)


def mapping_plot(path, stimulus, mapping):
    fig, ax = plt.subplots(figsize=(5, 3.6))
    if stimulus == 'numeral':
        x = np.linspace(*N['range'], 501)
        ax.plot(x, [value(stimulus, i, mapping) for i in x], color='#1f77b4')
        xlabel = 'Number'
    else:
        x = np.arange(LO, HI + 1)
        ax.plot(x, [value(stimulus, i, mapping) for i in x], 'o-', color='#1f77b4', ms=2.5, lw=1)
        xlabel = 'Number of dots'
    ax.set(xlabel=xlabel, ylabel='Value (CHF)', xlim=(-1, 52), ylim=(-1, 52), xticks=[1, 10, 20, 30, 40, 50],
           yticks=[1, 10, 20, 30, 40, 50], title=f'{mapping.capitalize()} mapping')
    ax.grid(alpha=.3)
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def figures(stimulus, mapping):
    key = f'{stimulus}_{mapping}'
    fig = {k: f'fig_{key}_{k}.png' for k in ('examples', 'mapping', 'training', 'auction', 'summary')}
    single(HERE / fig['examples'], f'{key}_examples')
    single(HERE / fig['summary'], f'{key}_run_summary')
    mapping_plot(HERE / fig['mapping'], stimulus, mapping)
    thing = 'Number' if stimulus == 'numeral' else 'Dot cloud'
    fix = [(f'{key}_fixation_green', f'Get ready\n(green cross, {DT["green_fixation"]:g} s)'),
           (f'{key}_fixation_white', f'Fixation\n({DT["white_fixation"]:g} s)')]
    strip(HERE / fig['training'], fix + [
        (f'{key}_stimulus', f'{thing}\n({DT["stimulus"]:g} s)'),
        (f'{key}_training_response', f'Type the value,\npress ENTER (max. {DT["response"]:g} s)'),
        (f'{key}_training_feedback_wrong', f'Feedback ({DT["feedback"]:g} s):\ncorrect value in red'),
        (f'{key}_training_feedback_right', f'... or in green\nif you were right')])
    strip(HERE / fig['auction'], fix + [
        (f'{key}_stimulus', f'{thing}\n({D["stimulus"]:g} s)'),
        (f'{key}_fixation_white', f'Short pause\n({min(D["isis"]):g}-{max(D["isis"]):g} s)'),
        (f'{key}_auction_response', f'Type your bid,\npress ENTER (max. {D["response"]:g} s)'),
        (f'{key}_auction_confirmed', f'Your bid in yellow\n({D["feedback"]:g} s, no feedback)')])
    return fig


def booklet(stimulus, mapping):
    numeral = stimulus == 'numeral'
    fig = figures(stimulus, mapping)
    x = EXAMPLE[stimulus]
    v = value(stimulus, x, mapping)
    bonus = expected_bonus(stimulus, mapping)
    per_session = M['show_up_fee'] + bonus
    total = M['n_sessions'] * per_session + M['completion_bonus']
    fee, n_ses, cb = M['show_up_fee'], M['n_sessions'], M['completion_bonus']
    if numeral:
        thing, things, Thing = 'number', 'numbers', 'Number'
        intro = (f'Your task is to learn the relation between a number and its monetary value. Each number between {LO} and '
                 f'{HI} has a specific monetary value assigned to it (like a bank note). The numbers are shown with two '
                 f'decimals, for example {x:.2f}.')
        note = ('**Note:** new numbers keep appearing, so you cannot memorize a list. Learn how the value changes with the '
                'number.')
        examples = f'{N["n_examples"]} numbers, spread evenly between {LO} and {HI},'
        ex_caption = f'one number ({x:.2f}) together with its value ({v:.2f} CHF)'
        shape = numeral_shape(mapping)
        typing = 'up to two decimals, for example 23.45'
        correct = (f'If your answer is within {N["feedback_tolerance"]:.2f} CHF of the true value, the correct value is shown '
                   'in green; if it is further away, it is shown in red.')
        rounds = (f'The numbers are drawn at random, evenly spread between {LO} and {HI}, so most numbers you see will be '
                  'new.')
    else:
        thing, things, Thing = 'dot cloud', 'dot clouds', 'Dot cloud'
        intro = ('Your task is to learn the relation between the number of dots in a cloud of dots and its monetary value. '
                 'Each dot cloud has a specific monetary value assigned to it according to its number of dots (like a bank '
                 'note). A cloud can have any number of dots from 1 to 50.')
        note = ('**Note:** you will not have time to count the dots one by one. Use your impression of how many dots there '
                'are. The dots are placed at new random positions every time, so learn how the value changes with the '
                'number of dots rather than memorizing particular clouds.')
        examples = f'{S["numerosity"]["n_examples"]} dot clouds, spread evenly between 1 and 50 dots,'
        ex_caption = f'one dot cloud ({x} dots) together with its value ({v:g} CHF)'
        shape = DOTS_SHAPE[mapping]
        typing = 'in steps of 0.5, for example 23.5'
        correct = ('If your answer is exactly right, the correct value is shown in green; otherwise it is shown in red.')
        rounds = ('The numbers of dots are drawn at random, evenly spread between 1 and 50, so you will also see numbers '
                  'of dots that were not among the examples in Phase 1.')

    return f"""# Instructions ({'numbers' if numeral else 'dot clouds'}, {mapping.upper()} mapping)

Welcome to this study, and thank you for participating!

Please read the following pages carefully. They explain the task and how you will be paid.

## Overview

The study consists of **{n_ses} sessions of about one hour each**, on separate days. **In every session you learn a new
relationship between {'numbers' if numeral else 'dot clouds'} and money**, so you will get a new booklet each time. Every
session follows the same three phases:

1. **Learn** (Phase 1): you look at {examples} together with their monetary values, at your own pace.
2. **Practice with feedback** (Phase 2): you see a {thing}, type its value, and are shown the correct value.
3. **Auction** (Phase 3): you see a {thing} and bid for it in an auction. There is no feedback. **This phase determines
   your bonus.**

{intro} {note}

## Payment

| | |
|---|---|
| Show-up fee | **{fee:g} CHF per session** |
| Auction bonus (Phase 3) | between 10 and 20 CHF per session, on average about **{bonus:.0f} CHF** if you bid well |
| Completion bonus | **{cb:g} CHF** after you have completed all {n_ses} sessions |
| **Total (typical)** | **about {total:.0f} CHF** for all {n_ses} sessions |

You are paid at the end of each session; the completion bonus is paid at the end of session {n_ses}. How the auction
bonus is computed is explained under Phase 3. In short: the better you know the value of each {thing}, and the more
consistently you bid that value, the more you earn.

Before you start, the experimenter will ask you a few questions to make sure you understand the task and the payment.

## Phase 1: learn the values

**You are shown {examples} together with their monetary values (Figure 1).** Press the RIGHT ARROW to see the next
{thing} and the LEFT ARROW to go back. Take as long as you like. Once you have seen all of them, press the SPACE BAR to
continue.

![]({fig['examples']}){{width=3.5in}}

*Figure 1: Phase 1 screen, showing {ex_caption}. The text at the bottom counts how many you have seen.*

The values range from {LO} to {HI} CHF. Figure 2 shows exactly how the value depends on the {'number' if numeral else
'number of dots'}. {shape} This is the relationship you need to learn.

![]({fig['mapping']}){{width=4in}}

*Figure 2: The value of each {thing} ({mapping.upper()} mapping). Each session has a different relationship; this booklet is for today's.*

## Phase 2: practice with feedback

**You see a {thing} and type its value.** Each round runs as in Figure 3:

![]({fig['training']}){{width=6.5in}}

*Figure 3: One round of Phase 2.*

1. A green cross tells you that a new round starts; it turns white.
2. The {thing} appears in the centre and stays on the screen.
3. After {DT['stimulus']:g} second a box appears below it. Type the value ({typing}) and **press ENTER**. You can correct
   typing errors with BACKSPACE. Only values between {LO} and {HI} are accepted. You have {DT['response']:g} seconds.
4. Your answer turns yellow and the correct value appears above the {thing}. {correct} If you do not press ENTER in time,
   you see "Too late!".

For every {thing}, ask yourself: **what is this {thing} worth? How much money would I get if I sold it?**

There are {S['training']['n_repeats'] * 23} rounds in {S['training']['n_blocks']} blocks, with a short break between
blocks. {rounds} Phase 2 itself is not paid, but it is your chance to learn the values precisely: **the better you learn
them here, the more you will earn in Phase 3.**

## Phase 3: the auction

**You see a {thing} and bid for it.** Each round runs as in Figure 4:

![]({fig['auction']}){{width=6.5in}}

*Figure 4: One round of Phase 3.*

The differences from Phase 2 are: the {thing} disappears before you answer, you have only **{D['response']:g} seconds**,
and **there is no feedback**. Type your bid and **press ENTER**. **If you do not press ENTER in time, your bid is not
registered and you earn nothing in that round** (not even the budget explained below).

Phase 3 has {M['n_runs']} runs of {M['n_repeats'] * 23} rounds. After each run you see what you earned so far (Figure 5).

![]({fig['summary']}){{width=3in}}

*Figure 5: The screen at the end of each run (example amounts).*

### How the auction works

Every round works the same way:

1. You get a **budget of {HI} CHF** for this round.
2. You **bid**: the most you would pay for the {thing}.
3. The computer draws a **random price** between {LO} and {HI} CHF. Every price is equally likely, and your bid does
   not influence it.
4. If your bid is **higher than the price**, you buy the {thing}: you pay the price and receive its true value.
   Otherwise you buy nothing and keep the {HI} CHF.

| Example: the {thing} is worth 30 CHF and you bid 30 | Your result for this round |
|---|---|
| The price is 12: you buy | {HI} − 12 + 30 = **{HI - 12 + 30} CHF** |
| The price is 40: you do not buy | **{HI} CHF** |

**Your bonus.** The round results are not paid out one by one. At the end of the session we take your **average
result over all {N_TRIALS} rounds** and pay you **one fifth of it**: an average of 60 CHF, for example, gives a bonus of
12 CHF. A round gives between {HI} and almost {2 * HI} CHF, so the bonus is between 10 and 20 CHF; with good bids it is
about {bonus:.0f} CHF. A round without a bid (no ENTER in time) counts as 0 CHF.

### Why you should always bid the true value

You might think it is better to bid less than the {thing} is worth. **This is incorrect.** The price you pay is the
random price, not your bid. Your bid only decides *whether* you buy.

For example, suppose the {thing} is worth 20 CHF:

- If you **bid 20**, you buy whenever the random price is below 20, so you always pay less than it is worth and make a
  profit.
- If you **bid less, say 5**, you still pay the same random price when you buy, but you miss all the chances to buy it
  at a price between 5 and 20. You lose profit.
- If you **bid more, say 35**, you also buy when the random price is between 20 and 35. Then you pay more than the
  {thing} is worth and lose money.

So there is no way to game the auction. **The best you can do in every round is to bid what you believe the {thing} is
truly worth.** When you buy, you pay on average about half of the value.

### In short

1. You bid on {N_TRIALS} {things} per session ({M['n_runs']} runs of {M['n_repeats'] * 23}).
2. Treat every bid as if it were the only one.
3. Always bid the value you believe is correct, and press ENTER within {D['response']:g} seconds.
4. Your bonus is one fifth of your average round result (an average of 60 CHF gives 12 CHF): between 10 and 20 CHF,
   about {bonus:.0f} CHF with good bids.
5. Together with the show-up fee of {fee:g} CHF, you earn about {per_session:.0f} CHF per session, plus {cb:g} CHF after
   the last session.

Thank you again for participating!
"""


if __name__ == '__main__':
    for stimulus, mappings in [('dots', ['linear', 'concave', 'convex']), ('numeral', ['concave', 'convex'])]:
        for mapping in mappings:
            md = HERE / f'instructions_{"numeral_" if stimulus == "numeral" else ""}{mapping}.md'
            md.write_text(booklet(stimulus, mapping))
            subprocess.run(['pandoc', md.name, '-o', md.with_suffix('.docx').name], cwd=HERE, check=True)
            print(md, f'bonus {expected_bonus(stimulus, mapping):.2f} CHF/session')
