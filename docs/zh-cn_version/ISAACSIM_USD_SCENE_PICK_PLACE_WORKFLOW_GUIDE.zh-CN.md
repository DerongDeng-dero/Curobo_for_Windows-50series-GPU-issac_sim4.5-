# Isaac Sim + cuRobo：加载自己 USD 场景并接入抓取 / 放置状态机指南

## 1. 这份文档解决什么问题

前面那份状态机模板：

- 会自己搭一个教学用场景
- 适合先学抓取 / 放置流程

但你真正长期会遇到的下一步是：

- 你已经有自己的 USD 场景
- 你想在 Isaac Sim 里正常打开它
- 然后把 cuRobo 的抓取 / 放置状态机接进去

这份文档解决的就是这个问题。

这次新增的脚本是：

- [`gui_in_app_pick_place_from_usd_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_from_usd_template.py)

它的定位非常明确：

- 先加载你自己的环境 USD 场景
- 再复用场景里已有机器人 articulation，或者按需运行时注入机器人
- 再把 pick-place 状态机接上去

这份脚本目前的默认路线是：

- **复用你自己的环境场景**
- **优先复用你自己的机器人 articulation**
- **缺失任务辅助物体时，再由脚本补 runtime helper**

这样做的好处是：

- 如果你的工位 USD 里已经有机器人，就不用重复导入第二台机器人
- 如果你的场景还没整理好，也还能退回到运行时注入模式
- 对初学者和长期维护两种工作流都兼容

---

## 2. 你会得到什么

运行这个模板后，你可以做到：

1. 用 `selector.bat` 正常启动 Isaac Sim Full
2. 打开你自己的 USD 场景
3. 在 `Script Editor` 里运行这个脚本
4. 让脚本读取你指定的场景障碍物 root
5. 复用场景里已有机器人 articulation，或者按需导入机器人
6. 使用你已有的拾取物体 / 拾取点 / 放置点，或者让脚本自动补 runtime marker
7. 让机器人执行：
   - 打开夹爪
   - 到预抓取位
   - 到抓取位
   - 闭合夹爪
   - 抬升
   - 移动到预放置位
   - 放置
   - 回撤

---

## 3. 这份脚本的两个使用模式

## 3.1 模式 A：你先在 GUI 里打开自己的场景

这是最推荐的模式。

步骤是：

1. 手工打开 Isaac Sim GUI
2. 手工打开你自己的 USD 场景
3. 再运行脚本

这时你在脚本里保持：

```python
OPEN_USD_STAGE_ON_RUN = False
```

好处是：

- 你可以先看清场景长什么样
- 你可以先在 GUI 里检查 prim 路径
- 你可以边看 Stage 树边改脚本配置

对小白最友好。

## 3.2 模式 B：让脚本主动打开某个 USD 文件

如果你已经很明确要加载哪个文件，也可以这样：

```python
OPEN_USD_STAGE_ON_RUN = True
USD_STAGE_PATH = r"D:\isaac-sim\your_scenes\pick_place_workcell.usd"
```

这样脚本会自动打开这个 USD。

好处是：

- 适合固定工作流
- 适合你以后反复调同一个场景

---

## 4. 先理解这份模板的思路

这份模板不是“万能自动识别任意场景语义”的系统。

它要求你至少明确 4 类东西：

1. 哪些 prim 属于静态障碍物
2. 哪个 prim 是机器人 articulation root
3. 哪个 prim 是要抓的物体
4. 哪个 prim 是拾取目标点，哪个 prim 是放置目标点

如果你没有现成的拾取 / 放置 marker，也没关系。

脚本会这样处理：

- 如果你给的 `PICK_TARGET_PRIM_PATH` 不存在：
  - 它会自动创建一个 runtime pick marker
- 如果你给的 `PLACE_TARGET_PRIM_PATH` 不存在：
  - 它会自动创建一个 runtime place marker
- 如果你给的 `PICK_OBJECT_PRIM_PATH` 不存在：
  - 它会自动创建一个 runtime 的教学方块

也就是说：

- **环境尽量用你自己的 USD**
- **任务辅助物体可以先让脚本补齐**

这是一个非常实用的过渡方案。

---

## 5. 推荐你把自己的 USD 场景整理成什么结构

最推荐的第一版结构是：

```text
/World
  /Franka
  /scene
    /table
    /wall
    /bin_left
    /bin_right
    /blocker
  /task
    /pick_cube
    /pick_target
    /place_target
```

这个结构的优点非常大：

- `/World/Franka` 或别的机器人 root 可以稳定给脚本复用
- `/World/scene` 专门放静态障碍物
- `/World/task` 专门放任务物体和任务目标点
- 脚本里 `SCENE_COLLISION_ROOTS = ["/World/scene"]` 可以直接工作

你以后维护的时候也会很轻松，因为你不用反复猜：

- 哪些东西应该给 cuRobo 当障碍物
- 哪些东西只是任务目标点

如果你自己的场景树不是这个结构，也没关系。

你只要改脚本里这些配置：

- `SCENE_COLLISION_ROOTS`
- `PICK_OBJECT_PRIM_PATH`
- `PICK_TARGET_PRIM_PATH`
- `PLACE_TARGET_PRIM_PATH`

就可以接上。

---

## 6. 小白一步一步操作

## 6.1 第一步：启动 Isaac Sim

运行：

```powershell
D:\isaac-sim\isaac-sim.selector.bat
```

进入：

- `Isaac Sim Full`

---

## 6.2 第二步：打开自己的 USD 场景

如果你用模式 A：

1. 在 GUI 里点击 `File > Open`
2. 选择你自己的 `.usd` 文件
3. 等场景加载完

这一步的目标是：

- 让你在界面里先看到自己的桌子、障碍物、任务区

---

## 6.3 第三步：打开 Stage 树，记住关键 prim 路径

你现在最该做的事不是马上跑脚本，而是先看清楚 Stage 里的路径。

重点记下面几类路径：

1. 环境障碍物 root 路径
2. 机器人 articulation root 路径
3. 要抓取的物体 prim 路径
4. 拾取目标点 prim 路径
5. 放置目标点 prim 路径

例如你可能看到：

```text
/World/scene
/World/Franka
/World/task/pick_cube
/World/task/pick_target
/World/task/place_target
```

这时候脚本里就填这些路径。

如果你看到的是别的结构，例如：

```text
/World/factory/table
/World/factory/props
/World/jobs/part_001
/World/jobs/pick_pose
/World/jobs/place_pose
```

那就对应改脚本里的配置，不要硬套之前的默认路径。

---

## 6.4 第四步：如果你的场景还没有 pick/place target，先在 GUI 里建简单 marker

最推荐的做法是：

- 在 GUI 里创建 2 个简单 Xform 或小方块
- 一个作为 pick target
- 一个作为 place target

为什么这样做很重要：

- 状态机规划的不是“物体网格中心”
- 而是“你定义的任务目标点”

如果你不显式建 target，后面你很难知道机器人到底应该瞄准哪里。

最简单的规则是：

- `pick_target` 放在要抓取物体上方一点点
- `place_target` 放在要放置的位置上方一点点

如果你懒得先建，脚本也会自动补 runtime marker。

但是建议你长期还是在 USD 里把任务 marker 管理好。

---

## 6.5 第五步：打开脚本

打开：

- [`gui_in_app_pick_place_from_usd_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_from_usd_template.py)

