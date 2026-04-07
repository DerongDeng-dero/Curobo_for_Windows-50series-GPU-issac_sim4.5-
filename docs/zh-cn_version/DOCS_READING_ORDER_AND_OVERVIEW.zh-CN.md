# Windows + Isaac Sim + cuRobo 文档阅读顺序与总览

## 1. 这份文档是做什么的

当前这套 Windows + Isaac Sim + cuRobo 工程，已经不再只有一篇安装说明。

现在的文档已经覆盖了：

- 安装与修复
- 可安装版本说明
- GUI 内 in-app 使用
- 自定义场景继续搭建
- 抓取 / 放置状态机
- 加载自己 USD 场景并接入状态机
- 完整修复记录与维护总结

文档一多，就会出现两个很常见的问题：

1. 不知道先看哪篇
2. 不知道某篇文档到底解决什么问题

这份文档的目的就是把当前这套**中文主文档**按逻辑顺序重新整理成一条清晰路线。

这里的“主文档”指的是当前这套 Windows + Isaac Sim + cuRobo 交付中，最直接面向使用者的文档。

---

## 2. 最推荐的总阅读顺序

如果你是从零开始，最推荐按下面顺序看：

(1) [`README.md`](../../README.md)

(2) [`WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.zh-CN.md`](./WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.zh-CN.md)

(3) [`INSTALLABLE_VERSION_MANUAL.zh-CN.md`](./INSTALLABLE_VERSION_MANUAL.zh-CN.md)

(4) [`ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.zh-CN.md`](./ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.zh-CN.md)

(5) [`ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.zh-CN.md`](./ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.zh-CN.md)

(6) [`ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.zh-CN.md`](./ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.zh-CN.md)

(7) [`ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.zh-CN.md`](./ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.zh-CN.md)

(8) [`curobo_isaacsim_windows_full_fix_guide.md`](./curobo_isaacsim_windows_full_fix_guide.zh-CN.md)

如果你不是从零开始，而是已经装好了，只想继续做 GUI 场景和任务流程，可以直接从：

- `(4)` 开始

如果你已经有自己的 USD 场景，想直接接 pick-place 状态机，可以直接从：

- `(7)` 开始

如果你遇到复杂环境问题、版本兼容问题、升级维护问题，再回头看：

- `(8)`

---

## 3. 不同人应该怎么读

## 3.1 路线 A：完全小白，从安装开始

按这个顺序：

- `(1) -> (2) -> (3) -> (4) -> (5) -> (6) -> (7)`

适合：

- 第一次在 Windows 上装 cuRobo
- 第一次在 Isaac Sim 里用 cuRobo
- 不想跳步骤

---

## 3.2 路线 B：已经装好了，只想在 GUI 里正常使用 cuRobo

按这个顺序：

- `(1) -> (4) -> (5)`

适合：

- 安装已经没问题
- 主要目标是“正常打开 Isaac Sim Full，然后在 GUI 里跑起来”

---

## 3.3 路线 C：已经能规划了，想做抓取 / 放置任务

按这个顺序：

- `(5) -> (6)`

适合：

- 已经会在 GUI 里跑单次规划
- 现在想做 pick-place 状态机

---

## 3.4 路线 D：已经有自己的 USD 场景，想接真实工作场景

按这个顺序：

- `(5) -> (6) -> (7)`

适合：

- 自己已经有桌子、工位、障碍物、料箱等 USD 资产
- 想把状态机接到自己的场景里

---

## 3.5 路线 E：维护者 / 排障 / 升级

按这个顺序：

- `(3) -> (8)`

适合：

- 你需要知道这套交付里到底改了什么
- 你准备维护、升级、迁移或排障

---

## 4. 各文档概览

## (1) [`README.md`](../../README.md)

定位：

- 总入口页

主要作用：

- 给出当前仓库最重要的文档入口
- 给出最短安装命令和 demo 启动命令
- 帮你快速定位后续该看哪篇

什么时候看：

- 第一次打开仓库时先看

看完后你应该知道：

- 当前有哪些主文档
- 安装和 demo 的最短入口是什么

---

## (2) [`WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.zh-CN.md`](./WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.zh-CN.md)

定位：

- 从零安装与修复的完整教程

主要作用：

- 面向 Windows + Isaac Sim 的真实安装流程
- 解释为什么原始安装方式会失败
- 给出一步一步可执行的修复和安装路径

什么时候看：

- 你还没有装好环境时
- 你还没跑通最小 smoke test 时

看完后你应该能完成：

- `install_in_isaacsim.bat`
- `verify_isaacsim_integration.bat`

---

## (3) [`INSTALLABLE_VERSION_MANUAL.zh-CN.md`](./INSTALLABLE_VERSION_MANUAL.zh-CN.md)

定位：

- 交付版本说明书

主要作用：

- 汇总当前这套“可安装版本”包含哪些脚本和文档
- 解释 wrapper、验证脚本、主入口脚本分别做什么
- 帮你理解这套交付的整体结构，而不只是会执行命令

什么时候看：

- 安装完成后
- 想知道仓库里每个关键脚本和文档有什么作用时
- 准备长期维护时

看完后你应该知道：

- 整套交付由哪些文件组成
- 哪个脚本负责安装、验证、demo、GUI 教学、正式入口

---

## (4) [`ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.zh-CN.md`](./ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.zh-CN.md)

定位：

