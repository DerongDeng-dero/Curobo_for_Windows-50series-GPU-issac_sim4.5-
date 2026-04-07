# Isaac Sim + cuRobo: Load a User-Provided USD Scene and Attach the Pick/Place State Machine

## 1. What this guide solves

The earlier pick/place teaching template builds its own small teaching scene.

That is useful during early task-flow learning.

But the next real step is different:

- a user-provided USD scene is already available
- the goal is to open it normally in Isaac Sim
- the goal is to attach the cuRobo pick/place state machine to it

This guide is for that step.

The key script is:

- [`gui_in_app_pick_place_from_usd_template.py`](../../examples/isaac_sim/gui_in_app_pick_place_from_usd_template.py)

Its role is very explicit:

- load a user-provided USD environment
- reuse a robot articulation that already exists in the stage, or inject one at runtime when needed
- attach the pick/place state machine to that environment

The default recommended path is now:

- keep the authored USD environment
- prefer reusing the robot articulation that is already in that USD stage
- let the script create runtime helpers only when task markers or pick objects are missing

## 2. What this template provides

After running it, the workflow supports:

1. start Isaac Sim Full normally through `selector.bat`
2. open a user-provided USD scene
3. run the script from Script Editor
4. let the script extract obstacles from the configured scene roots
5. reuse the robot already in the scene, or import one when needed
6. reusing existing pick object / pick target / place target prims, or creating runtime markers when needed
7. execute a full pick/place flow

## 3. Two ways to use the script

### 3.1 Mode A: open the scene manually in the GUI first

This is the recommended mode.

Use:

```python
OPEN_USD_STAGE_ON_RUN = False
```

Why it is recommended:

- the scene can be inspected first
- the Stage tree can be inspected first
- prim paths can be confirmed before the task logic runs

### 3.2 Mode B: let the script open a USD file automatically

Use:

```python
OPEN_USD_STAGE_ON_RUN = True
USD_STAGE_PATH = r"<ISAAC_SIM_ROOT>\your_scenes\pick_place_workcell.usd"
```

This is useful when:

- the scene path is fixed
- a repeatable workflow on one specific USD file is needed

## 4. Understand the template design first

This template is not trying to magically infer arbitrary scene semantics.

You still need to define four things clearly:

1. which prim roots contain static obstacles
2. which prim is the robot articulation root
3. which prim is the pick object
4. which prims are the pick target and place target

If the scene does not already contain task markers, the script can fill the gaps:

- if `PICK_TARGET_PRIM_PATH` does not exist, it creates a runtime pick marker
- if `PLACE_TARGET_PRIM_PATH` does not exist, it creates a runtime place marker
- if `PICK_OBJECT_PRIM_PATH` does not exist, it creates a teaching cube at runtime

That makes the transition practical:

- keep the environment from a user-provided USD scene
- let the task helpers be created at runtime if needed

## 5. Recommended USD scene structure

The most convenient first structure is:

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

Why this is useful:

- `/World/Franka` or another robot root gives the script a stable articulation path to reuse
- `/World/scene` clearly contains static obstacles
- `/World/task` clearly contains task objects and targets
- `SCENE_COLLISION_ROOTS = ["/World/scene"]` becomes simple and stable

If the scene tree is different, that is fine. Only these items need updates:

- `SCENE_COLLISION_ROOTS`
- `PICK_OBJECT_PRIM_PATH`
- `PICK_TARGET_PRIM_PATH`
- `PLACE_TARGET_PRIM_PATH`

## 6. Step-by-step beginner workflow

### 6.1 Step 1: start Isaac Sim

```powershell
<ISAAC_SIM_ROOT>\isaac-sim.selector.bat
```

Enter:

- `Isaac Sim Full`

### 6.2 Step 2: open the USD scene

For Mode A:

1. click `File -> Open`
2. select the target `.usd` file
3. wait for the scene to finish loading

### 6.3 Step 3: inspect the Stage tree and remember the key prim paths

Identify these items:

1. the static environment root path
2. the robot articulation root path
3. the pick object path
4. the pick target path
5. the place target path

Example:

```text
/World/scene
/World/Franka
/World/task/pick_cube
/World/task/pick_target
/World/task/place_target
```

### 6.4 Step 4: if the scene has no task markers yet, create simple ones

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
- `ROBOT_SCENE_MODE`
- `EXISTING_ROBOT_PRIM_PATH`
- `RESET_EXISTING_ROBOT_TO_RETRACT`
- `SCENE_COLLISION_ROOTS`
- `PICK_OBJECT_PRIM_PATH`
- `PICK_TARGET_PRIM_PATH`
- `PLACE_TARGET_PRIM_PATH`
- `ROBOT_CFG_NAME`
- `ROBOT_BASE_POSITION`
- `STATE_MACHINE_CONFIG`

Recommended beginner robot settings when the USD scene already contains the robot:

```python
ROBOT_SCENE_MODE = "reuse_existing"
EXISTING_ROBOT_PRIM_PATH = "/World/Franka"
RESET_EXISTING_ROBOT_TO_RETRACT = True
```