位置：

- `D:\isaac-sim\zzcurobo\curobo_for_windows\examples\isaac_sim\gui_in_app_pick_place_from_usd_template.py`

---

## 6.6 第六步：先只改最上面的配置块

你第一轮最重要的是改这几个配置。

### 场景加载模式

```python
OPEN_USD_STAGE_ON_RUN = False
USD_STAGE_PATH = r"D:\isaac-sim\your_scenes\pick_place_workcell.usd"
```

如果你已经在 GUI 里手工打开场景，就用：

```python
OPEN_USD_STAGE_ON_RUN = False
```

如果要脚本自己打开，就改成：

```python
OPEN_USD_STAGE_ON_RUN = True
USD_STAGE_PATH = r"你的真实路径"
```

### cuRobo 读取障碍物的 root

```python
SCENE_COLLISION_ROOTS = ["/World/scene"]
```

如果你的静态障碍物不在 `/World/scene`，这里必须改。

这是最容易出错的地方之一。

### 任务物体和目标点路径

```python
PICK_OBJECT_PRIM_PATH = "/World/task/pick_cube"
PICK_TARGET_PRIM_PATH = "/World/task/pick_target"
PLACE_TARGET_PRIM_PATH = "/World/task/place_target"
```

如果这些 prim 在你的场景里路径不同，这里也必须改。

