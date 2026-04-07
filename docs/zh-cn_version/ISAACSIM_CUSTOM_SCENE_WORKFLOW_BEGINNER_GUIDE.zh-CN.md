# Isaac Sim + cuRobo 自定义机器人与场景继续搭建指南

## 1. 这份文档是上一份入门指南的下一步

如果下面这些已经完成：

- 能正常运行 `install_in_isaacsim.bat`
- 能正常运行 `verify_isaacsim_integration.bat`
- 能通过 `isaac-sim.selector.bat` 进入 GUI
- 能在 `Window > Script Editor` 里运行
  - [`gui_in_app_motion_gen_beginner.py`](../../examples/isaac_sim/gui_in_app_motion_gen_beginner.py)

那么你现在已经进入第二阶段：

- 不再只是“证明能跑”
- 而是开始“搭自定义场景”

这份文档就是为这个阶段准备的。

---

## 2. 这一阶段你真正要学会的事情

你以后要在 Isaac Sim 里长期用 cuRobo，本质上要学会下面 5 件事：

1. 换机器人
2. 搭桌面 / 障碍物场景
3. 让 cuRobo 读取这些障碍物
4. 给目标姿态并规划
5. 反复修改，逐步演进成自定义任务脚本

如果你把这 5 件事掌握了，后面不管是抓取、堆叠还是搬运，都会顺很多。

---

## 3. 这一阶段我给你准备了什么

我新增了一个更适合继续改的 in-app 模板脚本：

- [`gui_in_app_custom_scene_template.py`](../../examples/isaac_sim/gui_in_app_custom_scene_template.py)

它和上一份 beginner 脚本的区别是：

- 上一份更像“最小演示”
- 这一份更像“自定义场景模板”

它把最常改的东西都集中到了文件顶部：

- `ROBOT_CFG_NAME`
- `EXTERNAL_ASSET_PATH`
- `EXTERNAL_ROBOT_CONFIGS_PATH`
- `ROBOT_BASE_POSITION`
- `GOAL_POSITION`
- `GOAL_QUATERNION`
- `SCENE_CUBOIDS`
- `RESET_STAGE_ON_RUN`

所以你以后继续搭场景时，优先改这个文件最上面的配置块就行。

---

## 4. 先用最标准的方式把模板跑起来

## 4.1 启动 Isaac Sim

```powershell
<ISAAC_SIM_ROOT>\isaac-sim.selector.bat
```

进入：

- `Isaac Sim Full`

## 4.2 打开 Script Editor

如果没有 Script Editor：

1. 打开 `Window > Extensions`
2. 搜索 `script editor`
3. 启用：
   - `omni.kit.window.script_editor`
4. 再打开：
   - `Window > Script Editor`

## 4.3 运行模板脚本

打开文件：

- `<REPO_ROOT>\examples\isaac_sim\gui_in_app_custom_scene_template.py`

点击 Run。

## 4.4 预期现象

预期现象：

- 一个机器人
- 一张桌子
- 两个箱子障碍物
- 一个红色目标块
- 机器人规划并执行到目标附近

Console 里应该出现类似：

```text
CUSTOM_TEMPLATE: robot imported at ...
CUSTOM_TEMPLATE: extracted ... obstacle(s) from stage
CUSTOM_TEMPLATE: motion generator warmed up
CUSTOM_TEMPLATE: planning success, trajectory points=...
CUSTOM_TEMPLATE: trajectory playback finished
```

---

## 5. 先理解这个模板的结构

你不需要一上来读懂所有代码。

只要先理解这几个部分就够了。

## 5.1 顶部配置块

这是你以后最常改的地方。

例如：

```python
RESET_STAGE_ON_RUN = True
ROBOT_CFG_NAME = "franka.yml"
GOAL_POSITION = [0.38, -0.22, 0.42]
SCENE_CUBOIDS = [...]
```

含义：

- 要不要每次运行都清空场景
- 用哪台机器人
- 目标点在哪里
- 桌子和障碍物怎么摆

## 5.2 `_load_robot_cfg()`

作用：

- 加载 robot yaml
- 如果你有外部资产路径，也在这里注入

## 5.3 `_build_world_config()`

作用：

- 把你写在 `SCENE_CUBOIDS` 里的障碍物转成 cuRobo 能理解的 `WorldConfig`

## 5.4 `_create_goal_marker()`

作用：

- 在 GUI 里画一个红色目标块
- 方便你直观看到目标在哪里

