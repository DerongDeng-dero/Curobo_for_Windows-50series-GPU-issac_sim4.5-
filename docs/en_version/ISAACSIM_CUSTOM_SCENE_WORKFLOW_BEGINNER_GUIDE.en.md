# Isaac Sim + cuRobo Custom Scene Workflow Guide

## 1. What this guide is

This guide is the next step after the in-app beginner guide.

If the following items are already complete:

- installed the environment successfully
- passed `verify_isaacsim_integration.bat`
- entered `Isaac Sim Full`
- run [`gui_in_app_motion_gen_beginner.py`](../../examples/isaac_sim/gui_in_app_motion_gen_beginner.py)

the workflow is now in the next phase:

- not just proving that the stack runs
- but starting to build a user-provided scene

## 2. What this phase covers

For long-term Isaac Sim + cuRobo use, five topics matter most:

1. change the robot
2. build a table and obstacle scene
3. let cuRobo read those obstacles
4. give a target pose and plan to it
5. iterate toward a custom task script

## 3. What this phase provides

The key in-app template is:

- [`gui_in_app_custom_scene_template.py`](../../examples/isaac_sim/gui_in_app_custom_scene_template.py)

Compared with the earlier beginner script:

- the beginner script is a minimal proof
- this script is closer to a reusable scene template

It collects the most common values at the top of the file:

- `ROBOT_CFG_NAME`
- `EXTERNAL_ASSET_PATH`
- `EXTERNAL_ROBOT_CONFIGS_PATH`
- `ROBOT_BASE_POSITION`
- `GOAL_POSITION`
- `GOAL_QUATERNION`
- `SCENE_CUBOIDS`
- `RESET_STAGE_ON_RUN`

## 4. Run the template the standard way first

### 4.1 Start Isaac Sim

Run:

```powershell
<ISAAC_SIM_ROOT>\isaac-sim.selector.bat
```

Enter:

- `Isaac Sim Full`

### 4.2 Open Script Editor

Use:

- `Window -> Script Editor`

### 4.3 Run the template script

Open:

- [`gui_in_app_custom_scene_template.py`](../../examples/isaac_sim/gui_in_app_custom_scene_template.py)

Press `Run`.

### 4.4 Expected result

Expected result:

- a robot imported into the stage
- a goal marker
- simple obstacle geometry added to the scene
- a planning result that moves the robot toward the target

If that does not happen, stop and debug this template before trying to build anything larger.

## 5. Understand the template structure first

### 5.1 The top configuration block

This is where most early scene changes should happen.

For beginners, the safest order is:

1. change the goal
2. change the obstacles
3. change the robot

### 5.2 `_load_robot_cfg()`

This function loads the robot YAML and applies optional external asset/config roots.

It is the correct place to understand:

- which robot config is actually being used
- where external URDF/USD assets come from

### 5.3 `_build_world_config()`

This function builds the obstacle description that cuRobo consumes.

That distinction matters:

- something visible in the GUI is not automatically something used in the collision world

### 5.4 `_create_goal_marker()`

This is the visual target marker inside the stage.

It is mainly for clarity while you tune the scene and target.

### 5.5 `main()`

This is where the full chain comes together:

- stage preparation
- robot import
- world extraction
- `MotionGen` construction
- planning
- execution

## 6. First learn to change the goal

The safest first edit is:

- `GOAL_POSITION`
- `GOAL_QUATERNION`

That lets you validate:

- robot import is correct
- world extraction is correct
- planning still succeeds after target changes

Do not change robot, obstacles, and goals all at once.

## 7. Then learn to change the table and obstacles

### 7.1 Where obstacles are defined

In this template they are defined in:

- `SCENE_CUBOIDS`

### 7.2 What the fields mean

Each obstacle entry contains:

- a name
- a pose
- dimensions

This is the minimum stable mental model:

- pose decides where the object is
- dimensions decide how large the collision shape is

### 7.3 Safest beginner editing pattern

Recommended order:

1. first change positions only
2. then change sizes
3. then add a new obstacle

That gives you the clearest feedback.

## 8. Then learn to change the robot

### 8.1 Easiest case: the robot YAML already exists in the repository

If the YAML is already present, usually you only need to change:

- `ROBOT_CFG_NAME`

### 8.2 If the robot is not under the default paths

Then you also need:

- `EXTERNAL_ASSET_PATH`
- `EXTERNAL_ROBOT_CONFIGS_PATH`

### 8.3 Common beginner mistake

Changing only the robot YAML is usually not enough.

You also need to think about:

- base position
- scene layout
- reachable goal

## 9. Understand the difference between “visible in GUI” and “actually used by cuRobo”

This is one of the most important concepts in this phase.

The GUI stage and the cuRobo collision world are related, but not identical.

You must always be able to answer:

- what is only visual
- what is actually being extracted into the collision world

If that distinction is not kept clear, the classic confusion eventually appears:

- “I can see the object in the GUI, so why did the robot ignore it?”

## 10. Practical workflow recommendation

The recommended habit is:

1. start from the custom scene template
2. change one thing at a time
3. rerun the script
4. confirm the scene and planning result together
5. only after that move toward task flow

## 11. Common pitfalls

### Pitfall 1: changing too many things at once

Result:

- you no longer know whether the problem is the robot, the scene, or the goal

### Pitfall 2: placing obstacles too aggressively

Result:

- the scene becomes impossible to solve
- it looks like the planner is bad, but the scene is actually overconstrained

### Pitfall 3: changing the robot without revisiting the goal and scene layout

Result:

- the old scene assumptions no longer match the new robot

## 12. Recommended next steps

Once this template works reliably, the next documents should be:

1. [`ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.en.md`](./ISAACSIM_PICK_PLACE_STATE_MACHINE_AND_SCENE_MODELING_GUIDE.en.md)
2. [`ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md`](./ISAACSIM_USD_SCENE_PICK_PLACE_WORKFLOW_GUIDE.en.md)

That takes you from:

- a custom single-plan scene

to:

- a full task flow in an authored environment