### 机器人

```python
ROBOT_CFG_NAME = "franka.yml"
ROBOT_SCENE_MODE = "reuse_existing"
EXISTING_ROBOT_PRIM_PATH = "/World/Franka"
RESET_EXISTING_ROBOT_TO_RETRACT = True
ROBOT_BASE_POSITION = [0.0, 0.0, 0.0]
```

如果你换机器人，这里和夹爪 joint 名也要一起改。

更具体地说：

- 如果你的 USD 里已经有机器人，优先用 `reuse_existing`
- 如果你的 USD 里还没有机器人，才用 `import_robot`
- `ROBOT_BASE_POSITION` 只在 `import_robot` 模式下生效

最推荐的小白第一版配置通常是：

```python
ROBOT_SCENE_MODE = "reuse_existing"
EXISTING_ROBOT_PRIM_PATH = "/World/Franka"
RESET_EXISTING_ROBOT_TO_RETRACT = True
```

### 状态机高度参数

```python
STATE_MACHINE_CONFIG = {
    "pregrasp_height": 0.16,
    "grasp_height": 0.085,
    "lift_height": 0.24,
    "preplace_height": 0.20,
    "place_height": 0.10,
    "retreat_height": 0.24,
}
```

如果你的桌面更高、物体更大、目标更深，这几项就要调。

### 目标姿态坐标系

```python
STATE_MACHINE_CONFIG = {
    "task_orientation": [0.0, 0.0, -1.0, 0.0],
    "task_orientation_frame": "world",
}
```

默认推荐保持：

- `task_orientation_frame = "world"`

这样即使你的机器人底座已经摆在自己的工位里，不在世界原点，脚本也会先把目标姿态转到 robot base frame 再规划。

---

## 6.7 第七步：运行脚本

在 `Window > Script Editor` 里点击 Run。

---

## 6.8 第八步：看 Console 输出

你应该至少看到下面这些类型的日志：

```text
USD_PICK_PLACE_TEMPLATE: using the stage that is already open in the GUI
USD_PICK_PLACE_TEMPLATE: extracted X obstacle object(s) from roots=[...]
USD_PICK_PLACE_TEMPLATE: motion generator warmed up
STATE_MACHINE: entering OPEN_GRIPPER
STATE_MACHINE: entering PLAN_PREGRASP
...
STATE_MACHINE: finished with state=DONE
```

如果你看到的是：

```text
warning: no obstacles were extracted
```

那通常说明：

- `SCENE_COLLISION_ROOTS` 写错了

这不是“小问题”，而是非常关键的问题。

因为这意味着：

- GUI 里你看得到场景
- 但 cuRobo 实际没有把它当成障碍物

---

## 7. 这份模板里最关键的配置解释

## 7.1 `SCENE_COLLISION_ROOTS`

这是给 cuRobo 看的环境障碍物入口。

例如：

```python
SCENE_COLLISION_ROOTS = ["/World/scene"]
```

含义是：

- 让 cuRobo 从 `/World/scene` 下面提取障碍物

如果你的环境是：

```text
/World/factory
  /table
  /shelf
  /blockers
```

那就改成：

```python
SCENE_COLLISION_ROOTS = ["/World/factory"]
```

如果你的场景散得比较开，也可以填多个 root：

```python
SCENE_COLLISION_ROOTS = [
    "/World/table_area",
    "/World/fixtures",
    "/World/storage",
]
```

---

