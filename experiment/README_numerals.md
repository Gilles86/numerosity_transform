# Running the Arabic-numeral versions on yourself

This is a guide for Saurabh to run both numeral versions of the task on himself, from installation to sending the data back.

**What you will do.** You learn how numbers between 1.00 and 50.00 translate into a value in CHF (1 is always worth 1 CHF and 50 is always worth 50 CHF), practise this with
feedback, and then bid for the numbers in an auction. You do this twice, each time with a different relationship between number
and value, so it is two sessions:

| Session | Mapping | How the value behaves |
|---|---|---|
| 1 | concave | Rises steeply for small numbers, then flattens out |
| 2 | convex | Rises slowly for small numbers, then rises steeply |

**How long it takes.** Plan about 45 minutes per session. In the pilots of the dot-cloud version (same trial numbers and timing), training took 10-14
minutes and each of the 4 auction runs 3.5-5 minutes, plus the time you spend on learning the values.

**Keep the sessions apart.** Do them on different days if you can, because the second mapping has to replace the first in your head.

## 1. Install (once)

You need a computer with a keyboard, an internet connection for the first run, and `git` and Python 3 (any version). The launcher
installs everything else (`uv`, and then the Python 3.10 environment with PsychoPy) by itself. It has been tested on macOS, not yet on
Windows; if the installation fails, send Gilles the error.

Open a terminal (macOS: Terminal; Windows: PowerShell) and run:

```bash
git clone -b numeral-version https://github.com/Gilles86/numerosity_transform.git
cd numerosity_transform/experiment
```

If you cloned the repository before, run `git fetch && git switch numeral-version && git pull` in that folder instead, and check that `README_numerals.md` is there.

## 2. Set up your screen (once)

Create a file `settings/saurabh.yml` in the `experiment` folder, with your own screen in it:

```yaml
window:
  size: [1920, 1080]  # width and height in pixels, as your operating system reports them
  fullscr: True
  screen: 0           # 0 = main screen

monitor:
  name: saurabh
  width: 34           # width of the visible screen area, in cm
  distance: 50        # your distance to the screen, in cm
```

With a scaled display, use the scaled size for `window.size`: on a Mac, the "looks like" size under System Settings > Displays; on Windows
at 200% scaling, half the resolution. If you are unsure, or just want to try things out, skip this file and choose `default` in the
launcher below: that is a 1200 x 800 window that works on any computer.

## 3. Read the instructions

Read the booklet of the session before you start. It explains the task, shows the exact mapping and explains why bidding your true value is
your best strategy.

- Session 1: `instructions/instructions_numeral_concave.docx`
- Session 2: `instructions/instructions_numeral_convex.docx`

Read only the booklet of the session you are about to do. The show-up fee in the booklet is still a placeholder, which you can ignore.

## 4. Run session 1 (concave)

Close other programs, turn off notifications, and in the `experiment` folder run:

```bash
python start.py
```

(`python3 start.py` if `python` is not found. The very first start downloads the environment, which takes a few minutes.)

Answer the questions as follows. For multiple-choice questions, type the number of the option and press ENTER:

| Question | Answer | Type |
|---|---|---|
| Subject | `saurabh` | `saurabh` |
| Session | 1 | `1` |
| Stimulus | `numeral` | `2` |
| Mapping | `concave` | `1` |
| Screen settings | `saurabh` (or `default`, see step 2) | The number shown next to it |
| Response | `typing` | `1` |
| Start at phase | `examples` | `1` |

The experiment then runs from start to finish, opening a new window for each phase. Keep your hands on the keyboard: you do not need the mouse.

### What you will see

**Phase 1: Examples (self-paced).** You see 23 numbers, each with its value. Use the RIGHT and LEFT ARROWS to browse. SPACE BAR continues, but
only once you have seen all 23. Take your time: later you will mostly see other numbers, so learn the shape of the relationship
rather than a list.

**Phase 2: Training (138 trials in 6 blocks, with a break between blocks).** Every trial goes as follows:

1. A fixation cross: green, then white. Get ready.
2. A number with two decimals (1 second). It stays on screen while you answer.
3. Type the value, up to two decimals, for example `23.45`, and press ENTER. Both `.` and `,` work as the decimal point, and BACKSPACE corrects. You have 5 seconds.
4. The correct value appears above the number: green if you were within 0.50 CHF, red if you were further away.

**Phase 3: Auction (4 runs of 46 trials).** Each run starts with an instruction screen; press SPACE BAR when you are ready, so you can rest in between. Trials are the same, except that:

- The number disappears after 1 second, and you answer after a short pause.
- You have 4 seconds, and you get no feedback.
- Your answer is your bid. Bid what you think the number is worth.

At the end of each run you see what you earned in that run and in total so far.

### Good to know

- **Only values from 1 to 50 are accepted.** If you press ENTER on anything else, nothing happens: correct it and press ENTER again.
- **"Too late!"** means you did not press ENTER in time. Your typed answer is not counted, and in the auction that trial pays nothing.
- **You do not have to type two decimals.** `23` or `23.5` is also accepted; use the precision you actually believe in.
- **Your mouse is not used.** If the mouse pointer or other windows are in the way in `default` mode, click once on the experiment window to make sure it has the keyboard focus.

## 5. Run session 2 (convex)

Read the convex booklet and run `python start.py` again, with the same answers except for:

| Question | Answer | Type |
|---|---|---|
| Session | 2 | `2` |
| Mapping | `convex` | `2` |

## 6. If something goes wrong

**You need to stop.** Press `q`. This ends only the current phase, and the launcher then starts the next phase. To stop altogether, press
`q` once more in each following phase until you are back in the terminal, or press Ctrl+C in the terminal.

**You want to continue after a stop or crash.** Run `python start.py` with the same subject, session, stimulus and mapping, and at **Start at phase** choose the phase that was interrupted (for example `run3`). The launcher warns that files
already exist; answer `y`. Only the phase you repeat (and the ones after it) gets overwritten; finished earlier phases are not touched. If a phase was interrupted, tell Gilles which one.

**The window is too large, cut off or tiny.** `window.size` in `settings/saurabh.yml` does not match your screen. See step 2, or choose `default`.

**You want to practise first.** This short run does not need the launcher. Use a separate subject name, so your real data stay clean:

```bash
uv run python training.py test 1 --mapping concave --stimulus numeral --settings saurabh --n_trials 5
```

(Delete `logs/numerals/sub-test` afterwards.) If `uv` is not found on macOS or Linux, it is in `~/.local/bin/uv`. Note that practising with a real mapping already teaches you part of it, so keep it short.

## 7. Send the data back

Everything is saved in `experiment/logs/numerals/sub-saurabh/`. Check it has both sessions: each `ses-*` folder should contain, per phase (examples, training and 4 auction runs),
an `_events.tsv` file, plus 4 `reward_*.txt` files. To see your earnings in the task:

```bash
uv run python earnings.py saurabh
```

This includes the show-up fee from the settings, which is still a placeholder.

Then zip the folder and send it to Gilles:

```bash
cd logs/numerals && zip -r sub-saurabh.zip sub-saurabh                          # macOS / Linux
cd logs/numerals; Compress-Archive sub-saurabh sub-saurabh.zip                  # Windows PowerShell
```

The logs are not tracked by git, so please do not try to push them.

**Please also tell Gilles:**

- Was 4 seconds enough to type a two-decimal answer in the auction? How many decimals did you actually use?
- Did you feel you were estimating from the curve or recalling specific numbers, and did this change during training?
- Was anything in the instructions unclear or wrong?
