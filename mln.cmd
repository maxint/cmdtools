@echo off
setlocal EnableExtensions EnableDelayedexpansion

if ["%~1"] == [""] (
    REM print help
    echo.
    echo usage:
    echo    %~n0 source [destination]
    echo.
) else if ["%~2"] == [""] (
    call :get_file_name filename %1
    call :is_dir isdir %1
    call :ln_file_or_dir %%isdir%% "!filename!" %1
) else (
    call :is_dir isdir %1
    call :ln_file_or_dir %%isdir%% %2 %1
)
endlocal
goto :eof


:get_file_name
REM usage:      call :get_file_name filename FilePath
REM echo %1
REM echo %2
for %%I in (%2) do set %~1=%%~nI%%~xI
goto :eof


:is_dir
REM usage:      call :is_dir isdir DirName
(2>c:\WINDOWS\Temp\null pushd %2) || (set %1=0 & goto :eof)
set %1=1
popd
goto :eof


:print_info
REM usage:      call print_info DST SRC
echo ==================================
echo Created: %~2
echo Target at: %~1
echo ==================================
goto :eof


:ln_file_or_dir
REM usage:      call ln_file_or_dir IS_DIR DST SRC
REM echo %1
if %1 == 1 (
    echo INFO: %3 is a directory.
    set LN_CMD=jun
) else (
    echo INFO: %3 is a file.
    set LN_CMD=fsutil hardlink create
)
REM @echo on
%LN_CMD% %2 %3
REM @echo off
goto :eof