## 7.2 `EXTRA_WORLD_IGNORE_PATHS`

这是给“宽 root”场景用的。

例如你图省事写成：

```python
SCENE_COLLISION_ROOTS = ["/World"]
```

那 cuRobo 就可能连任务 marker、任务物体、运行时辅助 prim 都一起读进去。

这时你就要通过：

```python
EXTRA_WORLD_IGNORE_PATHS = [
    "/World/task",
    "/World/task_runtime/markers",
]
```

把不该进碰撞世界的东西排除掉。

---

## 7.3 `PICK_OBJECT_PRIM_PATH`

这表示你要抓的对象 prim。

建议你把它设置成：

- 一个单独的物体根 prim
- 最好是一个可以直接移动姿态的 xform 根

不推荐一上来就把路径指到一个非常深的 mesh 子节点上。

更稳妥的做法是：

- 给这个物体包一个上层 Xform
- 然后把路径填到这个上层 Xform

这样脚本在“教学型附着”时更稳定。

---

## 7.4 `PICK_TARGET_PRIM_PATH` 和 `PLACE_TARGET_PRIM_PATH`

这两个不是“装饰物”，而是状态机真正要瞄准的目标。

它们最好满足：

- 都是单独 prim
- 路径稳定
- 你一眼就能在 Stage 树里找到

如果你长期要做任务脚本，我建议你在自己 USD 场景里长期保留它们。

---

## 7.5 `COLLISION_CHECKER`

默认给的是：

```python
COLLISION_CHECKER = "MESH"
```

原因很简单：

- 你自己的 USD 场景里通常不只是几个方块
- 很多时候会有 mesh

如果你的场景特别简单，几乎全是盒子，也可以改成：

```python
COLLISION_CHECKER = "PRIMITIVE"
```

这通常更轻一点。

---

## 7.6 `ROBOT_SCENE_MODE`、`EXISTING_ROBOT_PRIM_PATH`、`RESET_EXISTING_ROBOT_TO_RETRACT`

这是这次升级后最重要的新配置之一。

如果你的 USD 里已经有机器人，推荐：

```python
ROBOT_SCENE_MODE = "reuse_existing"
EXISTING_ROBOT_PRIM_PATH = "/World/Franka"
RESET_EXISTING_ROBOT_TO_RETRACT = True
```

这表示：

- 不再额外导入第二台机器人
- 直接接管 `/World/Franka` 这棵 articulation
- 运行脚本后先把机器人拉回 retract 姿态，便于稳定起步

如果你暂时还没有把机器人做进 USD，也可以退回老模式：

```python
ROBOT_SCENE_MODE = "import_robot"
ROBOT_BASE_POSITION = [0.0, 0.0, 0.0]
```

这时脚本会像之前一样运行时导入机器人。

---

## 7.7 `STATE_MACHINE_CONFIG["task_orientation_frame"]`

默认推荐：

```python
"task_orientation_frame": "world"
```

这表示：

- 你在脚本里写的末端目标姿态是按世界坐标系理解的
- 脚本会自动把它转换到 robot base frame

这对“机器人底座已经放在你自己的工位里，而且不在原点”的场景尤其重要。

如果你已经完全按机器人基座坐标系来思考，也可以改成：

```python
"task_orientation_frame": "robot"
```

---

## 8. 如何在 Isaac Sim 里建一个更适合 cuRobo 的 USD 场景

这部分很重要。

很多新手不是不会跑脚本，而是场景一开始就建得不利于规划。

## 8.1 先把环境和任务对象分层

最推荐的第一原则是：

- 静态环境单独一层
- 任务物体单独一层
- 任务 marker 单独一层

推荐：

```text
/World/scene
/World/task
/World/markers
```

这样做的直接好处是：

- cuRobo 世界读取简单
- 你不会反复把 marker 误当障碍物
- 你以后接感知、任务状态机时也更清楚

---

## 8.2 先用“少而稳”的障碍物建模

第一版场景建模，不要追求复杂。

建议只保留：

1. 桌子
2. 一两个料区
3. 一个中间阻挡块
4. 一个抓取物体
5. 一个放置区域

