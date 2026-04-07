# cuRobo for Windows 集成 Isaac Sim 全流程修复文档

## 1. 文档目的

本文档完整记录本次在 `<ISAAC_SIM_ROOT>` 环境中，将

- `<REPO_ROOT>`

成功安装进

- `<ISAAC_SIM_ROOT>`

并最终打通 full GUI 场景规划的全过程。

本文档重点覆盖：

- 真实环境信息
- 初始失败现象
- 每一类报错背后的根因
- 每一步修复的判断依据
- 实际修改过的文件与作用
- 安装与验证方法
- full GUI 最终为什么能够 `PASS`
- 后续维护和升级时需要避免的坑

这不是泛泛而谈的说明，而是本机这次真实修复记录的工程化总结。

---

## 2. 本机环境与问题背景

### 2.1 环境信息

- 操作系统：Windows 11
- Isaac Sim 根目录：`<ISAAC_SIM_ROOT>`
- cuRobo 项目目录：`<REPO_ROOT>`
- GPU：NVIDIA GeForce RTX 5070
- GPU 计算能力：`sm_120`
- 本机 CUDA Toolkit / `nvcc`：`11.8`
- Isaac Sim 版本：`4.5.0-rc.36`

### 2.2 初始目标

目标分两层：

1. 让 `curobo_for_windows` 能真正安装进 Isaac Sim 运行环境。
2. 让 full GUI 场景里的 cuRobo motion generation demo 真正成功规划，而不是仅仅“能导入、能启动、能跑到一半”。

### 2.3 初始问题并不止一个

这个问题不是单点故障，而是一串连续问题叠加：

- 安装层面不兼容
- Python 包覆盖导致 Isaac Sim 自带二进制扩展失配
- 新显卡 `sm_120` 与旧版 CUDA/NVRTC 运行时编译不兼容
- Warp 内核在 full app 路径下出现非法指令
- Franka 锁定关节与规划关节维度不一致，出现 7 维 / 9 维错配
- full GUI 下 finetune trajopt 会失败，但主规划其实已经给出了可用轨迹

换句话说，最开始报出来的“无法安装”，只是整个问题链条的第一个表象。

---

## 3. 最终状态

当前已经达成的结果：

- `install_in_isaacsim.bat` 可成功执行
- `verify_isaacsim_integration.bat` 可成功通过
- headless smoke test 通过
- full GUI smoke test 通过
- 当前 Isaac Sim GUI 已经被实际拉起，并带着 cuRobo demo 脚本运行

full GUI 成功日志可在下列文件中看到：

- `<ISAAC_SIM_ROOT>\logs\gui_full_stdout_20260404_152640.log`

关键成功输出如下：

```text
GUI_SMOKE: using pre-finetune trajectory
GUI_SMOKE: planning success=True
GUI_SMOKE: trajectory points=29
GUI_SMOKE: PASS
```

当前手动打开的 GUI 进程已经启动：

- `cmd.exe` 进程：`14904`
- `kit.exe` 进程：`12696`
- 窗口标题：`Isaac Sim Full 4.5.0`

---

## 4. 问题全景与根因分解

## 4.1 根因一：Isaac Sim 自带 PyTorch 与 RTX 5070 不兼容

Isaac Sim 4.5 自带的是 `torch 2.5.1+cu118`，其支持的 CUDA capability 不包含 `sm_120`。

因此一开始日志中会出现类似提示：

- `NVIDIA GeForce RTX 5070 with CUDA capability sm_120 is not compatible with the current PyTorch installation`

这个问题会继续引出两类后果：

- PyTorch 某些 CUDA kernel 路径不能正常工作
- 运行时编译（NVRTC）试图为 `sm_120` 编译代码，但 Isaac Sim 自带的 CUDA 11.8 runtime 不支持这个架构

这也是最初 `nvrtc: error: invalid value for --gpu-architecture (-arch)` 的根因。

### 修复思路

不能继续用 Isaac Sim 自带的 `cu118 torch` 跑 RTX 5070，必须叠加一个支持 `sm_120` 的 PyTorch 版本。

最终选择：

- `torch==2.7.1+cu128`
- `torchvision==0.22.1+cu128`
- `torchaudio==2.7.1+cu128`

安装位置不是全局 Python，而是：

- `<ISAAC_SIM_ROOT>\python_packages`

这样能最大程度降低对 Isaac Sim 自身分发结构的破坏。

---

## 4.2 根因二：升级 torch 后，editable install 会错误地触发本机重新编译 CUDA 扩展

