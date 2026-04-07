"""
Beginner-friendly in-app template for loading a user-provided USD scene and
attaching the cuRobo pick/place state machine to it.
适合入门的 in-app 模板：加载用户提供的 USD 场景，并接入 cuRobo 抓取/放置状态机。

How to run / 运行方式:
1. Start Isaac Sim from `isaac-sim.selector.bat`
   通过 `isaac-sim.selector.bat` 启动 Isaac Sim
2. Enter Isaac Sim Full
   进入 Isaac Sim Full
3. Open Window > Script Editor
   打开 Window > Script Editor
4. Open this file and press Run
   打开本文件并点击 Run

This script is designed for GUI-internal execution only.
这个脚本只适合在 GUI 内部运行。
It does not create `SimulationApp`.
它不会创建 `SimulationApp`。
"""

import asyncio
import os
import sys
import traceback

import numpy as np
import omni.usd
from omni.isaac.core import World

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from helper import add_robot_to_scene, attach_existing_robot_to_scene
from motion_gen_compat import describe_dof_layout, get_retract_state_for_articulation
from pick_place_state_machine_support import (
    PickPlaceTeachingStateMachine,
    create_fixed_box,
    create_visual_marker,
    next_frame,
    wrap_existing_prim,
)

from curobo.geom.sdf.world import CollisionCheckerType
from curobo.types.base import TensorDeviceType
from curobo.types.robot import JointState
from curobo.util.logger import setup_curobo_logger
from curobo.util.usd_helper import UsdHelper
from curobo.util_file import get_robot_configs_path, join_path, load_yaml
from curobo.wrap.reacher.motion_gen import MotionGen, MotionGenConfig

try:
    from isaacsim.core.utils.stage import open_stage_async
except ImportError:
    async def open_stage_async(usd_path: str):
        return await omni.usd.get_context().open_stage_async(usd_path)


# ---------------------------------------------
# Step 1: edit this config block before running
# 第一步：运行前先改这个配置块
# ---------------------------------------------

# Mode A / 模式 A:
# - Leave OPEN_USD_STAGE_ON_RUN = False
#   保持 OPEN_USD_STAGE_ON_RUN = False
# - Manually open the USD scene in Isaac Sim GUI first
#   先在 Isaac Sim GUI 里手工打开 USD 场景
# - Then run this script
#   再运行这个脚本
#
# Mode B / 模式 B:
# - Set OPEN_USD_STAGE_ON_RUN = True
#   设置 OPEN_USD_STAGE_ON_RUN = True
# - Set USD_STAGE_PATH to a `.usd` file path
#   把 USD_STAGE_PATH 设置成 `.usd` 文件路径
# - The script will open that stage automatically
#   由脚本自动打开该 Stage
OPEN_USD_STAGE_ON_RUN = False
USD_STAGE_PATH = None

ROBOT_CFG_NAME = "franka.yml"
EXTERNAL_ASSET_PATH = None
EXTERNAL_ROBOT_CONFIGS_PATH = None

# Robot source mode / 机器人来源模式:
# - "reuse_existing": attach to a robot articulation that is already in the USD stage
#   "reuse_existing"：接管 USD 场景里已经存在的机器人 articulation
# - "import_robot": import the robot from the YAML/URDF config at runtime
#   "import_robot"：按 YAML/URDF 配置在运行时导入机器人
ROBOT_SCENE_MODE = "reuse_existing"
EXISTING_ROBOT_PRIM_PATH = "/World/Franka"
RESET_EXISTING_ROBOT_TO_RETRACT = True

# Used only when ROBOT_SCENE_MODE == "import_robot"
# 仅在 ROBOT_SCENE_MODE == "import_robot" 时使用
ROBOT_BASE_POSITION = [0.0, 0.0, 0.0]
ADD_DEFAULT_GROUND_PLANE_IF_MISSING = False

