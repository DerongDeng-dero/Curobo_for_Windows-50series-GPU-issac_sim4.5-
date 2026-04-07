# Beginner Guide: Start Isaac Sim Normally and Use cuRobo Inside the GUI

## 1. Answer to the core question first

### 1.1 Can Isaac Sim be started normally through `isaac-sim.selector.bat` and then run cuRobo inside the software?

Yes.

That is a valid and normal workflow for the repaired environment.

The reason earlier work often used:

- `verify_isaacsim_integration.bat`
- `run_isaacsim_curobo_demo.bat`
- `isaac-sim.bat --exec ...`

is not that `selector.bat` was wrong.

The real reason is:

1. those paths are efficient for installation repair and automated regression
2. many sample scripts in the repository are standalone scripts
3. standalone scripts create their own `SimulationApp`
4. those scripts should not be executed again inside an already open GUI session

So the important distinction is not:

- whether `selector.bat` is allowed

It is:

- whether the script is standalone
- or whether it is an in-app script

That is the most important concept for beginners.

## 2. The single most important concept

## 2.1 There are really two script categories in Isaac Sim + cuRobo

### Category 1: standalone scripts

Characteristics:

- the script launches Isaac Sim itself
- the script usually creates `SimulationApp(...)`
- it is meant to be run directly from the command line

Examples:

- [`motion_gen_reacher.py`](../../examples/isaac_sim/motion_gen_reacher.py)
- [`simple_stacking.py`](../../examples/isaac_sim/simple_stacking.py)

Typical usage:

```powershell
.\run_isaacsim_curobo_demo.bat
```

### Category 2: in-app scripts

Characteristics:

- Isaac Sim is already running
- the script executes inside the existing GUI session
- the script does not create its own `SimulationApp`
- it is meant for `Window -> Script Editor`

Examples:

- [`gui_motion_gen_smoke.py`](../../examples/isaac_sim/gui_motion_gen_smoke.py)
- [`gui_in_app_motion_gen_beginner.py`](../../examples/isaac_sim/gui_in_app_motion_gen_beginner.py)

Typical usage:

1. start `<ISAAC_SIM_ROOT>\isaac-sim.selector.bat`
2. enter `Isaac Sim Full`
3. open `Window -> Script Editor`
4. load and run the script there

## 3. Why `selector.bat` can now see cuRobo

The current environment is no longer the original broken baseline.

The working chain is:

1. [`isaac-sim.selector.bat`](../../../../isaac-sim.selector.bat)
   - calls [`setup_python_env.bat`](../../../../setup_python_env.bat)
2. [`setup_python_env.bat`](../../../../setup_python_env.bat)
   - exposes `<ISAAC_SIM_ROOT>\site`
3. [`site/sitecustomize.py`](../../../../site/sitecustomize.py)
   - exposes `python_packages`
   - also adjusts package priority for `numpy` and `PIL` when needed
4. cuRobo was already installed through:
   - [`install_in_isaacsim.bat`](../../install_in_isaacsim.bat)

Practical conclusion:

- if Isaac Sim is started from this repaired `<ISAAC_SIM_ROOT>`
- and cuRobo has already been installed into that environment

then the GUI session should be able to import `curobo`.

## 4. Three common ways to use the environment

### Mode A: minimum acceptance check

Best for:

- freshly repaired environments
- quick validation

Command:

```powershell
cd <REPO_ROOT>
.\verify_isaacsim_integration.bat
```

### Mode B: one-command formal demo

Best for:

- quickly entering the formal standalone example
- skipping manual Script Editor work

Command:

```powershell
cd <REPO_ROOT>
.\run_isaacsim_curobo_demo.bat
```

Current default entry:

- [`motion_gen_reacher.py`](../../examples/isaac_sim/motion_gen_reacher.py)

### Mode C: start through selector, then use cuRobo inside the GUI

Best for:

- normal GUI workflow
- looking at the scene while editing scripts
- gradually building a user-provided scene instead of running a full automatic demo

