"""Numeral-version booklets (md, docx via pandoc) and their figures, one per mapping. The auction explanation is reused
from the dots booklet; everything that differs is written out here. Run with the experiment environment:
    cd experiment && uv run python instructions/make_numeral_booklets.py"""
import re
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
from common import get_numeral_value, load_settings

S = load_settings()
EXAMPLE, WRONG = 36.36, 3.5
FIGSIZE = (4.8, 3.2)


def value(x, mapping):
    return get_numeral_value(x, mapping, S)


def screen(path, numeral=None, top=None, top_color='#00ff00', box=None, box_y=-.42, bottom=None):
    """Sketch of a task screen, in the colours of the experiment."""
    fig, ax = plt.subplots(figsize=FIGSIZE, facecolor='#808080')
    ax.set(xlim=(-1, 1), ylim=(-1, 1))
    ax.axis('off')
    if numeral:
        ax.text(0, 0, numeral, color='white', fontsize=20, ha='center', va='center')
    if top:
        ax.text(0, .55, top, color=top_color, fontsize=14, ha='center', va='center')
    if box:
        ax.text(0, box_y, box, color='#ffff00', fontsize=14, ha='center', va='center',
                bbox=dict(facecolor='none', edgecolor='white', boxstyle='square,pad=.5'))
    if bottom:
        ax.text(0, -.6, bottom, color='white', fontsize=9, ha='center', va='center')
    fig.savefig(path, dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)


def figures(mapping):
    v = value(EXAMPLE, mapping)
    screen(HERE / f'numeral_examples_{mapping}.png', f'{EXAMPLE:.2f}', f'Value: {v:.2f} CHF',
           bottom='Left/right arrow: change number.')
    screen(HERE / f'numeral_training_{mapping}.png', f'{EXAMPLE:.2f}', f'{v:.2f}', '#ff0000', f'{WRONG:.2f}')
    screen(HERE / f'numeral_auction_{mapping}.png', box=f'{v - 1.24:.2f}', box_y=0,
           bottom='Type a value (6-50) and press ENTER')
    x = np.linspace(0, 100, 501)
    fig, ax = plt.subplots(figsize=(5, 3.6))
    ax.plot(x, [value(i, mapping) for i in x], color='#1f77b4')
    ax.set(xlabel='Number', ylabel='Value (CHF)', xlim=(-2, 102), ylim=(4, 52), xticks=range(0, 101, 20),
           yticks=range(10, 51, 10), title=f'{mapping.capitalize()} mapping')
    ax.spines[['top', 'right']].set_visible(False)
    fig.tight_layout()
    fig.savefig(HERE / f'mapping_numeral_{mapping}.png', dpi=200)
    plt.close(fig)


def shape_text(mapping):
    a0, a1, b0, b1 = (value(x, mapping) for x in (0, 25, 60, 85))
    rise, more = ('rises steeply for small numbers and then flattens out for large numbers', 'only ') if mapping == 'concave' \
        else ('rises only slowly for small numbers and then increases steeply for large numbers', '')
    first = '' if mapping == 'concave' else 'only '
    return (f'As you can see, the relationship between the number and its value is not linear: the value {rise}. For '
            f'example, going from 0 to 25 increases the value by {first}{a1 - a0:.2f} CHF (from {a0:.2f} to {a1:.2f} CHF), '
            f'whereas going from 60 to 85 increases the value by {more}{b1 - b0:.2f} CHF (from {b0:.2f} to {b1:.2f} CHF). '
            'So, this is what you are supposed to learn.')


def auction_explanation():
    """The dots booklet from the rule of the auction onwards, with numbers as the goods."""
    text = (HERE / 'instructions_concave.md').read_text()
    text = text[text.index('In every auction there is a rule'):]
    text = re.sub(r'dot\s+clouds', 'numbers', re.sub(r'dot\s+cloud', 'number', text))
    text = re.sub(r'bid\s+the\s+number\s+closest', 'bid the amount closest', text)  # 'number' is now the good being sold
    assert not re.search(r'\bdots?\b', text)
    return re.sub(r'6\.  Your average payout.*', '', text).rstrip()


