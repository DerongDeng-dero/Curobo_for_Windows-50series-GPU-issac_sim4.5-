"""
Beginner-friendly in-app template for building a custom Isaac Sim + cuRobo scene.
适合入门的 in-app 模板，用于搭建自定义 Isaac Sim + cuRobo 场景。

How to use / 使用方式:
1. Start Isaac Sim from `isaac-sim.selector.bat`
   通过 `isaac-sim.selector.bat` 启动 Isaac Sim
2. Enter Isaac Sim Full
   进入 Isaac Sim Full
3. Open Window > Script Editor
   打开 Window > Script Editor
4. Open this file and run it
   打开本文件并运行

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
import omni.kit.app
import omni.usd
from omni.isaac.core import World
from omni.isaac.core.objects import cuboid
from omni.isaac.core.utils.types import ArticulationAction

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from helper import add_robot_to_scene
from motion_gen_compat import (
    describe_dof_layout,
    get_full_articulation_plan,
    get_retract_state_for_articulation,
    plan_single_with_compat,
)

from curobo.geom.sdf.world import CollisionCheckerType
from curobo.geom.types import Cuboid, WorldConfig
from curobo.types.base import TensorDeviceType
from curobo.types.math import Pose
from curobo.types.robot import JointState
from curobo.util.logger import setup_curobo_logger
from curobo.util.usd_helper import UsdHelper
from curobo.util_file import get_robot_configs_path, join_path, load_yaml
from curobo.wrap.reacher.motion_gen import MotionGen, MotionGenConfig, MotionGenPlanConfig


# -----------------------------
# Step 1: edit these values first
# 第一步：先改这里的配置
# -----------------------------
RESET_STAGE_ON_RUN = True
ROBOT_CFG_NAME = "franka.yml"
EXTERNAL_ASSET_PATH = None
EXTERNAL_ROBOT_CONFIGS_PATH = None
ROBOT_BASE_POSITION = [0.0, 0.0, 0.0]
GOAL_POSITION = [0.38, -0.22, 0.42]
GOAL_QUATERNION = [1.0, 0.0, 0.0, 0.0]
PLAYBACK_FRAME_STEP = 2

# Workcell geometry for cuRobo and stage visualization.
# cuRobo 碰撞世界和 Stage 可视化共用的工作单元几何。
# `pose` format / `pose` 格式: [x, y, z, qw, qx, qy, qz]
SCENE_CUBOIDS = [
    {
        "name": "table_top",
        "pose": [0.62, 0.0, 0.20, 1.0, 0.0, 0.0, 0.0],
        "dims": [0.90, 1.20, 0.40],
    },
    {
        "name": "left_box",
        "pose": [0.52, 0.24, 0.47, 1.0, 0.0, 0.0, 0.0],
        "dims": [0.18, 0.18, 0.14],
    },
    {
        "name": "right_box",
        "pose": [0.72, -0.22, 0.46, 1.0, 0.0, 0.0, 0.0],
        "dims": [0.12, 0.24, 0.12],
    },
]


async def _next_frame(count: int = 1) -> None:
    app = omni.kit.app.get_app()
    for _ in range(count):
        await app.next_update_async()


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


def _build_world_config():
    cuboids = [
        Cuboid(
            name=item["name"],
            pose=item["pose"],
            dims=item["dims"],
        )
        for item in SCENE_CUBOIDS
    ]
    return WorldConfig(cuboid=cuboids)


def _create_goal_marker():
    cuboid.VisualCuboid(
        "/World/goal_marker",
        position=np.asarray(GOAL_POSITION, dtype=np.float32),
        orientation=np.asarray(GOAL_QUATERNION, dtype=np.float32),
        color=np.asarray([1.0, 0.0, 0.0], dtype=np.float32),
        size=0.05,
    )


async def _prepare_stage(usd_helper):
    if RESET_STAGE_ON_RUN:
        print("CUSTOM_TEMPLATE: creating a clean stage", flush=True)
        await omni.usd.get_context().new_stage_async()
        await _next_frame(2)

    world = World(stage_units_in_meters=1.0)
    await world.initialize_simulation_context_async()
    stage = world.stage
    if not stage.GetPrimAtPath("/World").IsValid():
        stage.DefinePrim("/World", "Xform")
    stage.SetDefaultPrim(stage.GetPrimAtPath("/World"))
    if not stage.GetPrimAtPath("/curobo").IsValid():
        stage.DefinePrim("/curobo", "Xform")
    usd_helper.load_stage(stage)
    return world


def _build_motion_gen(robot_cfg, parsed_world, tensor_args):
    motion_gen_config = MotionGenConfig.load_from_robot_config(
        robot_cfg,
        parsed_world,
        tensor_args,
        collision_checker_type=CollisionCheckerType.PRIMITIVE,
        interpolation_dt=0.05,
        num_ik_seeds=8,
        num_trajopt_seeds=4,
        num_graph_seeds=4,
        trajopt_tsteps=24,
        collision_cache={"obb": 16, "mesh": 4},
        evaluate_interpolated_trajectory=False,
    )
    motion_gen = MotionGen(motion_gen_config)
    motion_gen.warmup(enable_graph=False, warmup_js_trajopt=False)
    return motion_gen


async def main() -> None:
    setup_curobo_logger("warn")
    tensor_args = TensorDeviceType()
    usd_helper = UsdHelper()
    world = await _prepare_stage(usd_helper)

    robot_cfg = _load_robot_cfg()
    full_joint_names = list(robot_cfg["kinematics"]["cspace"]["joint_names"])
    full_retract_config = np.asarray(
        robot_cfg["kinematics"]["cspace"]["retract_config"],
        dtype=np.float32,
    )

    robot, robot_prim_path = add_robot_to_scene(
        robot_cfg,
        world,
        position=np.asarray(ROBOT_BASE_POSITION, dtype=np.float32),
        initialize_world=False,
    )
    print(f"CUSTOM_TEMPLATE: robot imported at {robot_prim_path}", flush=True)

    _create_goal_marker()
    stage_world = _build_world_config()
    usd_helper.add_world_to_stage(stage_world, base_frame="/World")
    parsed_world = usd_helper.get_obstacles_from_stage(only_paths=["/World/obstacles"])
    print(
        f"CUSTOM_TEMPLATE: extracted {len(parsed_world.objects)} obstacle(s) from stage",
        flush=True,
    )

    world.scene.add_default_ground_plane()
    await world.reset_async()
    robot.initialize()

    robot_dof_names = list(robot.dof_names)
    robot_idx_list = [robot.get_dof_index(name) for name in robot_dof_names]
    q_start_full = JointState.from_position(
        tensor_args.to_device(full_retract_config).view(1, -1),
        joint_names=full_joint_names,
    ).get_ordered_joint_state(robot_dof_names)
    robot.set_joint_positions(
        q_start_full.position.view(-1).detach().cpu().numpy(),
        robot_idx_list,
    )
    robot._articulation_view.set_max_efforts(
        values=np.full(len(robot_idx_list), 5000.0, dtype=np.float32),
        joint_indices=robot_idx_list,
    )

    await world.play_async()
    await _next_frame(3)

    motion_gen = _build_motion_gen(robot_cfg, parsed_world, tensor_args)
    print("CUSTOM_TEMPLATE: motion generator warmed up", flush=True)

    describe_dof_layout(
        "CUSTOM_TEMPLATE",
        full_joint_names,
        motion_gen.joint_names,
        robot_dof_names,
    )

    q_start, q_start_full = get_retract_state_for_articulation(
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

    goal_pose = Pose(
        position=tensor_args.to_device([GOAL_POSITION]),
        quaternion=tensor_args.to_device([GOAL_QUATERNION]),
    )
    primary_plan_config = MotionGenPlanConfig(
        enable_graph=False,
        max_attempts=12,
        timeout=20.0,
        enable_finetune_trajopt=True,
    )
    fallback_plan_config = MotionGenPlanConfig(
        enable_graph=True,
        max_attempts=12,
        timeout=20.0,
        enable_finetune_trajopt=False,
    )

    compat_plan = plan_single_with_compat(
        motion_gen,
        q_start,
        goal_pose,
        primary_plan_config,
        fallback_plan_config=fallback_plan_config,
        log_prefix="CUSTOM_TEMPLATE",
    )
    result = compat_plan.result
    if not compat_plan.success:
        print(f"CUSTOM_TEMPLATE: planning failed, status={result.status}", flush=True)
        return

    plan = get_full_articulation_plan(
        motion_gen,
        result.get_interpolated_plan(),
        robot_dof_names,
    )
    print(
        f"CUSTOM_TEMPLATE: planning success, trajectory points={plan.position.shape[0]}",
        flush=True,
    )

    articulation_controller = robot.get_articulation_controller()
    for step in range(plan.position.shape[0]):
        cmd_state = plan[step]
        articulation_controller.apply_action(
            ArticulationAction(
                cmd_state.position.cpu().numpy(),
                cmd_state.velocity.cpu().numpy(),
                joint_indices=robot_idx_list,
            )
        )
        await _next_frame(PLAYBACK_FRAME_STEP)

    print("CUSTOM_TEMPLATE: trajectory playback finished", flush=True)
    print(
        "CUSTOM_TEMPLATE: update the config block at the top of this file and run again",
        flush=True,
    )


async def _run() -> None:
    try:
        await main()
    except Exception:
        print("CUSTOM_TEMPLATE: unexpected failure", flush=True)
        traceback.print_exc()


asyncio.ensure_future(_run())
