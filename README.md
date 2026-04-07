<!--
Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.

NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
property and proprietary rights in and to this material, related
documentation and any modifications thereto. Any use, reproduction,
disclosure or distribution of this material and related documentation
without an express license agreement from NVIDIA CORPORATION or
its affiliates is strictly prohibited.
-->
# cuRobo for Windows + Isaac Sim 4.5

*CUDA Accelerated Robot Library with a Windows-focused Isaac Sim workflow*

This repository keeps the upstream cuRobo codebase while adding a practical
Windows + Isaac Sim 4.5 path for:

- installation on recent NVIDIA RTX Windows machines
- standalone Isaac Sim motion-generation entry points
- in-app Script Editor workflows inside Isaac Sim Full
- pick/place state-machine templates
- loading your own USD scene, including reusing an existing robot articulation
- bilingual Chinese / English documentation for setup, usage, and maintenance

[Legacy workspace note for Windows](workspace_win/readme.md)

## What This Fork Adds

- Windows installation helpers: `install_in_isaacsim.bat`, `verify_isaacsim_integration.bat`
- Standalone launchers: `isaacsim_python.bat`, `run_isaacsim_curobo_demo.bat`
- Shared planning compatibility layer for Isaac Sim examples under `examples/isaac_sim`
- GUI in-app templates for beginner motion generation, custom scenes, pick/place, and USD scene reuse
- Full bilingual docs under `docs/zh-cn_version` and `docs/en_version`

## Recommended Starting Points

- If you need installation from scratch on Windows: start with the tutorial docs below
- If you already have Isaac Sim running and want an in-app workflow: start with the Selector / in-app beginner guide
- If you want to reuse your own USD scene: go directly to the USD scene pick/place workflow guide
- If you want the main standalone scene demo: run `examples/isaac_sim/simple_stacking.py`

## Documentation

Chinese:

- [Reading order and overview](docs/zh-cn_version/DOCS_READING_ORDER_AND_OVERVIEW.zh-CN.md)
- [Windows + Isaac Sim 4.5+ full tutorial](docs/zh-cn_version/WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.zh-CN.md)
- [Installable version manual](docs/zh-cn_version/INSTALLABLE_VERSION_MANUAL.zh-CN.md)
- [Selector + in-app cuRobo beginner guide](docs/zh-cn_version/ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.zh-CN.md)
- [Custom scene workflow beginner guide](docs/zh-cn_version/ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.zh-CN.md)
- [Pick-place state machine and scene modeling guide](docs/zh-cn_version/ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.zh-CN.md)
- [Load your own USD scene, reuse an existing articulation, and attach the pick-place state machine guide](docs/zh-cn_version/ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.zh-CN.md)
- [Full repair log and maintenance guide](docs/zh-cn_version/curobo_isaacsim_windows_full_fix_guide.zh-CN.md)

English:

- [Reading order and overview](docs/en_version/DOCS_READING_ORDER_AND_OVERVIEW.en.md)
- [Windows + Isaac Sim 4.5+ full tutorial](docs/en_version/WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.en.md)
- [Installable version manual](docs/en_version/INSTALLABLE_VERSION_MANUAL.en.md)
- [Selector + in-app cuRobo beginner guide](docs/en_version/ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.en.md)
- [Custom scene workflow beginner guide](docs/en_version/ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.en.md)
- [Pick-place state machine and scene modeling guide](docs/en_version/ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.en.md)
- [Load your own USD scene, reuse an existing articulation, and attach the pick-place state machine guide](docs/en_version/ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md)
- [Full repair log and maintenance guide](docs/en_version/curobo_isaacsim_windows_full_fix_guide.en.md)

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

This launcher now defaults to `examples/isaac_sim/motion_gen_reacher.py`, while smoke validation remains available through `examples/isaac_sim/gui_motion_gen_smoke.py` and `run_gui_smoke_capture.ps1`.

**Check [curobo.org](https://curobo.org) for installing and getting started with examples!**

Use [Discussions](https://github.com/NVlabs/curobo/discussions) for questions on using this package.

Use [Issues](https://github.com/NVlabs/curobo/issues) if you find a bug.


cuRobo's collision-free motion planner is available for commercial applications as a
MoveIt plugin: [Isaac ROS cuMotion](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_cumotion)

For business inquiries of this python library, please visit our website and submit the form: [NVIDIA Research Licensing](https://www.nvidia.com/en-us/research/inquiries/)


## Overview

cuRobo is a CUDA accelerated library containing a suite of robotics algorithms that run significantly faster than existing implementations leveraging parallel compute. cuRobo currently provides the following algorithms: (1) forward and inverse kinematics,
(2) collision checking between robot and world, with the world represented as Cuboids, Meshes, and Depth images, (3) numerical optimization with gradient descent, L-BFGS, and MPPI, (4) geometric planning, (5) trajectory optimization, (6) motion generation that combines inverse kinematics, geometric planning, and trajectory optimization to generate global motions within 30ms.

<p align="center">
<img width="500" src="images/robot_demo.gif">
</p>


cuRobo performs trajectory optimization across many seeds in parallel to find a solution. cuRobo's trajectory optimization penalizes jerk and accelerations, encouraging smoother and shorter trajectories. Below we compare cuRobo's motion generation on the left to a BiRRT planner for the motion planning phases in a pick and place task.

<p align="center">
<img width="500" src="images/rrt_compare.gif">
</p>


## Citation

If you found this work useful, please cite the below report,

```
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
