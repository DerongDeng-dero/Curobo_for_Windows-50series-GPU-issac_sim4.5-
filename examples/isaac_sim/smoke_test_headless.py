try:
    import isaacsim
except ImportError:
    pass

# Standard Library
import sys

# Third Party
import numpy as np
from isaacsim.simulation_app import SimulationApp

simulation_app = SimulationApp(
    {
        "headless": True,
        "hide_ui": True,
        "fast_shutdown": True,
        "renderer": "RaytracedLighting",
    }
)

import torch
from helper import add_robot_to_scene
from omni.isaac.core import World

from curobo.geom.sdf.world import CollisionCheckerType
from curobo.geom.types import Cuboid, WorldConfig
from curobo.types.base import TensorDeviceType
from curobo.types.math import Pose
from curobo.types.robot import JointState
from curobo.util.logger import setup_curobo_logger
from curobo.util.usd_helper import UsdHelper
from curobo.util_file import get_robot_configs_path, join_path, load_yaml
from curobo.wrap.reacher.motion_gen import MotionGen, MotionGenConfig, MotionGenPlanConfig


def main():
    print("SMOKE: starting Isaac Sim + cuRobo smoke test", flush=True)

    setup_curobo_logger("warn")
    tensor_args = TensorDeviceType()
    usd_helper = UsdHelper()

    world = World(stage_units_in_meters=1.0)
    stage = world.stage
    stage.DefinePrim("/World", "Xform")
    stage.SetDefaultPrim(stage.GetPrimAtPath("/World"))
    stage.DefinePrim("/curobo", "Xform")
    usd_helper.load_stage(stage)

    robot_cfg = load_yaml(join_path(get_robot_configs_path(), "franka.yml"))["robot_cfg"]
    robot, robot_prim_path = add_robot_to_scene(
        robot_cfg,
        world,
        position=np.array([0.0, 0.0, 0.0]),
        initialize_world=False,
    )
    print(f"SMOKE: robot imported at {robot_prim_path}", flush=True)

    stage_world = WorldConfig(
        cuboid=[
            Cuboid(
                name="smoke_obstacle",
                pose=[1.1, 0.0, 0.25, 1.0, 0.0, 0.0, 0.0],
                dims=[0.1, 0.4, 0.5],
            )
        ]
    )
    usd_helper.add_world_to_stage(stage_world, base_frame="/World")
    parsed_world = usd_helper.get_obstacles_from_stage(only_paths=["/World/obstacles"])
    print(
        f"SMOKE: extracted {len(parsed_world.objects)} obstacle(s) from USD stage",
        flush=True,
    )

    world.initialize_physics()
    robot.initialize()
    world.reset()
    world.play()
    for _ in range(3):
        world.step(render=False)

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
    print("SMOKE: motion generator warmed up", flush=True)

    joint_names = robot_cfg["kinematics"]["cspace"]["joint_names"]
    q_start = JointState.from_position(
        tensor_args.to_device([robot_cfg["kinematics"]["cspace"]["retract_config"]]),
        joint_names=joint_names,
    )
    goal_pose = Pose(
        position=tensor_args.to_device([[0.45, 0.0, 0.35]]),
        quaternion=tensor_args.to_device([[1.0, 0.0, 0.0, 0.0]]),
    )

    result = motion_gen.plan_single(
        q_start,
        goal_pose,
        MotionGenPlanConfig(enable_graph=False, max_attempts=2, enable_finetune_trajopt=True),
    )
    success = bool(result.success.item())
    print(f"SMOKE: planning success={success}", flush=True)
    if success:
        plan = result.get_interpolated_plan()
        print(f"SMOKE: interpolated trajectory points={plan.position.shape[0]}", flush=True)
        print("SMOKE: PASS", flush=True)
        return 0

    print(f"SMOKE: status={result.status}", flush=True)
    print("SMOKE: FAIL", flush=True)
    return 1


if __name__ == "__main__":
    exit_code = 1
    try:
        exit_code = main()
    finally:
        simulation_app.close()
    sys.exit(exit_code)
