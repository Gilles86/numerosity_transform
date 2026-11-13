# BLU lab: quick guide

## Setup (once, on the ExpMaster PC)

1. Download https://github.com/Gilles86/numerosity_transform/archive/refs/heads/numeral-version.zip and unzip it into
   `C:\Users\<shortname>\Documents\`.
2. In PowerShell, in the `experiment` folder, run:
   `powershell -ExecutionPolicy ByPass -File lab\setup_lab_env.ps1`
   This builds Python and PsychoPy in `lab_python\` and prints the paths for LabControl.
3. Edit:
   - `lab\lab_config.yml`: `results_dir` = `N:\client_write\<shortname>\numerosity_transform`
   - `settings\lab.yml`: `monitor.distance` = the measured viewing distance in cm
4. Test: `& <printed python.exe> lab.py` (participant `1`; `q` quits a phase).
5. Copy the whole folder to `N:\expfiles\<shortname>\` (about 15 min the first time).

## LabControl (once)

Settings: set *Mirror from* to your shortname. Then create two Custom Command experiments:
- **numerosity A** (group on PCs 1–30): `C:\ExpFiles\<shortname>\numerosity_transform\experiment\lab.bat --auto`
- **numerosity B** (group on PCs 1–5): `C:\ExpFiles\<shortname>\numerosity_transform\experiment\lab.bat --auto --offset 30`

With `--auto`, nothing is clicked on the participant PCs. Participant = PC number (+ offset), so **every participant
sits at the same PC in every session**. The session and, after a crash, the phase are taken from the logs. Stimulus
and mapping come from `lab\participants.tsv`. Without `--auto`, a dialog asks for the participant number.

## Each session

1. In LabControl, select **only the occupied PCs**, choose A or B, tick **Mirror Experiment Files**, then click
   **Save and Start Clients**.
2. Everything runs by itself. At the end, the screen shows the earnings and the participant raises their hand.
3. Payment list: `lab_python\...\python.exe lab\payment_list.py <session>` (or `--all`).
4. Copy `N:\client_write\<shortname>\numerosity_transform` to the project's `_behavioural_lab` folder.

**After a crash:** start `lab.py` again (on any PC) with the same number. It continues where it stopped.

**Who gets which version:** `lab\participants.tsv` (from `lab\make_participants.py`).
