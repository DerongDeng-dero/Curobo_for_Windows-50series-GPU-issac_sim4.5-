# Windows + Isaac Sim + cuRobo 安装与修复完整教程

## 1. 这份教程是给谁用的

这份文档写给下面这类用户：

- 你在 Windows 10/11 上使用 Isaac Sim。
- 你的显卡比较新，比如 RTX 50 系。
- 你的 Isaac Sim 版本比较旧，内置的 PyTorch / CUDA 版本也比较旧。
- 你把 `curobo_for_windows` 放进 Isaac Sim 目录后，`pip install -e .` 一直报错。
- 你不想猜，不想试错，只想照着步骤把它装好。

这份文档基于一次真实修复过程整理，验证时间是 **2026-04-03**，验证环境如下：

- 操作系统：Windows 11 Home China 25H2
- CPU：Intel Core i5-14600K
- GPU：NVIDIA GeForce RTX 5070
- Isaac Sim：4.5.0
- Isaac Sim 内置 PyTorch：2.5.1+cu118
- 本机 CUDA Toolkit：11.8
- MSVC：Visual Studio 2022 Build Tools / 14.50
- cuRobo 代码位置：`D:\isaac-sim\zzcurobo\curobo_for_windows`

## 2. 最终结论

这套环境现在已经做到下面几点：

- `curobo_for_windows` 可以安装进 Isaac Sim 的 Python 环境。
- 编译出来的 Windows `.pyd` 扩展可以正常导入。
- Isaac Sim 的 `SimulationApp` 可以正常启动。
- 可以运行 headless 的 Isaac Sim + cuRobo 烟雾测试。
- 在 RTX 5070 这类 `sm_120` 新卡上，可以自动绕过旧版 PyTorch/NVRTC 的 JIT 架构兼容问题。

换句话说，现在不是“只能编译”，而是“已经能装、能导入、能跑最小规划验证”。

## 3. 这次真正的报错根因是什么

一开始看起来像“安装报错”，但其实是多层问题叠在一起。

### 问题 1：Isaac Sim 根目录的 `python.bat` 是空的

现象：

- 用 Isaac Sim 自带 Python 安装时，`import torch` 失败。
- `pip install -e .` 在生成元数据阶段就报：

```text
ModuleNotFoundError: No module named 'torch'
```

原因：

- Isaac Sim 的 PyTorch 不在普通 `site-packages` 里。
- 它在扩展目录的 `pip_prebundle` 里，比如：
  - `exts/omni.isaac.ml_archive/pip_prebundle`
  - `exts/omni.isaac.core_archive/pip_prebundle`
- 你的根目录 `python.bat` 是空文件，所以这些路径根本没加进 `PYTHONPATH`。

### 问题 2：`setup.py` 在“元数据阶段”就强行导入 `torch`

现象：

- 还没开始真正编译 C++ / CUDA，就已经在 `Preparing metadata (pyproject.toml)` 崩了。

原因：

- 原始 [`setup.py`](../../setup.py) 顶层直接写了：

```python
from torch.utils.cpp_extension import BuildExtension, CUDAExtension
```

- 这会导致 `pip` 在读取包信息时就要求构建环境里已经存在 PyTorch。
- 一旦 Isaac Sim 的 `torch` 没被正确暴露出来，就直接死在最前面。

### 问题 3：CUDA 11.8 和新版 MSVC 14.50 不兼容

现象：

- 编译真正开始以后，`nvcc` 报：

```text
error STL1002: Unexpected compiler version, expected CUDA 12.4 or newer.
```

原因：

- 你的机器上是新版本 Visual Studio Build Tools。
- CUDA 11.8 遇到新版 STL / 编译器时会卡这个静态断言。

### 问题 4：扩展编译成功后，`.pyd` 仍然 DLL 加载失败

现象：

- `pip install -e .` 看起来装成功了。
- 但导入扩展时报：

```text
ImportError: DLL load failed while importing lbfgs_step_cu: 找不到指定的模块。
```

原因：

- Windows 不会自动去 `torch/lib` 里找 PyTorch 依赖 DLL。
- `.pyd` 本体在，但它依赖的 `torch.dll`、`c10.dll`、`torch_cuda.dll` 等动态库没有进 DLL 搜索路径。

### 问题 5：RTX 5070 这类新卡会在 JIT / NVRTC 阶段炸掉

现象：

- 基础 `torch.cuda` 张量计算能跑。
- 但是高层模块，比如 `MotionGen`，导入时会在运行时编译阶段报：

```text
RuntimeError: nvrtc: error: invalid value for --gpu-architecture (-arch)
```

原因：

- 你的显卡是 `sm_120`。
- Isaac Sim 4.5.0 自带的是 `torch 2.5.1 + CUDA 11.8`。
- 这套运行时不认识 `sm_120` 的 NVRTC JIT 编译目标。
- 所以不是所有 CUDA 都不能跑，而是“运行时 JIT 编译的那部分”不能跑。

