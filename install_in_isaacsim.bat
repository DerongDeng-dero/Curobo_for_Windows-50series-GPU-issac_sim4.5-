@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "ISAAC_PYTHON=%SCRIPT_DIR%isaacsim_python.bat"
for %%I in ("%SCRIPT_DIR%..\..") do set "ISAAC_SIM_ROOT=%%~fI"
set "ISAAC_KIT_PYTHON=%ISAAC_SIM_ROOT%\python.bat"
set "PYTHON_PACKAGES=%ISAAC_SIM_ROOT%\python_packages"
set "TMP=%ISAAC_SIM_ROOT%\tmp"
set "TEMP=%ISAAC_SIM_ROOT%\tmp"
set "PIP_CACHE_DIR=%ISAAC_SIM_ROOT%\pip-cache"

if not exist "%ISAAC_PYTHON%" (
    echo Helper script not found: "%ISAAC_PYTHON%"
    endlocal
    exit /B 1
)
if not exist "%ISAAC_KIT_PYTHON%" (
    echo Isaac Sim python not found: "%ISAAC_KIT_PYTHON%"
    endlocal
    exit /B 1
)

pushd "%SCRIPT_DIR%"

if not exist "%TMP%" mkdir "%TMP%"
if not exist "%PIP_CACHE_DIR%" mkdir "%PIP_CACHE_DIR%"

echo [1/4] Checking Isaac Sim Python environment...
call "%ISAAC_PYTHON%" -c "import isaacsim, torch; print('isaacsim ok'); print(torch.__version__)"
if errorlevel 1 goto Error

echo [2/4] Installing RTX 50 compatible torch overlay...
call "%ISAAC_PYTHON%" -c "import sys, torch; sys.exit(0 if torch.__version__ == '2.7.1+cu128' and 'python_packages' in torch.__file__.lower() else 1)"
if errorlevel 1 (
    call "%ISAAC_KIT_PYTHON%" -m pip install --upgrade --target "%PYTHON_PACKAGES%" --index-url https://download.pytorch.org/whl/cu128 --progress-bar off --no-deps torch==2.7.1+cu128 torchvision==0.22.1+cu128 torchaudio==2.7.1+cu128
    if errorlevel 1 goto Error
) else (
    echo torch overlay already installed, skipping.
)

echo [3/4] Verifying torch overlay...
call "%ISAAC_PYTHON%" -c "import torch, numpy, PIL; print('torch', torch.__version__, torch.__file__); print('numpy', numpy.__version__, numpy.__file__); print('pillow', PIL.__version__, PIL.__file__)"
if errorlevel 1 goto Error

echo [4/4] Installing cuRobo into Isaac Sim...
call "%ISAAC_PYTHON%" -m pip install -e . --no-build-isolation
if errorlevel 1 goto Error

echo Installation complete.
popd
endlocal
exit /B 0

:Error
echo Installation failed.
popd
endlocal
exit /B 1