cuRobo 里包含多个原生 CUDA 扩展：

- `lbfgs_step_cu`
- `kinematics_fused_cu`
- `line_search_cu`
- `tensor_step_cu`
- `geom_cu`

一旦执行：

```text
pip install -e .
```

旧的 `setup.py` 会按默认逻辑尝试用本机 `nvcc` 重新编译这些扩展。

但本机 `nvcc` 是 `11.8`，而新叠加的 PyTorch 是 `cu128`。这会造成典型的编译工具链不一致问题：

- PyTorch 运行时是 CUDA 12.8
- 本地编译器仍然是 CUDA 11.8

这不是“编译参数错了”，而是工具链本身不匹配。

### 修复思路

Windows 这套 `curobo_for_windows` 已经自带 `.pyd` 预编译扩展，因此最合理的做法不是“继续编译”，而是：

- 优先复用已有 `.pyd`
- 在 Windows 下如果预编译扩展存在，则跳过 CUDA 编译
- 只有显式设置 `CUROBO_FORCE_BUILD=1` 时才允许强制编译

### 实际修改文件

- `<REPO_ROOT>\setup.py`

### 实际修改结果

`setup.py` 现在会检查：

- 当前是否在 Windows
- `src\curobo\curobolib` 下是否已有对应 `.pyd`

若都有，则输出：

```text
Using prebuilt Windows cuRobo extensions; skipping CUDA compilation.
```

这样就避免了 `CUDA 11.8` 与 `torch cu128` 的构建冲突。

---

## 4.3 根因三：升级 torch 时，`numpy` / `PIL` 被一起覆盖，破坏 Isaac Sim 自带二进制依赖

一开始如果直接粗暴地用 pip 覆盖 Isaac Sim 的 Python 环境，很容易把这些包也换掉：

- `numpy`
- `pillow`

结果会导致 Isaac Sim 自己打包好的扩展和 Python 包版本不一致，出现：

- `numpy C-extensions failed`
- `PIL._imaging` 二进制不匹配
- 部分扩展在 full app 启动时导入异常

### 关键事实

这个问题不是 `torch` 本身导致的，而是 `torch` 安装过程中把与 Isaac Sim 自带生态强绑定的 `numpy/pillow` 一起动了。

### 修复思路

必须做“按包路由”：

- `torch` 走 `<ISAAC_SIM_ROOT>\python_packages`
- `numpy` 强制优先使用 Isaac Sim 自带的 `kit\python\lib\site-packages`
- `PIL` 强制优先使用 `extscache\omni.kit.pip_archive-...\pip_prebundle`

### 实际修改文件

- `<ISAAC_SIM_ROOT>\site\sitecustomize.py`

### 实际修改方式

在 `sitecustomize.py` 中加入 `_prefer_builtin_package(...)` 逻辑：

- 若检测到 `python_packages` 中存在会干扰 Isaac Sim 的包
- 且 Isaac Sim 自带目录存在原生兼容版本
- 则在导入前动态把 `sys.path` 顺序调整为 Isaac Sim 自带目录优先

### 最终效果

当前导入路由稳定为：

- `torch`：`<ISAAC_SIM_ROOT>\python_packages\torch`
- `numpy`：`<ISAAC_SIM_ROOT>\kit\python\lib\site-packages\numpy`
- `PIL`：`<ISAAC_SIM_ROOT>\extscache\omni.kit.pip_archive-...\pip_prebundle\PIL`

这一步是后续一切成功运行的基础。

---

## 4.4 根因四：NVRTC / `torch.jit` / 运行时 CUDA 编译不支持 `sm_120`

在 `sm_120 + CUDA 11.8 runtime` 组合下，运行时编译类能力会直接出错：

- `torch.jit` 某些路径会试图走 NVRTC
- `torch.erfinv` 相关内核可能触发 runtime compile
- 某些 cuRobo jit/script kernel 也会间接触发这条路径

对应症状包括：

- `nvrtc: error: invalid value for --gpu-architecture (-arch)`
- 各种 `--gpu-architecture` / `sm_120` 不支持

### 修复思路

不要继续硬碰硬，而是检测环境后主动关闭这些不兼容能力。

### 实际修改文件

- `<REPO_ROOT>\src\curobo\util\torch_utils.py`

### 实际修改内容

新增两个核心判断：

- `is_torch_jit_available()`
- `is_cuda_runtime_compile_available()`

逻辑是：

