#
# Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.
#

"""curobo package setuptools."""

# NOTE: This file is still needed to allow the package to be
# installed in editable mode.
#
# References:
# * https://setuptools.pypa.io/en/latest/setuptools.html#setup-cfg-only-projects

# Standard Library
import glob
import os
import sys

# Third Party
import setuptools


_WINDOWS_PREBUILT_EXTENSIONS = [
    "lbfgs_step_cu",
    "kinematics_fused_cu",
    "line_search_cu",
    "tensor_step_cu",
    "geom_cu",
]


def _has_windows_prebuilt_extensions():
    if sys.platform != "win32":
        return False
    extension_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "src", "curobo", "curobolib"
    )
    for extension_name in _WINDOWS_PREBUILT_EXTENSIONS:
        if not glob.glob(os.path.join(extension_dir, f"{extension_name}*.pyd")):
            return False
    return True


def _needs_cuda_extensions(argv):
    build_commands = {
        "bdist",
        "bdist_wheel",
        "build",
        "build_clib",
        "build_ext",
        "develop",
        "editable_wheel",
        "install",
        "install_ext",
        "install_lib",
    }
    return any(arg in build_commands for arg in argv[1:])


def _get_build_configuration():
    if not _needs_cuda_extensions(sys.argv):
        return [], {}
    if os.environ.get("CUROBO_FORCE_BUILD", "0") != "1" and _has_windows_prebuilt_extensions():
        print("Using prebuilt Windows cuRobo extensions; skipping CUDA compilation.")
        return [], {}

    try:
        from torch.utils.cpp_extension import BuildExtension, CUDAExtension
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Building cuRobo CUDA extensions requires PyTorch build helpers. "
            "Use Isaac Sim's python.bat or add omni.isaac.ml_archive/pip_prebundle "
            "to PYTHONPATH, then install with --no-build-isolation."
        ) from exc

    extra_cuda_args = {
        "cxx": [],
        "nvcc": [
            "--threads=8",
            "-O3",
            "--ftz=true",
            "--fmad=true",
            "--prec-div=false",
            "--prec-sqrt=false",
        ]
    }

    if sys.platform == "win32":
        extra_cuda_args["cxx"].append("/D_ALLOW_COMPILER_AND_STL_VERSION_MISMATCH")
        extra_cuda_args["nvcc"].extend(
            [
                "--allow-unsupported-compiler",
                "-D_ALLOW_COMPILER_AND_STL_VERSION_MISMATCH",
                "-Xcompiler",
                "/D_ALLOW_COMPILER_AND_STL_VERSION_MISMATCH",
            ]
        )

    ext_modules = [
        CUDAExtension(
            "curobo.curobolib.lbfgs_step_cu",
            [
                "src/curobo/curobolib/cpp/lbfgs_step_cuda.cpp",
                "src/curobo/curobolib/cpp/lbfgs_step_kernel.cu",
            ],
            extra_compile_args=extra_cuda_args,
        ),
        CUDAExtension(
            "curobo.curobolib.kinematics_fused_cu",
            [
                "src/curobo/curobolib/cpp/kinematics_fused_cuda.cpp",
                "src/curobo/curobolib/cpp/kinematics_fused_kernel.cu",
            ],
            extra_compile_args=extra_cuda_args,
        ),
        CUDAExtension(
            "curobo.curobolib.line_search_cu",
            [
                "src/curobo/curobolib/cpp/line_search_cuda.cpp",
                "src/curobo/curobolib/cpp/line_search_kernel.cu",
                "src/curobo/curobolib/cpp/update_best_kernel.cu",
            ],
            extra_compile_args=extra_cuda_args,
        ),
        CUDAExtension(
            "curobo.curobolib.tensor_step_cu",
            [
                "src/curobo/curobolib/cpp/tensor_step_cuda.cpp",
                "src/curobo/curobolib/cpp/tensor_step_kernel.cu",
            ],
            extra_compile_args=extra_cuda_args,
        ),
        CUDAExtension(
            "curobo.curobolib.geom_cu",
            [
                "src/curobo/curobolib/cpp/geom_cuda.cpp",
                "src/curobo/curobolib/cpp/sphere_obb_kernel.cu",
                "src/curobo/curobolib/cpp/pose_distance_kernel.cu",
                "src/curobo/curobolib/cpp/self_collision_kernel.cu",
            ],
            extra_compile_args=extra_cuda_args,
        ),
    ]
    return ext_modules, {"build_ext": BuildExtension}


ext_modules, cmdclass = _get_build_configuration()

setuptools.setup(
    ext_modules=ext_modules,
    cmdclass=cmdclass,
    package_data={"": ["*.so"]},
    include_package_data=True,
)
