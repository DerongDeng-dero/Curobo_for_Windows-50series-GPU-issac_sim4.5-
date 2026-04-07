<!--
Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.

NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
property and proprietary rights in and to this material, related
documentation and any modifications thereto. Any use, reproduction,
disclosure or distribution of this material and related documentation
without an express license agreement from NVIDIA CORPORATION or
its affiliates is strictly prohibited.
-->

[![EN](https://img.shields.io/badge/README-EN-2563eb?style=for-the-badge)](./README.md)
[![ZH-CN](https://img.shields.io/badge/README-ZH--CN-16a34a?style=for-the-badge)](./README.zh-CN.md)

[![Docs Hub](https://img.shields.io/badge/Docs-Hub-0f766e?style=flat-square)](./docs/README.md)
[![GPU](https://img.shields.io/badge/GPU-NVIDIA%20RTX%2050--Series-16a34a?style=flat-square)](#repository-scope)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=flat-square)](#windows--isaac-sim-quick-start)
[![Isaac Sim](https://img.shields.io/badge/Isaac%20Sim-4.5%2B-76B900?style=flat-square)](#repository-scope)
[![Workflow](https://img.shields.io/badge/Workflow-cuRobo%20%2B%20Isaac%20Sim-111827?style=flat-square)](./docs/README.md)

# cuRobo for Windows + NVIDIA RTX 50-Series + Isaac Sim 4.5+

*CUDA Accelerated Robot Library with a Windows-focused Isaac Sim workflow*

This fork keeps the upstream cuRobo codebase while adding a practical
Windows + NVIDIA GeForce RTX 50-series + Isaac Sim 4.5+ path for installation, standalone scripts, in-app
Script Editor workflows, pick/place teaching templates, and
USD-scene-driven robot planning.

[Legacy workspace note for Windows](workspace_win/readme.md)

## Quick Links

- [Docs Hub](./docs/README.md)
- [Chinese landing page](./README.zh-CN.md)
- [Chinese docs hub](./docs/README.zh-CN.md)
- [Main standalone scene demo](./examples/isaac_sim/simple_stacking.py)
- [USD scene reuse template](./examples/isaac_sim/gui_in_app_pick_place_from_usd_template.py)

## Repository Scope

This repository is primarily maintained for:

- recent NVIDIA GeForce RTX 50-series GPUs on Windows
- Isaac Sim 4.5 and later

That is the main compatibility target for the installation path, the repaired
Python wrappers, the prebuilt extension loading path, and the Isaac Sim example
workflows in this fork.

## What This Fork Adds

- Windows installation helpers: `install_in_isaacsim.bat`, `verify_isaacsim_integration.bat`
- Standalone launchers: `isaacsim_python.bat`, `run_isaacsim_curobo_demo.bat`
- Shared Isaac Sim planning compatibility under `examples/isaac_sim`
- GUI in-app templates for custom scenes, pick/place, and USD scene reuse
- Bilingual Chinese / English documentation under `docs/zh-cn_version` and `docs/en_version`

## Recommended Starting Points

- If you need installation from scratch on Windows, start with the [Windows + Isaac Sim 4.5+ tutorial for RTX 50-series GPUs](./docs/en_version/WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.en.md)
- If you already have Isaac Sim running and want an in-app workflow, start with the [Selector + in-app beginner guide](./docs/en_version/ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.en.md)
- If you want to reuse your own USD scene, go directly to the [USD scene pick/place workflow guide](./docs/en_version/ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md)
- If you want the complete reading order, use the [docs hub](./docs/README.md)

## Documentation

English:

- [Docs hub](./docs/README.md)
- [Reading order and overview](./docs/en_version/DOCS_READING_ORDER_AND_OVERVIEW.en.md)
- [Installable version manual](./docs/en_version/INSTALLABLE_VERSION_MANUAL.en.md)
- [Full repair log and maintenance guide](./docs/en_version/curobo_isaacsim_windows_full_fix_guide.en.md)

Chinese:

- [Chinese landing page](./README.zh-CN.md)
- [Chinese docs hub](./docs/README.zh-CN.md)
- [Reading order and overview](./docs/zh-cn_version/DOCS_READING_ORDER_AND_OVERVIEW.zh-CN.md)
- [Full repair log and maintenance guide](./docs/zh-cn_version/curobo_isaacsim_windows_full_fix_guide.zh-CN.md)

## Windows / Isaac Sim Quick Start

```powershell
cd D:\isaac-sim\zzcurobo\curobo_for_windows
.\install_in_isaacsim.bat
.\verify_isaacsim_integration.bat
```

## Windows / Isaac Sim Demo Launch

```powershell
cd D:\isaac-sim\zzcurobo\curobo_for_windows
.\run_isaacsim_curobo_demo.bat
```

This launcher now defaults to `examples/isaac_sim/motion_gen_reacher.py`, while smoke validation remains available through `examples/isaac_sim/gui_motion_gen_smoke.py`.

## Overview

cuRobo is a CUDA accelerated library containing a suite of robotics algorithms
that run significantly faster than existing implementations leveraging
parallel compute. It currently provides:

1. forward and inverse kinematics
2. collision checking between robot and world, with the world represented as cuboids, meshes, and depth images
3. numerical optimization with gradient descent, L-BFGS, and MPPI
4. geometric planning
5. trajectory optimization
6. motion generation that combines inverse kinematics, geometric planning, and trajectory optimization to generate global motions within 30ms

<p align="center">
<img width="500" src="images/robot_demo.gif">
</p>

cuRobo performs trajectory optimization across many seeds in parallel to find a
solution. Its trajectory optimization penalizes jerk and accelerations,
encouraging smoother and shorter trajectories.

<p align="center">
<img width="500" src="images/rrt_compare.gif">
</p>

## Upstream References

- [curobo.org](https://curobo.org)
- [NVlabs/curobo discussions](https://github.com/NVlabs/curobo/discussions)
- [NVlabs/curobo issues](https://github.com/NVlabs/curobo/issues)
- [Isaac ROS cuMotion](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_cumotion)
- [NVIDIA Research Licensing](https://www.nvidia.com/en-us/research/inquiries/)

## Citation

If you found this work useful, please cite the report below:

```text
@misc{curobo_report23,
      title={cuRobo: Parallelized Collision-Free Minimum-Jerk Robot Motion Generation},
      author={Balakumar Sundaralingam and Siva Kumar Sastry Hari and Adam Fishman and Caelan Garrett
              and Karl Van Wyk and Valts Blukis and Alexander Millane and Helen Oleynikova and Ankur Handa
              and Fabio Ramos and Nathan Ratliff and Dieter Fox},
      year={2023},
      eprint={2310.17274},
      archivePrefix={arXiv},
      primaryClass={cs.RO}
}
```