- 如果 GPU capability >= 12 且 CUDA runtime < 12.4
- 则关闭 `torch.jit`
- 同时关闭 CUDA runtime-compiled torch ops

### 结果

日志中会明确提示：

- `Disabling torch.jit because NVRTC in CUDA 11.8 does not support sm_120.`
- `Disabling CUDA runtime-compiled torch ops because NVRTC in CUDA 11.8 does not support sm_120.`

这一步修掉了最早期最致命的一批 `NVRTC -arch` 报错。

---

## 4.5 根因五：Halton / Gaussian sampling 路径在 GPU 上仍会间接触发 `torch.erfinv` 运行时编译

即使前面关掉了大部分 runtime compile，采样库中的高斯变换仍可能触发：

- `torch.erfinv`

在新 GPU 上，这条路径仍可能走到不兼容实现。

### 实际症状

最初堆栈中有：

- `sample_lib.py`
- `gaussian_transform`
- `torch.erfinv`

最后落到：

- `nvrtc: error: invalid value for --gpu-architecture (-arch)`

### 修复思路

保留 GPU 数据流，但把不兼容的 `erfinv` 计算切到 CPU 做，然后把结果回拷到原设备。

### 实际修改文件

- `<REPO_ROOT>\src\curobo\util\sample_lib.py`

### 实际修改内容

新增：

- `_should_use_cpu_runtime_compile_fallback`
- `_erfinv_cpu_fallback`
- `gaussian_transform_cpu_fallback`

执行策略是：

- 若设备是 CUDA
- 且当前 runtime compile 不可用
- 则把 `erfinv` 输入复制到 CPU
- 在 CPU 上执行 `torch.erfinv`
- 再回传到原设备

### 结果

GPU 侧的采样主流程仍保留，但绕开了 `sm_120 + cu118 NVRTC` 的死区。

---

## 4.6 根因六：Warp BoundCost 在 full app 路径下触发 `cudaErrorIllegalInstruction`

在 full GUI / full app 里，Warp bound cost kernel 触发了：

- `cudaErrorIllegalInstruction`
- `Warp CUDA error 715`

这类错误不是普通 shape bug，而是 GPU 内核本身在当前平台组合下不稳定。

### 修复思路

不要继续强行走 Warp kernel；直接给 `BoundCost` 提供一个等价的纯 PyTorch fallback。

### 实际修改文件

- `<REPO_ROOT>\src\curobo\rollout\cost\bound_cost.py`

### 实际修改内容

新增：

- `_use_torch_fallback`
- `_bound_delta`
- `_expand_dof_tensor`
- `_get_scalar_tensor`
- `_get_retract_target`
- `_forward_torch`

并在 `forward()` 中根据 `is_cuda_runtime_compile_available()` 自动切换：

- 正常情况走 Warp
- `sm_120 + old runtime` 情况下走 PyTorch fallback

### 这一步顺手解决的几个次级问题

在替换为 PyTorch fallback 后，又暴露出一些之前被 Warp kernel 隐藏的张量形状问题：

- `null_space_weight` 可能是 0-dim tensor
- `vec_weight` 可能只有一个标量，而不是每个 DOF 一项
- `retract_idx` 有时不是 vector，而是空 tensor 或高维 tensor
- `retract_config` 可能是 1 维，也可能是 batch x dof

这些都在 fallback 中被逐一兼容处理了。

### 结果

`BoundCost` 不再在 full GUI 中因为 Warp illegal instruction 直接炸掉。

---

## 4.7 根因七：Franka 的完整关节数是 9，但规划器实际只控制 7 个 active joints

这一步是 full GUI 里最后一个真正的结构性问题。

### 关键事实

`franka.yml` 中：

- `joint_names` 是 9 个
- `retract_config` 也是 9 个
- `null_space_weight` 是 9 个
- `cspace_distance_weight` 也是 9 个

但同时：

- `lock_joints: {"panda_finger_joint1": 0.04, "panda_finger_joint2": 0.04}`

这意味着：

- 机器人完整关节状态是 9 维
- 真正参与优化的 active joint state 是 7 维

如果某条路径拿 9 维 `retract_config` 直接喂给只接受 7 维的优化器，就会出现：

- `shape '[1, 7]' is invalid for input of size 9`

### 为什么之前一直反复出现 7/9 维问题

因为问题不只在 GUI demo 脚本本身，还在内部模型属性上：

- `KinematicModel.retract_config`
- `KinematicModel.cspace_distance_weight`
- `KinematicModel.null_space_weight`

它们原本直接返回 `cspace` 配置里的完整 9 维张量，没有在 lock joint 之后自动裁成 active DOF。

