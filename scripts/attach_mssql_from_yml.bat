@echo off
setlocal EnableExtensions EnableDelayedExpansion

if /I "%~1"=="-h" goto :usage_ok
if /I "%~1"=="--help" goto :usage_ok

set /a ARG_COUNT=0
if not "%~1"=="" set /a ARG_COUNT+=1
if not "%~2"=="" set /a ARG_COUNT+=1
if not "%~3"=="" set /a ARG_COUNT+=1
if not "%~4"=="" goto :usage_error

if %ARG_COUNT% LSS 1 goto :usage_error
if %ARG_COUNT% GTR 3 goto :usage_error

set "DEFAULT_CONTAINER_NAME=vida-db"
set "CONTAINER_NAME="
set "YAML_FILE="
set "DB_FILES_DIR="

if %ARG_COUNT% EQU 1 (
    set "CONTAINER_NAME=%DEFAULT_CONTAINER_NAME%"
    set "YAML_FILE=%~1"
    set "DB_FILES_DIR=%VIDA_DB_HOST_PATH%"
) else if %ARG_COUNT% EQU 2 (
    set "FIRST_IS_YAML="
    if exist "%~1" set "FIRST_IS_YAML=1"
    if /I "%~x1"==".yml" set "FIRST_IS_YAML=1"
    if /I "%~x1"==".yaml" set "FIRST_IS_YAML=1"

    if defined FIRST_IS_YAML (
        set "CONTAINER_NAME=%DEFAULT_CONTAINER_NAME%"
        set "YAML_FILE=%~1"
        set "DB_FILES_DIR=%~2"
    ) else (
        set "CONTAINER_NAME=%~1"
        set "YAML_FILE=%~2"
        set "DB_FILES_DIR=%VIDA_DB_HOST_PATH%"
    )
) else (
    set "CONTAINER_NAME=%~1"
    set "YAML_FILE=%~2"
    set "DB_FILES_DIR=%~3"
)

if "%DB_FILES_DIR%"=="" (
    echo Error: DB files directory not provided and VIDA_DB_HOST_PATH is not set. 1>&2
    goto :usage_error
)

if not exist "%YAML_FILE%" (
    echo Error: YAML file not found: %YAML_FILE% 1>&2
    exit /b 1
)

if not exist "%DB_FILES_DIR%\" (
    echo Error: DB files directory not found: %DB_FILES_DIR% 1>&2
    exit /b 1
)

if not exist "%~dp0attach_mssql_from_yml.bat" (
    echo Error: script path validation failed. 1>&2
    exit /b 1
)

set "CURRENT_DB="
set "CURRENT_MDF="
set "CURRENT_LDF="
set /a ENTRY_COUNT=0

for /f "usebackq delims=" %%L in ("%YAML_FILE%") do (
    set "LINE=%%L"
    call :process_line
    if errorlevel 1 exit /b 1
)

call :run_entry
if errorlevel 1 exit /b 1

if %ENTRY_COUNT% EQU 0 (
    echo Error: No valid database entries found in YAML file. 1>&2
    exit /b 1
)

echo Done. Processed %ENTRY_COUNT% database^(s^).
exit /b 0

:process_line
set "TRIM=%LINE%"
for /f "tokens=* delims= " %%A in ("%TRIM%") do set "TRIM=%%A"

if /I "%TRIM:~0,11%"=="- database:" (
    call :run_entry
    if errorlevel 1 exit /b 1
    set "VALUE=%TRIM:~11%"
    call :normalize_value VALUE CURRENT_DB
    goto :eof
)

if /I "%TRIM:~0,9%"=="database:" (
    set "VALUE=%TRIM:~9%"
    call :normalize_value VALUE CURRENT_DB
    goto :eof
)

if /I "%TRIM:~0,4%"=="mdf:" (
    set "VALUE=%TRIM:~4%"
    call :normalize_value VALUE CURRENT_MDF
    goto :eof
)

if /I "%TRIM:~0,4%"=="ldf:" (
    set "VALUE=%TRIM:~4%"
    call :normalize_value VALUE CURRENT_LDF
    goto :eof
)

goto :eof

:normalize_value
set "RAW=!%~1!"
for /f "tokens=* delims= " %%A in ("!RAW!") do set "RAW=%%A"
if defined RAW (
    if "!RAW:~0,1!"=="\"" if "!RAW:~-1!"=="\"" set "RAW=!RAW:~1,-1!"
    if "!RAW:~0,1!"=="'" if "!RAW:~-1!"=="'" set "RAW=!RAW:~1,-1!"
)
set "%~2=!RAW!"
goto :eof

:build_file_path
set "FILE_NAME=!%~1!"
for %%F in ("!FILE_NAME!") do set "FILE_NAME=%%~nxF"
set "%~2=%DB_FILES_DIR%\!FILE_NAME!"
goto :eof

:run_entry
if "%CURRENT_DB%%CURRENT_MDF%%CURRENT_LDF%"=="" goto :eof

if "%CURRENT_DB%"=="" goto :incomplete_entry
if "%CURRENT_MDF%"=="" goto :incomplete_entry
if "%CURRENT_LDF%"=="" goto :incomplete_entry

call :build_file_path CURRENT_MDF MDF_PATH
call :build_file_path CURRENT_LDF LDF_PATH

echo Attaching database '%CURRENT_DB%'...
call :attach_db "%MDF_PATH%" "%LDF_PATH%" "%CURRENT_DB%" "%CONTAINER_NAME%"
if errorlevel 1 exit /b 1

set /a ENTRY_COUNT+=1
set "CURRENT_DB="
set "CURRENT_MDF="
set "CURRENT_LDF="
goto :eof

:incomplete_entry
echo Error: Incomplete entry in YAML. Required keys: database, mdf, ldf 1>&2
exit /b 1

