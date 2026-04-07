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
"""
cuRoboLib module contains CUDA implementations (kernels) of robotics algorithms, wrapped in
C++, and compiled with PyTorch for use in Python.

All implementations are in ``.cu`` files in ``cpp`` sub-directory.
"""

# Standard Library
import os
import pathlib
import sys

_DLL_DIRECTORIES = []


def _prepare_windows_torch_dlls():
    if sys.platform != "win32":
        return

    # Import torch before native extensions so its DLLs are available to dependent .pyd modules.
    import torch

    if not hasattr(os, "add_dll_directory"):
        return

    torch_lib_dir = pathlib.Path(torch.__file__).resolve().parent / "lib"
    if torch_lib_dir.exists():
        _DLL_DIRECTORIES.append(os.add_dll_directory(str(torch_lib_dir)))


_prepare_windows_torch_dlls()

del _prepare_windows_torch_dlls