## 5.5 `main()`

作用：

- 建 stage
- 导入机器人
- 放障碍物
- 构建 `MotionGen`
- 规划
- 执行

---

## 6. 第一步学会改目标点

这是最简单也最建议最先做的事情。

改这两个变量：

```python
GOAL_POSITION = [0.38, -0.22, 0.42]
GOAL_QUATERNION = [1.0, 0.0, 0.0, 0.0]
```

建议做法：

1. 先只改 `GOAL_POSITION`
2. 一次只改一点
3. 每改一次就重新运行

如果你是小白，一开始不要急着改姿态。

先把“不同位置都能到”练熟。

---

## 7. 第二步学会改桌子和障碍物

## 7.1 现在的障碍物在哪里定义

就在：

```python
SCENE_CUBOIDS = [
    {
        "name": "table_top",
        "pose": [0.62, 0.0, 0.20, 1.0, 0.0, 0.0, 0.0],
        "dims": [0.90, 1.20, 0.40],
    },
    ...
]
```

## 7.2 每个字段是什么意思

### `name`

就是障碍物名字。

### `pose`

格式是：

```text
[x, y, z, qw, qx, qy, qz]
```

前 3 个是位置，后 4 个是四元数。

### `dims`

格式是：

```text
[x_size, y_size, z_size]
```

也就是长宽高。

## 7.3 小白如何改最稳

推荐顺序：

1. 先只改 `pose`
2. 再改 `dims`
3. 最后再增加更多障碍物

不要一口气改很多项。

---

## 8. 第三步学会换机器人

## 8.1 最简单的情况：仓库里已经有这个 robot yaml

直接改：

```python
ROBOT_CFG_NAME = "your_robot.yml"
```

前提：

- 这个 yaml 已经能被 cuRobo 找到
- 它里面引用的模型路径没错

## 8.2 如果机器人不在默认路径里

就改这两个值：

```python
EXTERNAL_ASSET_PATH = r"<ASSET_ROOT>"
EXTERNAL_ROBOT_CONFIGS_PATH = r"<ROBOT_CONFIG_ROOT>"
```

这适合：

- 自定义 URDF / USD / mesh 不放在默认仓库资产目录里

## 8.3 小白最容易踩的坑

不要只改 `ROBOT_CFG_NAME`，却忘了：

- yaml 里引用的 URDF 路径
- 外部资产根目录
- mesh 是否真的存在

你看到“机器人导不进来”，很多时候不是 cuRobo 不行，而是资源路径没配对。

---

## 9. 第四步学会理解“GUI 看得见”和“cuRobo 真正拿来碰撞”的区别

这是继续搭场景时最关键的认知之一。

你在 GUI 里看到桌子和箱子，并不自动等于：

- cuRobo 已经拿它们做碰撞检测

cuRobo 必须明确拿到一份 world 数据。

这个模板里是这样做的：

1. 先根据 `SCENE_CUBOIDS` 创建 `WorldConfig`
2. 再用 `usd_helper.add_world_to_stage(...)` 把它加到 stage
3. 然后再通过：
   - `usd_helper.get_obstacles_from_stage(...)`
   - 把它重新读回 cuRobo world

这样做的好处是：

- GUI 和规划 world 来自同一个来源
- 不容易出现“看起来有障碍物，但规划没管它”的错觉

---

## 10. 第五步：学会保存 stage

小白做到这一步以后，经常会问：

- “我搭好的场景下次还想继续用，怎么办？”

答案就是：

- 保存 stage

## 10.1 最简单做法

在 Isaac Sim GUI 里直接：

- `File > Save As`

保存成一个 `.usd` 文件。

## 10.2 需要理解的一点

保存 stage 保存的是：

- GUI 里的场景内容

但并不自动替代你脚本里的逻辑。

所以后面你通常有两种路线：

### 路线 A：继续用代码建场景

优点：

- 版本清晰
- 好复制
- 好回归

适合：

- 你还在快速试错阶段

### 路线 B：加载保存好的 USD 场景

优点：

- 手工搭好的场景可重复打开

适合：

- 当前已经有比较稳定的 GUI 场景

对小白的建议是：

- 前期优先路线 A
- 等场景稳定以后再转路线 B

---

## 11. 第六步学会从“单次规划”升级到“任务脚本”

你现在这个模板是：

- 放一个目标
- 规划一次
- 执行一次

这叫“单次规划脚本”。

