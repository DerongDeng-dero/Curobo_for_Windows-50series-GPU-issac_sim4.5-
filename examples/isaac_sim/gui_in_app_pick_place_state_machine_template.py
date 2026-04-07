"""
Teaching template: pick / place / state machine inside an already-open Isaac Sim GUI.

How to run:
1. Start D:\isaac-sim\isaac-sim.selector.bat
2. Enter Isaac Sim Full
3. Open Window > Script Editor
4. Open this file and press Run

This script is intentionally beginner-friendly:
- cuRobo planning and robot execution are real.
- Object "attachment" is simplified for teaching: after grasp, the cube visually follows the hand.
- The script keeps the state machine explicit so that it is easy to edit.
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

try:
    from isaacsim.core.prims import SingleXFormPrim
except ImportError:
    from isaacsim.core.prims.impl import SingleXFormPrim

from curobo.geom.sdf.world import CollisionCheckerType
from curobo.geom.sphere_fit import SphereFitType
from curobo.types.base import TensorDeviceType
from curobo.types.math import Pose
from curobo.types.robot import JointState
from curobo.util.logger import setup_curobo_logger
from curobo.util.usd_helper import UsdHelper
from curobo.util_file import get_robot_configs_path, join_path, load_yaml
from curobo.wrap.reacher.motion_gen import MotionGen, MotionGenConfig, MotionGenPlanConfig


# -----------------------------
# Step 1: edit this config block
# -----------------------------
RESET_STAGE_ON_RUN = True
ROBOT_CFG_NAME = "franka.yml"
EXTERNAL_ASSET_PATH = None
EXTERNAL_ROBOT_CONFIGS_PATH = None
ROBOT_BASE_POSITION = [0.0, 0.0, 0.0]

GRIPPER_JOINT_NAMES = ["panda_finger_joint1", "panda_finger_joint2"]
GRIPPER_OPEN_POSITION = 0.04
GRIPPER_CLOSED_POSITION = 0.0
TASK_ORIENTATION = [0.0, 0.0, -1.0, 0.0]

PREGRASP_HEIGHT = 0.16
GRASP_HEIGHT = 0.085
LIFT_HEIGHT = 0.24
PREPLACE_HEIGHT = 0.20
PLACE_HEIGHT = 0.10
RETREAT_HEIGHT = 0.24

ATTACHED_OBJECT_WORLD_OFFSET = [0.0, 0.0, -0.06]
ATTACH_OBJECT_TO_COLLISION_MODEL = True
PLAYBACK_FRAME_STEP = 2
GRIPPER_ANIMATION_STEPS = 24

# Scene modeling:
# - Static workcell geometry lives under /World/scene
# - Task object lives under /World/task
# - Pick/place markers live under /World/markers
SCENE_STATIC_BOXES = [
    {
        "path": "/World/scene/table_top",
        "kind": "fixed",
        "position": [0.62, 0.00, 0.18],
        "scale": [0.95, 1.10, 0.36],
        "color": [0.62, 0.56, 0.50],
    },
    {
        "path": "/World/scene/back_wall",
        "kind": "fixed",
        "position": [0.98, 0.00, 0.62],
        "scale": [0.06, 1.20, 0.70],
        "color": [0.46, 0.48, 0.52],
    },
    {
        "path": "/World/scene/left_bin",
        "kind": "fixed",
        "position": [0.50, 0.26, 0.43],
        "scale": [0.18, 0.22, 0.14],
        "color": [0.22, 0.44, 0.64],
    },
    {
        "path": "/World/scene/right_bin",
        "kind": "fixed",
        "position": [0.72, -0.24, 0.43],
        "scale": [0.18, 0.22, 0.14],
        "color": [0.58, 0.36, 0.22],
    },
    {
        "path": "/World/scene/center_blocker",
        "kind": "fixed",
        "position": [0.58, 0.00, 0.45],
        "scale": [0.10, 0.28, 0.12],
        "color": [0.25, 0.25, 0.25],
    },
]

PICK_OBJECT_CFG = {
    "path": "/World/task/pick_cube",
    "position": [0.46, 0.26, 0.43],
    "scale": [0.045, 0.045, 0.045],
    "color": [0.94, 0.28, 0.24],
}

PLACE_MARKER_CFG = {
    "path": "/World/markers/place_target",
    "position": [0.74, -0.24, 0.445],
    "scale": [0.06, 0.06, 0.02],
    "color": [0.18, 0.75, 0.36],
}

PICK_MARKER_CFG = {
    "path": "/World/markers/pick_target",
    "position": [0.46, 0.26, 0.445],
    "scale": [0.06, 0.06, 0.02],
    "color": [0.84, 0.76, 0.18],
}


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


def _create_box(item):
    return cuboid.FixedCuboid(
        prim_path=item["path"],
        position=np.asarray(item["position"], dtype=np.float32),
        orientation=np.asarray([1.0, 0.0, 0.0, 0.0], dtype=np.float32),
        scale=np.asarray(item["scale"], dtype=np.float32),
        color=np.asarray(item["color"], dtype=np.float32),
        size=1.0,
    )


def _create_visual_marker(item):
    return cuboid.VisualCuboid(
        prim_path=item["path"],
        position=np.asarray(item["position"], dtype=np.float32),
        orientation=np.asarray([1.0, 0.0, 0.0, 0.0], dtype=np.float32),
        scale=np.asarray(item["scale"], dtype=np.float32),
        color=np.asarray(item["color"], dtype=np.float32),
        size=1.0,
    )


class PickPlaceTeachingStateMachine:
    def __init__(
        self,
        world,
        usd_helper,
        robot,
        robot_prim_path,
        robot_cfg,
        motion_gen,
        pick_cube,
        pick_marker,
        place_marker,
    ):
        self.world = world
        self.usd_helper = usd_helper
        self.robot = robot
        self.robot_prim_path = robot_prim_path
        self.robot_cfg = robot_cfg
        self.motion_gen = motion_gen
        self.pick_cube = pick_cube
        self.pick_marker = pick_marker
        self.place_marker = place_marker
        self.ee_prim = SingleXFormPrim(f"{robot_prim_path}/{robot_cfg['kinematics']['ee_link']}")
        self.tensor_args = motion_gen.tensor_args

        self.robot_dof_names = list(robot.dof_names)
        missing_gripper_joints = [
            joint_name for joint_name in GRIPPER_JOINT_NAMES if joint_name not in self.robot_dof_names
        ]
        if missing_gripper_joints:
            raise RuntimeError(
                "The configured gripper joints were not found in the robot DOF list. "
                f"Missing={missing_gripper_joints}, available={self.robot_dof_names}"
            )
        self.robot_idx_list = [robot.get_dof_index(name) for name in self.robot_dof_names]
        self.gripper_indices = [robot.get_dof_index(name) for name in GRIPPER_JOINT_NAMES]
        self.articulation_controller = robot.get_articulation_controller()
        self.gripper_target = GRIPPER_OPEN_POSITION
        self.object_attached = False
        self.object_in_collision_model = False
        self.state = "OPEN_GRIPPER"

    async def run(self) -> None:
        print("STATE_MACHINE: starting pick/place teaching flow", flush=True)
        while self.state not in {"DONE", "FAILED"}:
            print(f"STATE_MACHINE: entering {self.state}", flush=True)
            next_state = await self._execute_state(self.state)
            self.state = next_state
        print(f"STATE_MACHINE: finished with state={self.state}", flush=True)

    async def _execute_state(self, state: str) -> str:
        if state == "OPEN_GRIPPER":
            await self._animate_gripper(GRIPPER_OPEN_POSITION)
            return "PLAN_PREGRASP"

        if state == "PLAN_PREGRASP":
            success = await self._plan_and_execute(
                "PREGRASP",
                self._pick_pose(offset_z=PREGRASP_HEIGHT),
                attached=False,
            )
            return "PLAN_GRASP" if success else "FAILED"

        if state == "PLAN_GRASP":
            success = await self._plan_and_execute(
                "GRASP_APPROACH",
                self._pick_pose(offset_z=GRASP_HEIGHT),
                attached=False,
            )
            return "CLOSE_GRIPPER" if success else "FAILED"

        if state == "CLOSE_GRIPPER":
            await self._animate_gripper(GRIPPER_CLOSED_POSITION)
            await self._attach_pick_object()
            return "PLAN_LIFT"

        if state == "PLAN_LIFT":
            success = await self._plan_and_execute(
                "LIFT",
                self._pick_pose(offset_z=LIFT_HEIGHT),
                attached=True,
            )
            return "PLAN_PREPLACE" if success else "FAILED"

        if state == "PLAN_PREPLACE":
            success = await self._plan_and_execute(
                "PREPLACE",
                self._place_pose(offset_z=PREPLACE_HEIGHT),
                attached=True,
            )
            return "PLAN_PLACE" if success else "FAILED"

        if state == "PLAN_PLACE":
            success = await self._plan_and_execute(
                "PLACE_APPROACH",
                self._place_pose(offset_z=PLACE_HEIGHT),
                attached=True,
            )
            return "OPEN_AFTER_PLACE" if success else "FAILED"

        if state == "OPEN_AFTER_PLACE":
            await self._animate_gripper(GRIPPER_OPEN_POSITION)
            await self._detach_pick_object()
            return "PLAN_RETREAT"

        if state == "PLAN_RETREAT":
            success = await self._plan_and_execute(
                "RETREAT",
                self._place_pose(offset_z=RETREAT_HEIGHT),
                attached=False,
            )
            return "DONE" if success else "FAILED"

        return "FAILED"

    def _pick_pose(self, offset_z: float):
        pick_position, _ = self.pick_marker.get_world_pose()
        return np.asarray([pick_position[0], pick_position[1], pick_position[2] + offset_z], dtype=np.float32)

    def _place_pose(self, offset_z: float):
        place_position, _ = self.place_marker.get_world_pose()
        return np.asarray([place_position[0], place_position[1], place_position[2] + offset_z], dtype=np.float32)

    async def _plan_and_execute(self, label: str, goal_position: np.ndarray, attached: bool) -> bool:
        self._update_world(ignore_pick_object=not attached)
        sim_js = self.robot.get_joints_state()
        if sim_js is None:
            print(f"STATE_MACHINE: {label} aborted because sim joints are not ready", flush=True)
            return False

        full_js = JointState(
            position=self.tensor_args.to_device(sim_js.positions),
            velocity=self.tensor_args.to_device(sim_js.velocities) * 0.0,
            acceleration=self.tensor_args.to_device(sim_js.velocities) * 0.0,
            jerk=self.tensor_args.to_device(sim_js.velocities) * 0.0,
            joint_names=self.robot_dof_names,
        )
        active_js = full_js.get_ordered_joint_state(self.motion_gen.kinematics.joint_names)
        goal_pose = Pose(
            position=self.tensor_args.to_device([goal_position.tolist()]),
            quaternion=self.tensor_args.to_device([TASK_ORIENTATION]),
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
            self.motion_gen,
            active_js.unsqueeze(0),
            goal_pose,
            primary_plan_config,
            fallback_plan_config=fallback_plan_config,
            log_prefix=f"STATE_MACHINE:{label}",
        )
        result = compat_plan.result
        if not compat_plan.success:
            print(f"STATE_MACHINE: {label} planning failed, status={result.status}", flush=True)
            return False

        plan = get_full_articulation_plan(
            self.motion_gen,
            result.get_interpolated_plan(),
            self.robot_dof_names,
        )
        print(
            f"STATE_MACHINE: {label} planning success, trajectory points={plan.position.shape[0]}",
            flush=True,
        )
        await self._play_plan(plan)
        return True

    async def _play_plan(self, plan) -> None:
        for step in range(plan.position.shape[0]):
            cmd_state = plan[step]
            cmd_position = cmd_state.position.cpu().numpy().copy()
            cmd_velocity = cmd_state.velocity.cpu().numpy().copy()
            for finger_index in self.gripper_indices:
                cmd_position[finger_index] = self.gripper_target
                cmd_velocity[finger_index] = 0.0

            self.articulation_controller.apply_action(
                ArticulationAction(
                    cmd_position,
                    cmd_velocity,
                    joint_indices=self.robot_idx_list,
                )
            )
            await _next_frame(PLAYBACK_FRAME_STEP)
            if self.object_attached:
                self._update_attached_object_pose()

    async def _animate_gripper(self, target_position: float) -> None:
        sim_js = self.robot.get_joints_state()
        current_positions = sim_js.positions.copy()
        start_position = current_positions[self.gripper_indices[0]]
        for alpha in np.linspace(0.0, 1.0, GRIPPER_ANIMATION_STEPS):
            interpolated = (1.0 - alpha) * start_position + alpha * target_position
            cmd_position = current_positions.copy()
            cmd_velocity = np.zeros_like(cmd_position)
            for finger_index in self.gripper_indices:
                cmd_position[finger_index] = interpolated
            self.articulation_controller.apply_action(
                ArticulationAction(
                    cmd_position,
                    cmd_velocity,
                    joint_indices=self.robot_idx_list,
                )
            )
            await _next_frame(1)

        self.gripper_target = target_position

    async def _attach_pick_object(self) -> None:
        self.object_attached = True
        self._update_attached_object_pose()
        if not ATTACH_OBJECT_TO_COLLISION_MODEL:
            print("STATE_MACHINE: collision-model attachment is disabled in config", flush=True)
            return

        try:
            sim_js = self.robot.get_joints_state()
            cu_js = JointState(
                position=self.tensor_args.to_device(sim_js.positions),
                velocity=self.tensor_args.to_device(sim_js.velocities) * 0.0,
                acceleration=self.tensor_args.to_device(sim_js.velocities) * 0.0,
                jerk=self.tensor_args.to_device(sim_js.velocities) * 0.0,
                joint_names=self.robot_dof_names,
            )
            self.motion_gen.attach_objects_to_robot(
                cu_js,
                [self.pick_cube.prim_path],
                sphere_fit_type=SphereFitType.VOXEL_VOLUME_SAMPLE_SURFACE,
                world_objects_pose_offset=Pose.from_list([0, 0, 0, 1, 0, 0, 0], self.tensor_args),
            )
            self.object_in_collision_model = True
            print("STATE_MACHINE: attached object added to cuRobo collision model", flush=True)
        except Exception as exc:
            self.object_in_collision_model = False
            print(f"STATE_MACHINE: collision-model attach skipped: {exc}", flush=True)

    async def _detach_pick_object(self) -> None:
        self.object_attached = False
        place_position, _ = self.place_marker.get_world_pose()
        final_position = np.asarray(
            [place_position[0], place_position[1], place_position[2] + 0.03],
            dtype=np.float32,
        )
        self.pick_cube.set_world_pose(
            position=final_position,
            orientation=np.asarray([1.0, 0.0, 0.0, 0.0], dtype=np.float32),
        )
        if self.object_in_collision_model:
            try:
                self.motion_gen.detach_object_from_robot()
            except Exception as exc:
                print(f"STATE_MACHINE: collision-model detach warning: {exc}", flush=True)
        self.object_in_collision_model = False

    def _update_attached_object_pose(self) -> None:
        ee_position, ee_orientation = self.ee_prim.get_world_pose()
        attached_position = np.asarray(ee_position, dtype=np.float32) + np.asarray(
            ATTACHED_OBJECT_WORLD_OFFSET, dtype=np.float32
        )
        self.pick_cube.set_world_pose(position=attached_position, orientation=np.asarray(ee_orientation, dtype=np.float32))

    def _update_world(self, ignore_pick_object: bool) -> None:
        ignore_paths = [
            self.robot_prim_path,
            "/World/defaultGroundPlane",
            "/World/markers",
            "/curobo",
        ]
        if ignore_pick_object:
            ignore_paths.append(self.pick_cube.prim_path)

        scene_world = self.usd_helper.get_obstacles_from_stage(
            only_paths=["/World/scene"],
            reference_prim_path=self.robot_prim_path,
            ignore_substring=ignore_paths,
        ).get_collision_check_world()
        self.motion_gen.update_world(scene_world)


async def _prepare_world(usd_helper):
    if RESET_STAGE_ON_RUN:
        print("PICK_PLACE_TEMPLATE: creating a clean stage", flush=True)
        await omni.usd.get_context().new_stage_async()
        await _next_frame(2)

    world = World(stage_units_in_meters=1.0)
    await world.initialize_simulation_context_async()
    stage = world.stage
    if not stage.GetPrimAtPath("/World").IsValid():
        stage.DefinePrim("/World", "Xform")
    stage.SetDefaultPrim(stage.GetPrimAtPath("/World"))
    for prim_path in ["/World/scene", "/World/task", "/World/markers", "/curobo"]:
        if not stage.GetPrimAtPath(prim_path).IsValid():
            stage.DefinePrim(prim_path, "Xform")
    usd_helper.load_stage(stage)
    return world


def _build_scene_geometry():
    static_objects = [_create_box(item) for item in SCENE_STATIC_BOXES]
    pick_cube = cuboid.FixedCuboid(
        prim_path=PICK_OBJECT_CFG["path"],
        position=np.asarray(PICK_OBJECT_CFG["position"], dtype=np.float32),
        orientation=np.asarray([1.0, 0.0, 0.0, 0.0], dtype=np.float32),
        scale=np.asarray(PICK_OBJECT_CFG["scale"], dtype=np.float32),
        color=np.asarray(PICK_OBJECT_CFG["color"], dtype=np.float32),
        size=1.0,
    )
    pick_marker = _create_visual_marker(PICK_MARKER_CFG)
    place_marker = _create_visual_marker(PLACE_MARKER_CFG)
    return static_objects, pick_cube, pick_marker, place_marker


async def main() -> None:
    setup_curobo_logger("warn")
    usd_helper = UsdHelper()
    tensor_args = TensorDeviceType()
    world = await _prepare_world(usd_helper)

    _, pick_cube, pick_marker, place_marker = _build_scene_geometry()
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
    print(f"PICK_PLACE_TEMPLATE: robot imported at {robot_prim_path}", flush=True)

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

    initial_scene_world = usd_helper.get_obstacles_from_stage(
        only_paths=["/World/scene"],
        reference_prim_path=robot_prim_path,
        ignore_substring=[robot_prim_path, "/World/defaultGroundPlane", "/World/markers", "/curobo"],
    ).get_collision_check_world()
    motion_gen_config = MotionGenConfig.load_from_robot_config(
        robot_cfg,
        initial_scene_world,
        tensor_args,
        collision_checker_type=CollisionCheckerType.PRIMITIVE,
        interpolation_dt=0.05,
        num_ik_seeds=8,
        num_trajopt_seeds=4,
        num_graph_seeds=4,
        trajopt_tsteps=24,
        collision_cache={"obb": 24, "mesh": 2},
        evaluate_interpolated_trajectory=False,
    )
    motion_gen = MotionGen(motion_gen_config)
    motion_gen.warmup(enable_graph=False, warmup_js_trajopt=False)
    print("PICK_PLACE_TEMPLATE: motion generator warmed up", flush=True)

    describe_dof_layout(
        "PICK_PLACE_TEMPLATE",
        full_joint_names,
        motion_gen.joint_names,
        robot_dof_names,
    )

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
        pick_cube=pick_cube,
        pick_marker=pick_marker,
        place_marker=place_marker,
    )
    await state_machine.run()


async def _run() -> None:
    try:
        await main()
    except Exception:
        print("PICK_PLACE_TEMPLATE: unexpected failure", flush=True)
        traceback.print_exc()


asyncio.ensure_future(_run())
