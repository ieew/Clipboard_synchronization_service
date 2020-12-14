@echo off
color b
mode con cols=45 lines=10
set "PYTHON_PATH=Q:\Python38"

set "PATH=C:\bash\bin;C:\bash\lib;C:\bash\share;%PYTHON_PATH%;%PYTHON_PATH%\Scripts;%PYTHON_PATH%\DLLs;%PATH%"
start "" "D:\data\VSCode\Code.exe" "%~dp0"