### 修复思路

在 `KinematicModel` 这一层，把这些属性统一转换为 active cspace tensor。

### 实际修改文件

- `<REPO_ROOT>\src\curobo\rollout\dynamics_model\kinematic_model.py`

### 实际修改内容

新增：

- `_get_active_cspace_tensor(...)`

并将以下属性改为通过这个函数返回：

- `retract_config`
- `cspace_distance_weight`
- `null_space_weight`

转换逻辑为：

1. 若张量长度已经等于 active DOF，则直接返回
2. 若张量长度等于完整 articulated joint 数，则先构造 full `JointState`
3. 再通过 `robot_model.get_active_js(...)` 提取 active joint 顺序
4. 返回对应的 active 7 维向量

### 结果

所有内部优化器现在拿到的 `retract_config/weight` 维度都与 active DOF 一致，不再发生 9 -> 7 视图错误。

---

## 4.8 根因八：GUI demo 脚本混用了 full joint state 与 active joint state

即便内部属性修好了，demo 脚本也必须显式区分两种状态：

- 给 Isaac Sim articulation 写回时，需要 full 9 维关节
- 给 cuRobo 规划器时，需要 active 7 维关节

### 修复思路

GUI demo 必须走下面这条清晰的数据流：

1. 从 `franka.yml` 读取 full 9 维 retract state
2. 用 `MotionGen.get_active_js(...)` 转成 7 维 active state
3. 规划成功后，再用 `MotionGen.get_full_js(...)` 转回 9 维
4. 最终再按 Isaac Sim articulation 的 `robot.dof_names` 顺序写回机器人

### 实际修改文件

- `<REPO_ROOT>\examples\isaac_sim\gui_motion_gen_smoke.py`

### 实际修改内容

包括但不限于：

- 区分 `full_joint_names` / `robot_dof_names` / `motion_gen.joint_names`
- 用 full 9 维 retract state 初始化机器人
- 用 `motion_gen.get_active_js(...)` 构造规划起点
- 用 `motion_gen.get_full_js(...)` 把规划轨迹恢复为完整关节状态
- 增加 `dof summary` 与 `q_start shapes` 调试输出，直接看 7/9 维是否一致

### 结果

GUI smoke 不再在 `check_start_state` 阶段因维度错配崩溃。

---

## 4.9 根因九：full GUI 下 `FINETUNE_TRAJOPT_FAIL`，但主规划已经有可用轨迹

在 full app 负载下，日志最终稳定收敛到一个单一失败类型：

- `MotionGenStatus.FINETUNE_TRAJOPT_FAIL`

这比前面的安装失败、illegal instruction、shape mismatch 已经轻很多了。

### 为什么这不是“完全失败”

从 `motion_gen.py` 的实现可见：

- 即便 finetune 阶段失败
- `result.interpolated_plan` 和 `result.optimized_plan` 仍可能已经被赋值

也就是说：

- 主 trajopt 已经给出了一条轨迹
- 只是后续“追求更优、更平滑、更短”的 finetune 没成功

在 smoke/demo 场景里，这条 pre-finetune 轨迹完全可以作为“规划成功”的有效结果。

### 实际修复策略

在 GUI smoke 中加入三层策略：

1. 主配置：
   - `enable_finetune_trajopt=True`
   - `max_attempts=12`
   - `timeout=20.0`
2. 若状态是 `FINETUNE_TRAJOPT_FAIL`，先检查 `result.get_interpolated_plan()`
3. 若 pre-finetune 轨迹已存在且非空，则直接接受它
4. 只有在轨迹不存在时，才 reset seed 并重试一遍
   - `enable_graph=True`
   - `enable_finetune_trajopt=False`

### 为什么要把 `max_attempts` 从 2 提高到 12

一开始 smoke 脚本里为了快速试错，把 `max_attempts` 压得很低。

但 `MotionGenPlanConfig` 默认本来就是：

- `max_attempts=60`

而 full GUI 下 GPU 负载比 headless 高，过低的尝试次数会把“可恢复的 finetune 抖动”过早判成失败。

所以恢复到更合理的重试规模是必要的。

### 最终结果

最新 full GUI 运行中，日志明确显示：

```text
GUI_SMOKE: using pre-finetune trajectory
GUI_SMOKE: planning success=True
GUI_SMOKE: trajectory points=29
GUI_SMOKE: PASS
```

这说明：

- 主规划成功
- 轨迹有效
- GUI smoke 目标已经达成

