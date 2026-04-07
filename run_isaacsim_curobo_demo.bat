@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..") do set "ISAAC_SIM_ROOT=%%~fI"

set "OMNI_KIT_ACCEPT_EULA=YES"

if not defined CUROBO_DEMO_SCRIPT set "CUROBO_DEMO_SCRIPT=%SCRIPT_DIR%examples\isaac_sim\motion_gen_reacher.py"

call "%ISAAC_SIM_ROOT%\isaac-sim.bat" --info --exec "%CUROBO_DEMO_SCRIPT%"
