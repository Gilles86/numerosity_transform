# Numerosity transform

Behavioural (lab) port of the `abstract_values` task. The stimulus is a cloud of dots (6-50 dots, 23 levels); the
number of dots maps to a monetary value (CHF). Participants learn the mapping, estimate it with feedback, and then
bid for each cloud in a BDM auction.

## Run

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # once; installs uv
cd experiment && uv sync                          # once; creates .venv from uv.lock

uv run python examples.py <subject> <session> --mapping concave   # 1. learn the mapping
uv run python training.py <subject> <session> --mapping concave   # 2. estimation with feedback
uv run python task.py <subject> <session> <run> --mapping concave # 3. auction, one call per run (1-4)
uv run python earnings.py <subject>                               # payout from the reward files

uv run python start.py   # asks subject, session, mapping, screen, response, start phase; then runs 1-3
```

`--mapping {linear,concave,convex}` is required and chosen by hand. `--settings <name>` loads
`settings/<name>.yml` on top of `default.yml`: `dell_p2725qe` (Dell P2725QE 4K at ~50 cm, fullscreen) or `lab` (template). `--n_trials N` (training, task) runs a short test.
Responses are typed by default (type the number, ENTER confirms); `--response slider` (training, task)
uses the mouse slider instead. The subject can be a name (`gilles`): logs go to `logs/sub-gilles/`.
Press `q` to quit. Logs go to `logs/sub-XX/ses-Y/` (exptools2 `*_events.tsv` with numerosity, value, mapping,
response, response_time, price (random BDM price), reward; plus `reward_<sub>_<ses>_<run>.<mapping>.txt` per auction run).

## Phases and timing (seconds, all in `settings/default.yml`)

| Phase | Trials | Fixation (green + white) | Dots | ISI | Response | Feedback | ITI |
|---|---|---|---|---|---|---|---|
| `examples.py` | self-paced, arrow keys, must see all 23 | | | | | | |
| `training.py` | 23 x 6 in 6 blocks | 0.3 + 0.2 | 1.0 (stays on during response) | none | up to 5 | 1.0 (true value) | 0.5 |
| `task.py` | 23 x 2 per run, 4 runs | 0.3 + 0.2 | 1.0 | 0.5 / 0.75 / 1.0 | up to 4 | 1.0 (own answer, no value) | 0.5 |

Auction: random price drawn uniformly from 6-50; if bid > price the participant gets 50 + value - price, otherwise 50.
Run reward = sum over trials / `reward_scaling` (184) CHF; show-up fee in `main_task.show_up_fee`.

## Mappings (numerosity -> CHF)

| Dots | 6 | 8 | 10 | 12 | 14 | 16 | 18 | 20 | 22 | 24 | 26 | 28 | 30 | 32 | 34 | 36 | 38 | 40 | 42 | 44 | 46 | 48 | 50 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| linear | 6 | 8 | 10 | 12 | 14 | 16 | 18 | 20 | 22 | 24 | 26 | 28 | 30 | 32 | 34 | 36 | 38 | 40 | 42 | 44 | 46 | 48 | 50 |
| concave | 6 | 11.5 | 16.5 | 21 | 24.5 | 28 | 31 | 33.5 | 36 | 38 | 39.5 | 41.5 | 42.5 | 44 | 45 | 46 | 46.5 | 47.5 | 48 | 48.5 | 49 | 49.5 | 50 |
| convex | 6 | 6.5 | 7 | 7.5 | 8 | 8.5 | 9.5 | 10 | 11 | 12 | 13.5 | 14.5 | 16.5 | 18 | 20 | 22.5 | 25 | 28 | 31.5 | 35 | 39.5 | 44.5 | 50 |

Dot clouds: aperture radius 2.5 deg, dot radius 0.1 deg, minimum centre distance 2.2 dot radii, no dots within 0.4 deg of fixation; positions are
resampled on every presentation.
