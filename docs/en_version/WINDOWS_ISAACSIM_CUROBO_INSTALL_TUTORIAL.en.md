# Windows + NVIDIA RTX 50-Series + Isaac Sim 4.5+ cuRobo Installation and Repair Tutorial

## 1. Who this tutorial is for

This document is intended for users who match most of the following:

- you are on Windows 10 or Windows 11
- you are using Isaac Sim 4.5 or later
- the GPU is a newer NVIDIA GeForce RTX 50-series card
- a repository path that explicitly targets newer GPUs on Isaac Sim 4.5+ is needed
- `pip install -e .` keeps failing and a deterministic repair path is preferred

This repository is primarily maintained around that target combination:

- NVIDIA GeForce RTX 50-series GPUs
- Isaac Sim 4.5+
- Windows

This tutorial is based on a real repair and validation run in the following environment:

- OS: Windows 11
- Isaac Sim root: `<ISAAC_SIM_ROOT>`
- cuRobo project: `<REPO_ROOT>`
- GPU: NVIDIA GeForce RTX 5070
- GPU capability: `sm_120`
- Isaac Sim: `4.5.0`
- Isaac Sim bundled PyTorch: `2.5.1+cu118`
- local CUDA toolkit: `11.8`
- MSVC: Visual Studio 2022 Build Tools / `14.50`

## 2. Final result

The current repaired environment can:

- install `curobo_for_windows` into the Isaac Sim Python environment
- import the prebuilt Windows `.pyd` extensions successfully
- launch Isaac Sim `SimulationApp`
- run the headless Isaac Sim + cuRobo smoke test
- avoid the critical JIT / NVRTC failure path on `sm_120`
- run the formal GUI demo path with migrated planning compatibility logic

This is not just “it compiles”. It is “it installs, imports, validates, and runs the planning path”.

## 3. What actually caused the failures

The original problem was a failure chain, not a single error.

### Problem 1: the Isaac Sim Python entry path was incomplete

Symptoms:

- `import torch` failed during installation
- editable install failed very early

Typical error:

```text
ModuleNotFoundError: No module named 'torch'
```

Reason:

- Isaac Sim ships critical packages through bundled extension paths, not only normal `site-packages`
- if those paths are not exposed correctly, build metadata collection already fails

### Problem 2: `setup.py` tried to build CUDA extensions locally

Symptoms:

- `pip install -e .` tried to compile native CUDA extensions on Windows

Reason:

- the project contains native CUDA extensions
- once PyTorch was upgraded, editable install tried to rebuild them
- the machine had CUDA `11.8`, while the overlaid PyTorch runtime was `cu128`

That is a build-chain mismatch, not just a bad flag.

### Problem 3: upgrading torch also disturbed Isaac Sim bundled binary packages

Symptoms:

- `numpy` binary import issues
- `PIL._imaging` mismatches
- extension import failures when launching full Isaac Sim

Reason:

- a naive pip overlay can replace packages that Isaac Sim expects to remain at its own bundled versions

### Problem 4: old runtime compilation paths did not support `sm_120`

Typical error:

```text
nvrtc: error: invalid value for --gpu-architecture (-arch)
```

Reason:

- older CUDA/NVRTC runtime paths in the Isaac Sim stack cannot compile for `sm_120`

### Problem 5: some sampling paths still triggered runtime compilation indirectly

Even after the obvious JIT path was bypassed, some code paths could still hit runtime compilation indirectly, especially around sampling utilities.

### Problem 6: Warp BoundCost caused `cudaErrorIllegalInstruction` in the full app path

This was not only an import problem. It was also a runtime stability problem inside the full GUI application.

### Problem 7: Franka used 9 articulation DOFs but the planner controlled 7 active joints

This caused a real planning interface mismatch:

- the articulation had 9 joints including fingers / fixed layout details
- the planner expected the 7 active planning joints

### Problem 8: some GUI demo paths mixed full and active joint states

The result was not just a warning. It led to ordering and shape mismatches.

### Problem 9: `FINETUNE_TRAJOPT_FAIL` did not always mean “no usable trajectory”

In the full GUI path, finetuning could fail even when the pre-finetune trajectory was already valid enough to execute.

## 4. What was changed

### Environment and installation layer

- [`isaacsim_python.bat`](../../isaacsim_python.bat)
- [`install_in_isaacsim.bat`](../../install_in_isaacsim.bat)
- [`verify_isaacsim_integration.bat`](../../verify_isaacsim_integration.bat)
- `<ISAAC_SIM_ROOT>\site\sitecustomize.py`

Purpose:

- expose the right Isaac Sim Python paths
- route `torch` through `<ISAAC_SIM_ROOT>\python_packages`
- keep Isaac Sim bundled `numpy` and `PIL` preferred when needed

### Build layer

- [`setup.py`](../../setup.py)