Use `ROBOT_SCENE_MODE = "import_robot"` only when the authored USD scene does not contain the robot yet.

For task orientation, keep this by default:

```python
STATE_MACHINE_CONFIG = {
    "task_orientation": [0.0, 0.0, -1.0, 0.0],
    "task_orientation_frame": "world",
}
```

That lets the script convert world-frame targets into the robot base frame automatically.

### 6.7 Step 7: run the script

Press `Run` in Script Editor.

### 6.8 Step 8: inspect the console output

Expected logs:

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

If the environment lives somewhere else, change it.

### 7.2 `EXTRA_WORLD_IGNORE_PATHS`

Use this when the collision root is too broad, such as:

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

If the scene is extremely box-like and simple, `PRIMITIVE` may also work.

### 7.6 `ROBOT_SCENE_MODE`, `EXISTING_ROBOT_PRIM_PATH`, and `RESET_EXISTING_ROBOT_TO_RETRACT`

This is one of the most important additions in the upgraded template.

If the USD scene already contains the robot, the recommended setting is:

```python
ROBOT_SCENE_MODE = "reuse_existing"
EXISTING_ROBOT_PRIM_PATH = "/World/Franka"
RESET_EXISTING_ROBOT_TO_RETRACT = True
```

This means:

- do not import a second robot
- directly attach to the articulation under `/World/Franka`
- reset the robot to a clean retract pose before starting the task flow

If the USD scene does not contain the robot yet, this configuration still works:

```python
ROBOT_SCENE_MODE = "import_robot"
ROBOT_BASE_POSITION = [0.0, 0.0, 0.0]
```

### 7.7 `STATE_MACHINE_CONFIG["task_orientation_frame"]`

Recommended default:

```python
"task_orientation_frame": "world"
```

That means:

- you define the task orientation in world coordinates
- the script converts it into the robot base frame before planning

This matters when the robot is already positioned inside the authored workcell and is not sitting at the world origin.

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

### 8.6 Stabilize the robot base setup first

If you use:

- `ROBOT_SCENE_MODE = "reuse_existing"`

then first confirm:

- the robot root path is correct
- the robot base is placed correctly in the USD scene
- the initial pose is not already intersecting the table or the workcell

If you use:

- `ROBOT_SCENE_MODE = "import_robot"`

then first tune:

- `ROBOT_BASE_POSITION`

### 8.7 Keep the reused robot base upright in the first version

The upgraded template now converts world-frame target positions and orientations into the robot base frame.

That makes these cases much more stable than before:

- translated robot bases
- common planar yaw rotations of the robot base

For the first working version, I still recommend keeping the base upright and close to a typical tabletop setup. That keeps scene debugging much simpler.

## 9. Typical usage examples

### 9.1 The scene already follows the recommended structure

Then you often only need:

```python
OPEN_USD_STAGE_ON_RUN = False
ROBOT_SCENE_MODE = "reuse_existing"
EXISTING_ROBOT_PRIM_PATH = "/World/Franka"
SCENE_COLLISION_ROOTS = ["/World/scene"]
PICK_OBJECT_PRIM_PATH = "/World/task/pick_cube"
PICK_TARGET_PRIM_PATH = "/World/task/pick_target"
PLACE_TARGET_PRIM_PATH = "/World/task/place_target"
```

### 9.2 Your scene does not have markers yet

Then keep the target prim settings but let the script create runtime markers, and tune:

- `RUNTIME_PICK_MARKER_CFG`
- `RUNTIME_PLACE_MARKER_CFG`

### 9.3 Your scene already has a robot, but you do not want to reset it to retract

Use:

```python
ROBOT_SCENE_MODE = "reuse_existing"
EXISTING_ROBOT_PRIM_PATH = "/World/Franka"
RESET_EXISTING_ROBOT_TO_RETRACT = False
```

This is useful when:

- you want to preserve the current GUI pose
- you are doing in-app interactive debugging
- you want to test planning directly from the current joint state

### 9.4 Your scene tree is messy and you can only start from `/World`

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

- `EXISTING_ROBOT_PRIM_PATH`
- whether you are using `reuse_existing` or `import_robot`
- if you are importing the robot, then check `ROBOT_BASE_POSITION`
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

### The robot is not at the world origin, but the target orientation still feels wrong

Check:

- `STATE_MACHINE_CONFIG["task_orientation_frame"]` is still `"world"` unless you intentionally define orientations in the robot frame
- `EXISTING_ROBOT_PRIM_PATH` points to the robot root, not to a random mesh prim
- the robot base orientation is still a normal upright workcell layout

## 11. Recommended next step

After this template works:

1. keep your scene roots stable
2. keep pick/place targets authored in the USD scene
3. only then move toward more realistic grasp physics

For deep maintenance background, see:

- [`curobo_isaacsim_windows_full_fix_guide.en.md`](./curobo_isaacsim_windows_full_fix_guide.en.md)