# Pick the root paths that contain static obstacles for cuRobo.
# 选择 cuRobo 读取静态障碍物的根路径。
# If the whole scene is under /World/scene, keep this as-is.
# 如果整个场景都在 /World/scene 下面，可以直接保持默认值。
# If the scene is somewhere else, edit these paths first.
# 如果场景放在别的路径下，优先修改这里。
SCENE_COLLISION_ROOTS = ["/World/scene"]

# Add extra ignore paths when the scene tree is broad, e.g. when using
# SCENE_COLLISION_ROOTS = ["/World"].
# 当场景树较大时，补充额外忽略路径，例如直接从 /World 读取时。
EXTRA_WORLD_IGNORE_PATHS = [
    "/World/task",
    "/World/task_runtime/markers",
]

# For a user-provided USD scene, MESH is usually the safest default.
# 对用户提供的 USD 场景，MESH 通常是最稳妥的默认值。
# Supported values / 支持值: "MESH", "PRIMITIVE"
COLLISION_CHECKER = "MESH"

# If the prims already exist in the USD scene, point to them here.
# 如果这些 prim 已经存在于 USD 场景中，就在这里填它们的路径。
PICK_OBJECT_PRIM_PATH = "/World/task/pick_cube"
PICK_TARGET_PRIM_PATH = "/World/task/pick_target"
PLACE_TARGET_PRIM_PATH = "/World/task/place_target"

# Runtime helpers are created only when the prim paths above are missing.
# 只有当上面的 prim 路径不存在时，才会创建运行时辅助物体。
RUNTIME_PICK_OBJECT_CFG = {
    "path": "/World/task_runtime/pick_cube",
    "position": [0.46, 0.26, 0.43],
    "scale": [0.045, 0.045, 0.045],
    "color": [0.94, 0.28, 0.24],
}
RUNTIME_PICK_MARKER_CFG = {
    "path": "/World/task_runtime/markers/pick_target",
    "position": [0.46, 0.26, 0.445],
    "scale": [0.06, 0.06, 0.02],
    "color": [0.84, 0.76, 0.18],
}
RUNTIME_PLACE_MARKER_CFG = {
    "path": "/World/task_runtime/markers/place_target",
    "position": [0.74, -0.24, 0.445],
    "scale": [0.06, 0.06, 0.02],
    "color": [0.18, 0.75, 0.36],
}

# Optional add-on geometry if the authored USD scene is too empty for a first
# test. These boxes will be created under /World/task_runtime/scene_addons.
# 如果 authored USD 场景过于空，可以临时添加这些几何体做首次测试。
SCENE_ADDON_BOXES = []

# State-machine behavior / 状态机行为参数。
# The most important values to tune are / 最常需要调的参数有：
# - pregrasp_height / grasp_height
# - lift_height / preplace_height / place_height / retreat_height
# - gripper_joint_names when the robot changes
#   更换机器人时的 gripper_joint_names
# - task_orientation_frame:
#     "world" means the quaternion below is defined in world coordinates and
#     will be converted into the robot base frame automatically
#     "world" 表示下面的四元数定义在世界坐标系，会自动转换到机器人基座坐标系
#     "robot" means the quaternion is already defined in the robot base frame
#     "robot" 表示四元数已经定义在机器人基座坐标系
STATE_MACHINE_CONFIG = {
    "gripper_joint_names": ["panda_finger_joint1", "panda_finger_joint2"],
    "gripper_open_position": 0.04,
    "gripper_closed_position": 0.0,
    "task_orientation": [0.0, 0.0, -1.0, 0.0],
    "task_orientation_frame": "world",
    "pregrasp_height": 0.16,
    "grasp_height": 0.085,
    "lift_height": 0.24,
    "preplace_height": 0.20,
    "place_height": 0.10,
    "retreat_height": 0.24,
    "attached_object_world_offset": [0.0, 0.0, -0.06],
    "attach_object_to_collision_model": True,
    "playback_frame_step": 2,
    "gripper_animation_steps": 24,
    "plan_max_attempts": 12,
    "plan_timeout": 20.0,
    "plan_fallback_enable_graph": True,
    "place_release_height_offset": 0.03,
}