### 问题 6：`isaacsim.simulation_app` 一开始都导不出来

现象：

- 直接执行：

```powershell
D:\isaac-sim\python.bat -c "import isaacsim"
```

会报 `IndexError` 或 `ModuleNotFoundError: isaacsim.simulation_app`。

原因：

- `python_packages/isaacsim/__init__.py` 依赖环境变量：
  - `ISAAC_PATH`
  - `EXP_PATH`
  - `CARB_APP_PATH`
- 你的根入口脚本没有设置这些变量。

## 4. 这次到底改了哪些文件

下面这些改动已经落盘：

### Isaac Sim 根目录

- [`D:\isaac-sim\python.bat`](../../../../python.bat)
  - 补回 Isaac Sim Python 入口。
  - 增加 `ISAAC_PATH`、`EXP_PATH`、`CARB_APP_PATH`。

- [`D:\isaac-sim\setup_python_env.bat`](../../../../setup_python_env.bat)
  - 把 Isaac Sim 的 `pip_prebundle` 路径加回 `PYTHONPATH`。

### cuRobo 代码

- [`setup.py`](../../setup.py)
  - 把 `torch` 的导入延迟到真正 build 阶段。
  - 加入 Windows 下 `CUDA 11.8 + 新版 MSVC` 的兼容编译宏。

- [`src/curobo/curobolib/__init__.py`](../../src/curobo/curobolib/__init__.py)
  - Windows 下导原生扩展前，自动注册 `torch/lib` 为 DLL 搜索目录。

- [`src/curobo/util/torch_utils.py`](../../src/curobo/util/torch_utils.py)
  - 自动检测 “新 GPU + 老 CUDA/NVRTC” 组合。
  - 如果发现 `sm_120` 这类运行时 JIT 不支持的环境，就自动禁用 `torch.jit`，避免 `nvrtc -arch` 报错。

### 新增的安装版工具

- [`isaacsim_python.bat`](../../isaacsim_python.bat)
  - 自带环境修复的 Isaac Sim Python wrapper。

- [`install_in_isaacsim.bat`](../../install_in_isaacsim.bat)
  - 一键安装脚本。

- [`verify_isaacsim_integration.bat`](../../verify_isaacsim_integration.bat)
  - 一键验证脚本。

- [`examples/isaac_sim/smoke_test_headless.py`](../../examples/isaac_sim/smoke_test_headless.py)
  - Headless 最小自检脚本。

## 5. 最推荐的安装方法

这是最简单、最不容易出错的方式。

### 第 1 步：确认目录结构

推荐把仓库放在 Isaac Sim 根目录里，像这样：

```text
D:\isaac-sim
├─ kit
├─ exts
├─ apps
├─ python_packages
└─ zzcurobo
   └─ curobo_for_windows
```

### 第 2 步：进入 cuRobo 目录

在 PowerShell 里执行：

```powershell
cd D:\isaac-sim\zzcurobo\curobo_for_windows
```

### 第 3 步：运行安装脚本

直接执行：

```powershell
.\install_in_isaacsim.bat
```

你应该看到类似输出：

```text
[1/3] Checking Isaac Sim Python environment...
isaacsim ok
2.5.1+cu118
[2/3] Installing cuRobo into Isaac Sim...
...
Successfully installed nvidia_curobo-...
[3/3] Installation complete.
```

### 第 4 步：运行验证脚本

安装完立刻执行：

```powershell
.\verify_isaacsim_integration.bat
```

如果成功，你最后应该看到：

```text
Smoke test passed.
```

这一步会自动做下面这些事：

- 启动 Isaac Sim `SimulationApp`
- 导入 Franka 机器人到 USD 场景
- 从 USD 场景提取障碍物
- 构建 cuRobo `MotionGen`
- 做一次 headless 规划
- 成功后自动退出

## 6. 如果你想手工执行，也可以

### 使用自带 wrapper 进入 Isaac Sim Python

最稳妥的入口不是直接用 `kit/python/python.exe`，而是：

```powershell
.\isaacsim_python.bat -c "import isaacsim, torch; print(torch.__version__)"
```

如果 cuRobo 不在 Isaac Sim 根目录下面，也可以显式指定 Isaac Sim 根目录：

```powershell
.\isaacsim_python.bat --isaac-root D:\isaac-sim -c "import isaacsim"
```

### 手工安装

```powershell
.\isaacsim_python.bat -m pip install -e . --no-build-isolation
```

### 手工跑 smoke test

```powershell
.\isaacsim_python.bat -u .\examples\isaac_sim\smoke_test_headless.py
```

## 7. 为什么这个“新可安装版本”比原来稳定

因为它不再依赖“你本机正好配置对了”。

### 原来的脆弱点

- 依赖 Isaac Sim 根目录 `python.bat` 恰好是正常的。
- 依赖用户自己知道怎么把 `pip_prebundle` 塞进 `PYTHONPATH`。
- 依赖安装时先能看到 `torch`。
- 依赖 Windows 自动帮你找到 PyTorch 的 DLL。
- 依赖新显卡在旧 NVRTC 上也正好不炸。