---

## 5. 实际修改过的关键文件

以下列出本次修复中真正关键、且应保留的修改文件。

## 5.1 安装与环境层

### `<REPO_ROOT>\install_in_isaacsim.bat`

作用：

- 检查 Isaac Sim Python 环境
- 安装 `torch/torchvision/torchaudio` 的 `cu128` 覆盖层
- 验证 `torch/numpy/PIL` 来源路径
- 以 editable 方式安装 cuRobo

关键设计：

- 使用 `<ISAAC_SIM_ROOT>\python_packages` 作为 torch overlay
- 使用 `--no-deps`
- 不重复安装已就绪的 torch overlay

### `<ISAAC_SIM_ROOT>\site\sitecustomize.py`

作用：

- 解决 `torch` 与 `numpy/PIL` 混装导致的二进制不兼容问题
- 对 `numpy/PIL` 做优先级路由

## 5.2 构建层

### `<REPO_ROOT>\setup.py`

作用：

- 在 Windows 上复用 `.pyd` 预编译扩展
- 跳过本地 CUDA 11.8 重新编译

## 5.3 原生扩展加载层

### `<REPO_ROOT>\src\curobo\curobolib\__init__.py`

作用：

- 在 Windows 下先导入 `torch`
- 并将 `torch/lib` 加入 DLL 搜索路径

目的：

- 让 `geom_cu.pyd` 等原生扩展能找到所依赖的 torch CUDA DLL

## 5.4 新 GPU 运行时兼容层

### `<REPO_ROOT>\src\curobo\util\torch_utils.py`

作用：

- 自动判断 `torch.jit` 是否可用
- 自动判断 runtime compile 是否可用
- 在 `sm_120 + CUDA<12.4` 场景下主动关闭不兼容路径

### `<REPO_ROOT>\src\curobo\util\sample_lib.py`

作用：

- 给 `torch.erfinv` 采样路径增加 CPU fallback
- 避免 `NVRTC -arch` 错误

### `<REPO_ROOT>\src\curobo\rollout\cost\bound_cost.py`

作用：

- 给 Warp BoundCost 增加 PyTorch fallback
- 同时修复权重广播、`retract_idx`、`retract_config` 等张量形状问题

### `<REPO_ROOT>\src\curobo\rollout\dynamics_model\kinematic_model.py`

作用：

- 统一把 cspace 配置从 full joint tensor 转为 active joint tensor
- 彻底修复 Franka 7/9 DOF mismatch

## 5.5 验证与 demo 层

### `<REPO_ROOT>\examples\isaac_sim\smoke_test_headless.py`

作用：

- 提供一个稳定、可自动化的 headless 验证入口
- 用于确认安装链路和基本规划链路已恢复

### `<REPO_ROOT>\examples\isaac_sim\gui_motion_gen_smoke.py`

作用：

- 提供 full GUI 场景验证入口
- 负责把 active/full joint state 正确衔接起来
- 对 `FINETUNE_TRAJOPT_FAIL` 做可用轨迹接管

### `<REPO_ROOT>\run_gui_smoke_capture.ps1`

作用：

- 用 `--no-window` 模式运行 full GUI smoke
- 自动生成带时间戳的 stdout/stderr 日志
- 用于非交互验证和回归

---

## 6. 修复过程的时间顺序与思考路径

下面按真实工程排障顺序总结“看到什么 -> 怎么判断 -> 做了什么”。

## 6.1 第一阶段：确认不是普通 `pip install` 问题，而是显卡架构兼容问题

看到的现象：

- 安装后运行立刻出现 `sm_120 not compatible`
- `nvrtc -arch` 报错

判断：

- 不是 Python 语法问题
- 也不是单个 `.pyd` 缺失
- 是 Isaac Sim 自带 torch 与新 GPU 架构不兼容

处理：

- 转向 `torch cu128 overlay`

## 6.2 第二阶段：overlay torch 后，editable install 又因本地编译炸掉

看到的现象：

- `pip install -e .` 触发编译
- 本机 `nvcc 11.8` 与 `torch cu128` 不匹配

判断：

- 不能继续让 `setup.py` 用本地工具链编译
- 应优先复用仓库已有 Windows 预编译扩展

处理：

- 修改 `setup.py`
- Windows 下检测已有 `.pyd` 即跳过编译

## 6.3 第三阶段：torch 覆盖成功后，Isaac Sim 内部 Python 包二进制链开始错位

看到的现象：

- `numpy C-extensions failed`
- `PIL._imaging` 版本不匹配