def _load_robot_cfg():
    robot_cfg_root = get_robot_configs_path()
    if EXTERNAL_ROBOT_CONFIGS_PATH is not None:
        robot_cfg_root = EXTERNAL_ROBOT_CONFIGS_PATH

    robot_cfg = load_yaml(join_path(robot_cfg_root, ROBOT_CFG_NAME))["robot_cfg"]
    if EXTERNAL_ASSET_PATH is not None:
        robot_cfg["kinematics"]["external_asset_path"] = EXTERNAL_ASSET_PATH
    if EXTERNAL_ROBOT_CONFIGS_PATH is not None:
        robot_cfg["kinematics"]["external_robot_configs_path"] = EXTERNAL_ROBOT_CONFIGS_PATH
    return robot_cfg


def _ensure_xform(stage, prim_path: str) -> None:
    if not stage.GetPrimAtPath(prim_path).IsValid():
        stage.DefinePrim(prim_path, "Xform")


def _collision_checker_type_from_config():
    checker_name = str(COLLISION_CHECKER).upper()
    mapping = {
        "MESH": CollisionCheckerType.MESH,
        "PRIMITIVE": CollisionCheckerType.PRIMITIVE,
    }
    if checker_name not in mapping:
        raise ValueError(f"Unsupported COLLISION_CHECKER={COLLISION_CHECKER}")
    return mapping[checker_name]


def _create_or_reuse_robot(robot_cfg, world):
    scene_mode = str(ROBOT_SCENE_MODE).lower()
    if scene_mode == "reuse_existing":
        robot, robot_prim_path = attach_existing_robot_to_scene(
            robot_cfg,
            world,
            robot_prim_path=EXISTING_ROBOT_PRIM_PATH,
            initialize_world=False,
        )
        print(
            "USD_PICK_PLACE_TEMPLATE: reusing existing robot articulation "
            f"from {EXISTING_ROBOT_PRIM_PATH} (resolved root={robot_prim_path})",
            flush=True,
        )
        return robot, robot_prim_path

    if scene_mode == "import_robot":
        robot, robot_prim_path = add_robot_to_scene(
            robot_cfg,
            world,
            position=np.asarray(ROBOT_BASE_POSITION, dtype=np.float32),
            initialize_world=False,
        )
        print(f"USD_PICK_PLACE_TEMPLATE: imported robot at {robot_prim_path}", flush=True)
        return robot, robot_prim_path

    raise ValueError(
        "Unsupported ROBOT_SCENE_MODE. "
        f"Expected 'reuse_existing' or 'import_robot', got {ROBOT_SCENE_MODE}"
    )


async def _wait_for_stage_loading() -> None:
    context = omni.usd.get_context()
    while context.get_stage_loading_status()[2] > 0:
        await next_frame(1)
    await next_frame(2)


async def _prepare_world(usd_helper):
    if OPEN_USD_STAGE_ON_RUN:
        if not USD_STAGE_PATH:
            raise RuntimeError("OPEN_USD_STAGE_ON_RUN is True but USD_STAGE_PATH is empty")
        print(f"USD_PICK_PLACE_TEMPLATE: opening stage {USD_STAGE_PATH}", flush=True)
        World.clear_instance()
        result, error = await open_stage_async(USD_STAGE_PATH)
        if not result:
            raise RuntimeError(f"Failed to open USD stage: path={USD_STAGE_PATH}, error={error}")
        await _wait_for_stage_loading()
    else:
        stage = omni.usd.get_context().get_stage()
        if stage is None:
            raise RuntimeError(
                "No stage is currently open. Either open a USD scene in the GUI first "
                "or set OPEN_USD_STAGE_ON_RUN = True."
            )
        World.clear_instance()
        print("USD_PICK_PLACE_TEMPLATE: using the stage that is already open in the GUI", flush=True)

    world = World(stage_units_in_meters=1.0)
    await world.initialize_simulation_context_async()
    stage = world.stage

    if not stage.GetPrimAtPath("/World").IsValid():
        stage.DefinePrim("/World", "Xform")
    if not stage.GetDefaultPrim().IsValid():
        stage.SetDefaultPrim(stage.GetPrimAtPath("/World"))
    for prim_path in [
        "/curobo",
        "/World/task_runtime",
        "/World/task_runtime/markers",
        "/World/task_runtime/scene_addons",
    ]:
        _ensure_xform(stage, prim_path)

    if ADD_DEFAULT_GROUND_PLANE_IF_MISSING and not stage.GetPrimAtPath("/World/defaultGroundPlane").IsValid():
        world.scene.add_default_ground_plane()

    usd_helper.load_stage(stage)
    return world