def booklet(mapping):
    v = value(EXAMPLE, mapping)
    grid = np.linspace(0, 100, 10001)
    values = np.array([value(x, mapping) for x in grid])
    lo, hi = S['slider']['range']
    payout = round(hi + np.mean((values - lo) ** 2) / (2 * (hi - lo)))  # budget + expected BDM profit for true bids
    return f"""# Instructions (numbers, mapping {mapping.upper()})

Welcome to this study! And thank you for participating.

Please carefully read the material on the following pages to understand:

- The task you will complete today.

- The rules of how you will be paid out.

Your task today will be to learn the relation between a number and its monetary value. Each number between 0 and 100 has
a specific monetary value assigned to it (like a bank note). The numbers are shown with two decimals, for example
{EXAMPLE:.2f}. To learn the relation, you will first be shown 23 numbers spread evenly between 0 and 100, together with
their corresponding monetary value (Phase 1). After that you will be shown a random number and you need to input the
monetary amount that matches its value. You will get feedback on this (Phase 2). Finally, you will again be shown a
number and can bid money to purchase it. Later, you can sell it for its actual monetary value that you learned in the
previous phase (Phase 3). Since your bid is the maximum price you will have to pay to buy the number (the price is
randomly determined, up to your bid), you are best off to bid the real monetary value of the number. In this phase,
there is no feedback. So, in the end, you will be paid according to how well you learned the relationship between the
numbers and their values, and according to the difference between the random price set by the computer if you won the
bid and the resell value of the numbers you purchased in phase 3.

**Note:** new numbers keep appearing, so you cannot memorize a list. Learn how the value changes with the number. Each
number is shown for 1 second.

By agreeing to participate, you have already earned a show-up fee of **TODO(Gilles)** CHF. It is **very** important that
you understand the following instructions, since the additional payoffs from participating in the experiment will depend
on your ability to make good decisions. Thank you again for participating in this experiment!

## Experiment Description

## [First phase of the experiment]{{.underline}}

**In the first phase of the experiment, you learn the monetary value of the numbers. You are shown 23 numbers together
with their corresponding monetary values (see Figure 1).** You can look at the numbers and their values for as long as
you want. Press the RIGHT ARROW to see the next number and the LEFT ARROW to go back. Once you have seen all 23, press
the SPACE BAR to continue.

![](numeral_examples_{mapping}.png){{width=3in}}

*Figure 1: Example of one number ({EXAMPLE:.2f}) together with its corresponding correct value ({v:.2f} CHF).*

The values of the numbers range between {lo} and {hi} CHF. The value is a function of the number. The exact function is
shown in Figure 2. {shape_text(mapping)}

![](mapping_numeral_{mapping}.png){{width=4.2in}}

*Figure 2: Mapping function from the number to its value ({mapping.upper()} mapping).*

Pay close attention during this phase of the experiment already. You need to learn this exact relationship to earn the
maximum money possible.

## [Second phase of the experiment]{{.underline}}

**In the second phase of the experiment, you will be shown a number and have to input its associated monetary value.**
The number will be shown in the center of your screen for 1 second, after which a response box appears (see Figure 3).

![](numeral_training_{mapping}.png){{width=3in}}

*Figure 3: Example of one training trial with negative feedback, where the actual value is {v:.2f} and the input was
{WRONG:.2f}.*

For each round, your task is to input a monetary value so that it matches the value of the number that you learned in
phase 1. Type the value you believe corresponds to the number (up to two decimals, for example 23.45) and **press ENTER to
confirm**. Only values between {lo} and {hi} are accepted. If your input is within 0.50 CHF of the monetary value of the
number, you will be shown green feedback. If it is further away, you will be shown red feedback. Above the number, you
will be given its actual value. For every number, you should ask yourself: **What is the monetary value of this number?
That is, how much money would I get if I sold this number?** You have 5 seconds to make a guess. In total, you will
complete 138 rounds in this phase of the experiment (6 blocks). The numbers are drawn at random, evenly spread between
0 and 100, so most numbers you see will be new.

Try to predict the monetary value of the numbers in this phase as accurately as possible. **Your payment will depend on
how well you have learned this relationship.** You will earn more if you are able to guess the associated value of the
number with the **least possible difference to the true value in each guess**.

**Note:** You will have the opportunity to take short breaks between blocks. Use this time to rest if needed, but
remember that your performance -- and thus your earnings -- will depend on your focus and accuracy.

## [Third and final phase of the experiment]{{.underline}}

**In the third and final phase of the experiment, you have to input the monetary value of a presented number as a BID in
an AUCTION (see Figure 4).** The difference to the previous phase is that you will not receive feedback and that you only
have a very limited amount of time to input a value (4 seconds). The value of the number is exactly what you learnt in
the first two phases of the experiment.

Your budget for each trial is {hi} CHF. You will keep the rest of the budget after paying the price of the number if you
win the bidding. The numbers you bought will be exchanged for money at the end of the experiment, and you will get 1/184
of the money you win here as extra payment. As you will see in a moment, your best strategy is to bid your true value for
the number.

![](numeral_auction_{mapping}.png){{width=3in}}

*Figure 4: Example of the response screen of one phase 3 trial (final phase). The number has disappeared, and you input
its value without feedback.*

You can submit your value by confirming your response (**press ENTER**). **If you do not confirm, your input will not be
registered and you will not get any payout for this trial!** You only have a limited time of 4 seconds to input your
value. To maximize your payment, you should always make a choice within the given timeframe.

{auction_explanation()}

6.  Your average payout in the task will be around {payout} CHF (on top of the show-up fee).
"""


for mapping in ('concave', 'convex'):
    figures(mapping)
    md = HERE / f'instructions_numeral_{mapping}.md'
    md.write_text(booklet(mapping))
    subprocess.run(['pandoc', md.name, '-o', md.with_suffix('.docx').name], cwd=HERE, check=True)
