# 新可安装版本说明书

## 1. 这是什么

这是这次整理出来的 Windows / Isaac Sim 版 cuRobo 安装工具集。

它当前主要面向：

- Windows
- 英伟达 RTX 50 系显卡
- Isaac Sim 4.5 及以上版本

目标不是“理论上能装”，而是：

- 一键安装
- 一键验证
- 尽量不依赖用户手工配环境
- 尽量兼容新显卡 + 旧 Isaac Sim 的组合

## 2. 包含哪些文件

### [`docs/DOCS_READING_ORDER_AND_OVERVIEW.zh-CN.md`](./DOCS_READING_ORDER_AND_OVERVIEW.zh-CN.md)

作用：

- 这是当前整套中文主文档的总导航。
- 它会把现有文档按逻辑顺序编号，并说明：
  - 每篇文档适合什么时候看
  - 每篇文档主要解决什么问题
  - 新手、进阶用户、维护者分别应该怎么走阅读路线

如果你现在面对很多文档，不知道先看哪篇，优先先看这篇。

### [`docs/ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.zh-CN.md`](./ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.zh-CN.md)

作用：

- 面向小白解释“为什么可以正常通过 selector 启动后再在软件内使用 cuRobo”
- 讲清 standalone 脚本和 in-app 脚本的区别
- 提供 GUI 内使用 cuRobo 的一步一步操作手册

如果你更关心：

- 正常打开 Isaac Sim GUI
- 在软件里点开 Script Editor
- 一边看界面一边跑 cuRobo

那优先看这篇文档。

### [`docs/ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.zh-CN.md`](./ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.zh-CN.md)

作用：

- 这是“已经会在 GUI 里跑 cuRobo，下一步如何改成自定义机器人和场景”的继续教程。
- 重点讲：
  - 如何换机器人
  - 如何改桌子和障碍物
  - 如何保持 cuRobo world 与 GUI 场景同步
  - 如何从单次规划过渡到自定义任务脚本

如果已经跑通了 GUI 内 beginner 脚本，那么下一步优先看这篇。

### [`docs/ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.zh-CN.md`](./ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.zh-CN.md)

作用：

- 这是第三阶段教程。
- 重点讲：
  - 抓取 / 放置状态机如何组织
  - 如何把桌子、料区、阻挡块、任务物体分层建模
  - 为什么教学型“附着”比一开始就硬上复杂接触物理更适合小白

如果已经开始从“单次规划”走向“任务流程”，下一步优先看这篇。

### [`docs/ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.zh-CN.md`](./ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.zh-CN.md)

作用：

- 这是第四阶段教程。
- 重点讲：
  - 如何加载用户提供的 USD 场景
  - 如何指定 cuRobo 应该读取哪些场景 root 作为障碍物
  - 如何把已有 pick object / pick target / place target 接到状态机
  - 如果场景里还没有任务 marker，如何让脚本自动补 runtime marker

如果已经有自定义场景资产，准备从“教学场景”进入“真实工作场景”，下一步优先看这篇。

### [`isaacsim_python.bat`](../../isaacsim_python.bat)

作用：

- 这是一个带环境修复的 Isaac Sim Python wrapper。
- 它会自动设置：
  - `ISAAC_PATH`
  - `EXP_PATH`
  - `CARB_APP_PATH`
  - `OMNI_KIT_ACCEPT_EULA`
  - `PYTHONPATH`

它还会自动把这些目录加入 Python 环境：

- `python_packages`
- `site`
- `exts/omni.isaac.core_archive/pip_prebundle`
- `exts/omni.isaac.ml_archive/pip_prebundle`
- `exts/omni.pip.compute/pip_prebundle`
- `exts/omni.pip.cloud/pip_prebundle`

用法：

```powershell
.\isaacsim_python.bat -c "import isaacsim"
```

如果需要手动指定 Isaac Sim 根目录：

```powershell
.\isaacsim_python.bat --isaac-root <ISAAC_SIM_ROOT> -c "import isaacsim"
```

### [`install_in_isaacsim.bat`](../../install_in_isaacsim.bat)

作用：

- 检查 Isaac Sim Python 是否可用
- 把当前仓库以 editable 模式安装进 Isaac Sim

用法：

```powershell
.\install_in_isaacsim.bat
```

### [`verify_isaacsim_integration.bat`](../../verify_isaacsim_integration.bat)

作用：

- 执行最小集成验证
- 成功时输出 `Smoke test passed.`

用法：