def _create_scene_addons():
    if not SCENE_ADDON_BOXES:
        return []
    created = [create_fixed_box(item) for item in SCENE_ADDON_BOXES]
    print(f"USD_PICK_PLACE_TEMPLATE: created {len(created)} runtime scene addon box(es)", flush=True)
    return created


def _resolve_pick_object(stage):
    if stage.GetPrimAtPath(PICK_OBJECT_PRIM_PATH).IsValid():
        print(f"USD_PICK_PLACE_TEMPLATE: using existing pick object {PICK_OBJECT_PRIM_PATH}", flush=True)
        return wrap_existing_prim(PICK_OBJECT_PRIM_PATH)

    print(
        "USD_PICK_PLACE_TEMPLATE: existing pick object was not found, "
        f"creating runtime object at {RUNTIME_PICK_OBJECT_CFG['path']}",
        flush=True,
    )
    return create_fixed_box(RUNTIME_PICK_OBJECT_CFG)


def _resolve_pick_marker(stage, pick_object):
    if stage.GetPrimAtPath(PICK_TARGET_PRIM_PATH).IsValid():
        print(f"USD_PICK_PLACE_TEMPLATE: using existing pick target {PICK_TARGET_PRIM_PATH}", flush=True)
        return wrap_existing_prim(PICK_TARGET_PRIM_PATH)

    marker_cfg = dict(RUNTIME_PICK_MARKER_CFG)
    pick_position, _ = pick_object.get_world_pose()
    marker_cfg["position"] = [
        float(pick_position[0]),
        float(pick_position[1]),
        float(pick_position[2]),
    ]
    print(
        "USD_PICK_PLACE_TEMPLATE: existing pick target was not found, "
        f"creating runtime marker at {marker_cfg['path']}",
        flush=True,
    )
    return create_visual_marker(marker_cfg)


def _resolve_place_marker(stage):
    if stage.GetPrimAtPath(PLACE_TARGET_PRIM_PATH).IsValid():
        print(f"USD_PICK_PLACE_TEMPLATE: using existing place target {PLACE_TARGET_PRIM_PATH}", flush=True)
        return wrap_existing_prim(PLACE_TARGET_PRIM_PATH)

    print(
        "USD_PICK_PLACE_TEMPLATE: existing place target was not found, "
        f"creating runtime marker at {RUNTIME_PLACE_MARKER_CFG['path']}",
        flush=True,
    )
    return create_visual_marker(RUNTIME_PLACE_MARKER_CFG)


def _build_motion_gen(robot_cfg, parsed_world, tensor_args):
    motion_gen_config = MotionGenConfig.load_from_robot_config(
        robot_cfg,
        parsed_world,
        tensor_args,
        collision_checker_type=_collision_checker_type_from_config(),
        interpolation_dt=0.05,
        num_ik_seeds=8,
        num_trajopt_seeds=4,
        num_graph_seeds=4,
        trajopt_tsteps=24,
        collision_cache={"obb": 32, "mesh": 32},
        evaluate_interpolated_trajectory=False,
    )
    motion_gen = MotionGen(motion_gen_config)
    motion_gen.warmup(enable_graph=False, warmup_js_trajopt=False)
    return motion_gen


