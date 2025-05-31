# Third Party
import torch
import numpy as np

# cuRobo
from curobo.cuda_robot_model.cuda_robot_model import CudaRobotModel, CudaRobotModelState, CudaRobotModelConfig
from curobo.types.base import TensorDeviceType
from curobo.types.robot import RobotConfig
from curobo.types.math import Pose
from curobo.util_file import get_robot_path, join_path, load_yaml
from curobo.wrap.reacher.motion_gen import MotionGen, MotionGenConfig, MotionGenPlanConfig

class CuMotion:
    def __init__(self):

        # convenience function to store tensor type and device
        self.tensor_args = TensorDeviceType()
        self.motion_gen = None
        self.robots = {}
    
    def add_robot(self, yaml_file: str, robot_name: str = "robot1"):
        
        # config_file = load_yaml(yaml_file)

        motion_gen_config = MotionGenConfig.load_from_robot_config(
            yaml_file,
            # world_config,
            interpolation_dt=0.01,
        )
        motion_gen: MotionGen = MotionGen(motion_gen_config)
        motion_gen.warmup()

        self.robots[robot_name] = motion_gen

        print("warmup done")

    def check_joints(self, q: torch.Tensor, robot_name: str = "robot1"):
        robot: MotionGen = self.robots[robot_name]
        b, c = map(int, q.shape)
        if b!=1: # 只有一个维度
            print(f"Batch size mismatch: expected 1, got {b}")
            return False

        if c != robot.kinematics.get_dof():
            print(f"Joint size mismatch: expected {robot.kinematics.get_dof()}, got {c}")
            return False
        
        limit = robot.kinematics.get_joint_limits().position
        diff = (limit - q)
        if (diff[0] > 1e-3).any() or (diff[1] < -1e-3).any():
            print(f"Joint limits exceeded")
            return False

        return True

    def ik(self, pos: np.ndarray, rot: np.ndarray, robot_name: str = "robot1"):
        robot: MotionGen = self.robots[robot_name]
        goal = Pose(torch.tensor(pos, device=self.tensor_args.device, dtype=self.tensor_args.dtype),
             torch.tensor(rot, device=self.tensor_args.device, dtype=self.tensor_args.dtype))
        ik_result = robot.ik_solver.solve_single(goal)
        print(ik_result)
        return True, None, None

    def fk(self, q: np.ndarray, robot_name: str = "robot1"):
        """
        Forward kinematics
        :param q: joint angles
        :return: end-effector pose
        """
        q_tensor = torch.tensor(q, device=self.tensor_args.device, dtype=self.tensor_args.dtype)
        if not self.check_joints(q_tensor, robot_name):
            return False, None, None
        robot: MotionGen = self.robots[robot_name]
        state: CudaRobotModelState = robot.ik_solver.fk(q_tensor)
        return True, state.ee_position.cpu().numpy(), state.ee_quaternion.cpu().numpy()


if __name__ == "__main__":
    c = CuMotion()
    yaml_file = join_path(get_robot_path(), "ur5e.yml")
    c.add_robot(yaml_file)
    q1 = np.array([[0,0,0,0,0,70]])
    q1 = np.deg2rad(q1)  # Convert degrees to radians if necessary
    ret, pos, rot = c.fk(q1)
    print("End-effector position:", pos)
    print("End-effector orientation (quaternion):", rot)

    c.ik(pos, rot)