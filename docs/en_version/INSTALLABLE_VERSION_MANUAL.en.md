# Installable Version Manual

## 1. What this package is

This is the curated Windows / Isaac Sim delivery of `curobo_for_windows`.

It is primarily maintained for:

- Windows
- NVIDIA GeForce RTX 50-series GPUs
- Isaac Sim 4.5+

The target is not “it might install in theory”. The target is:

- one-command installation
- one-command verification
- minimal manual environment work
- practical compatibility for newer GPUs on older Isaac Sim stacks

## 2. What is included

### [`docs/en_version/DOCS_READING_ORDER_AND_OVERVIEW.en.md`](./DOCS_READING_ORDER_AND_OVERVIEW.en.md)

Purpose:

- the documentation entry point
- explains the reading order
- explains which document is for which stage

### [`docs/en_version/WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.en.md`](./WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.en.md)

Purpose:

- installation and repair tutorial
- explains why the original path fails
- gives the practical installation route

### [`docs/en_version/ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.en.md`](./ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.en.md)

Purpose:

- explains why starting Isaac Sim through `selector.bat` is valid
- explains standalone vs in-app scripts
- teaches GUI-internal usage through Script Editor

### [`docs/en_version/ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.en.md`](./ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.en.md)

Purpose:

- next step after the GUI beginner guide
- explains custom robots, obstacles, targets, and world sync

### [`docs/en_version/ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.en.md`](./ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.en.md)

Purpose:

- the pick/place teaching state machine guide
- explains the task flow and beginner-friendly scene modeling

### [`docs/en_version/ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md`](./ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md)

Purpose:

- explains how to load a user-provided USD scene
- explains how to attach the pick/place state machine to that scene

### [`docs/en_version/curobo_isaacsim_windows_full_fix_guide.en.md`](./curobo_isaacsim_windows_full_fix_guide.en.md)

Purpose:

- the full repair log and maintenance reference
- records what changed and why

### [`isaacsim_python.bat`](../../isaacsim_python.bat)

Purpose:

- repaired Isaac Sim Python wrapper
- exposes the needed Isaac Sim Python paths and packaged dependencies

Typical use:

```powershell
.\isaacsim_python.bat -c "import isaacsim"
```

### [`install_in_isaacsim.bat`](../../install_in_isaacsim.bat)

Purpose:

- install the current project into the Isaac Sim Python environment

### [`verify_isaacsim_integration.bat`](../../verify_isaacsim_integration.bat)

Purpose:

- run the minimum smoke validation

Success output includes:

```text
Smoke test passed.
```

### [`examples/isaac_sim/smoke_test_headless.py`](../../examples/isaac_sim/smoke_test_headless.py)

Purpose:

- headless `SimulationApp`
- import Franka
- build `MotionGen`
- plan once
- exit after validation

### [`examples/isaac_sim/motion_gen_compat.py`](../../examples/isaac_sim/motion_gen_compat.py)

Purpose:

- shared planning compatibility layer
- handles full / active / articulation joint mapping
- reuses pre-finetune trajectories when finetuning fails
- provides a no-finetune retry path

### [`examples/isaac_sim/gui_in_app_motion_gen_beginner.py`](../../examples/isaac_sim/gui_in_app_motion_gen_beginner.py)

Purpose:

- minimal in-app GUI script
- does not create `SimulationApp`
- intended for `Window -> Script Editor`

### [`examples/isaac_sim/gui_in_app_custom_scene_template.py`](../../examples/isaac_sim/gui_in_app_custom_scene_template.py)

Purpose:

- custom scene template for GUI-internal use
- collects the most common configuration values at the top of the file

### [`examples/isaac_sim/gui_in_app_pick_place_state_machine_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_state_machine_template.py)

Purpose:

- in-app pick/place teaching template
- explicit state machine
- basic scene modeling
- staged cuRobo planning

### [`examples/isaac_sim/gui_in_app_pick_place_from_usd_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_from_usd_template.py)

Purpose:

- in-app template that loads an already opened or explicitly selected USD scene
- extracts obstacles from configured roots
- attaches the pick/place state machine to a user-provided scene

