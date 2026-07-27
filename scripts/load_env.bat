@echo off

set "ENV_FILE=.env"
set "ENV_FILE_SET=0"
set /a LOADED=0

if /I "%~1"=="-h" goto :usage
if /I "%~1"=="--help" goto :usage

:parse_args
if "%~1"=="" goto :args_done
if "%ENV_FILE_SET%"=="1" (
    echo Error: unexpected argument "%~1"
    goto :usage_error
)
set "ENV_FILE=%~1"
set "ENV_FILE_SET=1"
shift
goto :parse_args

:args_done
if not exist "%ENV_FILE%" (
    echo Error: env file not found: %ENV_FILE%
    exit /b 1
)

for /f "usebackq delims=" %%L in ("%ENV_FILE%") do (
    call :process_line "%%L"
)

echo Loaded %LOADED% variable(s) from %ENV_FILE%.
exit /b 0

:process_line
set "line=%~1"
call :trim line
if not defined line goto :eof
if "%line:~0,1%"=="#" goto :eof

if /I "%line:~0,7%"=="export " (
    set "line=%line:~7%"
    call :trim line
)

set "key="
set "value="

for /f "tokens=1* delims==" %%A in ("%line%") do (
    set "key=%%A"
    set "value=%%B"
)

call :trim key

if not defined key goto :eof
if not defined value goto :eof

set "%key%=%value%"
set /a LOADED+=1
goto :eof

:trim
call set "_tmp=%%%~1%%"
if not defined _tmp (
    set "%~1="
    goto :eof
)

for /f "tokens=* delims= " %%A in ("%_tmp%") do set "_tmp=%%A"
:trim_right
if "%_tmp%"=="" goto :trim_done
if "%_tmp:~-1%"==" " (
    set "_tmp=%_tmp:~0,-1%"
    goto :trim_right
)
:trim_done
set "%~1=%_tmp%"
goto :eof

:usage
 echo Usage:
 echo   scripts\load_env.bat [path-to-env-file]
 echo.
 echo Arguments:
 echo   path-to-env-file   Optional. Defaults to .env in current directory.
 echo.
 echo Notes:
 echo   - Existing environment variables are overwritten by default.
 echo   - Supports lines in KEY=VALUE format, with optional leading "export ".
 echo   - Blank lines and lines starting with # are ignored.
 echo   - To use from another batch file, call it with CALL.
 exit /b 0

:usage_error
call :usage
exit /b 1
