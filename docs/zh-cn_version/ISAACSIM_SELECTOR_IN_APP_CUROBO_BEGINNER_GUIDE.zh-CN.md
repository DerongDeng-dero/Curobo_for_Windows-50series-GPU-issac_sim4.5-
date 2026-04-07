# Isaac Sim 正常启动并在软件内使用 cuRobo 的小白完整指南

## 1. 先回答你的核心问题

### 1.1 可以不可以正常通过 `isaac-sim.selector.bat` 启动，然后在软件内使用 cuRobo？

可以。

而且从你现在这套环境看，**这是完全合理的使用方式**。

你之前看到我更多用下面这些方式：

- `verify_isaacsim_integration.bat`
- `run_isaacsim_curobo_demo.bat`
- `isaac-sim.bat --exec ...`

并不是因为 `selector.bat` 不能用，而是因为：

1. 我当时主要在做“安装修复”和“自动回归验证”
2. 自动验证最适合用一条命令直接启动并执行脚本
3. 仓库里很多示例脚本本身是 **standalone 脚本**，它们会自己创建 `SimulationApp`
4. 这类脚本不适合在一个已经打开的 Isaac Sim GUI 里再次执行

所以真正的区别不是：

- `selector.bat` 能不能用

而是：

- 你运行的是 **standalone 脚本**
- 还是 **in-app 脚本**

这是小白最容易混淆、但也是最关键的概念。

---

## 2. 你要先理解的一个最重要概念

## 2.1 Isaac Sim + cuRobo 脚本其实分两类

### 第一类：standalone 脚本

特点：

- 脚本自己会启动 Isaac Sim
- 脚本里通常会出现 `SimulationApp(...)`
- 适合用命令行直接运行

例如：

- [`examples/isaac_sim/motion_gen_reacher.py`](../../examples/isaac_sim/motion_gen_reacher.py)
- [`examples/isaac_sim/simple_stacking.py`](../../examples/isaac_sim/simple_stacking.py)

这类脚本适合这样运行：

```powershell
.\run_isaacsim_curobo_demo.bat
```

或者：

```powershell
D:\isaac-sim\isaac-sim.bat --exec D:\isaac-sim\zzcurobo\curobo_for_windows\examples\isaac_sim\motion_gen_reacher.py
```

### 第二类：in-app 脚本

特点：

- Isaac Sim 已经启动好了
- 脚本只是在“已经打开的 GUI 里”执行
- 脚本不会自己创建 `SimulationApp`
- 适合从 Script Editor 里运行

例如：

- [`examples/isaac_sim/gui_motion_gen_smoke.py`](../../examples/isaac_sim/gui_motion_gen_smoke.py)
- [`examples/isaac_sim/gui_in_app_motion_gen_beginner.py`](../../examples/isaac_sim/gui_in_app_motion_gen_beginner.py)

这类脚本适合这样用：

1. 先双击或运行 `D:\isaac-sim\isaac-sim.selector.bat`
2. 在选择器里进入 `Isaac Sim Full`
3. 打开 `Window > Script Editor`
4. 载入脚本并执行

---

## 3. 为什么你现在通过 selector 正常启动后，也能看到 cuRobo

这是因为你当前环境已经不是原始裸环境了，而是已经被修好过。

关键链路是：

1. [`isaac-sim.selector.bat`](../../../../isaac-sim.selector.bat)
   - 会调用 [`setup_python_env.bat`](../../../../setup_python_env.bat)
2. [`setup_python_env.bat`](../../../../setup_python_env.bat)
   - 会把 `D:\isaac-sim\site` 放进 Python extra path
3. [`site/sitecustomize.py`](../../../../site/sitecustomize.py)
   - 会继续把 `python_packages` 挂进解释器路径
   - 还会处理 `numpy` / `PIL` 的优先级
4. 你已经通过：
   - [`install_in_isaacsim.bat`](../../install_in_isaacsim.bat)
   - 把 cuRobo 安装进这套 Isaac Sim Python 环境

所以结论是：

- **只要你从这份 `D:\isaac-sim` 里的启动器启动**
- **并且之前已经安装好 cuRobo**

那么通过 selector 启动后的 GUI，理论上就应该能导入 `curobo`

---

## 4. 三种最常见的使用方式，你该选哪一个

## 4.1 方式 A：最小验收

适合：

- 你刚装好环境
- 你想先确认有没有坏

命令：

```powershell
cd D:\isaac-sim\zzcurobo\curobo_for_windows
.\verify_isaacsim_integration.bat
```

作用：

- 跑 headless smoke
- 不需要你手动点 GUI

## 4.2 方式 B：一键启动正式示例

适合：

- 你想快速进入正式示例
- 不想手动打开 Script Editor

