import asyncio
import os
import sys
import traceback

import numpy as np
import omni.kit.app
import omni.usd
from omni.isaac.core import World
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


def _should_auto_quit() -> bool:
    return os.environ.get("CUROBO_GUI_SMOKE_AUTO_QUIT", "0") == "1"


async def _next_frame(count: int = 1) -> None:
    app = omni.kit.app.get_app()
    for _ in range(count):
        await app.next_update_async()


async def _finish_demo(success: bool) -> None:
    if success:
        print("GUI_SMOKE: PASS", flush=True)
    else:
        print("GUI_SMOKE: FAIL", flush=True)

    if _should_auto_quit():
        print("GUI_SMOKE: auto quit requested, closing Isaac Sim.", flush=True)
        omni.kit.app.get_app().post_quit()
        return

    print("GUI_SMOKE: Isaac Sim will stay open. Close the window when finished.", flush=True)


async def main() -> None:
    print("GUI_SMOKE: starting Isaac Sim + cuRobo demo", flush=True)
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

    robot_cfg = load_yaml(join_path(get_robot_configs_path(), "franka.yml"))["robot_cfg"]
    full_joint_names = robot_cfg["kinematics"]["cspace"]["joint_names"]
    full_retract_config = np.asarray(
        robot_cfg["kinematics"]["cspace"]["retract_config"], dtype=np.float32
    )

    robot, robot_prim_path = add_robot_to_scene(
        robot_cfg,
        world,
        position=np.array([0.0, 0.0, 0.0]),
        initialize_world=False,
    )
    print(f"GUI_SMOKE: robot imported at {robot_prim_path}", flush=True)

    stage_world = WorldConfig(
        cuboid=[
            Cuboid(
                name="gui_smoke_obstacle",
                pose=[1.1, 0.0, 0.25, 1.0, 0.0, 0.0, 0.0],
                dims=[0.1, 0.4, 0.5],
            )
        ]
    )
    usd_helper.add_world_to_stage(stage_world, base_frame="/World")
    parsed_world = usd_helper.get_obstacles_from_stage(only_paths=["/World/obstacles"])
    print(
        f"GUI_SMOKE: extracted {len(parsed_world.objects)} obstacle(s) from USD stage",
        flush=True,
    )

    world.scene.add_default_ground_plane()
    await world.reset_async()
    robot.initialize()
    robot_dof_names = list(robot.dof_names)
    robot_idx_list = list(range(len(robot_dof_names)))
    robot.set_joint_positions(full_retract_config, robot_idx_list)
    robot._articulation_view.set_max_efforts(
        values=np.full(len(robot_idx_list), 5000.0, dtype=np.float32),
        joint_indices=robot_idx_list,
    )
    await world.play_async()
    await _next_frame(3)

    print("GUI_SMOKE: building motion generator config", flush=True)
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
    print("GUI_SMOKE: motion generator warmed up", flush=True)
    describe_dof_layout(
        "GUI_SMOKE",
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
    print(
        "GUI_SMOKE: q_start shapes "
        f"active={tuple(q_start.position.shape)} "
        f"full={tuple(q_start_full.position.shape)}",
        flush=True,
    )
    goal_pose = Pose(
        position=tensor_args.to_device([[0.45, 0.0, 0.35]]),
        quaternion=tensor_args.to_device([[1.0, 0.0, 0.0, 0.0]]),
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

    print("GUI_SMOKE: planning from retract state", flush=True)
    compat_plan = plan_single_with_compat(
        motion_gen,
        q_start,
        goal_pose,
        primary_plan_config,
        fallback_plan_config=fallback_plan_config,
        log_prefix="GUI_SMOKE",
    )
    result = compat_plan.result
    success = compat_plan.success
    print(f"GUI_SMOKE: planning success={success}", flush=True)
    if not success:
        print(f"GUI_SMOKE: status={result.status}", flush=True)
        await _finish_demo(False)
        return

    plan = get_full_articulation_plan(
        motion_gen,
        result.get_interpolated_plan(),
        robot_dof_names,
    )
    articulation_controller = robot.get_articulation_controller()
    print(f"GUI_SMOKE: trajectory points={plan.position.shape[0]}", flush=True)

    if _should_auto_quit():
        print("GUI_SMOKE: skipping trajectory playback in auto-quit mode", flush=True)
        await _finish_demo(True)
        return

    for index in range(plan.position.shape[0]):
        cmd_state = plan[index]
        articulation_controller.apply_action(
            ArticulationAction(
                cmd_state.position.cpu().numpy(),
                cmd_state.velocity.cpu().numpy(),
                joint_indices=robot_idx_list,
            )
        )
        await _next_frame(2)

    await _finish_demo(True)


async def _run() -> None:
    try:
        await main()
    except Exception:
        await _finish_demo(False)
        traceback.print_exc()


asyncio.ensure_future(_run())