不要一开始就把场景做成很多细碎零件、很多随机小物体。

这样的问题是：

- 你很难判断到底是规划参数问题
- 还是场景本身已经无路可走

---

## 8.3 复杂网格先简化，再给 cuRobo 用

这是很实际的一条建议。

如果你自己的 USD 场景来自：

- CAD
- 工厂资源包
- 资产市场
- 其他美术模型

那么它很可能：

- 网格很多
- 细节很多
- 并不适合直接作为第一版规划障碍物

对于小白，最稳的做法是：

1. 先保留视觉模型做展示
2. 再单独加一些简化的碰撞表示
3. 先让 cuRobo 读简化后的桌面、柜体、挡板、箱体

例如：

- 真实桌子很复杂
- 但给规划时，先只用一个大长方体代表桌面

这样更容易调通。

---

## 8.4 pick target 最好不要直接贴物体中心

很多人会犯一个错误：

- 直接把 pick target 放在物体几何中心

这样不一定适合夹爪接近。

更稳的做法是：

- 把 `pick_target` 放在物体上方一点
- 再用状态机里的 `grasp_height` 做最终下探

也就是说：

- target 负责定义“抓哪里”
- `grasp_height` 负责定义“从多高往下接近”

这种分工更清楚。

---

## 8.5 place target 也要留出接近空间

放置时同样要注意：

- `place_target` 不能放得太激进
- 周围要给机械臂留接近和回撤空间

如果你把 place 点塞到角落最深处，小白阶段很容易以为是脚本坏了。

其实常常只是：

- 目标点本身就不适合接近

---

## 8.6 先稳定机器人基座，再谈任务点

如果你用的是：

- `ROBOT_SCENE_MODE = "reuse_existing"`

那你最该先确认的是：

- 场景里机器人 root 路径是否正确
- 机器人基座在 USD 里是否已经摆在合理位置
- 机器人初始姿态是否一开始就穿进桌面或设备

如果你用的是：

- `ROBOT_SCENE_MODE = "import_robot"`

那你最该先调的是：

- `ROBOT_BASE_POSITION`

一个很实用的工作流是：

1. 先只确认机器人基座和 retract 姿态干净
2. 再确认 pick/place marker 在 reachable workspace 里
3. 最后再调 `pregrasp_height`、`place_height` 这些任务参数

---

## 8.7 复用已有机器人时，尽量保持基座“直立”

这版模板已经会把目标点和末端姿态从 world frame 转到 robot base frame。

所以：

- 机器人基座有平移
- 机器人基座有常见的平面内旋转

这两类情况现在都比之前更稳。

但对于小白，我仍然建议第一版尽量保持：

- 机器人底座 roll / pitch 不要太复杂
- 先做典型桌面工位

原因不是脚本完全不能处理，而是：

- 工位越倾斜
- 任务点越复杂
- 你越难区分是场景问题、姿态定义问题，还是规划参数问题

---

## 9. 典型使用示例

## 9.1 你已经把场景整理成推荐结构

如果你的场景就是：

```text
/World/scene
/World/task/pick_cube
/World/task/pick_target
/World/task/place_target
```

那么你通常只要改：

```python
OPEN_USD_STAGE_ON_RUN = False
ROBOT_SCENE_MODE = "reuse_existing"
EXISTING_ROBOT_PRIM_PATH = "/World/Franka"
SCENE_COLLISION_ROOTS = ["/World/scene"]
PICK_OBJECT_PRIM_PATH = "/World/task/pick_cube"
PICK_TARGET_PRIM_PATH = "/World/task/pick_target"
PLACE_TARGET_PRIM_PATH = "/World/task/place_target"
```

这就是最省心的情况。

---

## 9.2 你的场景里没有 marker

那你可以先这样用：

```python
PICK_TARGET_PRIM_PATH = "/World/task/pick_target"
PLACE_TARGET_PRIM_PATH = "/World/task/place_target"
```

即使这两个 prim 不存在，脚本也会：

- 自动创建 runtime marker

这时你重点要改的是：

