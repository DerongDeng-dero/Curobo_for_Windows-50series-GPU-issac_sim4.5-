# Isaac Sim + cuRobo: Load Your Own USD Scene and Attach the Pick/Place State Machine

## 1. What this guide solves

The earlier pick/place teaching template builds its own small teaching scene.

That is useful when you are still learning the task flow.

But the next real step is different:

- you already have your own USD scene
- you want to open it normally in Isaac Sim
- you want to attach the cuRobo pick/place state machine to it

This guide is for that step.

The key script is:

- [`gui_in_app_pick_place_from_usd_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_from_usd_template.py)

Its role is very explicit:

- load your own USD environment
- inject the robot at runtime
- attach the pick/place state machine to that environment

## 2. What you get from this template

After running it, you can:

1. start Isaac Sim Full normally through `selector.bat`
2. open your own USD scene
3. run the script from Script Editor
4. let the script extract obstacles from the configured scene roots
5. add the robot into that scene
6. use your existing pick object / pick target / place target, or let the script create runtime markers
7. execute a full pick/place flow

## 3. Two ways to use the script

### 3.1 Mode A: open your scene manually in the GUI first

This is the recommended mode.

Use:

```python
OPEN_USD_STAGE_ON_RUN = False
```

Why it is recommended:

- you can inspect the scene first
- you can inspect the Stage tree first
- you can confirm prim paths before running the task logic

### 3.2 Mode B: let the script open a USD file for you

Use:

```python
OPEN_USD_STAGE_ON_RUN = True
USD_STAGE_PATH = r"D:\isaac-sim\your_scenes\pick_place_workcell.usd"
```

This is useful when:

- the scene path is fixed
- you want a repeatable workflow on one specific USD file

## 4. Understand the template design first

This template is not trying to magically infer arbitrary scene semantics.

You still need to define three things clearly:

1. which prim roots contain static obstacles
2. which prim is the pick object
3. which prims are the pick target and place target

If your scene does not already contain task markers, the script can fill the gaps:

- if `PICK_TARGET_PRIM_PATH` does not exist, it creates a runtime pick marker
- if `PLACE_TARGET_PRIM_PATH` does not exist, it creates a runtime place marker
- if `PICK_OBJECT_PRIM_PATH` does not exist, it creates a teaching cube at runtime

That makes the transition practical:

- keep the environment from your own USD scene
- let the task helpers be created at runtime if needed

## 5. Recommended USD scene structure

The most convenient first structure is:

```text
/World
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

Why this is useful:

- `/World/scene` clearly contains static obstacles
- `/World/task` clearly contains task objects and targets
- `SCENE_COLLISION_ROOTS = ["/World/scene"]` becomes simple and stable

If your scene tree is different, that is fine. You only need to update:

- `SCENE_COLLISION_ROOTS`
- `PICK_OBJECT_PRIM_PATH`
- `PICK_TARGET_PRIM_PATH`
- `PLACE_TARGET_PRIM_PATH`

## 6. Step-by-step beginner workflow

### 6.1 Step 1: start Isaac Sim

```powershell
D:\isaac-sim\isaac-sim.selector.bat
```

Enter:

- `Isaac Sim Full`

### 6.2 Step 2: open your USD scene

If you use Mode A:

1. click `File -> Open`
2. select your `.usd` file
3. wait for the scene to finish loading

### 6.3 Step 3: inspect the Stage tree and remember the key prim paths

You need to identify:

1. the static environment root path
2. the pick object path
3. the pick target path
4. the place target path

Example:

```text
/World/scene
/World/task/pick_cube
/World/task/pick_target
/World/task/place_target
```

### 6.4 Step 4: if your scene has no task markers yet, create simple ones

Recommended first approach:

- create two simple Xforms or small marker objects
- one for pick
- one for place

Why:

- the state machine plans to a task target, not to “whatever the mesh center happens to be”

### 6.5 Step 5: open the script

Open:

- [`gui_in_app_pick_place_from_usd_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_from_usd_template.py)

### 6.6 Step 6: edit only the top configuration block first

Most important settings:

- `OPEN_USD_STAGE_ON_RUN`
- `USD_STAGE_PATH`
- `SCENE_COLLISION_ROOTS`
- `PICK_OBJECT_PRIM_PATH`
- `PICK_TARGET_PRIM_PATH`
- `PLACE_TARGET_PRIM_PATH`
- `ROBOT_CFG_NAME`
- `ROBOT_BASE_POSITION`
- `STATE_MACHINE_CONFIG`

### 6.7 Step 7: run the script

Press `Run` in Script Editor.

### 6.8 Step 8: inspect the console output

You should see logs similar to:

```text
USD_PICK_PLACE_TEMPLATE: using the stage that is already open in the GUI
USD_PICK_PLACE_TEMPLATE: extracted X obstacle object(s) from roots=[...]
USD_PICK_PLACE_TEMPLATE: motion generator warmed up
STATE_MACHINE: entering OPEN_GRIPPER
STATE_MACHINE: entering PLAN_PREGRASP
...
STATE_MACHINE: finished with state=DONE
```

If you see:

```text
warning: no obstacles were extracted
```

then `SCENE_COLLISION_ROOTS` is likely wrong.

That is a real issue, because it means:

- the GUI shows the scene
- but cuRobo is not using it as collision geometry

## 7. Most important configuration values

### 7.1 `SCENE_COLLISION_ROOTS`

This tells cuRobo where to read the static environment from.

Example:

```python
SCENE_COLLISION_ROOTS = ["/World/scene"]
```

If your environment lives somewhere else, change it.

### 7.2 `EXTRA_WORLD_IGNORE_PATHS`

Use this when your collision root is too broad, such as:

```python
SCENE_COLLISION_ROOTS = ["/World"]
```

Then you may need to explicitly ignore:

- task objects
- markers
- runtime helpers

### 7.3 `PICK_OBJECT_PRIM_PATH`

This should point to the object you want to pick.

Recommended practice:

- point it at a clean object root prim
- ideally an upper Xform root, not a deep mesh child

### 7.4 `PICK_TARGET_PRIM_PATH` and `PLACE_TARGET_PRIM_PATH`

These are not decorative helpers. They are the real task targets used by the state machine.

Recommended properties:

- stable paths
- easy to find in the Stage tree
- clearly separated from static environment geometry

### 7.5 `COLLISION_CHECKER`

Default:

```python
COLLISION_CHECKER = "MESH"
```

Why:

- real USD scenes usually contain mesh geometry

If your scene is extremely box-like and simple, `PRIMITIVE` may also work.

## 8. Scene modeling guidance for cuRobo-friendly USD scenes

### 8.1 Separate environment and task objects

Recommended roots:

- `/World/scene`
- `/World/task`
- `/World/markers`

This separation keeps clear:

- what is static environment
- what is a task object
- what is only a task marker

### 8.2 Start with fewer, cleaner obstacles

The first usable version does not need to be visually rich.

Keep:

1. a table
2. one or two bins or zones
3. a blocker
4. a pick object
5. a place area

### 8.3 Simplify complex meshes before relying on them for planning

If your USD scene comes from CAD or asset packs, it may contain:

- many meshes
- too much detail
- geometry that is visually nice but planning-unfriendly

A practical first approach is:

1. keep the detailed visual scene for display
2. add simplified collision-like geometry for planning
3. start with boxes for tables, walls, blockers, and bins

### 8.4 Do not place the pick target directly at the object center by default

A better pattern is:

- put `pick_target` slightly above the object
- use `grasp_height` for the final downward approach

That separation is clearer and easier to tune.

### 8.5 The place target also needs approach space

Do not bury the place target too deep into corners or clutter.

If the robot cannot approach or retreat cleanly, the scene is badly posed even if the script is correct.

### 8.6 Stabilize the robot base position first

Because the robot is injected at runtime, you must ensure:

- `ROBOT_BASE_POSITION` is reasonable
- the robot does not spawn in collision with the table or environment

## 9. Typical usage examples

### 9.1 Your scene already follows the recommended structure

Then you often only need:

```python
OPEN_USD_STAGE_ON_RUN = False
SCENE_COLLISION_ROOTS = ["/World/scene"]
PICK_OBJECT_PRIM_PATH = "/World/task/pick_cube"
PICK_TARGET_PRIM_PATH = "/World/task/pick_target"
PLACE_TARGET_PRIM_PATH = "/World/task/place_target"
```

### 9.2 Your scene does not have markers yet

Then keep the target prim settings but let the script create runtime markers, and tune:

- `RUNTIME_PICK_MARKER_CFG`
- `RUNTIME_PLACE_MARKER_CFG`

### 9.3 Your scene tree is messy and you can only start from `/World`

You can temporarily use:

```python
SCENE_COLLISION_ROOTS = ["/World"]
EXTRA_WORLD_IGNORE_PATHS = [
    "/World/task",
    "/World/task_runtime/markers",
]
```

This can work, but it is not the best long-term structure.

## 10. Common problems

### The table is visible in the GUI, but zero obstacles were extracted

Usually:

- `SCENE_COLLISION_ROOTS` is wrong

### The robot starts in collision

Check:

- `ROBOT_BASE_POSITION`
- table height
- initial retract pose clearance

### Planning works, but the grasp motion is strange

Tune first:

- `pregrasp_height`
- `grasp_height`

### The gripper does not move after you change the robot

Check:

- `ROBOT_CFG_NAME`
- `STATE_MACHINE_CONFIG["gripper_joint_names"]`
- open and closed gripper positions

## 11. Recommended next step

After this template works:

1. keep your scene roots stable
2. keep pick/place targets authored in the USD scene
3. only then move toward more realistic grasp physics

For deep maintenance background, see:

- [`curobo_isaacsim_windows_full_fix_guide.en.md`](./curobo_isaacsim_windows_full_fix_guide.en.md)