后面如果需要做抓取、搬运、堆叠，需要升级成“任务脚本”。

一个任务脚本通常会多出下面这些结构：

1. 当前任务状态
   - 还没抓
   - 正在去抓
   - 已抓住
   - 正在去放
2. world update
   - 什么时候刷新障碍物
3. 传感器或目标更新
   - 目标变了要不要重规划
4. 执行器控制
   - 夹爪开合
   - 轨迹播放

现成参考是：

- [`simple_stacking.py`](../../examples/isaac_sim/simple_stacking.py)

但我不建议你直接从那里开始改。

更稳的路线是：

1. 先把 `gui_in_app_custom_scene_template.py` 改熟
2. 再把它复制成自定义任务模板
3. 最后参考 `simple_stacking.py` 加状态机

---

## 12. 推荐开发节奏

这是我最推荐的小白节奏。

## 12.1 第一步：固定一个最小工作模板

先别换太多东西。

只确认：

- 一个机器人
- 一张桌子
- 两个障碍物
- 一个目标
- 一次规划成功

## 12.2 第二步：一次只改一个变量

例如这周只练：

- 改目标点

下一步再练：

- 改桌子尺寸

再下一步：

- 换机器人

不要一次同时改 5 件事。

## 12.3 第三步：每次改完都做回归

建议你每次改完，都至少做两个检查：

1. GUI 里是否看到了正确的场景
2. cuRobo 是否还在 Console 里打印 `planning success`

## 12.4 第四步：开始做“自定义脚本副本”

不要永远直接改模板原件。

建议你复制一份：

- `my_scene_v1.py`
- `my_scene_v2.py`

这样你每一步都能回退。

---

## 13. 建议现在就按这个顺序继续走

### 今天先做

1. 运行：
   - [`gui_in_app_custom_scene_template.py`](../../examples/isaac_sim/gui_in_app_custom_scene_template.py)
2. 只改：
   - `GOAL_POSITION`
3. 重新运行 3 次

### 然后做

1. 改 `SCENE_CUBOIDS`
2. 把桌子尺寸改大或改小
3. 加一个新障碍物

### 再然后做

1. 把 `ROBOT_CFG_NAME` 换成机器人
2. 如果需要，设置：
   - `EXTERNAL_ASSET_PATH`
   - `EXTERNAL_ROBOT_CONFIGS_PATH`

### 最后做

1. 复制这个脚本
2. 加入自定义抓取逻辑
3. 慢慢演进成自定义任务脚本

---

## 14. 常见问题

## 14.1 我已经开了 GUI，为什么不能直接跑 `motion_gen_reacher.py`

因为它是 standalone 脚本。

里面会自己创建 `SimulationApp`。

而你当前 GUI 已经是一个正在运行的 Isaac Sim 实例了。

这两套启动逻辑不能这么直接叠在一起。

## 14.2 我在 GUI 里看到了障碍物，为什么机器人还是撞上去

先检查：

1. 障碍物是不是在 cuRobo world 里
2. `get_obstacles_from_stage(...)` 读出来了多少个 object
3. 是否真的把这个 parsed world 传进 `MotionGenConfig`

不要只看 GUI，要看 Console 输出。

## 14.3 我换了机器人后立刻报关节维度错误

这通常说明：

- full joint state
- active joint state
- articulation joint order

三者没有对齐。

不建议单独重写这套逻辑。

优先复用：

- [`motion_gen_compat.py`](../../examples/isaac_sim/motion_gen_compat.py)

里的：

- `get_retract_state_for_articulation(...)`
- `get_full_articulation_plan(...)`

## 14.4 如果规划失败怎么办

先看是不是：

- 目标太远
- 目标在桌子里
- 障碍物太近
- 姿态太苛刻

然后再看：

- `status`
- 是否已有 pre-finetune 轨迹

当前模板已经复用了兼容规划入口：

- `plan_single_with_compat(...)`

所以不要先怀疑环境坏了，先怀疑目标和场景是否合理。

---

## 15. 这一阶段的最短结论

你接下来最应该做的，不是一下子做复杂抓取，而是：

1. 跑 [`gui_in_app_custom_scene_template.py`](../../examples/isaac_sim/gui_in_app_custom_scene_template.py)
2. 学会改目标
3. 学会改障碍物
4. 学会换机器人
5. 保证每一步改完都还能规划成功

只要这一步站稳，后面无论是抓取、堆叠、搬运、状态机，都会容易很多。

