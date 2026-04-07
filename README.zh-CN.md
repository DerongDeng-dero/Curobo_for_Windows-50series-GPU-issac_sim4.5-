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

# cuRobo for Windows + Isaac Sim 4.5

*面向 Windows + Isaac Sim 工作流整理的 CUDA 机器人运动规划库*

这个仓库保留了上游 cuRobo 的主体代码，同时补齐了一套更适合 Windows + Isaac Sim 4.5 的实际使用路径，包括：

- 适用于新款 NVIDIA RTX Windows 机器的安装流程
- standalone 模式的 Isaac Sim 运动规划入口
- Isaac Sim Full 内 `Script Editor` 的 in-app 工作流
- pick/place 状态机模板
- 加载自己的 USD 场景，并直接复用场景里已有机器人 articulation
- 中英文双语文档体系，覆盖安装、使用、维护和排障

[Windows 历史工作区说明](workspace_win/readme.md)

## 这个分支额外补了什么

- Windows 安装与校验脚本：`install_in_isaacsim.bat`、`verify_isaacsim_integration.bat`
- Standalone 启动脚本：`isaacsim_python.bat`、`run_isaacsim_curobo_demo.bat`
- `examples/isaac_sim` 下统一的 Isaac Sim 兼容规划层
- GUI 内可直接运行的入门模板、自定义场景模板、抓放状态机模板、USD 场景复用模板
- 放在 `docs/zh-cn_version` 和 `docs/en_version` 下的完整双语文档

## 推荐从哪里开始

- 如果你要从零安装 Windows 版本：先看下面的安装教程文档
- 如果你已经能打开 Isaac Sim，想直接在软件里用：先看 selector / in-app 入门文档
- 如果你要复用自己的 USD 场景：直接看 USD 场景 pick/place 工作流文档
- 如果你要先运行主场景示例：直接运行 `examples/isaac_sim/simple_stacking.py`

## 中文文档

- [文档阅读顺序与总览](docs/zh-cn_version/DOCS_READING_ORDER_AND_OVERVIEW.zh-CN.md)
- [Windows + Isaac Sim 4.5+ 完整安装教程](docs/zh-cn_version/WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.zh-CN.md)
- [可安装版本使用手册](docs/zh-cn_version/INSTALLABLE_VERSION_MANUAL.zh-CN.md)
- [Selector + 软件内使用 cuRobo 小白指南](docs/zh-cn_version/ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.zh-CN.md)
- [自定义场景工作流入门指南](docs/zh-cn_version/ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.zh-CN.md)
- [抓取 / 放置状态机与场景建模指南](docs/zh-cn_version/ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.zh-CN.md)
- [加载自己的 USD 场景、复用现有 articulation 并接入抓放状态机指南](docs/zh-cn_version/ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.zh-CN.md)
- [完整修复记录与维护指南](docs/zh-cn_version/curobo_isaacsim_windows_full_fix_guide.zh-CN.md)

## English Documentation

- [English landing page](README.md)
- [Reading order and overview](docs/en_version/DOCS_READING_ORDER_AND_OVERVIEW.en.md)
- [Windows + Isaac Sim 4.5+ full tutorial](docs/en_version/WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.en.md)
- [Installable version manual](docs/en_version/INSTALLABLE_VERSION_MANUAL.en.md)
- [Selector + in-app cuRobo beginner guide](docs/en_version/ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.en.md)
- [Custom scene workflow beginner guide](docs/en_version/ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.en.md)
- [Pick-place state machine and scene modeling guide](docs/en_version/ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.en.md)
- [Load your own USD scene, reuse an existing articulation, and attach the pick-place state machine guide](docs/en_version/ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md)
- [Full repair log and maintenance guide](docs/en_version/curobo_isaacsim_windows_full_fix_guide.en.md)

## Windows / Isaac Sim 快速开始

```powershell
cd D:\isaac-sim\zzcurobo\curobo_for_windows
.\install_in_isaacsim.bat
.\verify_isaacsim_integration.bat
```

## Windows / Isaac Sim 演示启动

```powershell
cd D:\isaac-sim\zzcurobo\curobo_for_windows
.\run_isaacsim_curobo_demo.bat
```

这个启动脚本现在默认进入 `examples/isaac_sim/motion_gen_reacher.py`，而 smoke 校验入口仍然保留在 `examples/isaac_sim/gui_motion_gen_smoke.py`。

## 项目概览

cuRobo 是一个 CUDA 加速的机器人算法库，目标是在并行计算下，把常见机器人运动学、碰撞检测和轨迹优化做得比传统实现更快。当前主要包括：

1. 正向运动学和逆向运动学
2. 机器人与环境之间的碰撞检测，环境可表示为 cuboid、mesh、depth image
3. 基于梯度下降、L-BFGS、MPPI 的数值优化
4. 几何规划
5. 轨迹优化
6. 将 IK、几何规划和轨迹优化组合起来的全局运动生成

<p align="center">
<img width="500" src="images/robot_demo.gif">
</p>

cuRobo 会并行评估多组 seed 轨迹来寻找可行解，并通过对 jerk 和 acceleration 进行惩罚得到更平滑、更短的轨迹。下面的对比图展示了 cuRobo 与 BiRRT 在 pick/place 任务中的规划差异。

<p align="center">
<img width="500" src="images/rrt_compare.gif">
</p>

## 上游参考

- [curobo.org](https://curobo.org)
- [NVlabs/curobo Discussions](https://github.com/NVlabs/curobo/discussions)
- [NVlabs/curobo Issues](https://github.com/NVlabs/curobo/issues)
- [Isaac ROS cuMotion](https://github.com/NVIDIA-ISAAC-ROS/isaac_ros_cumotion)
- [NVIDIA Research Licensing](https://www.nvidia.com/en-us/research/inquiries/)

## 引用

如果这个项目对你有帮助，可以引用下面这篇报告：

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
