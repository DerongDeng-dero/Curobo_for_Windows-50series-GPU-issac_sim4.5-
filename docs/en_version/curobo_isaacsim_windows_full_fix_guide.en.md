# cuRobo for Windows + Isaac Sim Full Repair Guide

## 1. Purpose

This document records the full repair process that made the current Windows + Isaac Sim + cuRobo workflow usable in `<ISAAC_SIM_ROOT>`.

It covers:

- the actual machine environment
- the initial failure symptoms
- the real root causes behind each failure
- the reasoning behind each repair step
- the key files that were changed
- the final validation path
- maintenance guidance for future upgrades

This is not a generic note. It is the engineering record of the repair path that produced the current working setup.

## 2. Environment and background

### Environment

- OS: Windows 11
- Isaac Sim root: `<ISAAC_SIM_ROOT>`
- cuRobo project: `<REPO_ROOT>`
- GPU: NVIDIA GeForce RTX 5070
- GPU capability: `sm_120`
- CUDA toolkit / `nvcc`: `11.8`
- Isaac Sim: `4.5.0-rc.36`

### Initial goal

The target had two layers:

1. install `curobo_for_windows` into the Isaac Sim runtime correctly
2. make the full GUI motion-generation path actually plan successfully, not merely import and start

### Important observation

The original failure was not a single point failure. It was a stack of problems:

- installation incompatibility
- packaged Python binary dependency drift inside Isaac Sim
- new-GPU incompatibility with old CUDA/NVRTC runtime compilation
- Warp runtime instability inside the full app path
- Franka full-vs-active joint dimension mismatch
- GUI finetune failure even when a usable primary trajectory already existed

## 3. Final state

The current repaired stack can now do the following:

- `install_in_isaacsim.bat` succeeds
- `verify_isaacsim_integration.bat` succeeds
- the headless smoke test passes
- the GUI smoke path passes
- the formal standalone demo path reuses the migrated compatibility logic
- in-app beginner, custom-scene, state-machine, and USD-scene workflows exist

The important engineering result is this:

- compatibility logic is no longer trapped inside smoke-only scripts
- it was migrated into the formal long-term script path

## 4. Root causes and their fixes

### 4.1 Isaac Sim bundled PyTorch was not compatible with RTX 5070

Isaac Sim 4.5 shipped with `torch 2.5.1+cu118`.

That stack does not natively fit `sm_120`.

Consequences:

- some CUDA kernels fail
- runtime compilation tries to target an unsupported architecture

Fix:

- overlay a newer PyTorch runtime in `<ISAAC_SIM_ROOT>\python_packages`
- avoid relying on the old bundled JIT path

### 4.2 Editable install incorrectly tried to rebuild CUDA extensions locally

The project contains multiple native CUDA extensions.

Once editable install tried to rebuild them with local `nvcc 11.8` while PyTorch runtime was `cu128`, the build chain became inconsistent.

Fix:

- prefer the existing prebuilt `.pyd` files on Windows
- skip local CUDA compilation unless explicitly forced

Implemented in:

- [`setup.py`](../../setup.py)

### 4.3 Torch overlay also disturbed Isaac Sim packaged `numpy` and `PIL`

This caused import mismatches inside the full app path.

Fix:

- route `torch` through `<ISAAC_SIM_ROOT>\python_packages`
- keep Isaac Sim bundled `numpy` and `PIL` preferred when needed

Implemented in:

- `<ISAAC_SIM_ROOT>\site\sitecustomize.py`

### 4.4 NVRTC / `torch.jit` paths did not support `sm_120`

This produced:

```text
nvrtc: error: invalid value for --gpu-architecture (-arch)
```

Fix:

- keep normal CUDA execution where it still works
- disable or bypass the runtime-compiled paths that are known to fail on this stack

Primary runtime compatibility implementation:

- [`src/curobo/util/torch_utils.py`](../../src/curobo/util/torch_utils.py)

### 4.5 Sampling paths could still trigger runtime compilation indirectly

Some paths still reached unsupported runtime compile logic indirectly, especially around sampling.

Fix:

- continue reducing dependence on runtime-compiled math paths for this environment

### 4.6 Warp BoundCost triggered `cudaErrorIllegalInstruction` in the full app path

This was a full application runtime failure, not just a setup issue.

Fix:

- route away from the unstable runtime path for this GPU/stack combination
- keep validation focused on stable planning and execution paths

### 4.7 Franka had 9 articulation joints but only 7 active planning joints

That mismatch surfaced as shape and ordering problems.

Fix:

- make the mapping between full articulation state and active planning state explicit

### 4.8 GUI demo scripts mixed full joint state and active joint state

Fix:

- normalize joint ordering and state conversion through shared compatibility logic

### 4.9 `FINETUNE_TRAJOPT_FAIL` did not always mean “no usable plan”

In the full GUI path, finetuning could fail while the pre-finetune result still contained a usable trajectory.

Fix:

- reuse that trajectory when it exists
- add a retry path without finetuning
- migrate this logic into the formal entry path

Implemented in:

- [`examples/isaac_sim/motion_gen_compat.py`](../../examples/isaac_sim/motion_gen_compat.py)

## 5. Key files that were changed

### Installation and environment layer