命令：

```powershell
cd D:\isaac-sim\zzcurobo\curobo_for_windows
.\run_isaacsim_curobo_demo.bat
```

当前默认会启动：

- [`examples/isaac_sim/motion_gen_reacher.py`](../../examples/isaac_sim/motion_gen_reacher.py)

## 4.3 方式 C：正常通过 selector 启动，然后在软件里运行 cuRobo

适合：

- 你想按正常 GUI 工作流操作
- 你想边看界面边改脚本
- 你想一点点搭场景，而不是全自动跑完

这就是本篇文档重点讲的方式。

---

## 5. 小白先做的第一步：先确认环境没坏

请先做下面两步。

## 5.1 安装 / 补装

```powershell
cd D:\isaac-sim\zzcurobo\curobo_for_windows
.\install_in_isaacsim.bat
```

## 5.2 验证

```powershell
.\verify_isaacsim_integration.bat
```

你至少要看到类似：

```text
Smoke test passed.
```

如果这里都没过，就不要直接进入 GUI 操作。

先把基础链路修通，再做下一步。

---

## 6. 正常通过 selector 启动 Isaac Sim 的完整步骤

## 6.1 启动 selector

运行：

```powershell
D:\isaac-sim\isaac-sim.selector.bat
```

或者在资源管理器里双击它。

## 6.2 在选择器里选哪个 App

请选择：

- `Isaac Sim Full`

不建议小白一开始就选：

- streaming
- websocket
- 其他远程模式

原因：

- 本地调试最稳定的是 Full
- 出问题时最容易判断

## 6.3 进入 GUI 后建议先打开哪些窗口

建议先确认下面几个窗口可见：

- `Window > Stage`
- `Window > Content`
- `Window > Console`
- `Window > Extensions`

等你后面要在软件里执行 Python 时，还需要：

- `Window > Script Editor`

如果 `Window > Script Editor` 看不到，继续下一步。

---

## 7. 如何在 GUI 里打开 Script Editor

## 7.1 如果菜单里已经有

直接点：

- `Window > Script Editor`

## 7.2 如果菜单里没有

按下面步骤启用扩展：

1. 打开 `Window > Extensions`
2. 搜索：
   - `script editor`
3. 找到扩展：
   - `omni.kit.window.script_editor`
4. 点启用
5. 再回到：
   - `Window > Script Editor`

这个扩展在你当前环境里是存在的。

---

## 8. 先做最小导入测试，确认 GUI 内真的能看到 cuRobo

## 8.1 打开 Script Editor

在里面新建一个脚本，粘贴下面内容：

```python
import sys
import torch
import curobo

print("torch:", torch.__file__)
print("curobo:", curobo.__file__)
print("python path count:", len(sys.path))
```

点击运行。

## 8.2 你应该看到什么

理想情况：

- 不报错
- 能打印出 `torch` 路径
- 能打印出 `curobo` 路径

如果这里就报：

- `ModuleNotFoundError: No module named 'curobo'`

那通常说明：

1. 你没有先运行 `install_in_isaacsim.bat`
2. 你不是从这份 `D:\isaac-sim` 的启动器进入的
3. 当前环境被别的 Python 路径污染了

---

## 9. 在 GUI 内跑一个真正能动起来的 cuRobo 入门脚本

## 9.1 不要在已经打开的 GUI 里直接运行这些脚本

不要直接在 Script Editor 里跑下面这些：

- [`motion_gen_reacher.py`](../../examples/isaac_sim/motion_gen_reacher.py)
- [`simple_stacking.py`](../../examples/isaac_sim/simple_stacking.py)

原因：

- 它们是 standalone 脚本
- 里面会自己创建 `SimulationApp`
- 而你当前 GUI 已经有一个 Isaac Sim 进程在运行了

这就是很多人“明明 GUI 都打开了，脚本却跑不对”的根因。

## 9.2 正确做法：运行 in-app 入门脚本

请运行这个文件：

- [`examples/isaac_sim/gui_in_app_motion_gen_beginner.py`](../../examples/isaac_sim/gui_in_app_motion_gen_beginner.py)

操作步骤：

1. 打开 `Window > Script Editor`
2. 选择 `Open`
3. 打开文件：
   - `D:\isaac-sim\zzcurobo\curobo_for_windows\examples\isaac_sim\gui_in_app_motion_gen_beginner.py`
4. 点击运行

## 9.3 这个脚本会帮你做什么

它会自动：

1. 新建一个干净的 stage
2. 创建 `/World`
3. 导入 Franka 机器人
4. 放一个红色目标块
5. 放一个简单障碍物
6. 构建 `MotionGen`
7. 执行一次规划
8. 把轨迹回放到机器人上