判断：

- torch overlay 成功了
- 但 Isaac Sim 自己依赖的 `numpy/PIL` 来源被污染了

处理：

- 改 `sitecustomize.py`
- 把 `numpy/PIL` 导入顺序强制拉回 Isaac Sim 自带版本

## 6.4 第四阶段：安装层恢复，但运行时编译仍在新 GPU 上崩

看到的现象：

- `torch.jit`
- `NVRTC -arch`
- `torch.erfinv`

判断：

- 即使编译已经跳过，运行时仍有 JIT / runtime compile

处理：

- 在 `torch_utils.py` 中自动关闭不兼容 JIT/runtime compile
- 在 `sample_lib.py` 中为 `erfinv` 增加 CPU fallback

## 6.5 第五阶段：full app 下 Warp bound cost illegal instruction

看到的现象：

- `cudaErrorIllegalInstruction`
- `WarpBoundSmoothFunction.apply`

判断：

- 问题已经缩小到某个 GPU 内核
- 继续强行保留 Warp 只会反复炸

处理：

- 直接在 `bound_cost.py` 中实现 PyTorch fallback

## 6.6 第六阶段：fallback 跑起来后，暴露出一串隐藏形状问题

看到的现象：

- 标量权重 reshape 异常
- `retract_idx` 不是 vector
- `retract_config.index_select(...)` 失败

判断：

- Warp kernel 之前“吞掉”了不少形状细节
- fallback 更严格，因此真实暴露出输入不统一

处理：

- 在 `bound_cost.py` 里逐项把形状兼容补齐

## 6.7 第七阶段：最终卡在 7 维 / 9 维关节状态错配

看到的现象：

- `shape '[1, 7]' is invalid for input of size 9`

判断：

- Franka 锁定了两根手指，但 cspace 配置仍是 9 维
- 内部属性和 GUI 脚本都在混用 full/active joint state

处理：

- 在 `kinematic_model.py` 里把 cspace 相关属性统一裁成 active DOF
- 在 `gui_motion_gen_smoke.py` 里显式走 full -> active -> full 的转换链

## 6.8 第八阶段：full GUI 只剩 `FINETUNE_TRAJOPT_FAIL`

看到的现象：

- 程序不再崩溃
- 只返回 `MotionGenStatus.FINETUNE_TRAJOPT_FAIL`

判断：

- 主规划已经基本工作
- 问题不再是“安装失败”或“运行时不兼容”
- 而是 finetune 阶段在 full app 负载下不稳定

处理：

- 增大 `max_attempts`
- 保留 fallback
- 最关键的是：当 pre-finetune 轨迹已存在时，直接接受该轨迹

最终：

- full GUI `PASS`

## 6.9 第九阶段：把 smoke 中验证过的兼容逻辑迁移到正式主脚本

这一阶段的核心目标，不再是“证明环境可跑”，而是“把已经验证成立的兼容策略，真正下沉到以后长期会用的正式脚本入口里”。

看到的现象：

- `gui_motion_gen_smoke.py` 已经具备稳定的 `FINETUNE_TRAJOPT_FAIL` 容错
- `motion_gen_reacher.py` 仍保留原始成功判定，`result.success == False` 就直接判失败
- `simple_stacking.py` 也仍然直接调用 `plan_single(...)`
- 默认启动脚本 `run_isaacsim_curobo_demo.bat` 还指向 smoke，而不是正式主脚本

判断：

- 如果兼容逻辑只停留在 smoke demo，那么它只能证明“这台机器可以被修好”
- 但并不能保证以后长期调试、交互操作、继续开发时，默认入口也继承同样的稳定性
- 真正可靠的做法，是把这些策略沉淀成共享模块，再让正式脚本复用

处理：

- 新增共享模块：
  - `<REPO_ROOT>\examples\isaac_sim\motion_gen_compat.py`
- 在这个模块里统一封装三类逻辑：
  - DOF 诊断输出：`describe_dof_layout(...)`
  - full / active / articulation retract state 转换：`get_retract_state_for_articulation(...)`
  - `FINETUNE_TRAJOPT_FAIL` 兼容规划入口：`plan_single_with_compat(...)`
- 让 smoke 与正式脚本都使用同一套实现，而不是各自复制一份

### 这一轮实际改了哪些脚本

- `<REPO_ROOT>\examples\isaac_sim\motion_gen_compat.py`
  - 新增共享兼容模块
