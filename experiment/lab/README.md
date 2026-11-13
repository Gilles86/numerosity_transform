# BLU lab: quick guide

## Setup (once, on the ExpMaster PC)

1. Download https://github.com/Gilles86/numerosity_transform/archive/refs/heads/numeral-version.zip and unzip it into
   `C:\Users\<shortname>\Documents\`.
2. In PowerShell, in the `experiment` folder, run:
   `powershell -ExecutionPolicy ByPass -File lab\setup_lab_env.ps1`
   This builds Python and PsychoPy in `lab_python\` and prints the paths for Lab Control.
3. Edit:
   - `lab\lab_config.yml`: `results_dir` = `N:\client_write\<shortname>\numerosity_transform`
   - `settings\lab.yml`: `monitor.distance` = the measured viewing distance in cm
4. Test: `& <printed python.exe> lab.py` (participant `1`; `q` quits a phase).
5. Copy the whole folder to `N:\expfiles\<shortname>\` (about 15 min the first time).

## Lab Control (once)

Settings → Create → Custom Experiment, type **Python**:
- Executable: `C:\ExpFiles\<shortname>\numerosity_transform\experiment\lab_python\...\python.exe` (printed by the setup)
- Script: `C:\ExpFiles\<shortname>\numerosity_transform\experiment\lab.py`

## Each session

1. In Lab Control, select the clients, choose the experiment, tick **Mirror Experiment Files**, then click
   **Save and Start Clients**.
2. Participants type their **participant number** (1–35, the same in every session). The session number is filled in.
3. Everything else runs by itself. At the end, the screen shows the earnings and the participant raises their hand.
4. Payment list: `<python.exe> lab\payment_list.py <session>` (or `--all` for the totals over all sessions).
5. Copy `results_dir` to the project's `_behavioural_lab` folder.

**After a crash:** start `lab.py` again (on any PC) with the same number. It continues where it stopped.

**Who gets which version:** `lab\participants.tsv` (from `lab\make_participants.py`).