async def main() -> None:
    setup_curobo_logger("warn")
    usd_helper = UsdHelper()
    tensor_args = TensorDeviceType()
    world = await _prepare_world(usd_helper)
    stage = world.stage

    _create_scene_addons()
    pick_object = _resolve_pick_object(stage)
    pick_marker = _resolve_pick_marker(stage, pick_object)
    place_marker = _resolve_place_marker(stage)

    robot_cfg = _load_robot_cfg()
    full_joint_names = list(robot_cfg["kinematics"]["cspace"]["joint_names"])
    full_retract_config = np.asarray(
        robot_cfg["kinematics"]["cspace"]["retract_config"],
        dtype=np.float32,
    )

    robot, robot_prim_path = _create_or_reuse_robot(robot_cfg, world)

    await world.reset_async()
    robot.initialize()

    robot_dof_names = list(robot.dof_names)
    robot_idx_list = [robot.get_dof_index(name) for name in robot_dof_names]
    should_reset_to_retract = (
        str(ROBOT_SCENE_MODE).lower() != "reuse_existing" or bool(RESET_EXISTING_ROBOT_TO_RETRACT)
    )
    if should_reset_to_retract:
        q_start_full = JointState.from_position(
            tensor_args.to_device(full_retract_config).view(1, -1),
            joint_names=full_joint_names,
        ).get_ordered_joint_state(robot_dof_names)
        robot.set_joint_positions(
            q_start_full.position.view(-1).detach().cpu().numpy(),
            robot_idx_list,
        )
        print("USD_PICK_PLACE_TEMPLATE: robot reset to retract configuration", flush=True)
    else:
        print(
            "USD_PICK_PLACE_TEMPLATE: keeping the existing articulation pose from the USD stage",
            flush=True,
        )
    robot._articulation_view.set_max_efforts(
        values=np.full(len(robot_idx_list), 5000.0, dtype=np.float32),
        joint_indices=robot_idx_list,
    )

    await world.play_async()
    await next_frame(3)

    initial_scene_world = usd_helper.get_obstacles_from_stage(
        only_paths=SCENE_COLLISION_ROOTS,
        reference_prim_path=robot_prim_path,
        ignore_substring=[robot_prim_path, "/World/defaultGroundPlane", "/curobo"] + EXTRA_WORLD_IGNORE_PATHS,
    ).get_collision_check_world()
    world_object_count = len(initial_scene_world.objects)
    print(
        "USD_PICK_PLACE_TEMPLATE: extracted "
        f"{world_object_count} obstacle object(s) from roots={SCENE_COLLISION_ROOTS}",
        flush=True,
    )
    if world_object_count == 0:
        print(
            "USD_PICK_PLACE_TEMPLATE: warning: no obstacles were extracted. "
            "If this is not intentional, check SCENE_COLLISION_ROOTS.",
            flush=True,
        )

    motion_gen = _build_motion_gen(robot_cfg, initial_scene_world, tensor_args)
    print("USD_PICK_PLACE_TEMPLATE: motion generator warmed up", flush=True)

    describe_dof_layout(
        "USD_PICK_PLACE_TEMPLATE",
        full_joint_names,
        motion_gen.joint_names,
        robot_dof_names,
    )

    if should_reset_to_retract:
        _, q_start_full = get_retract_state_for_articulation(
            motion_gen,
            tensor_args,
            full_joint_names,
            full_retract_config,
            robot_dof_names,
        )
        robot.set_joint_positions(
            q_start_full.position.view(-1).detach().cpu().numpy(),
            robot_idx_list,
        )

    state_machine = PickPlaceTeachingStateMachine(
        world=world,
        usd_helper=usd_helper,
        robot=robot,
        robot_prim_path=robot_prim_path,
        robot_cfg=robot_cfg,
        motion_gen=motion_gen,
        pick_object=pick_object,
        pick_marker=pick_marker,
        place_marker=place_marker,
        state_config=STATE_MACHINE_CONFIG,
        scene_collision_roots=SCENE_COLLISION_ROOTS,
        static_ignore_paths=EXTRA_WORLD_IGNORE_PATHS,
    )
    await state_machine.run()


async def _run() -> None:
    try:
        await main()
    except Exception:
        print("USD_PICK_PLACE_TEMPLATE: unexpected failure", flush=True)
        traceback.print_exc()


asyncio.ensure_future(_run())
