"""
Shared support for GUI in-app pick/place teaching templates.

This module keeps the state machine reusable so multiple in-app scripts can
attach the same planning/execution flow to different scene sources.
"""

from __future__ import annotations

import copy
from typing import Dict, List, Optional, Sequence

import numpy as np
import omni.kit.app
from omni.isaac.core.objects import cuboid
from omni.isaac.core.utils.types import ArticulationAction

try:
    from isaacsim.core.prims import SingleXFormPrim
except ImportError:
    from isaacsim.core.prims.impl import SingleXFormPrim

from curobo.geom.sphere_fit import SphereFitType
from curobo.types.math import Pose
from curobo.types.robot import JointState
from curobo.wrap.reacher.motion_gen import MotionGenPlanConfig

from motion_gen_compat import get_full_articulation_plan, plan_single_with_compat


DEFAULT_STATE_MACHINE_CONFIG = {
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


def _normalize_quaternion(quaternion: np.ndarray) -> np.ndarray:
    quat = np.asarray(quaternion, dtype=np.float32)
    quat_norm = np.linalg.norm(quat)
    if quat_norm <= 0.0:
        raise ValueError("Quaternion norm is zero")
    return quat / quat_norm


def _quaternion_conjugate(quaternion: np.ndarray) -> np.ndarray:
    quat = _normalize_quaternion(quaternion)
    return np.asarray([quat[0], -quat[1], -quat[2], -quat[3]], dtype=np.float32)


def _quaternion_multiply(lhs: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    lhs = np.asarray(lhs, dtype=np.float32)
    rhs = np.asarray(rhs, dtype=np.float32)
    return np.asarray(
        [
            lhs[0] * rhs[0] - lhs[1] * rhs[1] - lhs[2] * rhs[2] - lhs[3] * rhs[3],
            lhs[0] * rhs[1] + lhs[1] * rhs[0] + lhs[2] * rhs[3] - lhs[3] * rhs[2],
            lhs[0] * rhs[2] - lhs[1] * rhs[3] + lhs[2] * rhs[0] + lhs[3] * rhs[1],
            lhs[0] * rhs[3] + lhs[1] * rhs[2] - lhs[2] * rhs[1] + lhs[3] * rhs[0],
        ],
        dtype=np.float32,
    )


def _rotate_vector_by_quaternion(vector: np.ndarray, quaternion: np.ndarray) -> np.ndarray:
    quat = _normalize_quaternion(quaternion)
    vec_quat = np.asarray([0.0, vector[0], vector[1], vector[2]], dtype=np.float32)
    rotated = _quaternion_multiply(_quaternion_multiply(quat, vec_quat), _quaternion_conjugate(quat))
    return rotated[1:]


def world_position_to_local_frame(
    world_position: np.ndarray,
    frame_position: np.ndarray,
    frame_orientation: np.ndarray,
) -> np.ndarray:
    relative_position = np.asarray(world_position, dtype=np.float32) - np.asarray(
        frame_position,
        dtype=np.float32,
    )
    return _rotate_vector_by_quaternion(relative_position, _quaternion_conjugate(frame_orientation))


def world_orientation_to_local_frame(
    world_orientation: np.ndarray,
    frame_orientation: np.ndarray,
) -> np.ndarray:
    local_orientation = _quaternion_multiply(
        _quaternion_conjugate(frame_orientation),
        _normalize_quaternion(world_orientation),
    )
    return _normalize_quaternion(local_orientation)


async def next_frame(count: int = 1) -> None:
    app = omni.kit.app.get_app()
    for _ in range(count):
        await app.next_update_async()


def build_state_machine_config(overrides: Optional[Dict] = None) -> Dict:
    cfg = copy.deepcopy(DEFAULT_STATE_MACHINE_CONFIG)
    if overrides is not None:
        cfg.update(copy.deepcopy(overrides))
    return cfg


def create_fixed_box(item: Dict):
    return cuboid.FixedCuboid(
        prim_path=item["path"],
        position=np.asarray(item["position"], dtype=np.float32),
        orientation=np.asarray([1.0, 0.0, 0.0, 0.0], dtype=np.float32),
        scale=np.asarray(item["scale"], dtype=np.float32),
        color=np.asarray(item["color"], dtype=np.float32),
        size=1.0,
    )


def create_visual_marker(item: Dict):
    return cuboid.VisualCuboid(
        prim_path=item["path"],
        position=np.asarray(item["position"], dtype=np.float32),
        orientation=np.asarray([1.0, 0.0, 0.0, 0.0], dtype=np.float32),
        scale=np.asarray(item["scale"], dtype=np.float32),
        color=np.asarray(item["color"], dtype=np.float32),
        size=1.0,
    )


def wrap_existing_prim(prim_path: str):
    return SingleXFormPrim(prim_path)


class PickPlaceTeachingStateMachine:
    def __init__(
        self,
        world,
        usd_helper,
        robot,
        robot_prim_path: str,
        robot_cfg: Dict,
        motion_gen,
        pick_object,
        pick_marker,
        place_marker,
        state_config: Optional[Dict] = None,
        scene_collision_roots: Optional[Sequence[str]] = None,
        static_ignore_paths: Optional[Sequence[str]] = None,
    ):
        self.world = world
        self.usd_helper = usd_helper
        self.robot = robot
        self.robot_prim_path = robot_prim_path
        self.robot_cfg = robot_cfg
        self.motion_gen = motion_gen
        self.pick_object = pick_object
        self.pick_marker = pick_marker
        self.place_marker = place_marker
        self.robot_root_prim = SingleXFormPrim(robot_prim_path)
        self.ee_prim = SingleXFormPrim(f"{robot_prim_path}/{robot_cfg['kinematics']['ee_link']}")
        self.tensor_args = motion_gen.tensor_args
        self.cfg = build_state_machine_config(state_config)
        self.scene_collision_roots = list(scene_collision_roots or ["/World/scene"])
        self.static_ignore_paths = list(static_ignore_paths or [])

        self.robot_dof_names = list(robot.dof_names)
        gripper_joint_names = self.cfg["gripper_joint_names"]
        missing_gripper_joints = [
            joint_name for joint_name in gripper_joint_names if joint_name not in self.robot_dof_names
        ]
        if missing_gripper_joints:
            raise RuntimeError(
                "The configured gripper joints were not found in the robot DOF list. "
                f"Missing={missing_gripper_joints}, available={self.robot_dof_names}"
            )
        self.robot_idx_list = [robot.get_dof_index(name) for name in self.robot_dof_names]
        self.gripper_indices = [robot.get_dof_index(name) for name in gripper_joint_names]
        self.articulation_controller = robot.get_articulation_controller()
        self.gripper_target = float(self.cfg["gripper_open_position"])
        self.object_attached = False
        self.object_in_collision_model = False
        self.state = "OPEN_GRIPPER"

        base_position, base_orientation = self.robot_root_prim.get_world_pose()
        print(
            "STATE_MACHINE: robot base world pose "
            f"position={np.asarray(base_position, dtype=np.float32).tolist()} "
            f"orientation={np.asarray(base_orientation, dtype=np.float32).tolist()}",
            flush=True,
        )
        print(
            "STATE_MACHINE: task_orientation_frame="
            f"{self.cfg.get('task_orientation_frame', 'world')}",
            flush=True,
        )

    async def run(self) -> None:
        print("STATE_MACHINE: starting pick/place teaching flow", flush=True)
        while self.state not in {"DONE", "FAILED"}:
            print(f"STATE_MACHINE: entering {self.state}", flush=True)
            self.state = await self._execute_state(self.state)
        print(f"STATE_MACHINE: finished with state={self.state}", flush=True)

    async def _execute_state(self, state: str) -> str:
        if state == "OPEN_GRIPPER":
            await self._animate_gripper(float(self.cfg["gripper_open_position"]))
            return "PLAN_PREGRASP"

        if state == "PLAN_PREGRASP":
            success = await self._plan_and_execute(
                "PREGRASP",
                self._pick_pose(offset_z=float(self.cfg["pregrasp_height"])),
                attached=False,
            )
            return "PLAN_GRASP" if success else "FAILED"

        if state == "PLAN_GRASP":
            success = await self._plan_and_execute(
                "GRASP_APPROACH",
                self._pick_pose(offset_z=float(self.cfg["grasp_height"])),
                attached=False,
            )
            return "CLOSE_GRIPPER" if success else "FAILED"

        if state == "CLOSE_GRIPPER":
            await self._animate_gripper(float(self.cfg["gripper_closed_position"]))
            await self._attach_pick_object()
            return "PLAN_LIFT"

        if state == "PLAN_LIFT":
            success = await self._plan_and_execute(
                "LIFT",
                self._pick_pose(offset_z=float(self.cfg["lift_height"])),
                attached=True,
            )
            return "PLAN_PREPLACE" if success else "FAILED"

        if state == "PLAN_PREPLACE":
            success = await self._plan_and_execute(
                "PREPLACE",
                self._place_pose(offset_z=float(self.cfg["preplace_height"])),
                attached=True,
            )
            return "PLAN_PLACE" if success else "FAILED"

        if state == "PLAN_PLACE":
            success = await self._plan_and_execute(
                "PLACE_APPROACH",
                self._place_pose(offset_z=float(self.cfg["place_height"])),
                attached=True,
            )
            return "OPEN_AFTER_PLACE" if success else "FAILED"

        if state == "OPEN_AFTER_PLACE":
            await self._animate_gripper(float(self.cfg["gripper_open_position"]))
            await self._detach_pick_object()
            return "PLAN_RETREAT"

        if state == "PLAN_RETREAT":
            success = await self._plan_and_execute(
                "RETREAT",
                self._place_pose(offset_z=float(self.cfg["retreat_height"])),
                attached=False,
            )
            return "DONE" if success else "FAILED"

        return "FAILED"

    def _goal_position_from_marker(self, marker, offset_z: float) -> np.ndarray:
        marker_position, _ = marker.get_world_pose()
        world_goal_position = np.asarray(
            [
                marker_position[0],
                marker_position[1],
                marker_position[2] + offset_z,
            ],
            dtype=np.float32,
        )
        return self._world_position_to_robot_frame(world_goal_position)

    def _pick_pose(self, offset_z: float) -> np.ndarray:
        return self._goal_position_from_marker(self.pick_marker, offset_z)

    def _place_pose(self, offset_z: float) -> np.ndarray:
        return self._goal_position_from_marker(self.place_marker, offset_z)

    def _world_position_to_robot_frame(self, world_position: np.ndarray) -> np.ndarray:
        base_position, base_orientation = self.robot_root_prim.get_world_pose()
        return world_position_to_local_frame(
            np.asarray(world_position, dtype=np.float32),
            np.asarray(base_position, dtype=np.float32),
            np.asarray(base_orientation, dtype=np.float32),
        )

    def _task_orientation_in_robot_frame(self) -> np.ndarray:
        task_orientation = np.asarray(self.cfg["task_orientation"], dtype=np.float32)
        frame_name = str(self.cfg.get("task_orientation_frame", "world")).lower()
        if frame_name == "robot":
            return _normalize_quaternion(task_orientation)
        if frame_name == "world":
            _, base_orientation = self.robot_root_prim.get_world_pose()
            return world_orientation_to_local_frame(
                task_orientation,
                np.asarray(base_orientation, dtype=np.float32),
            )
        raise ValueError(
            "Unsupported task_orientation_frame. "
            f"Expected 'world' or 'robot', got {self.cfg.get('task_orientation_frame')}"
        )

    def _sim_joint_state_to_curobo(self) -> JointState:
        sim_js = self.robot.get_joints_state()
        if sim_js is None:
            raise RuntimeError("Robot joint state is not ready yet")

        positions = np.asarray(sim_js.positions, dtype=np.float32)
        velocities = np.asarray(
            sim_js.velocities if sim_js.velocities is not None else np.zeros_like(positions),
            dtype=np.float32,
        )
        zeros = np.zeros_like(positions)
        return JointState(
            position=self.tensor_args.to_device(positions),
            velocity=self.tensor_args.to_device(velocities * 0.0),
            acceleration=self.tensor_args.to_device(zeros),
            jerk=self.tensor_args.to_device(zeros),
            joint_names=self.robot_dof_names,
        )

    async def _plan_and_execute(self, label: str, goal_position: np.ndarray, attached: bool) -> bool:
        self._update_world(ignore_pick_object=not attached)
        try:
            full_js = self._sim_joint_state_to_curobo()
        except RuntimeError:
            print(f"STATE_MACHINE: {label} aborted because sim joints are not ready", flush=True)
            return False

        active_js = full_js.get_ordered_joint_state(self.motion_gen.kinematics.joint_names)
        goal_pose = Pose(
            position=self.tensor_args.to_device([goal_position.tolist()]),
            quaternion=self.tensor_args.to_device([self._task_orientation_in_robot_frame().tolist()]),
        )
        primary_plan_config = MotionGenPlanConfig(
            enable_graph=False,
            max_attempts=int(self.cfg["plan_max_attempts"]),
            timeout=float(self.cfg["plan_timeout"]),
            enable_finetune_trajopt=True,
        )
        fallback_plan_config = MotionGenPlanConfig(
            enable_graph=bool(self.cfg["plan_fallback_enable_graph"]),
            max_attempts=int(self.cfg["plan_max_attempts"]),
            timeout=float(self.cfg["plan_timeout"]),
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
            await next_frame(int(self.cfg["playback_frame_step"]))
            if self.object_attached:
                self._update_attached_object_pose()

    async def _animate_gripper(self, target_position: float) -> None:
        sim_js = self.robot.get_joints_state()
        current_positions = np.asarray(sim_js.positions, dtype=np.float32).copy()
        start_position = current_positions[self.gripper_indices[0]]
        for alpha in np.linspace(0.0, 1.0, int(self.cfg["gripper_animation_steps"])):
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
            await next_frame(1)

        self.gripper_target = target_position

    async def _attach_pick_object(self) -> None:
        self.object_attached = True
        self._update_attached_object_pose()
        if not bool(self.cfg["attach_object_to_collision_model"]):
            print("STATE_MACHINE: collision-model attachment is disabled in config", flush=True)
            return

        try:
            cu_js = self._sim_joint_state_to_curobo()
            self.motion_gen.attach_objects_to_robot(
                cu_js,
                [self.pick_object.prim_path],
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
            [
                place_position[0],
                place_position[1],
                place_position[2] + float(self.cfg["place_release_height_offset"]),
            ],
            dtype=np.float32,
        )
        self.pick_object.set_world_pose(
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
            self.cfg["attached_object_world_offset"],
            dtype=np.float32,
        )
        self.pick_object.set_world_pose(
            position=attached_position,
            orientation=np.asarray(ee_orientation, dtype=np.float32),
        )

    def _update_world(self, ignore_pick_object: bool) -> None:
        ignore_paths: List[str] = [
            self.robot_prim_path,
            "/World/defaultGroundPlane",
            "/curobo",
            self.pick_marker.prim_path,
            self.place_marker.prim_path,
        ] + self.static_ignore_paths
        if ignore_pick_object:
            ignore_paths.append(self.pick_object.prim_path)

        scene_world = self.usd_helper.get_obstacles_from_stage(
            only_paths=self.scene_collision_roots,
            reference_prim_path=self.robot_prim_path,
            ignore_substring=ignore_paths,
        ).get_collision_check_world()
        self.motion_gen.update_world(scene_world)