Purpose:

- skip local CUDA compilation on Windows when prebuilt `.pyd` files already exist
- only allow forced rebuild when explicitly requested

### Native extension loading layer

- [`src/curobo/curobolib/__init__.py`](../../src/curobo/curobolib/__init__.py)

Purpose:

- make Windows native dependency loading more robust

### Runtime compatibility layer

- [`src/curobo/util/torch_utils.py`](../../src/curobo/util/torch_utils.py)
- [`examples/isaac_sim/motion_gen_compat.py`](../../examples/isaac_sim/motion_gen_compat.py)

Purpose:

- avoid unsupported runtime JIT / NVRTC paths on newer GPUs
- handle full-joint vs active-joint ordering
- reuse a valid pre-finetune trajectory when finetuning fails

### Demo and validation layer

- [`examples/isaac_sim/smoke_test_headless.py`](../../examples/isaac_sim/smoke_test_headless.py)
- [`examples/isaac_sim/gui_motion_gen_smoke.py`](../../examples/isaac_sim/gui_motion_gen_smoke.py)
- [`examples/isaac_sim/motion_gen_reacher.py`](../../examples/isaac_sim/motion_gen_reacher.py)
- [`examples/isaac_sim/simple_stacking.py`](../../examples/isaac_sim/simple_stacking.py)
- [`run_isaacsim_curobo_demo.bat`](../../run_isaacsim_curobo_demo.bat)

Purpose:

- validate the stack in both smoke and formal entry paths
- migrate the compatibility logic into the formal long-term script

## 5. Recommended installation method

```powershell
cd <REPO_ROOT>
.\install_in_isaacsim.bat
.\verify_isaacsim_integration.bat
```

If both pass, the environment is in the expected state.

## 6. Manual method for running the steps directly

### Step 1: verify the Isaac Sim Python wrapper

```powershell
cd <REPO_ROOT>
.\isaacsim_python.bat -c "import isaacsim, torch; print(torch.__version__)"
```

### Step 2: install the package with the repaired wrapper

```powershell
.\isaacsim_python.bat -m pip install -e . --no-build-isolation
```

### Step 3: run the headless smoke test

```powershell
.\isaacsim_python.bat -u .\examples\isaac_sim\smoke_test_headless.py
```

### Step 4: run the formal GUI demo entry

```powershell
.\run_isaacsim_curobo_demo.bat
```

## 7. Why this installable version is more stable than the original path

The main improvements are practical:

- it uses the repaired Isaac Sim Python wrapper instead of assuming `python.bat` is enough
- it reuses prebuilt Windows extensions instead of recompiling CUDA locally
- it preserves Isaac Sim bundled binary dependencies where that matters
- it adds GPU/runtime compatibility downgrades for unsupported JIT paths
- it validates both smoke and formal GUI entry paths

## 8. Warnings that look scary but are still acceptable

You may still see compatibility warnings related to:

- a newer GPU on an older Isaac Sim release
- disabled JIT / NVRTC paths
- finetuning failures that still return a usable pre-finetune plan

Those warnings are acceptable if:

- installation succeeds
- the smoke test succeeds
- planning still returns a usable trajectory

## 9. Common issue map

### `No module named 'torch'`

Likely cause:

- wrong Python entry point
- Isaac Sim bundled paths are not exposed

### `No module named 'isaacsim.simulation_app'`

Likely cause:

- not running inside the Isaac Sim Python environment

### `DLL load failed while importing ...`

Likely cause:

- native dependency loading order on Windows

### `nvrtc: error: invalid value for --gpu-architecture (-arch)`

Likely cause:

- unsupported runtime compilation path on a new GPU

### `FINETUNE_TRAJOPT_FAIL`

Likely cause:

- finetuning failed, but the primary planning result may still contain a usable trajectory

Check:

- [`motion_gen_compat.py`](../../examples/isaac_sim/motion_gen_compat.py)

## 10. Recommended day-to-day usage

Use this order:

1. install or repair with `install_in_isaacsim.bat`
2. validate with `verify_isaacsim_integration.bat`
3. use `run_isaacsim_curobo_demo.bat` for the formal standalone demo path
4. use the in-app scripts for GUI-internal workflows

Do not start from random direct `pip install` or random Python binaries.

## 11. Boundaries of this solution

This delivery is designed for:

- Windows
- Isaac Sim 4.5-era structure
- the repaired `curobo_for_windows` tree in this repository

If Isaac Sim, PyTorch, CUDA, or cuRobo native extensions change, revalidate the install and runtime assumptions.

## 12. Short version for normal users

Shortest practical path:

```powershell
cd <REPO_ROOT>
.\install_in_isaacsim.bat
.\verify_isaacsim_integration.bat
.\run_isaacsim_curobo_demo.bat
```

If install and verification pass, continue with the GUI beginner guides.
