@echo off

set "BAT_DIR=%~dp0"

python "%BAT_DIR%toredis.py" %*