这就是“在已经打开的 Isaac Sim 里，正常使用 cuRobo”的最基础闭环。

---

## 10. 这一步跑通后，你在界面里应该看到什么

你应该能看到：

- 一个 Franka 机械臂
- 一个红色目标块
- 一个障碍物
- 机械臂从初始位姿运动到目标附近

Console 里应该看到类似：

```text
IN_APP_BEGINNER: robot imported at ...
IN_APP_BEGINNER: extracted 1 obstacle(s) from stage
IN_APP_BEGINNER: motion generator warmed up
IN_APP_BEGINNER: planning success, trajectory points=...
IN_APP_BEGINNER: trajectory playback finished
```

---

## 11. 跑通以后，怎么继续搭建你自己的仿真场景

下面按“小白能理解”的方式讲。

## 11.1 你要搭一个 cuRobo 仿真场景，本质上就是 6 件事

1. 启动 Isaac Sim
2. 创建或加载场景
3. 把机器人放进去
4. 把障碍物放进去
5. 让 cuRobo 读取当前 world
6. 给一个目标姿态，然后规划并执行

你只要一直围绕这 6 件事组织脚本，就不会乱。

## 11.2 推荐你从哪里开始改

不要一上来就改正式大脚本。

推荐顺序是：

1. 先改 [`gui_in_app_motion_gen_beginner.py`](../../examples/isaac_sim/gui_in_app_motion_gen_beginner.py)
2. 再理解 [`gui_motion_gen_smoke.py`](../../examples/isaac_sim/gui_motion_gen_smoke.py)
3. 最后再去读 [`motion_gen_reacher.py`](../../examples/isaac_sim/motion_gen_reacher.py)

原因：

- beginner 脚本最短
- smoke 脚本更接近真实兼容逻辑
- `motion_gen_reacher.py` 更像正式交互式主脚本，逻辑更长

---

## 12. 你改场景时，通常改哪几个地方

## 12.1 改机器人

先从：

- `ROBOT_CFG_NAME = "franka.yml"`

改成你自己的 robot yaml。

前提是：

- 你的 robot yaml 已经存在
- 它引用的 URDF / USD / mesh 路径都是对的

## 12.2 改目标

改这两个变量：

```python
GOAL_POSITION = [0.45, 0.0, 0.35]
GOAL_QUATERNION = [1.0, 0.0, 0.0, 0.0]
```

这对应的是：

- 末端目标位置
- 末端目标姿态

## 12.3 改障碍物

脚本里这一段就是障碍物：

```python
stage_world = WorldConfig(
    cuboid=[
        Cuboid(
            name="beginner_obstacle",
            pose=[1.1, 0.0, 0.25, 1.0, 0.0, 0.0, 0.0],
            dims=[0.1, 0.4, 0.5],
        )
    ]
)
```

你可以改：

- `pose`
- `dims`
- 甚至增加多个 `Cuboid`

## 12.4 改规划参数

脚本里最常改的是：

- `interpolation_dt`
- `num_ik_seeds`
- `num_trajopt_seeds`
- `trajopt_tsteps`
- `max_attempts`
- `timeout`

小白建议：

- 先别乱改太多
- 先只改 `max_attempts` 和 `timeout`

---

## 13. 如果你想在软件里“手动摆场景”，然后再让 cuRobo 读进去

这也是完全可以的。

## 13.1 推荐流程

1. 先通过 selector 进入 `Isaac Sim Full`
2. 用 GUI 手动拖模型、加桌子、加盒子、摆障碍物
3. 保存 stage
4. 再写一个 in-app 脚本，让 `UsdHelper` 从当前 stage 读取障碍物
5. 调 `motion_gen.update_world(...)`
6. 再规划

## 13.2 你要理解的一点

cuRobo 不会“自动知道 GUI 里有什么东西”。

它要么：

- 你用代码手动构造 `WorldConfig`

要么：

- 你让它从 USD stage 中读取障碍物

所以：

- “界面里看得到”

不等于：

- “cuRobo 已经拿来做碰撞检测了”

你仍然要走：

- `UsdHelper.get_obstacles_from_stage(...)`

这一步。

---

## 14. 为什么我们现在还保留 wrapper，而不是只讲 selector

因为 selector 适合“人工操作”。

而 wrapper 适合：

- 自动执行脚本
- 自动写日志
- 自动回归验证
- 避免你每次都手动点按钮

所以三种入口最好都保留：

1. `verify_isaacsim_integration.bat`
   - 做基础验收
2. `run_isaacsim_curobo_demo.bat`
   - 做一键正式示例
3. `isaac-sim.selector.bat`
   - 做正常 GUI 工作流