- `<ISAAC_SIM_ROOT>\site\sitecustomize.py`
- [`isaacsim_python.bat`](../../isaacsim_python.bat)
- [`install_in_isaacsim.bat`](../../install_in_isaacsim.bat)
- [`verify_isaacsim_integration.bat`](../../verify_isaacsim_integration.bat)

### Build layer

- [`setup.py`](../../setup.py)

### Native extension loading layer

- [`src/curobo/curobolib/__init__.py`](../../src/curobo/curobolib/__init__.py)

### Runtime compatibility layer

- [`src/curobo/util/torch_utils.py`](../../src/curobo/util/torch_utils.py)
- [`examples/isaac_sim/motion_gen_compat.py`](../../examples/isaac_sim/motion_gen_compat.py)

### Validation and demo layer

- [`examples/isaac_sim/smoke_test_headless.py`](../../examples/isaac_sim/smoke_test_headless.py)
- [`examples/isaac_sim/gui_motion_gen_smoke.py`](../../examples/isaac_sim/gui_motion_gen_smoke.py)
- [`examples/isaac_sim/motion_gen_reacher.py`](../../examples/isaac_sim/motion_gen_reacher.py)
- [`examples/isaac_sim/simple_stacking.py`](../../examples/isaac_sim/simple_stacking.py)
- [`run_isaacsim_curobo_demo.bat`](../../run_isaacsim_curobo_demo.bat)

### Documentation and teaching layer

- the Chinese and English guide sets under:
  - `docs/zh-cn_version`
  - `docs/en_version`

## 6. Repair timeline in engineering terms

### Stage 1: identify that this was not a normal pip problem

The first visible failure looked like a package install problem.

But the deeper issue was GPU/runtime compatibility on a newer card against an older Isaac Sim stack.

### Stage 2: after overlaying torch, editable install still exploded

That revealed a second class of issue:

- local rebuild attempts on Windows were not acceptable for this setup

### Stage 3: after torch overlay succeeded, Isaac Sim packaged Python dependencies drifted

That exposed the need for package routing and priority control in `sitecustomize.py`.

### Stage 4: installation recovered, but runtime compilation still failed

That led to the explicit JIT / NVRTC compatibility downgrades.

### Stage 5: full app runtime still had Warp instability

That made it clear the stack needed more than install fixes. It needed runtime-path discipline.

### Stage 6: once fallback paths ran, hidden joint-state problems surfaced

The 7-vs-9 mismatch then became the main issue.

### Stage 7: after the joint-state mapping was fixed, GUI planning still reported `FINETUNE_TRAJOPT_FAIL`

That turned out to be a compatibility gap, not a total planning failure.

### Stage 8: migrate smoke-only compatibility into the formal entry

This was the critical productization step:

- do not keep the stable logic in smoke only
- move it into the script people will actually use long term

## 7. Recommended current validation and usage path

### Reinstall or repair cuRobo

```powershell
cd <REPO_ROOT>
.\install_in_isaacsim.bat
```

### Validate the installation chain

```powershell
.\verify_isaacsim_integration.bat
```

### Run the formal standalone demo

```powershell
.\run_isaacsim_curobo_demo.bat
```

### Run GUI-internal workflows

Use the in-app scripts through:

- `Isaac Sim Full -> Window -> Script Editor`

## 8. Most important engineering conclusions

### 8.1 On RTX 50 / `sm_120`, older Isaac Sim bundled torch is not enough by itself

You need a compatibility strategy, not optimism.

### 8.2 Rebuilding cuRobo CUDA extensions locally on this machine is the wrong default

The right default is to reuse the existing Windows prebuilt native extensions.

### 8.3 Do not let pip casually replace Isaac Sim bundled binary dependencies

Especially not when those packages are tightly coupled to Isaac Sim shipped extensions.

### 8.4 Franka planning here is really 7 active joints, not the full 9 articulation layout

That distinction must stay explicit.

### 8.5 In the full GUI path, `FINETUNE_TRAJOPT_FAIL` is not automatically a total failure

You must inspect whether a usable pre-finetune trajectory exists.

### 8.6 Compatibility logic must live in formal scripts, not only in smoke demos

That was one of the most important structural fixes in this work.

## 9. Maintenance recommendations

### 9.1 Do not casually do the following

- do not remove the wrapper scripts
- do not revert the build guards in `setup.py`
- do not remove the runtime compatibility downgrades without revalidation
- do not force local native rebuilds unless you explicitly know why

### 9.2 If you upgrade Isaac Sim or cuRobo later

Re-check all of the following:

- Python path exposure
- native extension loading
- runtime compilation behavior
- smoke validation
- GUI planning behavior
- joint state mapping assumptions

### 9.3 If you want to productize the repair further

The next step is not “more patching”.

It is to keep:

- a stable wrapper
- a stable validation path
- stable formal entries
- stable documentation

and to continue moving compatibility logic out of demos and into shared modules and formal workflows.

## 10. Conclusion

The final working stack was not achieved by a single fix.

It required:

- installation repair
- build-logic repair
- runtime compatibility downgrades
- Windows native loading fixes
- explicit joint-state mapping
- formal migration of smoke-validated planning compatibility

That is why the current repository should be treated as a maintained, repaired delivery, not as a raw upstream checkout.