```powershell
.\verify_isaacsim_integration.bat
```

### [`examples/isaac_sim/smoke_test_headless.py`](../../examples/isaac_sim/smoke_test_headless.py)

作用：

- Headless 启动 `SimulationApp`
- 导入 Franka 到 USD
- 从 USD 读取障碍物
- 构建 `MotionGen`
- 规划一次
- 成功后退出

这是当前最推荐的最小功能自检脚本。

### [`examples/isaac_sim/motion_gen_compat.py`](../../examples/isaac_sim/motion_gen_compat.py)

作用：

- 这是 smoke 与正式 Isaac Sim 主脚本共享的规划兼容模块。
- 统一处理：
  - full / active / articulation joint state 映射
  - `FINETUNE_TRAJOPT_FAIL` 时的 pre-finetune 轨迹接管
  - 禁用 finetune 后的二次重试
  - planner / config / sim DOF 诊断输出

这意味着：

- 兼容逻辑不再只存在于 smoke demo
- 正式主脚本也继承同样的稳定性策略

### [`examples/isaac_sim/gui_in_app_motion_gen_beginner.py`](../../examples/isaac_sim/gui_in_app_motion_gen_beginner.py)

作用：

- 这是专门给“已经打开 Isaac Sim GUI，再在软件内运行”的 in-app 入门脚本。
- 它不会自己创建 `SimulationApp`。
- 适合从 `Window > Script Editor` 里直接打开并执行。

它的定位是：

- 给小白做 GUI 内最小可视化闭环
- 给后续自定义场景提供最容易理解的起点

### [`examples/isaac_sim/gui_in_app_custom_scene_template.py`](../../examples/isaac_sim/gui_in_app_custom_scene_template.py)

作用：

- 这是第二阶段的 in-app 模板脚本。
- 它把最常需要修改的内容集中在文件顶部：
  - 机器人
  - 外部资产路径
  - 机器人底座位置
  - 目标点
  - 桌面与障碍物配置

适合：

- 已经跑通 beginner 脚本
- 准备开始搭建自定义工作台、障碍物和目标点

### [`examples/isaac_sim/gui_in_app_pick_place_state_machine_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_state_machine_template.py)

作用：

- 这是第三阶段的 in-app 教学模板。
- 它具备：
  - 抓取 / 放置状态机
  - 基础场景建模
  - cuRobo 分阶段规划
  - 教学型物体附着

适合：

- 已经理解单次规划模板
- 准备开始做 pick-place 任务流

### [`examples/isaac_sim/gui_in_app_pick_place_from_usd_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_from_usd_template.py)

作用：

- 这是第四阶段的 in-app 模板脚本。
- 它具备：
  - 加载当前已打开的 USD 场景，或主动打开一个 USD 文件
  - 从指定 root 提取场景障碍物
  - 将 pick-place 状态机接到用户提供的 USD 场景
  - 缺少任务 marker 时自动补 runtime marker

适合：

- 已经有用户提供的 USD 场景
- 准备把 pick-place 状态机接入真实工作场景

### [`run_isaacsim_curobo_demo.bat`](../../run_isaacsim_curobo_demo.bat)

作用：

- 启动 Isaac Sim 正式交互式 demo。
- 当前默认目标已经从 smoke 改为：
  - `examples/isaac_sim/motion_gen_reacher.py`

如果需要临时覆盖脚本入口，可以先设置：

```powershell
$env:CUROBO_DEMO_SCRIPT='<REPO_ROOT>\examples\isaac_sim\gui_motion_gen_smoke.py'
.\run_isaacsim_curobo_demo.bat
```

## 3. 推荐使用流程

### 标准流程

```powershell
cd <REPO_ROOT>
.\install_in_isaacsim.bat
.\verify_isaacsim_integration.bat
```

### 调试流程

如果需要手工调试：

```powershell
.\isaacsim_python.bat -c "import isaacsim, torch"
.\isaacsim_python.bat -m pip show nvidia_curobo
.\isaacsim_python.bat -u .\examples\isaac_sim\smoke_test_headless.py
.\run_isaacsim_curobo_demo.bat
```

### 正式主脚本与 smoke 的分工

- `smoke_test_headless.py`：最小集成验收
- `gui_motion_gen_smoke.py`：GUI 验证型 smoke
- `motion_gen_reacher.py`：长期交互式正式主脚本

推荐习惯：

- 每次修安装链路，先跑 smoke
- 需要长期交互调试时，再跑 `run_isaacsim_curobo_demo.bat`

