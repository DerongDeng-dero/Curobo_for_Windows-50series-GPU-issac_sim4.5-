@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "ISAAC_SIM_ROOT=%SCRIPT_DIR%..\.."

if /I "%~1"=="--isaac-root" (
    if "%~2"=="" (
        echo Missing path after --isaac-root
        endlocal
        exit /B 1
    )
    set "ISAAC_SIM_ROOT=%~2"
    shift
    shift
)

set "FORWARD_ARGS="
:collect_args
if "%~1"=="" goto after_collect
set "FORWARD_ARGS=%FORWARD_ARGS% "%~1""
shift
goto collect_args
:after_collect

for %%I in ("%ISAAC_SIM_ROOT%") do set "ISAAC_SIM_ROOT=%%~fI"

if not exist "%ISAAC_SIM_ROOT%\kit\python.bat" (
    echo Isaac Sim kit python not found: "%ISAAC_SIM_ROOT%\kit\python.bat"
    endlocal
    exit /B 1
)

set "ISAAC_PATH=%ISAAC_SIM_ROOT%"
set "EXP_PATH=%ISAAC_SIM_ROOT%\apps"
set "CARB_APP_PATH=%ISAAC_SIM_ROOT%\kit"
set "OMNI_KIT_ACCEPT_EULA=YES"
set "ORIGINAL_PYTHONPATH=%PYTHONPATH%"

set "PYTHONPATH=%ISAAC_SIM_ROOT%\python_packages;%ISAAC_SIM_ROOT%\site"
if exist "%ISAAC_SIM_ROOT%\exts\omni.isaac.core_archive\pip_prebundle" (
    set "PYTHONPATH=%PYTHONPATH%;%ISAAC_SIM_ROOT%\exts\omni.isaac.core_archive\pip_prebundle"
)
if exist "%ISAAC_SIM_ROOT%\exts\omni.isaac.ml_archive\pip_prebundle" (
    set "PYTHONPATH=%PYTHONPATH%;%ISAAC_SIM_ROOT%\exts\omni.isaac.ml_archive\pip_prebundle"
)
if exist "%ISAAC_SIM_ROOT%\exts\omni.pip.compute\pip_prebundle" (
    set "PYTHONPATH=%PYTHONPATH%;%ISAAC_SIM_ROOT%\exts\omni.pip.compute\pip_prebundle"
)
if exist "%ISAAC_SIM_ROOT%\exts\omni.pip.cloud\pip_prebundle" (
    set "PYTHONPATH=%PYTHONPATH%;%ISAAC_SIM_ROOT%\exts\omni.pip.cloud\pip_prebundle"
)
if defined ORIGINAL_PYTHONPATH (
    set "PYTHONPATH=%PYTHONPATH%;%ORIGINAL_PYTHONPATH%"
)

call "%ISAAC_SIM_ROOT%\kit\python.bat" %FORWARD_ARGS%
set "EXIT_CODE=%ERRORLEVEL%"

endlocal & exit /B %EXIT_CODE%
