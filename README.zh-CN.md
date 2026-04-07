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

[![Docs Hub](https://img.shields.io/badge/Docs-Hub-0f766e?style=flat-square)](./docs/README.zh-CN.md)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D4?style=flat-square)](#windows--isaac-sim-快速开始)
[![Isaac Sim](https://img.shields.io/badge/Isaac%20Sim-4.5-76B900?style=flat-square)](#windows--isaac-sim-快速开始)
[![Workflow](https://img.shields.io/badge/Workflow-cuRobo%20%2B%20Isaac%20Sim-111827?style=flat-square)](./docs/README.zh-CN.md)

# cuRobo for Windows + Isaac Sim 4.5

*面向 Windows + Isaac Sim 工作流整理的 CUDA 机器人规划库*

这个仓库保留了上游 cuRobo 的主体代码，同时补齐了一套更适合
Windows + Isaac Sim 4.5 的实际使用路径，覆盖：

- Windows 安装与环境校验
- standalone 模式的 Isaac Sim 启动入口
- Isaac Sim Full 内 `Script Editor` 的 in-app 工作流
- pick/place 状态机模板
- 加载自己的 USD 场景，并复用场景里已有机器人 articulation
- 中英文双语文档体系

[Windows 历史工作区说明](./workspace_win/readme.md)

## 快速入口

- [文档总入口](./docs/README.zh-CN.md)
- [English landing page](./README.md)
- [English docs hub](./docs/README.md)
- [主场景 standalone 示例](./examples/isaac_sim/simple_stacking.py)
- [复用 USD 场景现有机器人的模板](./examples/isaac_sim/gui_in_app_pick_place_from_usd_template.py)

## 这个分支额外补了什么

- Windows 安装与校验脚本：`install_in_isaacsim.bat`、`verify_isaacsim_integration.bat`
- Standalone 启动脚本：`isaacsim_python.bat`、`run_isaacsim_curobo_demo.bat`
- `examples/isaac_sim` 下统一的 Isaac Sim 兼容规划层
- GUI 内可直接运行的入门模板、自定义场景模板、抓放状态机模板、USD 场景复用模板
- 放在 `docs/zh-cn_version` 和 `docs/en_version` 下的完整双语文档

## 推荐从哪里开始

- 如果你要从零安装 Windows 版本：先看[安装教程](./docs/zh-cn_version/WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.zh-CN.md)
- 如果你已经能打开 Isaac Sim，想直接在软件里使用：先看[Selector + 软件内使用 cuRobo 指南](./docs/zh-cn_version/ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.zh-CN.md)
- 如果你要复用自己的 USD 场景：直接看[USD 场景工作流指南](./docs/zh-cn_version/ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.zh-CN.md)
- 如果你想看完整阅读顺序：直接进入[文档总入口](./docs/README.zh-CN.md)

## 文档

中文：

- [文档总入口](./docs/README.zh-CN.md)
- [文档阅读顺序与总览](./docs/zh-cn_version/DOCS_READING_ORDER_AND_OVERVIEW.zh-CN.md)
- [可安装版本使用手册](./docs/zh-cn_version/INSTALLABLE_VERSION_MANUAL.zh-CN.md)
- [完整修复记录与维护指南](./docs/zh-cn_version/curobo_isaacsim_windows_full_fix_guide.zh-CN.md)

English:

- [English landing page](./README.md)
- [Docs hub](./docs/README.md)
- [Reading order and overview](./docs/en_version/DOCS_READING_ORDER_AND_OVERVIEW.en.md)
- [Full repair log and maintenance guide](./docs/en_version/curobo_isaacsim_windows_full_fix_guide.en.md)

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

这个启动脚本现在默认进入 `examples/isaac_sim/motion_gen_reacher.py`，smoke 校验入口仍然保留在 `examples/isaac_sim/gui_motion_gen_smoke.py`。

## 项目概览

cuRobo 是一个 CUDA 加速的机器人算法库，目标是在并行计算下，把常见
机器人运动学、碰撞检测和轨迹优化做得更快。当前主要包括：

1. 正向运动学和逆向运动学
2. 机器人与环境之间的碰撞检测，环境可表示为 cuboid、mesh、depth image
3. 基于梯度下降、L-BFGS、MPPI 的数值优化
4. 几何规划
5. 轨迹优化
6. 将 IK、几何规划和轨迹优化组合起来的全局运动生成

<p align="center">
<img width="500" src="images/robot_demo.gif">
</p>

cuRobo 会并行评估多组 seed 轨迹来寻找可行解，并通过对 jerk 和
acceleration 进行惩罚得到更平滑、更短的轨迹。

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
