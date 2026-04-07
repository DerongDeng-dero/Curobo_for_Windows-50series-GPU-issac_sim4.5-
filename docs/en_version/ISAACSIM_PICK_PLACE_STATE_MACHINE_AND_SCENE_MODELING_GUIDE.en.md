# Isaac Sim + cuRobo Pick/Place State Machine and Scene Modeling Guide

## 1. What this guide is for

This guide is for the next step after the custom-scene template.

The key script is:

- [`gui_in_app_pick_place_state_machine_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_state_machine_template.py)

Its role is very specific:

- real cuRobo planning
- real staged execution
- a teaching-friendly pick/place state machine
- a simple but useful scene modeling example

The important simplification is this:

- the robot motion is real
- the state machine is real
- the object attachment is simplified for teaching

After grasp, the object follows the hand visually. That makes the state machine much easier to understand before you move to full contact-rich grasp physics.

## 2. What the template does

The template runs a full task flow:

1. open gripper
2. plan to pregrasp
3. plan to grasp approach
4. close gripper
5. attach the object in the teaching model
6. lift
7. plan to preplace
8. plan to place approach
9. open gripper
10. release the object
11. retreat
12. finish

The console logs make the state transitions explicit.

## 3. How to run the template

### 3.1 Start Isaac Sim

```powershell
D:\isaac-sim\isaac-sim.selector.bat
```

Enter:

- `Isaac Sim Full`

### 3.2 Open Script Editor

Use:

- `Window -> Script Editor`

### 3.3 Run the script

Open:

- [`gui_in_app_pick_place_state_machine_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_state_machine_template.py)

Press `Run`.

## 4. What you should see

You should see:

- a robot
- a table
- left and right bins or work zones
- a center blocker
- a cube to pick
- a pick marker
- a place marker

Then the robot should:

- approach the pick area
- close the gripper
- lift the cube
- move to the place area
- release the cube
- retreat

## 5. The three most important structural layers in the script

### 5.1 The top configuration block

This is your parameter panel.

Most common edits happen here:

- robot config
- gripper joint names
- target orientation
- approach/lift/place heights
- scene boxes
- pick and place marker configuration

### 5.2 The scene modeling layer

The teaching template separates the scene into:

- `/World/scene`
- `/World/task`
- `/World/markers`

That separation is useful because it keeps clear:

- what is static environment
- what is a task object
- what is only a visual task marker

### 5.3 The state machine layer

The core logic lives in:

- `PickPlaceTeachingStateMachine`

That is much clearer than mixing all task logic directly into `main()`.

## 6. Scene modeling guidance: how beginners should build a plannable workcell

### 6.1 First principle

The best beginner scene is not the most complex scene.

It is the scene that is easiest to reason about and easiest to plan through.

### 6.2 Recommended first workcell layout

For the first version, keep only:

1. a table
2. one pick object
3. one place area
4. one or two obvious obstacles

### 6.3 How to model the table safely

The safest beginner choice is:

- model the table as one large box first

Do not start with a complicated table model full of legs, trim, and decorative geometry.

### 6.4 How to model pickup and placement zones

The bins or zones in the teaching template are not there to make a realistic storage simulation first.

They are there to:

- add structure to the workcell
- make the task zones obvious
- make the task flow easier to understand

### 6.5 Why add a center blocker

The center blocker prevents the scene from becoming a trivial straight-line demonstration.

It forces the planner to route around something.

## 7. Scene modeling guidance: how to change coordinates and sizes

### 7.1 What `position` means

Format:

```text
[x, y, z]
```

Practical beginner rule:

- larger `x`: farther forward
- larger `y`: farther left
- smaller `y`: farther right
- larger `z`: higher

### 7.2 What `scale` means

In the template, `scale` is the box size factor in each axis.

You can think of it as:

- x size
- y size
- z size

### 7.3 Safest beginner editing order

1. change positions first
2. then change scales
3. only then add more objects

## 8. Scene modeling guidance: how to judge whether your layout is reasonable

At minimum, check these four things:

### 8.1 The robot should not start in collision

If the arm begins intersecting the table or the wall, many later failures are just the result of a broken initial state.

### 8.2 The pick area must have enough vertical clearance

`PREGRASP_HEIGHT` and `GRASP_HEIGHT` should allow a clean downward approach.

### 8.3 The place area must also have clearance

`PREPLACE_HEIGHT` and `PLACE_HEIGHT` need room for both approach and release.

### 8.4 Do not block the path completely

If the obstacles leave no route at all, the planner is not at fault. The scene is simply overconstrained.

## 9. How to tune the grasp and placement heights

The main parameters are:

- `PREGRASP_HEIGHT`
- `GRASP_HEIGHT`
- `LIFT_HEIGHT`
- `PREPLACE_HEIGHT`
- `PLACE_HEIGHT`
- `RETREAT_HEIGHT`

Practical beginner order:

1. tune `PREGRASP_HEIGHT` first
2. then tune `GRASP_HEIGHT`
3. then tune `PLACE_HEIGHT`

## 10. How to change the gripper-related settings

The default template assumes Franka:

```python
GRIPPER_JOINT_NAMES = ["panda_finger_joint1", "panda_finger_joint2"]
GRIPPER_OPEN_POSITION = 0.04
GRIPPER_CLOSED_POSITION = 0.0
```

If you change the robot, you usually need to change all of these together:

1. `ROBOT_CFG_NAME`
2. `GRIPPER_JOINT_NAMES`
3. `GRIPPER_OPEN_POSITION`
4. `GRIPPER_CLOSED_POSITION`

## 11. Why the attachment model is simplified

A full physical grasping pipeline usually involves:

- contact settings
- friction
- rigid-body constraints
- gripper stability
- object mass
- grasp pose selection
- contact detection

That is too much complexity for the first teaching version.

The current simplified attachment model is there to teach:

- state machine structure
- planning flow
- scene organization

before adding hard grasp physics.

## 12. Recommended next steps

After this template works reliably:

1. move to your own USD scene
2. keep the same task structure
3. only then add more realistic grasp physics

For that next step, read:

- [`ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md`](./ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md)
