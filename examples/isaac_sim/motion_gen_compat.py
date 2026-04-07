from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

import numpy as np

from curobo.types.robot import JointState


@dataclass
class MotionGenCompatPlanResult:
    result: object
    success: bool
    used_pre_finetune_plan: bool = False
    used_finetune_disabled_retry: bool = False


def describe_dof_layout(
    log_prefix: str,
    full_joint_names: Sequence[str],
    active_joint_names: Sequence[str],
    robot_dof_names: Sequence[str],
) -> None:
    print(
        f"{log_prefix}: dof summary "
        f"planner={len(active_joint_names)} "
        f"config_full={len(full_joint_names)} "
        f"sim={len(robot_dof_names)}",
        flush=True,
    )


def get_retract_state_for_articulation(
    motion_gen,
    tensor_args,
    full_joint_names: Sequence[str],
    full_retract_config: Sequence[float],
    robot_dof_names: Sequence[str],
) -> Tuple[JointState, JointState]:
    q_start_full = JointState.from_position(
        tensor_args.to_device(np.asarray(full_retract_config, dtype=np.float32)).view(1, -1),
        joint_names=list(full_joint_names),
    )
    q_start = motion_gen.get_active_js(q_start_full)
    q_start_full = motion_gen.get_full_js(q_start).get_ordered_joint_state(list(robot_dof_names))
    return q_start, q_start_full


def get_full_articulation_plan(motion_gen, active_plan, robot_dof_names: Sequence[str]) -> JointState:
    full_plan = motion_gen.get_full_js(active_plan)
    return full_plan.get_ordered_joint_state(list(robot_dof_names))


def plan_single_with_compat(
    motion_gen,
    start_state,
    goal_pose,
    primary_plan_config,
    fallback_plan_config=None,
    log_prefix: str = "MOTION_GEN",
) -> MotionGenCompatPlanResult:
    result = motion_gen.plan_single(start_state, goal_pose, primary_plan_config)
    success, used_pre_finetune_plan = _accept_pre_finetune_plan(result, log_prefix)
    used_finetune_disabled_retry = False

    if (
        not success
        and fallback_plan_config is not None
        and "FINETUNE_TRAJOPT_FAIL" in str(result.status)
    ):
        print(f"{log_prefix}: retrying without finetune trajopt", flush=True)
        motion_gen.reset_seed()
        result = motion_gen.plan_single(start_state, goal_pose, fallback_plan_config)
        success, fallback_used_pre_finetune = _accept_pre_finetune_plan(result, log_prefix)
        used_pre_finetune_plan = used_pre_finetune_plan or fallback_used_pre_finetune
        used_finetune_disabled_retry = True

    return MotionGenCompatPlanResult(
        result=result,
        success=success,
        used_pre_finetune_plan=used_pre_finetune_plan,
        used_finetune_disabled_retry=used_finetune_disabled_retry,
    )


def _accept_pre_finetune_plan(result, log_prefix: str) -> Tuple[bool, bool]:
    success = bool(result.success.item())
    if success or "FINETUNE_TRAJOPT_FAIL" not in str(result.status):
        return success, False

    pre_finetune_plan = _get_interpolated_plan(result)
    if pre_finetune_plan is None:
        return False, False

    print(f"{log_prefix}: using pre-finetune trajectory", flush=True)
    result.success[:] = True
    return True, True


def _get_interpolated_plan(result) -> Optional[JointState]:
    try:
        plan = result.get_interpolated_plan()
    except Exception:
        return None

    if plan is None or getattr(plan, "position", None) is None:
        return None

    if plan.position.shape[0] <= 0:
        return None

    return plan