### 现在的稳定点

- `isaacsim_python.bat` 自己补环境。
- `setup.py` 不会在元数据阶段抢先导 `torch`。
- `.pyd` 导入前会自动补 `torch/lib`。
- 遇到 `sm_120 + CUDA 11.8` 会自动禁用 JIT。
- 安装脚本和验证脚本是成对存在的，不需要靠“装完自己猜”。

## 8. 你会看到哪些“看起来吓人但其实可以接受”的警告

下面这些警告，在当前验证环境里是可以接受的：

### 警告 1：PyTorch 说 RTX 5070 不受支持

类似：

```text
NVIDIA GeForce RTX 5070 with CUDA capability sm_120 is not compatible with the current PyTorch installation.
```

解释：

- 这是 Isaac Sim 自带 PyTorch 的兼容性警告。
- 在本次验证里，基础 CUDA 张量运算可以跑，cuRobo 规划 smoke test 也能跑。
- 真正致命的是 JIT/NVRTC；这个已经由代码自动降级绕开。

### 警告 2：Iray 不支持新显卡

类似：

```text
GPU ... compute capability 12.0 is unsupported by this version of iray photoreal
```

解释：

- 这是渲染器 Iray 的警告。
- 和 cuRobo 安装、编译、最小规划验证不是一回事。

### 警告 3：大量 `deprecated`

解释：

- Isaac Sim 4.5.0 对很多 `omni.isaac.*` 命名空间都加了弃用警告。
- 这些不是这次安装失败的根因。
- 它们会影响“代码现代化程度”，但不阻止当前 smoke test 成功。

## 9. 常见故障对照表

### `ModuleNotFoundError: No module named 'torch'`

说明：

- 你没有通过正确的 Isaac Sim Python 入口安装。

解决：

- 不要直接用系统 Python。
- 不要直接裸跑 `kit/python/python.exe`。
- 用：

```powershell
.\install_in_isaacsim.bat
```

或者：

```powershell
.\isaacsim_python.bat -m pip install -e . --no-build-isolation
```

### `ModuleNotFoundError: No module named 'pkg_resources'`

说明：

- 你在一个不完整的 Python 环境里构建，或者 build isolation 环境不对。

解决：

- 继续使用上面的 wrapper。
- 保留 `--no-build-isolation`。

### `error STL1002: Unexpected compiler version, expected CUDA 12.4 or newer`

说明：

- CUDA 11.8 遇到了过新的 MSVC。

解决：

- 使用当前仓库里的修复版 [`setup.py`](../../setup.py)。
- 不要恢复成原始版。

### `ImportError: DLL load failed while importing *.pyd`

说明：

- Windows 没找到 PyTorch 动态库。

解决：

- 使用当前仓库里的修复版 [`src/curobo/curobolib/__init__.py`](../../src/curobo/curobolib/__init__.py)。

### `RuntimeError: nvrtc: error: invalid value for --gpu-architecture (-arch)`

说明：

- 新显卡触发了旧版 NVRTC/JIT 架构不兼容。

解决：

- 使用当前仓库里的修复版 [`src/curobo/util/torch_utils.py`](../../src/curobo/util/torch_utils.py)。
- 它会自动禁用有问题的 JIT 路径。

### `ModuleNotFoundError: isaacsim.simulation_app` 或 `IndexError`

说明：

- `ISAAC_PATH / EXP_PATH / CARB_APP_PATH` 没设置好。

解决：

- 用：

```powershell
.\isaacsim_python.bat -c "import isaacsim"
```

- 不要直接用没修过的空 `python.bat`。

## 10. 我建议你以后怎么用

### 安装

始终用：

```powershell
.\install_in_isaacsim.bat
```

### 验证

始终用：

```powershell
.\verify_isaacsim_integration.bat
```

### 进入 Isaac Sim Python 做调试

始终用：

```powershell
.\isaacsim_python.bat
```

## 11. 这份方案的边界

这次已经验证：

- 安装成功
- 原生扩展导入成功
- Isaac Sim headless 启动成功
- cuRobo 最小规划 smoke test 成功

这次还没有做的事：

- 没有把所有旧 example 都逐个现代化为 Isaac Sim 4.5 风格
- 没有逐个验证所有机器人配置
- 没有做大规模长期稳定性压力测试

所以这套方案的定位是：

- **已经足够安装和验证使用**
- **已经比原版 Windows 安装流程稳定很多**
- **如果要做更大范围发布，还可以继续补更多 example 适配**

## 12. 最后给普通用户的最短版本

如果你什么都不想研究，只想装上，请照这 4 条做：

1. 打开 PowerShell。
2. `cd D:\isaac-sim\zzcurobo\curobo_for_windows`
3. 执行 `.\install_in_isaacsim.bat`
4. 执行 `.\verify_isaacsim_integration.bat`

如果最后看到：

```text
Smoke test passed.
```

就说明这套环境已经装好了。