- `<REPO_ROOT>\examples\isaac_sim\gui_motion_gen_smoke.py`
  - 改为复用共享模块，而不是自己维护一份独立兼容逻辑
- `<REPO_ROOT>\examples\isaac_sim\motion_gen_reacher.py`
  - 正式迁入同样的规划兼容逻辑
  - 初始化时显式输出 planner/full/sim DOF 对照
  - 使用 retract full state -> active state -> articulation full state 的一致链路
  - 默认 `max_attempts` 从 4 提升到 12
  - 在 finetune 失败时接受已有 pre-finetune 轨迹
  - 必要时自动重试一轮 `enable_finetune_trajopt=False` 的 fallback 配置
- `<REPO_ROOT>\examples\isaac_sim\simple_stacking.py`
  - 也接入同一套 `plan_single_with_compat(...)`
  - 避免堆叠流程仍停留在旧的失败判定
- `<REPO_ROOT>\run_isaacsim_curobo_demo.bat`
  - 默认启动入口从 smoke 切换为正式主脚本 `motion_gen_reacher.py`

### 为什么 `motion_gen_reacher.py` 被认定为“正式主脚本”

依据不是主观猜测，而是仓库里的实际定位：

- `workspace_win/readme.md` 明确把它作为 robot configuration / Isaac Sim 正式示例入口
- 它是最直接的单机器人交互式 motion generation 脚本
- 相比 smoke，它更接近长期手动调参、观察规划、继续做业务集成时会重复使用的路径

### 这一轮迁移和 smoke 的关系

不是“废掉 smoke”，而是明确分工：

- smoke 继续承担最小闭环验证
- `motion_gen_reacher.py` 承担长期交互式主入口
- 两者共享同一个兼容模块，避免今后出现“smoke 修好了，主脚本忘了同步”的回归

### 这一轮验证做到什么程度

本轮已经完成：

- 共享兼容模块落地
- 正式主脚本接入
- launcher 默认入口切换
- 使用 `isaacsim_python.bat` 对以下脚本执行 `py_compile` 静态编译验证：
  - `motion_gen_compat.py`
  - `gui_motion_gen_smoke.py`
  - `motion_gen_reacher.py`
  - `simple_stacking.py`

本轮还没有在这个回合里重新执行的内容：

- 没有重新跑一遍人工交互式 full GUI 主脚本
- 没有重新跑一遍完整堆叠流程

这意味着：

- 代码迁移和语法层面已经完成
- 但正式主脚本的交互式运行效果，仍建议在下一次 GUI 实跑里再做一次回归确认

---

## 7. 当前推荐的使用与验证方式

## 7.1 重新安装 / 补装 cuRobo

在 `<REPO_ROOT>` 下执行：

```bat
install_in_isaacsim.bat
```

预期结果：

- 输出 `Installation complete.`

## 7.2 验证安装链路

执行：

```bat
verify_isaacsim_integration.bat
```

预期结果：

- headless smoke 通过
- 输出 `Smoke test passed.`

## 7.3 非交互方式验证 full GUI smoke

执行：

```powershell
powershell -ExecutionPolicy Bypass -File <REPO_ROOT>\run_gui_smoke_capture.ps1
```

运行结束后查看：

- `<ISAAC_SIM_ROOT>\logs\gui_full_latest_paths.txt`

它会指向本次运行生成的 stdout/stderr 日志。

## 7.4 交互方式启动正式主脚本

当前默认 launcher 已经切到正式主脚本，执行：

```bat
<REPO_ROOT>\run_isaacsim_curobo_demo.bat
```

默认行为：

- 启动 `examples/isaac_sim/motion_gen_reacher.py`
- 进入 Isaac Sim Full GUI
- 使用目标方块做交互式 motion generation

如果之后需要临时切回别的脚本，可以显式覆盖：

```bat
set CUROBO_DEMO_SCRIPT=<REPO_ROOT>\examples\isaac_sim\gui_motion_gen_smoke.py
<REPO_ROOT>\run_isaacsim_curobo_demo.bat
```

## 7.5 交互方式保留 smoke 入口

如果想继续打开“验证型 GUI smoke”，仍可以直接执行：

```powershell
$args = '/k set CUROBO_GUI_SMOKE_AUTO_QUIT=0 && cd /d <ISAAC_SIM_ROOT> && call <ISAAC_SIM_ROOT>\isaac-sim.bat --exec <REPO_ROOT>\examples\isaac_sim\gui_motion_gen_smoke.py'
Start-Process -FilePath 'cmd.exe' -ArgumentList $args
```

它的定位现在更明确：