### [`run_isaacsim_curobo_demo.bat`](../../run_isaacsim_curobo_demo.bat)

Purpose:

- start the formal interactive Isaac Sim demo path

Current default:

- `examples/isaac_sim/motion_gen_reacher.py`

## 3. Recommended usage flow

### Standard flow

```powershell
cd <REPO_ROOT>
.\install_in_isaacsim.bat
.\verify_isaacsim_integration.bat
```

### Debug flow

For manual inspection:

```powershell
.\isaacsim_python.bat -c "import isaacsim, torch"
.\isaacsim_python.bat -m pip show nvidia_curobo
.\isaacsim_python.bat -u .\examples\isaac_sim\smoke_test_headless.py
.\run_isaacsim_curobo_demo.bat
```

### Practical role split

- `smoke_test_headless.py`: minimum integration acceptance
- `gui_motion_gen_smoke.py`: GUI smoke validation
- `motion_gen_reacher.py`: the formal long-term standalone interactive entry
- in-app scripts: GUI-internal teaching and scene-building workflow

Recommended habit:

- always run smoke first after installation or compatibility changes
- then use the formal demo or in-app scripts according to the workflow goal

## 4. Why this is different from a direct `pip install -e .`

Direct editable install often fails on this stack because:

- the wrong Python entry point is used
- Isaac Sim bundled `torch` is not exposed correctly
- required Isaac Sim environment variables are missing
- Windows DLL loading and packaged dependency ordering are fragile

This delivery improves that by:

- using the repaired Isaac Sim wrapper
- reusing prebuilt Windows native extensions
- preserving critical Isaac Sim packaged dependencies
- validating the stack immediately after installation

## 5. Compatibility strategy

### New GPU + older Isaac Sim

Handled issues include:

- older bundled PyTorch on newer GPU generations
- unsupported JIT / NVRTC compilation paths
- Windows native dependency loading
- planning fallback migration from smoke-only logic into formal scripts

### Formal planning compatibility

Current strategy:

- `motion_gen_reacher.py` and `simple_stacking.py` reuse the shared compatibility module
- Franka full 9-joint articulation state and 7-joint active planning state are mapped explicitly
- `FINETUNE_TRAJOPT_FAIL` no longer means “total planning failure” by default

## 6. When the installation counts as successful

Treat the installation as successful when:

1. `.\install_in_isaacsim.bat` succeeds
2. `.\verify_isaacsim_integration.bat` succeeds
3. the output contains:

```text
Smoke test passed.
```

## 7. When you still need to investigate

Continue debugging if any of the following is true:

- `No module named 'torch'`
- `No module named 'isaacsim.simulation_app'`
- `DLL load failed while importing ...`
- `error STL1002`
- `nvrtc: error: invalid value for --gpu-architecture (-arch)`
- the verification script exits non-zero

## 8. Advice for maintainers

### Do not remove the wrapper

`isaacsim_python.bat` is a core part of the solution.

### Do not revert `setup.py` back to eager top-level torch import

That would reintroduce failures during metadata collection.

### Do not remove the runtime compatibility downgrades lightly

For RTX 50 / `sm_120` style setups, those paths are part of the system staying runnable.

### Re-run verification after environment changes

After changes to install scripts, build logic, path logic, or environment variables, always re-run:

```powershell
.\verify_isaacsim_integration.bat
```

## 9. Suggested release note wording

Short version:

This is a repaired Windows + Isaac Sim build of cuRobo that installs and runs on newer GPU setups where the original path is unstable.

Recommended user commands:

```powershell
.\install_in_isaacsim.bat
.\verify_isaacsim_integration.bat
```

## 10. Current state

As of **2026-04-07**, the delivered installable version includes:

- repaired installation path
- Windows build compatibility updates
- native DLL loading fixes
- new-GPU runtime compatibility fixes
- headless Isaac Sim validation
- shared compatibility logic between smoke and formal scripts
- a formal default demo entry on `motion_gen_reacher.py`
- in-app beginner, custom scene, pick/place, and USD-scene workflow templates
- Chinese and English documentation sets