:attach_db
set "MDF_PATH=%~1"
set "LDF_PATH=%~2"
set "DB_NAME=%~3"
set "TARGET_CONTAINER=%~4"
set "TARGET_DIR=/var/opt/mssql/data"

if not exist "%MDF_PATH%" (
    echo Error: MDF file not found: %MDF_PATH% 1>&2
    exit /b 1
)

if not exist "%LDF_PATH%" (
    echo Error: LDF file not found: %LDF_PATH% 1>&2
    exit /b 1
)

where docker >nul 2>&1
if errorlevel 1 (
    echo Error: docker is not installed or not in PATH. 1>&2
    exit /b 1
)

set "CONTAINER_RUNNING="
for /f "delims=" %%R in ('docker inspect -f "{{.State.Running}}" "%TARGET_CONTAINER%" 2^>nul') do set "CONTAINER_RUNNING=%%R"
if /I not "%CONTAINER_RUNNING%"=="true" (
    echo Error: container '%TARGET_CONTAINER%' is not running. 1>&2
    exit /b 1
)

set "SA_PASSWORD=%MSSQL_SA_PASSWORD%"
if not defined SA_PASSWORD (
    for /f "tokens=1,* delims==" %%A in ('docker inspect -f "{{range .Config.Env}}{{println .}}{{end}}" "%TARGET_CONTAINER%" 2^>nul ^| findstr /B /C:"MSSQL_SA_PASSWORD="') do set "SA_PASSWORD=%%B"
)

if not defined SA_PASSWORD (
    echo Error: MSSQL SA password is missing. Set MSSQL_SA_PASSWORD or ensure the container has MSSQL_SA_PASSWORD configured. 1>&2
    exit /b 1
)

docker exec "%TARGET_CONTAINER%" test -x /opt/mssql-tools18/bin/sqlcmd >nul 2>&1
if not errorlevel 1 (
    set "SQLCMD_BIN=/opt/mssql-tools18/bin/sqlcmd"
) else (
    docker exec "%TARGET_CONTAINER%" test -x /opt/mssql-tools/bin/sqlcmd >nul 2>&1
    if not errorlevel 1 (
        set "SQLCMD_BIN=/opt/mssql-tools/bin/sqlcmd"
    ) else (
        echo Error: sqlcmd not found in container '%TARGET_CONTAINER%'. 1>&2
        exit /b 1
    )
)

for %%F in ("%MDF_PATH%") do set "MDF_BASENAME=%%~nxF"
for %%F in ("%LDF_PATH%") do set "LDF_BASENAME=%%~nxF"
set "MDF_TARGET=%TARGET_DIR%/%MDF_BASENAME%"
set "LDF_TARGET=%TARGET_DIR%/%LDF_BASENAME%"

echo Copying data files into container...
docker cp "%MDF_PATH%" "%TARGET_CONTAINER%:%MDF_TARGET%"
if errorlevel 1 exit /b 1
docker cp "%LDF_PATH%" "%TARGET_CONTAINER%:%LDF_TARGET%"
if errorlevel 1 exit /b 1

set "DB_NAME_ESCAPED=%DB_NAME:]=]]%"
set "DB_NAME_SQL=%DB_NAME:'=''%"

set "DB_EXISTS="
for /f "usebackq delims=" %%E in (`docker exec -e SQLCMDPASSWORD="%SA_PASSWORD%" "%TARGET_CONTAINER%" "%SQLCMD_BIN%" -S localhost -U sa -C -h -1 -W -Q "SET NOCOUNT ON; SELECT CASE WHEN DB_ID(N'%DB_NAME_SQL%') IS NULL THEN 0 ELSE 1 END;" 2^>nul`) do set "DB_EXISTS=%%E"
set "DB_EXISTS=%DB_EXISTS: =%"

if /I "%DB_EXISTS%"=="1" (
    echo Skipped. Database '%DB_NAME%' already exists in container '%TARGET_CONTAINER%'.
    exit /b 0
)

set "SQL=CREATE DATABASE [%DB_NAME_ESCAPED%] ON (FILENAME = N'%MDF_TARGET%'), (FILENAME = N'%LDF_TARGET%') FOR ATTACH;"

echo Attaching database '%DB_NAME%' to SQL Server in container '%TARGET_CONTAINER%'...
docker exec -e SQLCMDPASSWORD="%SA_PASSWORD%" "%TARGET_CONTAINER%" "%SQLCMD_BIN%" -S localhost -U sa -C -b -Q "%SQL%"
if errorlevel 1 exit /b 1

echo Done. Database '%DB_NAME%' attached successfully.
exit /b 0

:usage_ok
call :usage
exit /b 0

:usage_error
call :usage
exit /b 1

:usage
echo Usage:
echo   attach_mssql_from_yml.bat ^<path-to-db_files.yml^> [db-files-directory]
echo   attach_mssql_from_yml.bat [container-name] ^<path-to-db_files.yml^> [db-files-directory]
echo.
echo Arguments:
echo   container-name         Optional. Name of the running SQL Server container.
echo                          Defaults to 'vida-db' when omitted.
echo   path-to-db_files.yml   Path to YAML file containing database entries.
echo                          Expected entry keys: database, mdf, ldf
echo   db-files-directory     Optional. Directory containing MDF/LDF files referenced by YAML.
echo                          If omitted, VIDA_DB_HOST_PATH is used.
echo.
echo Notes:
echo   - mdf/ldf values in YAML are treated as filenames.
echo   - Paths are built as ^<db-files-directory^>\^<mdf-or-ldf-filename^>.
echo   - If [db-files-directory] is omitted, VIDA_DB_HOST_PATH must be set.
echo   - Each entry is attached by executing docker commands directly.
goto :eof