## 4. 这套安装版和“直接 pip install”的区别

### 直接 `pip install -e .` 的问题

- 很容易拿错 Python
- 很容易看不到 Isaac Sim 预打包的 `torch`
- 很容易缺 `ISAAC_PATH` / `EXP_PATH`
- 很容易在 Windows 上遇到 DLL 搜索路径问题

### 这套安装版的优势

- 自动使用正确的 Isaac Sim Python 环境
- 自动暴露 `torch` 和其他预打包依赖
- 自动走修复后的构建链路
- 安装后立刻可验收

## 5. 兼容性策略

### 新显卡 + 旧 Isaac Sim

当前已经特别处理了这条路径：

- 旧 Isaac Sim 自带旧版 PyTorch / CUDA
- 新显卡如 RTX 5070 属于 `sm_120`
- 运行时 `torch.jit` / `NVRTC` 可能不认识这个架构

当前策略：

- 保留正常 CUDA 执行路径
- 自动禁用会炸掉的 JIT 路径
- 用 smoke test 确认最小规划仍然可跑
- 在正式主脚本中复用同一套 `plan_single_with_compat(...)` 容错逻辑

### 正式主脚本规划兼容

当前策略：

- `motion_gen_reacher.py` 与 `simple_stacking.py` 都通过共享模块复用规划 fallback
- Franka 的 full 9 维配置和 active 7 维规划状态由共享函数统一转换
- 当 finetune 失败但 pre-finetune 轨迹有效时，脚本不再误判为“完全失败”

### Windows 动态库问题

当前策略：

- 在 `curobo.curobolib` 导入时自动注册 `torch/lib`
- 避免 `.pyd` 找不到依赖 DLL

### 新版 MSVC 问题

当前策略：

- 在 `setup.py` 里加入 Windows 下的兼容宏
- 允许 CUDA 11.8 在新工具链上继续编译

## 6. 什么时候算安装成功

满足下面三条，就算成功：

1. `.\install_in_isaacsim.bat` 返回成功
2. `.\verify_isaacsim_integration.bat` 返回成功
3. 输出包含：

```text
Smoke test passed.
```

## 7. 什么时候算需要继续排查

只要出现下面任意一种，就说明还没完全成功：

- `No module named 'torch'`
- `No module named 'isaacsim.simulation_app'`
- `DLL load failed while importing ...`
- `error STL1002`
- `nvrtc: error: invalid value for --gpu-architecture (-arch)`
- 验证脚本返回非 0

## 8. 对维护者的建议

如果你后面继续维护这套 Windows 版本，我建议遵守下面几条：

### 不要删除 wrapper

`isaacsim_python.bat` 是这套方案的关键之一。

没有它，很多用户会再次掉回：

- 用错 Python
- 找不到 `torch`
- 找不到 `isaacsim.simulation_app`

### 不要把 `setup.py` 改回顶层导入 `torch`

一旦改回去，`pip` 又会在元数据阶段提前崩。

### 不要移除 JIT 降级逻辑

对于 RTX 50 系这类新卡，这层兼容逻辑不是优化，而是运行必要条件之一。

### 新增功能前先跑验证脚本

每次改完安装、编译、路径、环境变量相关逻辑，都先跑：

```powershell
.\verify_isaacsim_integration.bat
```

## 9. 推荐发布说明写法

如果你准备把这个版本发给别人，推荐写成这样：

### 一句话说明

这是一个可在 Windows + Isaac Sim 4.5 + 新显卡环境中安装和运行的 cuRobo 修复版。

### 推荐用户执行的两条命令

```powershell
.\install_in_isaacsim.bat
.\verify_isaacsim_integration.bat
```

### 必须说明的已知事实

- 旧 Isaac Sim 内置 PyTorch 仍会对新显卡打印兼容性警告
- 当前版本已经自动绕过了最关键的 JIT/NVRTC 崩溃路径
- 最小 smoke test 已验证通过

## 10. 当前状态

截至 **2026-04-04**，这套“新可安装版本”已经完成：

- 安装链路修复
- Windows 编译链兼容修复
- DLL 导入修复
- 新显卡 JIT 兼容修复
- Isaac Sim headless 集成验证
- smoke 与正式主脚本共享兼容模块
- 默认 demo launcher 切到 `motion_gen_reacher.py`
- 一键安装脚本
- 一键验证脚本
- 详细中文教程

这就是当前推荐交付给其他用户的版本。

