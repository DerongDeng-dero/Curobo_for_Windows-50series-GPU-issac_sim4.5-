@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "ISAAC_PYTHON=%SCRIPT_DIR%isaacsim_python.bat"
set "SMOKE_TEST=%SCRIPT_DIR%examples\isaac_sim\smoke_test_headless.py"

if not exist "%SMOKE_TEST%" (
    echo Smoke test script not found: "%SMOKE_TEST%"
    endlocal
    exit /B 1
)

call "%ISAAC_PYTHON%" -u "%SMOKE_TEST%"
set "EXIT_CODE=%ERRORLEVEL%"

if %EXIT_CODE% neq 0 (
    echo Smoke test failed.
    endlocal
    exit /B %EXIT_CODE%
)

echo Smoke test passed.
endlocal
exit /B 0
