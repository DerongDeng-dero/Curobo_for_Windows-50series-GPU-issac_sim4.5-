# Isaac Sim + cuRobo 抓取 / 放置 / 状态机模板与场景建模指南

## 1. 这份文档是做什么的

这份文档解决的是下一步问题：

- 当前已经会在 Isaac Sim GUI 里跑 cuRobo
- 你现在想做一个“抓取 -> 抬升 -> 搬运 -> 放置 -> 回撤”的完整流程
- 你还希望脚本里带一点场景建模内容，而不只是一个空场景

这次我给你新增的脚本是：

- [`gui_in_app_pick_place_state_machine_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_state_machine_template.py)

它的定位是：

- **教学型抓放状态机模板**

要特别说明：

- 机器人规划与轨迹执行是真实的
- 状态机是真实的
- 场景建模是真实的
- 物体“附着到机械手”这一步，为了让小白更容易上手，采用了**教学型简化实现**

也就是：

- 抓取后，物体会跟着手走
- 但不是完整依赖复杂接触物理来夹住物体

这样做的好处是：

- 小白能先看清楚抓放流程
- 后续再把它升级成更复杂的物理抓取，也更容易

---

## 2. 先告诉你这个模板会做什么

它会自动完成下面这些状态：

1. 打开夹爪
2. 规划到抓取上方
3. 规划到抓取位置
4. 闭合夹爪
5. 把物体附着到机械手
6. 抬升
7. 规划到放置上方
8. 规划到放置位置
9. 打开夹爪
10. 释放物体
11. 回撤
12. 结束

你在 Console 里会看到明确的状态切换日志，例如：

```text
STATE_MACHINE: entering OPEN_GRIPPER
STATE_MACHINE: entering PLAN_PREGRASP
STATE_MACHINE: entering PLAN_GRASP
...
STATE_MACHINE: finished with state=DONE
```

---

## 3. 如何运行这个抓放模板

## 3.1 启动 Isaac Sim

```powershell
<ISAAC_SIM_ROOT>\isaac-sim.selector.bat
```

进入：

- `Isaac Sim Full`

## 3.2 打开 Script Editor

如果菜单里没有 `Script Editor`：

1. 打开 `Window > Extensions`
2. 搜索 `script editor`
3. 启用：
   - `omni.kit.window.script_editor`
4. 再打开：
   - `Window > Script Editor`

## 3.3 运行脚本

打开：

- `<REPO_ROOT>\examples\isaac_sim\gui_in_app_pick_place_state_machine_template.py`

点击 Run。

---

## 4. 预期现象

你会看到：

- 一台机器人
- 一张桌子
- 左右两个料区 / 箱体
- 一个中间阻挡块
- 一个待抓取方块
- 一个抓取标记
- 一个放置标记

然后机器人会执行：

- 靠近抓取位置
- 闭合夹爪
- 抬起方块
- 搬到放置区
- 放下
- 回撤

---

## 5. 先理解脚本里最重要的三层结构

## 5.1 顶部配置区

你以后最常改的就是这里。

主要包括：

- `ROBOT_CFG_NAME`
- `GRIPPER_JOINT_NAMES`
- `TASK_ORIENTATION`
- `PREGRASP_HEIGHT`
- `GRASP_HEIGHT`
- `LIFT_HEIGHT`
- `PREPLACE_HEIGHT`
- `PLACE_HEIGHT`
- `RETREAT_HEIGHT`
- `SCENE_STATIC_BOXES`
- `PICK_OBJECT_CFG`
- `PICK_MARKER_CFG`
- `PLACE_MARKER_CFG`

这一区域就是“参数面板”。

## 5.2 场景建模区

这个脚本把场景拆成 3 类：

### `/World/scene`

放静态结构：

- 桌子
- 墙
- 料区
- 阻挡块

### `/World/task`

放任务对象：

- 待抓取方块

### `/World/markers`

放视觉标记：

- 抓取点标记
- 放置点标记

这种划分非常适合继续维护。

因为你以后会经常遇到一个问题：

- 哪些东西应该参与碰撞？
- 哪些东西只是视觉提示？

如果你一开始就把它们分清楚，后面会省很多时间。

## 5.3 状态机区

脚本里最核心的是：

- `PickPlaceTeachingStateMachine`

它把抓放过程拆成一个一个明确状态。

这比把所有逻辑混在 `main()` 里清楚得多。

---

## 6. 场景建模指导：小白应该怎么摆一个能规划的工作台

这是这份文档最重要的部分之一。

## 6.1 先记住一个原则

**场景不是越复杂越好，而是越“容易规划成功”越好。**

很多小白一开始最容易做的事就是：

- 障碍物摆得很满
- 目标点给得很极限
- 结果以为是 cuRobo 坏了

其实常常只是场景设计太激进。

## 6.2 最推荐的第一版工作台结构

建议的第一版工作台永远只保留这 4 类物体：

1. 桌子
2. 一个待抓取物体
3. 一个放置区
4. 一两个明显障碍物

不要第一版就放很多零碎东西。

## 6.3 桌子怎么建模最稳

建议：

- 先把桌子建成一个大长方体
- 不要一开始做太复杂的腿、边框、斜面

例如模板里的桌子：

- `position = [0.62, 0.00, 0.18]`
- `scale = [0.95, 1.10, 0.36]`

可以把它理解成：

- 中心在前方一点
- 台面足够宽
- 高度适中

## 6.4 料区 / 放置区怎么建模

模板里用了左右两个箱体：

- `left_bin`
- `right_bin`

它们的作用不是为了做真实容器，而是为了：

- 给工作台增加一点结构感
- 提供明显的抓取区和放置区
- 让状态机动作更像真实任务

## 6.5 为什么要加一个中间阻挡块

模板里有：

- `center_blocker`

它的意义是：

- 让轨迹不是一路直线冲过去
- 逼着规划器更像在真实工作站中绕障

如果没有它，很多演示会显得过于简单。

---

## 7. 场景建模指导：坐标和尺寸怎么改

## 7.1 `position` 是什么

格式：

```text
[x, y, z]
```

其中：

- `x`：前后
- `y`：左右
- `z`：上下

小白可以先这样记：

- 往前放，增大 `x`
- 往左放，增大 `y`
- 往右放，减小 `y`
- 往高放，增大 `z`

## 7.2 `scale` 是什么

这里的 `scale` 就是这个盒子的三维尺寸比例。

在这个模板里，盒子基准 size 是 1，所以可以近似理解为：

- `scale[0]`：x方向尺寸
- `scale[1]`：y方向尺寸
- `scale[2]`：z方向尺寸

## 7.3 小白最稳的改法

建议顺序：

1. 先只改 `position`
2. 再改 `scale`
3. 最后再增加新盒子

不要上来就把位置和尺寸全改得很大。

---

## 8. 场景建模指导：怎么判断布局是否合理

你至少要检查 4 件事。

## 8.1 机器人起始位姿不要一开场就碰桌子

如果一开始机械臂就压着桌子或侧壁，后面很多规划都会乱掉。

## 8.2 抓取点上方要有足够净空

模板里有：

- `PREGRASP_HEIGHT`
- `GRASP_HEIGHT`

这两个值必须保证：

- 机械手从上往下靠近时，不会先撞到别的障碍物

## 8.3 放置点上方也要留净空

同理：

- `PREPLACE_HEIGHT`
- `PLACE_HEIGHT`

也需要有足够空间。

## 8.4 障碍物不要把起点和终点之间彻底堵死

如果你把障碍物摆成了“完全没有路”，那就不是模板有问题，而是场景本身无解。

---

## 9. 抓放高度怎么调

这个模板里的动作高度主要看这几个参数：

- `PREGRASP_HEIGHT`
- `GRASP_HEIGHT`
- `LIFT_HEIGHT`
- `PREPLACE_HEIGHT`
- `PLACE_HEIGHT`
- `RETREAT_HEIGHT`

小白建议：

### 先改 `PREGRASP_HEIGHT`

如果机器人经常在接近前就撞到东西：

- 把它调高一点

### 再改 `GRASP_HEIGHT`

如果机器人已经到物体上方，但抓取点太高或太低：

- 调这个值

### 再改 `PLACE_HEIGHT`

如果放置时太悬空或插进物体里：

- 调这个值

---

## 10. 夹爪相关怎么改

## 10.1 当前模板默认是 Franka

默认：

```python
GRIPPER_JOINT_NAMES = ["panda_finger_joint1", "panda_finger_joint2"]
GRIPPER_OPEN_POSITION = 0.04
GRIPPER_CLOSED_POSITION = 0.0
```

如果你换机器人，这里通常也要一起改。

## 10.2 如果你换成别的机器人

你至少要同步改：

1. `ROBOT_CFG_NAME`
2. `GRIPPER_JOINT_NAMES`
3. `GRIPPER_OPEN_POSITION`
4. `GRIPPER_CLOSED_POSITION`

否则很可能会出现：

- 机械臂能动
- 但夹爪不对

---

## 11. 这个模板里的“附着”为什么是教学型简化

这是一个很重要的现实说明。

完整物理抓取通常会牵涉：

- 接触参数
- 摩擦
- 刚体约束
- 夹爪闭合稳定性
- 物体质量
- 抓取姿态
- 传感器 / 接触判断

对于小白来说，一上来就把这些全塞进去，几乎一定会崩。

所以这个模板采用的是：

- 抓取后让方块跟着手走
- 同时尽量把 cuRobo 的规划部分保留为真实流程

这不是“偷懒”，而是为了把学习曲线拆开。

正确顺序是：

1. 先学会状态机
2. 先学会场景建模
3. 先学会规划和执行
4. 后面再升级成真实接触抓取

---

## 12. 这个模板里 cuRobo 是怎么参与的

每个关键运动状态，例如：

- `PLAN_PREGRASP`
- `PLAN_GRASP`
- `PLAN_LIFT`
- `PLAN_PREPLACE`
- `PLAN_PLACE`
- `PLAN_RETREAT`

都会：

1. 重新读取当前静态场景
2. 构建目标 pose
3. 调用：
   - `plan_single_with_compat(...)`
4. 把结果转回 articulation joint 顺序
5. 播放轨迹

这就保证了：

- 你不是在写“假状态机”
- 而是真的每个阶段都在做规划

---

## 13. 为什么脚本把 `/World/scene`、`/World/task`、`/World/markers` 分开

因为这会直接影响你后面是否容易维护。

## 13.1 `/World/scene`

只放静态障碍物。

好处：

- `UsdHelper.get_obstacles_from_stage(only_paths=["/World/scene"])`
  很清晰

## 13.2 `/World/task`

只放任务对象，例如待抓取方块。

好处：

- 可以决定它是否参与碰撞
- 可以单独处理“附着”逻辑

## 13.3 `/World/markers`

只放可视化标记。

好处：

- 规划读取 world 时可以明确排除它们

这就是为什么模板不是随手乱建 prim，而是故意分层。

---

## 14. 你接下来应该怎么改这个模板

按下面顺序最稳。

## 14.1 第一轮：只改抓取点和放置点

先改：

- `PICK_OBJECT_CFG["position"]`
- `PLACE_MARKER_CFG["position"]`

不要先改别的。

## 14.2 第二轮：只改静态障碍物

改：

- `SCENE_STATIC_BOXES`

建议：

- 每次只加一个障碍物
- 每加一个就重新运行

## 14.3 第三轮：换机器人

改：

- `ROBOT_CFG_NAME`
- `GRIPPER_JOINT_NAMES`
- 可能还包括：
  - `EXTERNAL_ASSET_PATH`
  - `EXTERNAL_ROBOT_CONFIGS_PATH`

## 14.4 第四轮：改状态机顺序

比如可以新增一个状态：

- 先去观察位
- 再去预抓取位

或者加一个中转位：

- 先抬升到更高
- 再横向移动

---

## 15. 如果需要把它升级成更真实的抓取

未来可以继续加这些东西：

1. 用真实动态刚体代替教学型附着
2. 用接触或夹爪宽度判断是否抓取成功
3. 抓取后重新更新 world
4. 给被抓物体增加碰撞几何与质量
5. 把放置后物体真正留在台面上

但建议不要一步跨太大。

先把这份模板改熟，再做升级。

---

## 16. 小白最常见错误

## 16.1 一开始就把场景建得太复杂

结果：

- 你分不清到底是场景有问题，还是脚本有问题

## 16.2 抓取高度给得太低

结果：

- 机械手直接撞物体或撞桌面

## 16.3 忘记同步修改夹爪 joint name

换机器人后很常见。

## 16.4 GUI 里看到物体，就以为 cuRobo 一定在考虑它

不对。

需要看脚本里到底是从哪里读取 obstacle 的。

---

## 17. 这份模板最短结论

如果你现在要继续往“抓取 / 放置 / 状态机”方向走，最推荐的起点就是：

- [`gui_in_app_pick_place_state_machine_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_state_machine_template.py)

它已经同时具备：

- 明确状态机
- 场景建模
- cuRobo 规划
- 轨迹执行
- 教学型抓取附着

这比直接从复杂任务脚本硬改，更适合你当前阶段。