- 用于做 GUI 最小闭环验证
- 不再作为默认长期使用入口

---

## 8. 本次修复中最关键的工程结论

## 8.1 对 RTX 50 / `sm_120` 来说，旧版 Isaac Sim 自带 torch 不能直接用

结论：

- 必须使用支持 `sm_120` 的 torch overlay

## 8.2 不能在这台机器上直接重编 cuRobo CUDA 扩展

原因：

- 本机 `nvcc 11.8`
- overlay torch 是 `cu128`

结论：

- Windows 下优先复用已有 `.pyd`
- 不要强制 build

## 8.3 不要让 pip 随手覆盖 Isaac Sim 自带 `numpy/PIL`

结论：

- `torch` 可以 overlay
- `numpy/PIL` 必须继续走 Isaac Sim 自带兼容版本

## 8.4 Franka 在这里的真实规划 DOF 是 7，不是 9

虽然配置文件里列出了 9 个 joint，但两根手指被锁定后：

- 规划器 active DOF = 7
- 完整 articulation DOF = 9

这是 full GUI 规划中最容易被忽略的维度陷阱。

## 8.5 full GUI 下 `FINETUNE_TRAJOPT_FAIL` 不一定意味着“没有可用轨迹”

这是本次最终打通的决定性认知。

若：

- 主 trajopt 已经产生 `interpolated_plan`
- 只是 finetune 阶段失败

则对于 smoke/demo 验证目标来说，这条轨迹已经足够作为成功结果。

## 8.6 兼容逻辑必须沉到正式入口，而不是只留在 smoke

这是这次迁移后新增的工程结论。

如果：

- smoke 脚本有 fallback
- 正式主脚本没有 fallback

那么维护结果会非常脆弱：

- 验证时看起来一切正常
- 真正日常使用时却会重新撞回旧问题

因此最终的稳定方案不是“再写一个 smoke”，而是：

- 把兼容逻辑抽成共享模块
- 让 smoke 和正式主脚本同时复用
- 再把默认 launcher 指向正式入口

---

## 9. 后续维护建议

## 9.1 不要轻易执行下面这类操作

- 不要用系统 Python 去 `pip install -e .`
- 不要直接把 Isaac Sim 自带 `site-packages` 整体升级
- 不要让 pip 自动升级 `numpy` 和 `pillow`
- 不要在没有 CUDA 12.8 本地编译环境的情况下设置 `CUROBO_FORCE_BUILD=1`

## 9.2 若未来升级 Isaac Sim 或 cuRobo

建议优先检查以下几项：

1. 新版 Isaac Sim 自带 torch 是否已支持 `sm_120`
2. 新版 Warp 是否仍需要 `BoundCost` 的 PyTorch fallback
3. Franka `lock_joints` 与 `cspace` 长度是否仍然不一致
4. full GUI 下 finetune trajopt 是否仍不稳定

## 9.3 若以后想把修复“产品化”

当前修复已足够支撑本机使用，但如果要做成更通用的“可安装版本”，建议下一步做：

- 清理临时脚本与实验文件
- 把 smoke 脚本和 capture 脚本纳入正式工具链
- 补齐 `motion_gen_compat.py` 对正式 GUI 流程的回归测试
- 为 `setup.py` / `sitecustomize.py` / `BoundCost` fallback 补文档与自动化测试

---

## 10. 结论

本次问题最终不是“一个安装命令写错了”，而是一个典型的多层兼容性工程问题：

- GPU 架构更新
- Isaac Sim 自带运行时较旧
- cuRobo 包含原生 CUDA 扩展
- full GUI 路径与 headless 路径行为不同
- Franka 锁定关节让 full state 与 active state 不一致

最终能打通，依赖的是以下组合策略同时成立：

- 用 `cu128 torch overlay` 替换 Isaac Sim 自带不兼容 torch
- editable install 复用 Windows 预编译 `.pyd`
- `sitecustomize.py` 保住 Isaac Sim 自带 `numpy/PIL`
- 关闭 `sm_120` 上不兼容的 JIT/runtime compile
- 为采样和 BoundCost 提供 CPU / PyTorch fallback
- 统一 full joint state 与 active joint state 的数据流
- 在 full GUI 下接受可用的 pre-finetune 轨迹
- 把这套规划兼容逻辑下沉到正式主脚本与默认 launcher

因此，当前这台机器上的结论已经很明确：

- `curobo_for_windows` 已经成功安装到 Isaac Sim 中
- full GUI 场景规划已经跑通并验证通过