- GUI 内 in-app 使用 cuRobo 的入门文档

主要作用：

- 解释为什么可以正常通过 `selector.bat` 启动 Isaac Sim
- 解释 standalone 脚本和 in-app 脚本的区别
- 教你如何在 `Isaac Sim Full -> Window > Script Editor` 里运行 cuRobo

什么时候看：

- 你已经安装好
- 你想在正常 GUI 里使用 cuRobo，而不是只会命令行启动

看完后你应该能完成：

- 在 GUI 内跑通最基础的 in-app 脚本

---

## (5) [`ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.zh-CN.md`](./ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.zh-CN.md)

定位：

- 自定义机器人与场景的继续教程

主要作用：

- 讲如何换机器人
- 讲如何搭桌子和障碍物
- 讲如何让 cuRobo world 和 GUI 场景同步
- 讲如何从“单次规划”继续演进成你自己的场景模板

什么时候看：

- 你已经能在 GUI 里跑 beginner 脚本
- 你要开始搭自己的桌面、障碍物、目标点

看完后你应该能完成：

- 在 GUI 里搭出自己的基础工作台场景

---

## (6) [`ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.zh-CN.md`](./ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.zh-CN.md)

定位：

- 抓取 / 放置状态机与教学型场景建模文档

主要作用：

- 把单次规划升级成抓取 / 抬升 / 搬运 / 放置 / 回撤的完整流程
- 解释状态机每一步在做什么
- 解释如何做适合初学者的场景建模

什么时候看：

- 你已经不满足于“单次到点规划”
- 你要开始做任务流

看完后你应该能完成：

- 跑通教学型 pick-place 状态机
- 理解为什么要把 `/World/scene`、`/World/task`、`/World/markers` 分开

---

## (7) [`ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.zh-CN.md`](./ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.zh-CN.md)

定位：

- 将自己的 USD 场景接入 pick-place 状态机的教程

主要作用：

- 讲如何加载你自己的 USD 场景
- 讲如何指定 cuRobo 该从哪些 root 读取障碍物
- 讲如何把现有 pick object / pick target / place target 接入状态机
- 讲如果场景里没有 marker，如何让脚本自动补 runtime marker

什么时候看：

- 你已经有自己的 USD 场景
- 你要把之前的教学模板升级成真实工作场景模板

看完后你应该能完成：

- 用自己的 USD 场景驱动 pick-place 状态机

---

## (8) [`curobo_isaacsim_windows_full_fix_guide.md`](./curobo_isaacsim_windows_full_fix_guide.zh-CN.md)

定位：

- 完整修复记录与维护总结

主要作用：

- 记录这次真实修复过程中的判断、报错、根因和改动
- 解释兼容层、fallback、脚本迁移和文档演进
- 适合维护者、升级者和排障时查背景

什么时候看：

- 你要理解为什么现在这套方案能跑
- 你要升级 Isaac Sim、PyTorch、CUDA 或 cuRobo
- 你要做长期维护

看完后你应该知道：

- 这套工程的历史修复逻辑
- 关键兼容点和后续维护风险

---

## 5. 最推荐的实际使用步骤

如果你现在要真正开始上手，我建议你按下面步骤执行。

### 第一步：先确认环境已经通

看：

- `(2)`

执行：

```powershell
cd D:\isaac-sim\zzcurobo\curobo_for_windows
.\install_in_isaacsim.bat
.\verify_isaacsim_integration.bat
```

目标：

- 先确认不是环境问题

---

### 第二步：学会在 GUI 内正常运行

看：

- `(4)`

目标：

- 学会 `selector -> Isaac Sim Full -> Script Editor -> Run`

---

### 第三步：搭自己的基础工作台

看：

- `(5)`

目标：

- 学会换机器人、改障碍物、改目标点、同步 world

---

### 第四步：把单次规划升级成任务流

看：

- `(6)`

目标：

- 学会状态机和教学型场景建模

---

### 第五步：把自己的 USD 场景接进来

看：

- `(7)`

目标：

- 学会把真实工作场景接到状态机上

---

### 第六步：只有需要维护和深挖时，再看完整修复记录

看：

- `(3)`
- `(8)`

目标：

- 理解结构、兼容逻辑和历史修复背景

---

## 6. 一句话总结每篇文档

(1) `README.md`：总入口，先知道去哪里。

(2) `WINDOWS_ISAACSIM_CUROBO_INSTALL_TUTORIAL.zh-CN.md`：从零安装、修复、跑通环境。

(3) `INSTALLABLE_VERSION_MANUAL.zh-CN.md`：理解当前交付版本里每个脚本和文档的角色。

(4) `ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.zh-CN.md`：学会在正常 Isaac Sim GUI 里用 cuRobo。

(5) `ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.zh-CN.md`：开始搭自己的机器人和场景。

(6) `ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.zh-CN.md`：把单次规划升级成 pick-place 状态机。

(7) `ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.zh-CN.md`：把自己的 USD 场景接入状态机。

(8) `curobo_isaacsim_windows_full_fix_guide.md`：需要维护、升级、排障时再深入看。

---

## 7. 最后给你的最短建议

如果你现在已经安装成功，并且下一步目标是“在自己的场景里做任务”，那最短路线就是：

- 先看 `(4)`
- 再看 `(5)`
- 然后看 `(6)`
- 最后看 `(7)`

如果你后面准备长期维护这套工程，再补看：

- `(3)`
- `(8)`

