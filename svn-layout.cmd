REM @echo off
if ["%~1"] == [""] (
    echo "usage: %0 <svn-path>"
) else (
    svn mkdir %1 %1/trunk %1/branches %1/tags -m "New project %1" --parents
)