它们不是互斥关系，而是分工不同。

---

## 15. 继续搭建场景时，我建议你的目录和脚本怎么组织

## 15.1 最推荐的方式

把你自己的脚本分成两类：

### A. in-app 脚本

用途：

- 在已经打开的 GUI 里运行
- 适合你边看界面边调

建议命名：

- `my_scene_in_app.py`
- `my_pick_place_in_app.py`

### B. standalone 脚本

用途：

- 一条命令直接启动并运行
- 适合回归和批量实验

建议命名：

- `my_scene_standalone.py`
- `my_pick_place_standalone.py`

## 15.2 小白常犯的错误

最常见的就是把这两类脚本混在一起。

比如：

- 先打开 GUI
- 然后在 Script Editor 里直接运行一个会创建 `SimulationApp` 的脚本

这通常就会出问题。

你以后只要记住这一句就够了：

- **已经打开 GUI，就运行 in-app 脚本**
- **还没打开 GUI，就运行 standalone 脚本**

---

## 16. 推荐你的实际学习顺序

按照下面顺序走，最稳：

1. 先跑：
   - [`verify_isaacsim_integration.bat`](../../verify_isaacsim_integration.bat)
2. 再跑：
   - [`run_isaacsim_curobo_demo.bat`](../../run_isaacsim_curobo_demo.bat)
3. 然后通过：
   - [`isaac-sim.selector.bat`](../../../../isaac-sim.selector.bat)
   - 正常进入 GUI
4. 在 Script Editor 里跑：
   - [`gui_in_app_motion_gen_beginner.py`](../../examples/isaac_sim/gui_in_app_motion_gen_beginner.py)
5. 改目标位置、障碍物尺寸，再重复运行
6. 再开始改成你自己的 robot / scene / task

---

## 17. 常见报错与最直白解释

## 17.1 `No module named 'curobo'`

说明：

- 还没安装好
- 或者不是从这份修好的 Isaac Sim 环境启动

做法：

```powershell
cd D:\isaac-sim\zzcurobo\curobo_for_windows
.\install_in_isaacsim.bat
.\verify_isaacsim_integration.bat
```

## 17.2 `No module named 'helper'`

说明：

- 你在 Script Editor 里直接复制粘贴了部分代码
- 但没有把 `examples/isaac_sim` 所在目录加进 `sys.path`

做法：

- 直接 `Open` 整个脚本文件执行
- 或在脚本开头加入目录注入逻辑

## 17.3 `SimulationApp` 相关报错

说明：

- 你把 standalone 脚本拿到 GUI 内执行了

做法：

- 换成 in-app 脚本

## 17.4 `nvrtc: error: invalid value for --gpu-architecture (-arch)`

说明：

- 这是旧 runtime / 新显卡的经典兼容问题

做法：

- 不要自己删掉当前仓库里的兼容层
- 优先复用当前脚本里的共享兼容模块：
  - [`motion_gen_compat.py`](../../examples/isaac_sim/motion_gen_compat.py)

## 17.5 `FINETUNE_TRAJOPT_FAIL`

说明：

- 不一定是完全失败
- 可能只是 finetune 没过，但主轨迹已经有了

做法：

- 用当前已经接好的兼容入口
- 不要再用最原始的裸 `plan_single(...)` 失败判定

---

## 18. 你现在最推荐怎么做

如果你是小白，我建议你从今天开始按这个节奏来：

### 第一天

- 跑安装
- 跑 headless 验证
- 通过 selector 进 GUI
- 在 Script Editor 里跑 `gui_in_app_motion_gen_beginner.py`

### 第二天

- 改目标位置
- 改障碍物
- 重复跑
- 看 cuRobo 是否还能规划成功

### 第三天

- 把 Franka 替换成你的机器人
- 保留同样的 in-app 架构

### 第四天以后

- 再考虑做抓取、放置、状态机、相机、传感器、完整任务

---

## 19. 本文档最短结论

一句话版本：

- **可以正常通过 `isaac-sim.selector.bat` 启动，然后在软件里使用 cuRobo。**

但前提是你要分清：

- `motion_gen_reacher.py` 这种是 standalone
- `gui_in_app_motion_gen_beginner.py` 这种才是适合 GUI 内执行的 in-app 脚本

如果你想要“正常打开软件，然后像普通用户一样在界面里用 cuRobo”，那你接下来应该用的就是：

1. `isaac-sim.selector.bat`
2. `Isaac Sim Full`
3. `Window > Script Editor`
4. 运行 [`gui_in_app_motion_gen_beginner.py`](../../examples/isaac_sim/gui_in_app_motion_gen_beginner.py)

这就是最适合小白理解、也最接近正常软件操作习惯的一条路径。