- `RUNTIME_PICK_MARKER_CFG`
- `RUNTIME_PLACE_MARKER_CFG`

---

## 9.3 你的场景里已经有机器人，但你不想重置到 retract

那你可以这样：

```python
ROBOT_SCENE_MODE = "reuse_existing"
EXISTING_ROBOT_PRIM_PATH = "/World/Franka"
RESET_EXISTING_ROBOT_TO_RETRACT = False
```

这适合：

- 你想保留场景里机器人当前姿态
- 你正在做 GUI 内交互调试
- 你先想观察当前关节状态下能不能直接规划

但我仍然建议第一轮排错先用：

- `RESET_EXISTING_ROBOT_TO_RETRACT = True`

---

## 9.4 你的场景树比较乱，只能先从 `/World` 读

这种情况下可以临时这么做：

```python
SCENE_COLLISION_ROOTS = ["/World"]
EXTRA_WORLD_IGNORE_PATHS = [
    "/World/task",
    "/World/task_runtime/markers",
]
```

这可以跑，但我不建议长期这样。

更好的长期方案是：

- 重新整理你的场景树
- 或者至少给静态环境单独做一个 root

---

## 10. 常见问题和排查

## 10.1 GUI 里看得到桌子，但日志说提取到 0 个障碍物

通常就是：

- `SCENE_COLLISION_ROOTS` 配错了

先回去看 Stage 树，不要先怀疑 cuRobo。

---

## 10.2 机器人一开始就撞到桌子

先看：

- `EXISTING_ROBOT_PRIM_PATH` 对不对
- 你当前到底在用 `reuse_existing` 还是 `import_robot`
- 如果是 `import_robot`，再看 `ROBOT_BASE_POSITION`

然后看：

- 你的桌子高度是不是过高
- retract 姿态是不是压在桌面里

---

## 10.3 机器人能规划，但抓取动作老是很奇怪

重点先调：

- `pregrasp_height`
- `grasp_height`

不要一开始就乱改所有参数。

---

## 10.4 你换了机器人后夹爪不动

重点先检查：

- `ROBOT_CFG_NAME`
- `STATE_MACHINE_CONFIG["gripper_joint_names"]`
- `gripper_open_position`
- `gripper_closed_position`

这是换机器人后最常见的问题之一。

---

## 10.5 你把 pick object 指到了一个很深的 mesh 子节点

如果脚本在“附着”阶段表现不稳定，优先检查这个。

更稳的做法是：

- 给任务物体建立一个上层 Xform root
- 把 `PICK_OBJECT_PRIM_PATH` 指到这个 root

---

## 10.6 机器人明明不在原点，但目标姿态还是别扭

先检查：

- `STATE_MACHINE_CONFIG["task_orientation_frame"]` 是否还在默认的 `"world"`
- 你的机器人底座是否是常见的桌面工位摆放
- `EXISTING_ROBOT_PRIM_PATH` 是否真的指向机器人 root，而不是随便某个 mesh 节点

如果你已经明确按机器人基座坐标系定义姿态了，再考虑把：

- `task_orientation_frame`

改成：

- `"robot"`

---

## 11. 推荐的继续演进方向

把这份模板跑通以后，你下一步最值得做的是下面 3 件事：

1. 把自己的场景整理成稳定的 root 结构
2. 把 pick/place target 固化到自己的 USD 里
3. 再逐步把“教学型附着”升级成更真实的物理抓取

不要一开始就把所有复杂度同时拉满。

更稳的顺序是：

1. 先跑通自己的 USD 场景
2. 再让状态机稳定
3. 再加更复杂的建模、感知和物理

---

## 12. 相关文档

如果你还没看过前面的文档，建议按这个顺序读：

1. [`ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.zh-CN.md`](./ISAACSIM_SELECTOR_IN_APP_CUROBO_BEGINNER_GUIDE.zh-CN.md)
2. [`ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.zh-CN.md`](./ISAACSIM_CUSTOM_SCENE_WORKFLOW_BEGINNER_GUIDE.zh-CN.md)
3. [`ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.zh-CN.md`](./ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.zh-CN.md)
4. 这篇文档