This guide focuses on this mode.

## 5. First thing beginners should do: verify the environment first

### 5.1 Install or repair

```powershell
cd <REPO_ROOT>
.\install_in_isaacsim.bat
```

### 5.2 Verify

```powershell
.\verify_isaacsim_integration.bat
```

Expected output:

```text
Smoke test passed.
```

If that does not pass, do not start debugging the GUI workflow yet.

## 6. Full steps to start Isaac Sim through selector

### 6.1 Start the selector

Run:

```powershell
<ISAAC_SIM_ROOT>\isaac-sim.selector.bat
```

### 6.2 Which app to choose

Choose:

- `Isaac Sim Full`

For beginners, do not start with streaming or remote modes first.

### 6.3 Which windows to keep visible

Recommended:

- `Window -> Stage`
- `Window -> Content`
- `Window -> Console`
- `Window -> Extensions`

Also required:

- `Window -> Script Editor`

## 7. How to open Script Editor

If it already exists:

- open `Window -> Script Editor`

If it does not:

1. open `Window -> Extensions`
2. search for `script editor`
3. enable `omni.kit.window.script_editor`
4. go back to `Window -> Script Editor`

## 8. Run a minimal import test first

Open Script Editor and run:

```python
import curobo
print("curobo import ok")
```

This confirms that the GUI session can actually see the installed package.

## 9. Run a real in-app beginner script

Do not run standalone scripts from Script Editor, for example:

- [`motion_gen_reacher.py`](../../examples/isaac_sim/motion_gen_reacher.py)
- [`simple_stacking.py`](../../examples/isaac_sim/simple_stacking.py)

Use the in-app beginner script instead:

- [`gui_in_app_motion_gen_beginner.py`](../../examples/isaac_sim/gui_in_app_motion_gen_beginner.py)

Steps:

1. start `Isaac Sim Full`
2. open `Window -> Script Editor`
3. open the file
4. press `Run`

This is the recommended beginner entry because:

- it does not create `SimulationApp`
- it is designed for an already open GUI session
- it reuses the planning compatibility logic already added to the repo

## 10. Common mistakes

### Mistake 1: running a standalone script from Script Editor

Result:

- duplicate app lifecycle logic
- broken execution path

### Mistake 2: skipping smoke validation

Result:

- you do not know whether the problem is installation or scene logic

### Mistake 3: assuming “visible in GUI” means “already in cuRobo world”

Result:

- the scene looks correct visually
- but cuRobo may not be using the expected collision world yet

## 11. Common issue checklist

### `No module named 'curobo'` inside Script Editor

Check:

- whether cuRobo was installed through [`install_in_isaacsim.bat`](../../install_in_isaacsim.bat)
- whether you started Isaac Sim from the repaired `<ISAAC_SIM_ROOT>`

### `No module named 'torch'`

Check:

- the wrapper and path exposure
- the repaired environment, not a random Python interpreter

### GUI opens, but planning scripts fail later

Check:

- whether you are using an in-app script
- whether the compatibility logic is present through [`motion_gen_compat.py`](../../examples/isaac_sim/motion_gen_compat.py)

## 12. Recommended next steps

Once the in-app beginner script works, continue in this order:

1. read the custom scene workflow guide
2. read the pick/place state machine guide
3. read the USD scene workflow guide

That path moves the workflow from:

- “GUI can import cuRobo”

to:

- “I can build and run my own scene and task flow in Isaac Sim”

## 13. Short version

Shortest practical route:

1. run [`verify_isaacsim_integration.bat`](../../verify_isaacsim_integration.bat)
2. start [`isaac-sim.selector.bat`](../../../../isaac-sim.selector.bat)
3. enter `Isaac Sim Full`
4. open `Window -> Script Editor`
5. run [`gui_in_app_motion_gen_beginner.py`](../../examples/isaac_sim/gui_in_app_motion_gen_beginner.py)
