"""
Run this file from an already-open Isaac Sim GUI:
Window > Script Editor > Open > this file > Run

Do not run this file with isaac-sim.bat --exec or isaacsim_python.bat.
This script assumes Isaac Sim is already running and does not create SimulationApp.
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


ROBOT_CFG_NAME = "franka.yml"
GOAL_POSITION = [0.45, 0.0, 0.35]
GOAL_QUATERNION = [1.0, 0.0, 0.0, 0.0]
PLAYBACK_FRAME_STEP = 2


async def _next_frame(count: int = 1) -> None:
    app = omni.kit.app.get_app()
    for _ in range(count):
        await app.next_update_async()


async def main() -> None:
    print("IN_APP_BEGINNER: creating a clean stage", flush=True)
    await omni.usd.get_context().new_stage_async()
    await _next_frame(2)

    setup_curobo_logger("warn")
    tensor_args = TensorDeviceType()
    usd_helper = UsdHelper()

    world = World(stage_units_in_meters=1.0)
    await world.initialize_simulation_context_async()
    stage = world.stage
    stage.DefinePrim("/World", "Xform")
    stage.SetDefaultPrim(stage.GetPrimAtPath("/World"))
    stage.DefinePrim("/curobo", "Xform")
    usd_helper.load_stage(stage)

    robot_cfg = load_yaml(join_path(get_robot_configs_path(), ROBOT_CFG_NAME))["robot_cfg"]
    full_joint_names = robot_cfg["kinematics"]["cspace"]["joint_names"]
    full_retract_config = np.asarray(
        robot_cfg["kinematics"]["cspace"]["retract_config"],
        dtype=np.float32,
    )

    robot, robot_prim_path = add_robot_to_scene(
        robot_cfg,
        world,
        position=np.array([0.0, 0.0, 0.0]),
        initialize_world=False,
    )
    print(f"IN_APP_BEGINNER: robot imported at {robot_prim_path}", flush=True)

    cuboid.VisualCuboid(
        "/World/goal_marker",
        position=np.asarray(GOAL_POSITION, dtype=np.float32),
        orientation=np.asarray(GOAL_QUATERNION, dtype=np.float32),
        color=np.asarray([1.0, 0.0, 0.0], dtype=np.float32),
        size=0.05,
    )

    stage_world = WorldConfig(
        cuboid=[
            Cuboid(
                name="beginner_obstacle",
                pose=[1.1, 0.0, 0.25, 1.0, 0.0, 0.0, 0.0],
                dims=[0.1, 0.4, 0.5],
            )
        ]
    )
    usd_helper.add_world_to_stage(stage_world, base_frame="/World")
    parsed_world = usd_helper.get_obstacles_from_stage(only_paths=["/World/obstacles"])
    print(
        f"IN_APP_BEGINNER: extracted {len(parsed_world.objects)} obstacle(s) from stage",
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
        collision_cache={"obb": 8, "mesh": 2},
        evaluate_interpolated_trajectory=False,
    )
    motion_gen = MotionGen(motion_gen_config)
    motion_gen.warmup(enable_graph=False, warmup_js_trajopt=False)
    print("IN_APP_BEGINNER: motion generator warmed up", flush=True)

    describe_dof_layout(
        "IN_APP_BEGINNER",
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
        log_prefix="IN_APP_BEGINNER",
    )
    result = compat_plan.result
    if not compat_plan.success:
        print(f"IN_APP_BEGINNER: planning failed, status={result.status}", flush=True)
        return

    plan = get_full_articulation_plan(
        motion_gen,
        result.get_interpolated_plan(),
        robot_dof_names,
    )
    print(
        f"IN_APP_BEGINNER: planning success, trajectory points={plan.position.shape[0]}",
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

    print("IN_APP_BEGINNER: trajectory playback finished", flush=True)
    print("IN_APP_BEGINNER: you can now modify this file and re-run it from Script Editor", flush=True)


async def _run() -> None:
    try:
        await main()
    except Exception:
        print("IN_APP_BEGINNER: unexpected failure", flush=True)
        traceback.print_exc()


asyncio.ensure_future(_run())
