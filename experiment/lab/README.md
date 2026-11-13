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

Settings: set *Mirror from* to your shortname. Custom Command experiments (`<exp>` = `C:\ExpFiles\<shortname>\numerosity_transform\experiment`):
- **numerosity A** (group on PCs 1–30): `<exp>\lab.bat --auto --session 1`
- **numerosity B** (group on PCs 1–5): `<exp>\lab.bat --auto --offset 30 --session 1`
- **numerosity TEST**: `<exp>\lab.bat --auto --test` (everything goes to `*_test` folders; never counts as a real session)

`--auto`: nothing is clicked on the participant PCs. Participant = PC number (+ offset), so **every participant sits at
the same PC in every session**. Stimulus and mapping come from `lab\participants.tsv`.

**Session failsafe.** Each PC works out the session from the logs on the network, and `--session` is what you expect.
If they disagree, that PC shows an EXPERIMENTER dialog and starts nothing until you decide. If the network folder is
unreachable, the PC refuses to start (it never guesses).

## Each session

1. In LabControl Settings, set `--session` in the command to today's session.
2. Select **only the occupied PCs**, choose A or B, tick **Mirror Experiment Files**, then click **Save and Start Clients**.
3. On the ExpMaster, run **`status`**: a table of every PC with its participant, session, version and phase. Check it
   before participants start, and keep it open (it warns if different sessions are running).
4. Optionally run `collect -Watch` to copy data to the project folder every minute.
5. At the end each screen shows the earnings. Payment list: `lab_python\...\python.exe lab\payment_list.py <session>`.

**After a crash:** start `lab.py` again (on any PC) with the same number. It continues where it stopped.

**Who gets which version:** `lab\participants.tsv` (from `lab\make_participants.py`).
